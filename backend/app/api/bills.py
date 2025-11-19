from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas, dependencies
from ..database import get_db
from ..crud import bills as bills_crud
from typing import List, Optional
from datetime import date

router = APIRouter()

# 获取当前用户所有账单列表（支持筛选）
@router.get("/", response_model=schemas.PaginatedBillResponse)
def get_bills(
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user),
    bill_type: Optional[schemas.BillType] = None,
    bill_date: Optional[date] = None,
    page: int = 1,
    page_size: int = 5
):
    # bills = bills_crud.get_bills(db, user_id=current_user.id, bill_type=bill_type)
    # return bills

    # 验证分页参数合法性
    if page < 1:
        raise HTTPException(status_code=400, detail="页码不能小于1")
    if page_size < 1 or page_size > 100:
        raise HTTPException(status_code=400, detail="每页数量必须在1~100之间")

    return bills_crud.get_bills(
        db,
        user_id=current_user.id,
        bill_type=bill_type,
        bill_date=bill_date,
        page=page,
        page_size=page_size
    )

# 获取账单 by ID
@router.get("/{bill_id}", response_model=schemas.EnergyBillResponse)
def get_bill_by_id(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    db_bill = bills_crud.get_bill_by_id(db, user_id=current_user.id, bill_id=bill_id)

    if db_bill is None:
        raise HTTPException(status_code=404, detail="账单不存在")

    return db_bill

# 修改账单
@router.put("/{bill_id}", response_model=schemas.EnergyBillResponse)
def update_bill(
    bill_id: int,
    bill_update: schemas.EnergyBillUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    return bills_crud.update_bill(db, bill_id=bill_id, bill_update=bill_update, user_id=current_user.id)

# 删除账单
@router.delete("/{bill_id}")
def delete_bill(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    return bills_crud.delete_bill(db, bill_id=bill_id, user_id=current_user.id)

# 创建账单
@router.post("/", response_model=schemas.EnergyBillResponse)
def create_bill(
    bill: schemas.EnergyBillCreate,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    return bills_crud.create_bill(db, bill=bill, user_id=current_user.id)
