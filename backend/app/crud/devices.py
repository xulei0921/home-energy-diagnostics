from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from .. import models, schemas
from typing import List, Optional

# 获取当前用户设备列表（支持筛选）
def get_devices(
    db: Session,
    user_id: int,
    device_type: Optional[schemas.DeviceType] = None
):
    query = db.query(models.Device).filter(models.Device.user_id == user_id)

    # 按设备类型筛选
    if device_type:
        query = query.filter(models.Device.device_type == device_type)

    # 执行查询
    return query.all()

# 创建设备
def create_device(
    db: Session,
    device: schemas.DeviceCreate,
    user_id: int
):
    db_device = models.Device(**device.model_dump(), user_id=user_id)

    # 保存设备信息
    db.add(db_device)
    db.commit()
    db.refresh(db_device)

    return db_device

# 新增设备使用记录
def create_device_usage(
    db: Session,
    device_usage: schemas.DeviceUsageCreate,
    user_id: int
):
    device = db.query(models.Device).filter(
        models.Device.id == device_usage.device_id,
        models.Device.user_id == user_id
    ).first()

    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")

    # 检查是否已经存在当日记录
    existing = db.query(models.DeviceUsage).filter(
        models.DeviceUsage.device_id == device_usage.device_id,
        models.DeviceUsage.usage_date == device_usage.usage_date
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="该设备当日使用记录已存在")

    db_usage = models.DeviceUsage(**device_usage.model_dump())
    db.add(db_usage)
    db.commit()
    db.refresh(db_usage)

    return db_usage