from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import models, schemas, dependencies
from ..database import get_db
from ..services.analysis_service import energy_analysis_service
from typing import List, Optional
from datetime import date

router = APIRouter()

# 获取能耗趋势数据
@router.get("/energy-trend", response_model=List[schemas.EnergyTrendItem])
def get_energy_trend(
    period: schemas.AnalysisPeriod,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    bill_type: Optional[schemas.BillType] = None,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    return energy_analysis_service.get_energy_trend(db, user_id=current_user.id, period=period, start_date=start_date, end_date=end_date, bill_type=bill_type)

# 计算同比、环比数据
@router.get("/energy-comparison", response_model=schemas.EnergyComparison)
def get_energy_comparison(
    period: schemas.AnalysisPeriod = schemas.AnalysisPeriod.monthly,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    bill_type: Optional[schemas.BillType] = None,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    trend_data = energy_analysis_service.get_energy_trend(db, user_id=current_user.id, period=period, start_date=start_date, end_date=end_date, bill_type=bill_type)

    return energy_analysis_service.calculate_comparison(trend_data)

# 获取能耗分析结果
@router.get("/{bill_type}", response_model=schemas.AnalysisResult)
def get_energy_analysis(
    bill_type: schemas.BillType,
    period: schemas.AnalysisPeriod,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user),
):
    return energy_analysis_service.generate_analysis_and_suggestions(
        db=db,
        user_id=current_user.id,
        bill_type=bill_type,
        period=period,
        start_date=start_date,
        end_date=end_date
    )

# 获取能源费用分布数据
@router.get("/energy-costs-distribution", response_model=schemas.LatestEnergyDistribution)
def get_energy_costs_distribution(
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
