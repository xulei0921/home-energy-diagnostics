from datetime import datetime, date
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from .. import models, schemas
from typing import Optional

# 获取当前用户所有的节能建议列表（支持筛选）
def get_suggestions(
    db: Session,
    user_id: int,
    bill_type: Optional[schemas.BillType] = None,
    suggestion_date: Optional[date] = None,
    impact_rating: Optional[int] = None,
    is_implemented: Optional[bool] = None,
    page: int = 1,
    page_size: int = 5
):
    query = db.query(models.EnergySavingSuggestion).filter(models.EnergySavingSuggestion.user_id == user_id)

    # 按账单类型筛选
    if bill_type:
        query = query.filter(models.EnergySavingSuggestion.bill_type == bill_type)

    if suggestion_date:
        query = query.filter(models.EnergySavingSuggestion.suggestion_date == suggestion_date)

    if impact_rating:
        query = query.filter(models.EnergySavingSuggestion.impact_rating == impact_rating)

    if is_implemented:
        query = query.filter(models.EnergySavingSuggestion.is_implemented == is_implemented)

    # 查询符合条件的总记录数
    total = query.count()

    # 计算需要跳过的记录数
    offset = (page - 1) * page_size

    # return query.order_by(models.EnergySavingSuggestion.suggestion_date.desc()).all()

    # 应用分页
    items = query.order_by(
        models.EnergySavingSuggestion.suggestion_date.desc(),
        models.EnergySavingSuggestion.created_at.desc()
    ).offset(offset).limit(page_size).all()
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }

# 获取节能建议 by ID
def get_suggestion_by_id(
    db: Session,
    suggestion_id: int,
    user_id: int
):
    return db.query(models.EnergySavingSuggestion).filter(
        models.EnergySavingSuggestion.user_id == user_id,
        models.EnergySavingSuggestion.id == suggestion_id
    ).first()

# 新增节能建议
def create_suggestion(
    db: Session,
    suggestion: schemas.EnergySavingSuggestionCreate,
    user_id: int
):
    db_suggestion = models.EnergySavingSuggestion(**suggestion.model_dump(), user_id=user_id)

    db.add(db_suggestion)
    db.commit()
    db.refresh(db_suggestion)

    return db_suggestion

# 编辑节能建议
def update_suggestion(
    db: Session,
    suggestion_id: int,
    suggestion_update: schemas.EnergySavingSuggestionUpdate,
    user_id: int
):
    db_suggestion = get_suggestion_by_id(db, suggestion_id=suggestion_id, user_id=user_id)

    if not db_suggestion:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="建议不存在"
        )

    if db_suggestion.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限编辑此建议"
        )

    # 更新字段
    update_data = suggestion_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_suggestion, key, value)

    db.commit()
    db.refresh(db_suggestion)

    return db_suggestion

# 删除节能建议
def delete_suggestion(
    db: Session,
    suggestion_id: int,
    user_id: int
):
    db_suggestion = get_suggestion_by_id(db, suggestion_id=suggestion_id, user_id=user_id)

    if not db_suggestion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="建议不存在"
        )

    db.delete(db_suggestion)
    db.commit()

    return db_suggestion