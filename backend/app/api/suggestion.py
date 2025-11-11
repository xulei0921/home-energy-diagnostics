from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from .. import schemas, dependencies
from ..database import get_db
from ..crud import suggestion as suggestion_crud
from typing import Optional, List

router = APIRouter()

# 获取当前用户所有的节能建议列表（支持筛选）
@router.get("/", response_model=List[schemas.EnergySavingSuggestionResponse])
def get_suggestion(
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user),
    bill_type: Optional[schemas.BillType] = None
):
    suggestions = suggestion_crud.get_suggestions(db, user_id=current_user.id, bill_type=bill_type)

    return suggestions