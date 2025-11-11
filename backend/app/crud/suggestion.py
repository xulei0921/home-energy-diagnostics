from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from .. import models, schemas
from typing import Optional

# 获取当前用户所有的节能建议列表（支持筛选）
def get_suggestions(
    db: Session,
    user_id: int,
    bill_type: Optional[schemas.BillType] = None
):
    query = db.query(models.EnergySavingSuggestion).filter(models.EnergySavingSuggestion.user_id == user_id)

    # 按账单类型筛选
    if bill_type:
        query = query.filter(models.EnergySavingSuggestion.bill_type == bill_type)

    return query.order_by(models.EnergySavingSuggestion.suggestion_date.desc()).all()

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