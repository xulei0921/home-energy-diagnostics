from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas, dependencies
from ..database import get_db
from ..crud import devices as devices_crud
from typing import List, Optional
from datetime import date

router = APIRouter()

# 获取当前用户设备列表（支持筛选）
@router.get("/", response_model=schemas.PaginatedDeviceResponse)
def get_devices(
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user),
    device_type: Optional[schemas.DeviceType] = None,
    page: int = 1,
    page_size: int = 5
):
    # devices = devices_crud.get_devices(db, user_id=current_user.id, device_type=device_type)
    #
    # return devices

    # 验证分页参数合法性
    if page < 1:
        raise HTTPException(status_code=400, detail="页码不能小于1")
    if page_size < 1 or page_size > 100:
        raise HTTPException(status_code=400, detail="每页数量必须在1~100之间")

    return devices_crud.get_devices(
        db,
        user_id=current_user.id,
        device_type=device_type,
        page=page,
        page_size=page_size
    )

# 获取设备 by ID
@router.get("/{device_id}", response_model=schemas.DeviceResponse)
def get_device_by_id(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user),
):
    db_device = devices_crud.get_device_by_id(db, user_id=current_user.id, device_id=device_id)

    if db_device is None:
        raise HTTPException(status_code=404, detail="设备不存在")

    return db_device

# 新增设备
@router.post("/", response_model=schemas.DeviceResponse)
def create_device(
    device: schemas.DeviceCreate,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    return devices_crud.create_device(db, device=device, user_id=current_user.id)

# 修改设备信息
@router.put("/{device_id}", response_model=schemas.DeviceResponse)
def update_device(
    device_id: int,
    device_update: schemas.DeviceUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    return devices_crud.update_device(db, user_id=current_user.id, device_id=device_id, device_update=device_update)

# 删除设备信息
@router.delete("/{device_id}")
def delete_device(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    return devices_crud.delete_device(db, device_id=device_id, user_id=current_user.id)

# 新增设备使用记录
@router.post("/usage", response_model=schemas.DeviceUsageResponse)
def create_device_usage(
    usage: schemas.DeviceUsageCreate,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    return devices_crud.create_device_usage(db, device_usage=usage, user_id=current_user.id)

# 获取设备使用记录
@router.get("/usage/{device_id}", response_model=schemas.PaginatedDeviceUsageResponse)
def get_device_usage(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user),
    usage_date: Optional[date] = None,
    page: int = 1,
    page_size: int = 5
):
    if page < 1:
        raise HTTPException(status_code=400, detail="页码不能小于1")
    if page_size < 1 or page_size > 100:
        raise HTTPException(status_code=400, detail="每页数量必须在1~100之间")

    return devices_crud.get_device_usage(
        db,
        device_id=device_id,
        user_id=current_user.id,
        usage_date=usage_date,
        page=page,
        page_size=page_size
    )

# 编辑设备使用记录
@router.put("/usage/{device_id}/{usage_id}", response_model=schemas.DeviceUsageResponse)
def update_device_usage(
    device_id: int,
    usage_id: int,
    usage_update: schemas.DeviceUsageUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    return devices_crud.update_device_usage(db, device_id=device_id, usage_id=usage_id, user_id=current_user.id, usage_update=usage_update)

# 删除设备使用记录
@router.delete("/usage/{device_id}/{usage_id}")
def delete_device_usage(
    device_id: int,
    usage_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    return devices_crud.delete_device_usage(db, device_id=device_id, usage_id=usage_id, user_id=current_user.id)