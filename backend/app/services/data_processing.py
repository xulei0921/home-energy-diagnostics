from .. import schemas
from typing import Optional, Tuple
from datetime import date, datetime, timedelta

def get_date_range_for_period(
    period: schemas.AnalysisPeriod,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> Tuple[date, date]:

    """根据分析周期获取日期范围"""

    today = date.today()

    if period == schemas.AnalysisPeriod.monthly:
        # 从去年上上个月到今年上个月
        first_day_current_month = today.replace(day=1)
        last_month_last_day = first_day_current_month - timedelta(days=1)

        # 结束日期: 今年上个月
        end_date = last_month_last_day
        # 开始日期: 去年上上个月第一天
        start_date = last_month_last_day.replace(year=last_month_last_day.year-1, month=last_month_last_day.month-1, day=1)

    elif period == schemas.AnalysisPeriod.quarter:
        start_date = today.replace(month=1, day=1)
        end_date = today.replace(month=12, day=1)

    elif period == schemas.AnalysisPeriod.annual:
        start_date = today.replace(month=1, day=1)
        end_date = today

    elif period == schemas.AnalysisPeriod.custom:
        # 自定义日期范围
        start_date = start_date
        end_date = end_date

    return start_date, end_date