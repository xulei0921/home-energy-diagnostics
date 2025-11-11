from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import models, schemas, dependencies
from ..database import get_db
from ..services.analysis_service import energy_analysis_service

router = APIRouter()

# 获取能耗分析结果
@router.get("/{bill_type}", response_model=schemas.AnalysisResult)
def get_energy_analysis(
    bill_type: schemas.BillType,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    return energy_analysis_service.generate_analysis_and_suggestions(db=db, user_id=current_user.id, bill_type=bill_type)