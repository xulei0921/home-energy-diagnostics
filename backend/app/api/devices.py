from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas, dependencies
from ..database import get_db
from ..crud import devices as devices_crud
from typing import List, Optional

router = APIRouter()

# 获取当前用户设备列表（支持筛选）
@router.get("/", response_model=List[schemas.DeviceResponse])
def get_devices(
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user),
    device_type: Optional[schemas.DeviceType] = None
):
    devices = devices_crud.get_devices(db, user_id=current_user.id, device_type=device_type)

    return devices

# 新增设备
@router.post("/", response_model=schemas.DeviceResponse)
def create_device(
    device: schemas.DeviceCreate,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    return devices_crud.create_device(db, device=device, user_id=current_user.id)

# 新增设备使用记录
@router.post("/usage", response_model=schemas.DeviceUsageResponse)
def create_device_usage(
    usage: schemas.DeviceUsageCreate,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    return devices_crud.create_device_usage(db, device_usage=usage, user_id=current_user.id)