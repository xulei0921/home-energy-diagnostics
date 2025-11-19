from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from .. import schemas, models
from typing import Optional, Tuple, List
from datetime import date

# 获取当前用户所有账单列表（支持筛选）
def get_bills(
    db: Session,
    user_id: int,
    bill_type: Optional[schemas.BillType] = None,
    bill_date: Optional[date] = None,
    page: int = 1,
    page_size: int = 5
):
    query = db.query(models.EnergyBill).filter(models.EnergyBill.user_id == user_id)

    # 按账单类型筛选
    if bill_type:
        query = query.filter(models.EnergyBill.bill_type == bill_type)

    if bill_date:
        query = query.filter(models.EnergyBill.bill_date == bill_date)

    # 查询符合条件的总记录数
    total = query.count()

    # offset: 计算需要跳过的记录数
    offset = (page - 1) * page_size

    # 执行查询
    # return query.order_by(models.EnergyBill.bill_date.desc()).all()

    # 应用分页
    # limit: 限制返回的记录数
    items = query.order_by(models.EnergyBill.bill_date.desc()).offset(offset).limit(page_size).all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": ( total + page_size - 1 ) // page_size  # 计算总页数
    }

# 获取账单 by ID
def get_bill_by_id(
    db: Session,
    user_id: int,
    bill_id: int
):
    return db.query(models.EnergyBill).filter(
        models.EnergyBill.id == bill_id,
        models.EnergyBill.user_id == user_id
    ).first()

# 创建账单
def create_bill(db: Session, bill: schemas.EnergyBillCreate, user_id: int):
    # 检查该类型当月账单是否已存在
    db_bill = db.query(models.EnergyBill).filter(
        models.EnergyBill.user_id == user_id,
        models.EnergyBill.bill_type == bill.bill_type,
        models.EnergyBill.bill_date == bill.bill_date
    ).first()

    if db_bill:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该类型当月账单已存在"
        )

    # 创建账单信息对象
    db_bill = models.EnergyBill(**bill.model_dump(), user_id=user_id)

    # 保存账单信息
    db.add(db_bill)
    db.commit()
    db.refresh(db_bill)

    return db_bill

# 修改账单
def update_bill(db: Session, bill_id: int, bill_update: schemas.EnergyBillUpdate, user_id: int):
    db_bill = get_bill_by_id(db, user_id=user_id, bill_id=bill_id)

    if not db_bill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="账单不存在"
        )

    if db_bill.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限修改此账单"
        )

    # 更新字段
    update_data = bill_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_bill, key, value)

    db.commit()
    db.refresh(db_bill)

    return db_bill

# 删除账单
def delete_bill(db: Session, bill_id: int, user_id: int):
    db_bill = get_bill_by_id(db, user_id=user_id, bill_id=bill_id)

    if not db_bill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="账单不存在"
        )

    db.delete(db_bill)
    db.commit()

    return db_bill