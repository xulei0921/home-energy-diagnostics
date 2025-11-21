from dns.e164 import query
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from .. import models, schemas
from typing import List, Optional

# 获取当前用户设备列表（支持筛选）
def get_devices(
    db: Session,
    user_id: int,
    device_type: Optional[schemas.DeviceType] = None,
    page: int = 1,
    page_size: int = 5
):
    query = db.query(models.Device).filter(models.Device.user_id == user_id)

    # 按设备类型筛选
    if device_type:
        query = query.filter(models.Device.device_type == device_type)

    # 查询符合条件的总记录数
    total = query.count()

    # offset: 计算需要跳过的记录数
    offset = (page - 1) * page_size

    # 执行查询
    # return query.all()

    # 应用分页
    # limit: 限制返回的记录数
    items = query.offset(offset).limit(page_size).all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": ( total + page_size - 1 ) // page_size
    }

# 获取设备 by ID
def get_device_by_id(
    db: Session,
    user_id: int,
    device_id: int
):
    return db.query(models.Device).filter(
        models.Device.id == device_id,
        models.Device.user_id == user_id
    ).first()

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

# 修改设备信息
def update_device(
    db: Session,
    user_id: int,
    device_id: int,
    device_update: schemas.DeviceUpdate
):
    db_device = get_device_by_id(db, user_id=user_id, device_id=device_id)

    if  not db_device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在"
        )

    if db_device.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限修改此设备"
        )

    # 更新字段
    update_data = device_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_device, key, value)

    db.commit()
    db.refresh(db_device)

    return db_device

# 删除设备信息
def delete_device(
    db: Session,
    device_id: int,
    user_id: int
):
    db_device = get_device_by_id(db, user_id=user_id, device_id=device_id)

    if not db_device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在"
        )

    db.delete(db_device)
    db.commit()

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