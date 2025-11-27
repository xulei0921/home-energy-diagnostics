from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import models, schemas, dependencies
from ..database import get_db
from ..services.analysis_service import energy_analysis_service
from ..services.enhanced_analysis_service import enhanced_analysis_service
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

# 获取能源费用分布数据
@router.get("/energy-costs-distribution", response_model=schemas.LatestCostResponse)
def get_energy_costs_distribution(
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    """获取最新月份的各类能源花费数据"""
    return energy_analysis_service.get_latest_month_costs(db, user_id=current_user.id)

# 综合能耗分析 - 新增的增强分析接口
@router.get("/comprehensive-analysis", response_model=schemas.ComprehensiveAnalysisResult)
def get_comprehensive_analysis(
    bill_type: Optional[schemas.BillType] = None,  # 不指定则分析所有能源类型
    period: schemas.AnalysisPeriod = schemas.AnalysisPeriod.monthly,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    """
    获取综合能耗分析结果 - 支持多能源类型和AI智能分析

    Args:
        bill_type: 能源类型（可选，不填时分析所有类型）
        period: 分析周期（月度/季度/年度/自定义）
        start_date: 开始日期（自定义周期时使用）
        end_date: 结束日期（自定义周期时使用）
        db: 数据库会话
        current_user: 当前用户

    Returns:
        ComprehensiveAnalysisResult: 综合分析结果，包含多能源类型分析和AI建议
    """
    return enhanced_analysis_service.generate_analysis_and_suggestions(
        db=db,
        user_id=current_user.id,
        bill_type=bill_type,
        period=period,
        start_date=start_date,
        end_date=end_date
    )

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

    # 使用原来的分析服务来保持接口兼容性
    return energy_analysis_service.generate_analysis_and_suggestions(
        db=db,
        user_id=current_user.id,
        bill_type=bill_type,
        period=period,
        start_date=start_date,
        end_date=end_date
    )

# 检测异常月份
@router.get("/{bill_type}/anomaly-months", response_model=List[schemas.AnomalyMonthResult])
def get_anomaly_months(
    bill_type: schemas.BillType,
    months: int = 24,  # 默认分析最近24个月
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    """
    检测指定能源类型的异常月份

    Args:
        bill_type: 能源类型 (electricity/gas/water)
        months: 分析的月数，默认24个月
        db: 数据库会话
        current_user: 当前用户

    Returns:
        List[AnomalyMonthResult]: 异常月份列表，按严重程度和时间排序
    """
    return energy_analysis_service.detect_anomaly_months(
        db=db,
        user_id=current_user.id,
        bill_type=bill_type,
        months=months
    )


# 获取单种能源类型的增强分析
@router.get("/{bill_type}/enhanced-analysis", response_model=schemas.EnergyTypeAnalysis)
def get_enhanced_energy_analysis(
    bill_type: schemas.BillType,
    period: schemas.AnalysisPeriod = schemas.AnalysisPeriod.monthly,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    """
    获取单种能源类型的增强分析结果

    Args:
        bill_type: 能源类型
        period: 分析周期
        start_date: 开始日期
        end_date: 结束日期
        db: 数据库会话
        current_user: 当前用户

    Returns:
        EnergyTypeAnalysis: 单种能源类型的详细分析结果
    """
    comprehensive_result = enhanced_analysis_service.generate_analysis_and_suggestions(
        db=db,
        user_id=current_user.id,
        bill_type=bill_type,
        period=period,
        start_date=start_date,
        end_date=end_date
    )

    # 返回指定能源类型的分析结果
    for analysis in comprehensive_result.energy_analyses:
        if analysis.bill_type == bill_type:
            return analysis

    # 如果没有找到，返回空的分析结果
    return schemas.EnergyTypeAnalysis(
        bill_type=bill_type,
        trend_data=[],
        comparison=schemas.EnergyComparison(
            current_usage=0,
            current_amount=0,
            current_unit_price=0,
            is_abnormal=False
        ),
        device_consumption=[],
        anomaly_months=[],
        ai_analysis=schemas.AIEnergyAnalysis(
            overall_assessment="暂无数据",
            key_insights=[],
            risk_level="low",
            optimization_potential="low",
            seasonal_analysis="暂无季节性分析",
            suggestions=[],
            confidence_score=0.0
        ),
        suggestions=[]
    )