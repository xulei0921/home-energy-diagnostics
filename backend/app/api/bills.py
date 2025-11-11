from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas, dependencies
from ..database import get_db
from ..crud import bills as bills_crud
from typing import List, Optional

router = APIRouter()

# 获取当前用户所有账单列表（支持筛选）
@router.get("/", response_model=List[schemas.EnergyBillResponse])
def get_bills(
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user),
    bill_type: Optional[schemas.BillType] = None
):
    bills = bills_crud.get_bills(db, user_id=current_user.id, bill_type=bill_type)
    return bills

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

# 创建账单
@router.post("/", response_model=schemas.EnergyBillResponse)
def create_bill(
    bill: schemas.EnergyBillCreate,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    return bills_crud.create_bill(db, bill=bill, user_id=current_user.id)