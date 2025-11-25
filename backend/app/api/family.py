from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas, dependencies
from ..database import get_db
from ..crud import family as family_crud

router = APIRouter()

# 获取当前用户家庭信息
@router.get("/", response_model=schemas.FamilyInfoResponse)
def get_family_info(
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    family_info = family_crud.get_family_info(db, user_id=current_user.id)

    if family_info is None:
        raise HTTPException(status_code=404, detail="家庭信息不存在")

    return family_info

# 创建家庭信息
@router.post("/", response_model=schemas.FamilyInfoResponse)
def create_family_info(
    family_info: schemas.FamilyInfoCreate,
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user),
    db: Session = Depends(get_db)
):
    db_family_info = family_crud.get_family_info(db, user_id=current_user.id)

    if db_family_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前家庭家庭信息已存在"
        )

    return family_crud.create_family_info(db, family_info=family_info, user_id=current_user.id)

# 修改家庭信息
@router.put("/", response_model=schemas.FamilyInfoResponse)
def update_family_info(
    family_info_update: schemas.FamilyInfoUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    return family_crud.update_family_info(db, family_info_update=family_info_update, user_id=current_user.id)

# 删除家庭信息
@router.delete("/")
def delete_family_info(
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    return family_crud.delete_family_info(db, user_id=current_user.id)

# 当前用户是否有家庭信息
@router.get("/is-exist")
def is_family_info_exist(
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    return family_crud.is_family_info_exist(db, user_id=current_user.id)