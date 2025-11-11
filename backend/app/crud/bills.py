from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from .. import schemas, models
from typing import Optional

# 获取当前用户所有账单列表（支持筛选）
def get_bills(
    db: Session,
    user_id: int,
    bill_type: Optional[schemas.BillType] = None
):
    query = db.query(models.EnergyBill).filter(models.EnergyBill.user_id == user_id)

    # 按账单类型筛选
    if bill_type:
        query = query.filter(models.EnergyBill.bill_type == bill_type)

    # 执行查询
    return query.order_by(models.EnergyBill.bill_date.desc()).all()

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