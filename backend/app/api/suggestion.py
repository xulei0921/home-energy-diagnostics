from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from .. import schemas, dependencies
from ..database import get_db
from ..crud import suggestion as suggestion_crud
from typing import Optional, List
from datetime import date

router = APIRouter()

# 获取当前用户所有的节能建议列表（支持筛选）
@router.get("/", response_model=schemas.PaginatedSuggestionResponse)
def get_suggestion(
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user),
    bill_type: Optional[schemas.BillType] = None,
    suggestion_date: Optional[date] = None,
    impact_rating: Optional[int] = None,
    is_implemented: Optional[bool] = None,
    page: int = 1,
    page_size: int = 5
):
    # suggestions = suggestion_crud.get_suggestions(
    #     db,
    #     user_id=current_user.id,
    #     bill_type=bill_type,
    #     suggestion_date=suggestion_date,
    #     impact_rating=impact_rating,
    #     is_implemented=is_implemented
    # )
    #
    # return suggestions

    # 验证分页参数合法性
    if page < 1:
        raise HTTPException(status_code=400, detail="页面不能小于1")
    if page_size < 1 or page_size > 100:
        raise HTTPException(status_code=400, detail="每页数量必须在1~100之间")

    return suggestion_crud.get_suggestions(
        db,
        user_id=current_user.id,
        bill_type=bill_type,
        suggestion_date=suggestion_date,
        impact_rating=impact_rating,
        is_implemented=is_implemented,
        page=page,
        page_size=page_size
    )

# 编辑节能建议
@router.put("/{suggestion_id}", response_model=schemas.EnergySavingSuggestionResponse)
def update_suggestion(
    suggestion_id: int,
    suggestion_update: schemas.EnergySavingSuggestionUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    return suggestion_crud.update_suggestion(db, suggestion_id=suggestion_id, suggestion_update=suggestion_update, user_id=current_user.id)

# 删除节能建议
@router.delete("/{suggestion_id}")
def delete_suggestion(
    suggestion_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    return suggestion_crud.delete_suggestion(db, suggestion_id=suggestion_id, user_id=current_user.id)