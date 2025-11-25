from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from .. import models, schemas

# 获取家庭信息
def get_family_info(db: Session, user_id: int):
    """根据用户ID查找对应家庭信息"""
    return db.query(models.FamilyInfo).filter(models.FamilyInfo.user_id == user_id).first()

# 创建家庭信息
def create_family_info(db: Session, family_info: schemas.FamilyInfoCreate, user_id: int):
    # 创建家庭信息对象
    db_family_info = models.FamilyInfo(**family_info.model_dump(), user_id = user_id)

    # 保存家庭信息
    db.add(db_family_info)
    db.commit()
    db.refresh(db_family_info)

    return db_family_info

# 更新家庭信息
def update_family_info(db: Session, family_info_update: schemas.FamilyInfoUpdate, user_id: int):
    db_family_info = get_family_info(db, user_id)

    if not db_family_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="家庭信息不存在"
        )

    # 检查权限
    if db_family_info.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限修改此信息"
        )

    # 更新字段
    update_data = family_info_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_family_info, key, value)

    db.commit()
    db.refresh(db_family_info)

    return db_family_info

# 删除家庭信息
def delete_family_info(db: Session, user_id: int):
    db_family_info = get_family_info(db, user_id=user_id)

    if not db_family_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="家庭信息不存在"
        )

    db.delete(db_family_info)
    db.commit()

    return db_family_info

# 当前用户是否有家庭信息
def is_family_info_exist(db: Session, user_id: int):
    db_family_info = get_family_info(db, user_id=user_id)

    if not db_family_info:
        return False

    return True