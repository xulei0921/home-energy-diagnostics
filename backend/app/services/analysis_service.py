import json
from datetime import datetime, timedelta, date

from sqlalchemy import extract, case, func
from sqlalchemy.orm import Session
from typing import List, Tuple, Optional, Dict
import numpy as np
from . import data_processing
from .. import schemas, models
from .ai_service import AISuggestionService
from .anomaly_detection import anomaly_detection_service
from .ai_anomaly_detection import ai_anomaly_detection_service

class EnergyAnalysisService:
    @staticmethod
    def get_energy_trend(
        db: Session,
        user_id: int,
        period: schemas.AnalysisPeriod,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        bill_type: Optional[schemas.BillType] = None,
    ) -> List[schemas.EnergyTrendItem]:

        """获取能耗趋势数据"""

        analysis_start_date, analysis_end_date = data_processing.get_date_range_for_period(period, start_date, end_date)

        if period == schemas.AnalysisPeriod.monthly:
            bills = db.query(models.EnergyBill).filter(
                models.EnergyBill.user_id == user_id,
                models.EnergyBill.bill_date >= analysis_start_date,
                models.EnergyBill.bill_date <= analysis_end_date
            )

            if bill_type:
                bills = bills.filter(models.EnergyBill.bill_type == bill_type)

            bills = bills.order_by(models.EnergyBill.bill_type, models.EnergyBill.bill_date).all()

            trend_data = [
                schemas.EnergyTrendItem(
                    bill_type=bill.bill_type,
                    bill_date=bill.bill_date,
                    usage=bill.usage,
                    amount=bill.amount,
                    year=str(bill.bill_date.year),
                    month=str(bill.bill_date.month)
                ) for bill in bills
            ]
            return trend_data

        elif period == schemas.AnalysisPeriod.quarter:
            # 基础查询条件
            query = db.query(
                models.EnergyBill.bill_type,
                # 季度标识（1-4）
                case(
                    (extract('month', models.EnergyBill.bill_date).between(1, 3), 1),
                    (extract('month', models.EnergyBill.bill_date).between(4, 6), 2),
                    (extract('month', models.EnergyBill.bill_date).between(7, 9), 3),
                    (extract('month', models.EnergyBill.bill_date).between(10, 12), 4),
                ).label('quarter'),
                # --- 核心修正：使用 MySQL 兼容的函数替代 date_trunc ---
                # 季度起始日期（Q1: 01-01, Q2: 04-01, Q3: 07-01, Q4: 10-01）
                case(
                    # Q1: 年份的第一天
                    (extract('month', models.EnergyBill.bill_date).between(1, 3),
                     func.makedate(func.year(models.EnergyBill.bill_date), 1)),
                    # Q2: 年份的第91天 (4月1日)
                    (extract('month', models.EnergyBill.bill_date).between(4, 6),
                     func.makedate(func.year(models.EnergyBill.bill_date), 91)),
                    # Q3: 年份的第182天 (7月1日)
                    (extract('month', models.EnergyBill.bill_date).between(7, 9),
                     func.makedate(func.year(models.EnergyBill.bill_date), 182)),
                    # Q4: 年份的第274天 (10月1日)
                    (extract('month', models.EnergyBill.bill_date).between(10, 12),
                     func.makedate(func.year(models.EnergyBill.bill_date), 274)),
                ).label('quarter_start'),
                # --- 修正结束 ---
                # 汇总季度用量和金额
                func.sum(models.EnergyBill.usage).label('total_usage'),
                func.sum(models.EnergyBill.amount).label('total_amount'),
                extract('year', models.EnergyBill.bill_date).label('bill_year')
            ).filter(
                models.EnergyBill.user_id == user_id,
                models.EnergyBill.bill_date >= analysis_start_date,
                models.EnergyBill.bill_date <= analysis_end_date
            )

            # 按账单类型筛选
            if bill_type:
                query = query.filter(models.EnergyBill.bill_type == bill_type)

            # 按季度和账单类型分组
            query = query.group_by(
                'bill_type', 'quarter', 'quarter_start', 'bill_year'
            ).order_by('bill_type', 'bill_year', 'quarter')

            # 执行查询并处理结果
            quarter_data = query.all()

            # 转换为EnergyTrendItem格式
            trend_data = []
            for item in quarter_data:
                quarter_start_date = item.quarter_start if item.quarter_start else None

                trend_data.append(
                    schemas.EnergyTrendItem(
                        bill_type=item.bill_type,
                        bill_date=quarter_start_date,
                        usage=round(item.total_usage, 2),
                        amount=round(item.total_amount, 2),
                        year=str(item.bill_year) if item.bill_year else None,
                        month=None
                    )
                )

            return trend_data

        elif period == schemas.AnalysisPeriod.custom:
            bills = db.query(models.EnergyBill).filter(
                models.EnergyBill.user_id == user_id,
                models.EnergyBill.bill_date >= analysis_start_date,
                models.EnergyBill.bill_date <= analysis_end_date
            )

            if bill_type:
                bills = bills.filter(models.EnergyBill.bill_type == bill_type)

            bills = bills.order_by(models.EnergyBill.bill_type, models.EnergyBill.bill_date).all()

            trend_data = [
                schemas.EnergyTrendItem(
                    bill_type=bill.bill_type,
                    bill_date=bill.bill_date,
                    usage=bill.usage,
                    amount=bill.amount,
                    year=str(bill.bill_date.year),
                    month=str(bill.bill_date.month)
                ) for bill in bills
            ]
            return trend_data

        elif period == schemas.AnalysisPeriod.annual:
            # 基础查询条件
            query = db.query(
                models.EnergyBill.bill_type,
                func.sum(models.EnergyBill.usage).label('total_usage'),
                func.sum(models.EnergyBill.amount).label('total_amount'),
                extract('year', models.EnergyBill.bill_date).label('bill_year')
            ).filter(
                models.EnergyBill.user_id == user_id,
                models.EnergyBill.bill_date <= analysis_end_date
            )

            # 按账单类型筛选
            if bill_type:
                query = query.filter(models.EnergyBill.bill_type == bill_type)

            # 按照年份和账单类型分组
            query = query.group_by(
                'bill_type', 'bill_year'
            ).order_by('bill_type', 'bill_year')

            # 执行查询并处理结果
            year_data = query.all()
            trend_data = []
            for item in year_data:
                # 构造年度起始日期 YYYY-01-01
                year_start_date = date(int(item.bill_year),1, 1) if item.bill_year else None

                trend_data.append(
                    schemas.EnergyTrendItem(
                        bill_type=item.bill_type,
                        bill_date=year_start_date,
                        usage=round(item.total_usage, 2),
                        amount=round(item.total_amount, 2),
                        year=str(item.bill_year) if item.bill_year else None,
                        month=None
                    )
                )
            return trend_data

    @staticmethod
    def calculate_comparison(trend_data: List[schemas.EnergyTrendItem]) -> schemas.EnergyComparison:
        """计算同比、环比增长率，判断是否异常"""
        if not trend_data:
            return schemas.EnergyComparison(
                current_usage=0,
                current_amount=0,
                current_unit_price=0,
                previous_usage=None,
                previous_amount=None,
                previous_unit_price=None,
                usage_yoy_rate=None,
                usage_mom_rate=None,
                amount_yoy_rate=None,
                amount_mom_rate=None,
                unit_price_yoy_rate=None,
                unit_price_mom_rate=None,
                is_abnormal=False
            )

        # 当前最新数据
        current = trend_data[-1]
        current_usage = current.usage
        current_amount = current.amount
        current_unit_price = current_amount / current_usage if current_usage != 0 else 0

        # 环比（与上一个月比较）
        usage_mom_rate = None
        amount_mom_rate = None
        unit_price_mom_rate = None
        previous_usage = None
        previous_amount = None
        previous_unit_price = None
        if len(trend_data) >= 2:
            previous = trend_data[-2]
            previous_usage = previous.usage
            previous_amount = previous.amount
            previous_unit_price = previous_amount / previous_usage
            usage_mom_rate = ((current_usage - previous_usage) / previous_usage) * 100 if previous_usage != 0 else 0
            amount_mom_rate = ((current_amount - previous_amount) / previous_amount) * 100 if previous_amount != 0 else 0
            unit_price_mom_rate = ((current_unit_price - previous_unit_price) / previous_unit_price) * 100 if previous_unit_price != 0 else 0

        # 同比（与去年同月比较）
        usage_yoy_rate = None
        amount_yoy_rate = None
        unit_price_yoy_rate = None
        current_year = current.bill_date.year
        current_month = current.bill_date.month
        for item in trend_data[:-1]:  # 排除当前月
            if item.bill_date.year == current_year - 1 and item.bill_date.month == current_month:
                usage_yoy_rate = ((current_usage - item.usage) / item.usage) * 100 if item.usage != 0 else 0
                amount_yoy_rate = ((current_amount - item.amount) / item.amount) * 100 if item.amount !=0 else 0
                unit_price_yoy_rate = ((current_unit_price - (item.amount / item.usage)) / (item.amount / item.usage)) * 100 if (item.amount / item.usage) != 0 else 0
                break

        # 使用智能异常检测算法判断是否异常
        anomaly_result = anomaly_detection_service.comprehensive_anomaly_detection(trend_data)
        is_abnormal = anomaly_result.is_abnormal

        return schemas.EnergyComparison(
            current_usage=current_usage,
            current_amount=current_amount,
            current_unit_price=round(current_unit_price, 2),
            previous_usage=previous_usage if previous_usage is not None else None,
            previous_amount=previous_amount if previous_amount is not None else None,
            previous_unit_price=round(previous_unit_price, 2) if previous_unit_price is not None else None,
            usage_yoy_rate=round(usage_yoy_rate, 2) if usage_yoy_rate else None,
            usage_mom_rate=round(usage_mom_rate, 2) if usage_mom_rate else None,
            amount_yoy_rate=round(amount_yoy_rate, 2) if amount_yoy_rate else None,
            amount_mom_rate=round(amount_mom_rate, 2) if amount_mom_rate else None,
            unit_price_yoy_rate=round(unit_price_yoy_rate, 2) if unit_price_yoy_rate else None,
            unit_price_mom_rate=round(unit_price_mom_rate, 2) if unit_price_mom_rate else None,
            is_abnormal=is_abnormal
        )

    @staticmethod
    def calculate_device_consumption(
        db: Session, user_id: int, bill_type: schemas.BillType, bill_date: datetime.date
    ) -> List[schemas.DeviceEnergyConsumption]:
        """计算设备能耗占比（基于功率和使用时长）"""
        # 获取该用户该类型的所有设备
        devices = db.query(models.Device).filter(
            models.Device.user_id == user_id,
            models.Device.device_type == bill_type
        ).all()

        if not devices:
            return []

        # 计算每月总能耗（度/立方米）
        device_consumptions = []
        for device in devices:
            usage_date_str = bill_date.strftime("%Y-%m-%d")
            usage_record = db.query(models.DeviceUsage).filter(
                models.DeviceUsage.device_id == device.id,
                models.DeviceUsage.usage_date == usage_date_str
            ).first()

            if usage_record:
                monthly_hours = usage_record.usage_hours
            else:
                # 按30天估算月使用小时数
                monthly_hours = device.usage_hours_per_day * 30 if device.usage_hours_per_day else 0

            # 计算能耗
            # 电力：功率(W) * 时长(h) / 1000 = 度
            # 燃气：流量(m³/h) * 时长(h) = 立方米
            # 水资源：流量(L/h) * 时长(h) / 1000 = 立方米
            if bill_type == schemas.BillType.electricity:
                monthly_usage = (device.power_rating * monthly_hours) / 1000 if device.power_rating else 0
            elif bill_type == schemas.BillType.gas:
                monthly_usage = device.power_rating * monthly_hours if device.power_rating else 0
            else:  # water
                monthly_usage = (device.power_rating * monthly_hours) / 1000 if device.power_rating else 0

            device_consumptions.append({
                "device_id": device.id,
                "device_name": device.name,
                "monthly_usage": monthly_usage
            })

        # 计算总能耗和占比
        total_usage = sum([d["monthly_usage"] for d in device_consumptions])
        if total_usage == 0:
            return [
                schemas.DeviceEnergyConsumption(
                    device_id=d["device_id"],
                    device_name=d["device_name"],
                    consumption=0,
                    monthly_usage=d["monthly_usage"]
                ) for d in device_consumptions
            ]

        # 按能耗占比降序排序
        result = sorted([
            schemas.DeviceEnergyConsumption(
                device_id=d["device_id"],
                device_name=d["device_name"],
                consumption=round((d["monthly_usage"] / total_usage) * 100, 2),
                monthly_usage=round(d["monthly_usage"], 2)
            ) for d in device_consumptions
        ], key=lambda x: x.consumption, reverse=True)

        return result

    @staticmethod
    def get_latest_month_costs(
        db: Session,
        user_id: int
    ) -> schemas.LatestCostResponse:
        """获取最新月份的各类能源花费及占比"""
        # 获取最新月份（有数据的最后一个月）
        latest_bill = db.query(
            models.EnergyBill.bill_date
        ).filter(
            models.EnergyBill.user_id == user_id
        ).order_by(
            models.EnergyBill.bill_date.desc()
        ).first()

        if not latest_bill:
            return schemas.LatestCostResponse(
                total_amount=0,
                items=[],
                month=""
            )

        latest_month = latest_bill.bill_date
        month_str = latest_month.strftime("%Y-%m")

        # 查询该月份所有类型的账单
        bills = db.query(
            models.EnergyBill.bill_type,
            func.sum(models.EnergyBill.amount).label('total_amount')
        ).filter(
            models.EnergyBill.user_id == user_id,
            extract('year', models.EnergyBill.bill_date) == latest_month.year,
            extract('month', models.EnergyBill.bill_date) == latest_month.month
        ).group_by(
            models.EnergyBill.bill_type
        ).all()

        # 计算总花费
        total_amount = sum(bill.total_amount for bill in bills) if bills else 0

        # 计算各类型占比并构造返回数据
        items = []
        for bill in bills:
            percentage = (bill.total_amount / total_amount) * 100 if total_amount > 0 else 0
            items.append(schemas.LatestCostItem(
                bill_type=bill.bill_type,
                amount=round(bill.total_amount, 2),
                percentage=round(percentage, 2)
            ))

        return schemas.LatestCostResponse(
            total_amount=round(total_amount, 2),
            items=items,
            month=month_str
        )

    @staticmethod
    def get_device_consumption(
        db: Session,
        bill_type: schemas.BillType,
        user_id: int
    ):
        # 获取最新月份（有数据的最后一个月）
        latest_bill = db.query(
            models.EnergyBill.bill_date
        ).filter(
            models.EnergyBill.user_id == user_id
        ).order_by(
            models.EnergyBill.bill_date.desc()
        ).first()

        latest_month = latest_bill.bill_date

        # 获取该用户该类型的所有设备
        devices = db.query(models.Device).filter(
            models.Device.user_id == user_id,
            models.Device.device_type == bill_type
        ).all()

        if not devices:
            return []

        # 计算每月总能耗（度/立方米）
        device_consumptions = []
        for device in devices:
            usage_date_str = latest_month.strftime("%Y-%m-%d")
            usage_record = db.query(models.DeviceUsage).filter(
                models.DeviceUsage.device_id == device.id,
                models.DeviceUsage.usage_date == usage_date_str
            ).first()

            if usage_record:
                monthly_hours = usage_record.usage_hours
            else:
                # 按30天估算月使用小时数
                monthly_hours = device.usage_hours_per_day * 30 if device.usage_hours_per_day else 0

            # 计算能耗
            # 电力：功率(W) * 时长(h) / 1000 = 度
            # 燃气：流量(m³/h) * 时长(h) = 立方米
            # 水资源：流量(L/h) * 时长(h) / 1000 = 立方米
            if bill_type == schemas.BillType.electricity:
                monthly_usage = (device.power_rating * monthly_hours) / 1000 if device.power_rating else 0
            elif bill_type == schemas.BillType.gas:
                monthly_usage = device.power_rating * monthly_hours if device.power_rating else 0
            else:  # water
                monthly_usage = (device.power_rating * monthly_hours) / 1000 if device.power_rating else 0

            device_consumptions.append({
                "device_id": device.id,
                "device_name": device.name,
                "monthly_usage": monthly_usage
            })

        # 计算总能耗和占比
        total_usage = sum([d["monthly_usage"] for d in device_consumptions])
        if total_usage == 0:
            return [
                schemas.DeviceEnergyConsumption(
                    device_id=d["device_id"],
                    device_name=d["device_name"],
                    consumption=0,
                    monthly_usage=d["monthly_usage"]
                ) for d in device_consumptions
            ]

        # 按能耗占比降序排序
        result = sorted([
            schemas.DeviceEnergyConsumption(
                device_id=d["device_id"],
                device_name=d["device_name"],
                consumption=round((d["monthly_usage"] / total_usage) * 100, 2),
                monthly_usage=round(d["monthly_usage"], 2)
            ) for d in device_consumptions
        ], key=lambda x: x.consumption, reverse=True)

        return result

    def generate_analysis_and_suggestions(
        self,
        db: Session,
        user_id: int,
        bill_type: Optional[schemas.BillType] = None,
        period: schemas.AnalysisPeriod = schemas.AnalysisPeriod.monthly,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> schemas.AnalysisResult:
        """生成智能能耗分析结果和AI节能建议"""
        # 1. 获取趋势数据
        trend_data = self.get_energy_trend(db, user_id, period, start_date, end_date, bill_type)

        # 2. 计算同比环比
        comparison = self.calculate_comparison(trend_data)

        # 3. 计算设备能耗占比
        latest_bill_date = trend_data[-1].bill_date if trend_data else datetime.now().date()
        device_consumption = self.calculate_device_consumption(db, user_id, bill_type, latest_bill_date)

        # 4. 获取家庭信息
        family_info = db.query(models.FamilyInfo).filter(models.FamilyInfo.user_id == user_id).first()
        family_info_dict = {
            "家庭人口": family_info.family_size if family_info else 1,
            "住房面积(㎡)": family_info.house_area if family_info else None,
            "所在地区": family_info.location if family_info else None,
            "房龄(年)": family_info.building_age if family_info else None
        }

        # 5. 检测异常月份
        try:
            anomaly_months = self.detect_anomaly_months(db, user_id, bill_type, months=12, use_ai=True)
        except Exception as e:
            print(f"AI异常检测失败，使用统计方法: {str(e)}")
            anomaly_months = []

        # 6. 调用AI生成建议
        ai_service = AISuggestionService()
        try:
            # 构建趋势分析文本
            trend_analysis = f"""
            最近{len(trend_data)}个月{bill_type.value if bill_type else '能源'}使用情况:
            - 最新月份 ({latest_bill_date.strftime("%Y-%m")}) 用量: {trend_data[-1].usage if trend_data else 0} {'度' if bill_type == schemas.BillType.electricity else '立方米'}
            - 费用: {trend_data[-1].amount if trend_data else 0}元
            - 环比变化: {comparison.usage_mom_rate if comparison.usage_mom_rate else 0}%
            - 同比变化: {comparison.usage_yoy_rate if comparison.usage_yoy_rate else 0}%
            """

            # 构建设备能耗占比文本
            device_text = "高耗能设备TOP3: \n"
            for i, device in enumerate(device_consumption[:3], 1):
                device_text += f"- {device.device_name}: 月能耗{device.monthly_usage} {'度' if bill_type == schemas.BillType.electricity else '立方米'}, 占比{device.consumption}%\n"

            suggestion_text = ai_service.generate_suggestion(
                bill_type=bill_type,
                trend_analysis=trend_analysis,
                device_consumption=device_text,
                family_info=family_info_dict,
                abnormal=comparison.is_abnormal if comparison else False
            )

            response_data = json.loads(suggestion_text)
            text_content = response_data.get("output", {}).get("text", "")
            parsed_text = json.loads(text_content)

            # 7. 保存建议到数据库
            for suggestion in parsed_text.get('suggestions', []):
                # 检查是否已存在类似建议
                existing = db.query(models.EnergySavingSuggestion).filter(
                    models.EnergySavingSuggestion.suggestion_title == suggestion.get("suggestion_title", ""),
                    models.EnergySavingSuggestion.user_id == user_id
                ).first()

                if not existing:
                    db_suggestion = models.EnergySavingSuggestion(
                        user_id=user_id,
                        bill_type=bill_type or schemas.BillType.electricity,
                        suggestion_title=suggestion.get("suggestion_title", ""),
                        suggestion_text=suggestion.get("suggestion_text", ""),
                        suggestion_date=datetime.now().date(),
                        impact_rating=3 if (comparison and comparison.is_abnormal) else 2
                    )
                    db.add(db_suggestion)
                    db.commit()
                    db.refresh(db_suggestion)

        except Exception as e:
            print(f"AI建议生成失败: {str(e)}")
            # 继续执行，不影响其他功能

        # 8. 获取历史建议（最近3条）
        db_suggestions = db.query(models.EnergySavingSuggestion).filter(
            models.EnergySavingSuggestion.user_id == user_id,
            models.EnergySavingSuggestion.bill_type == bill_type
        ).order_by(models.EnergySavingSuggestion.created_at.desc()).limit(3).all()

        suggestions = []
        for sugg in db_suggestions:
            sugg_dict = {k: v for k, v in sugg.__dict__.items() if not k.startswith('_')}
            suggestions.append(schemas.EnergySavingSuggestionResponse.model_validate(sugg_dict))

        return schemas.AnalysisResult(
            trend_data=trend_data,
            comparison=comparison,
            device_consumption=device_consumption,
            suggestions=suggestions
        )

    @staticmethod
    def detect_anomaly_months(
        db: Session,
        user_id: int,
        bill_type: schemas.BillType,
        months: int = 24,
        use_ai: bool = True
    ) -> List[schemas.AnomalyMonthResult]:
        """
        检测指定时间范围内的异常月份 - 增强版本，支持AI辅助检测

        Args:
            db: 数据库会话
            user_id: 用户ID
            bill_type: 能源类型
            months: 检测的月数范围
            use_ai: 是否使用AI辅助检测

        Returns:
            异常月份列表，按严重程度和时间排序
        """
        from dateutil.relativedelta import relativedelta

        # 获取指定月数的历史数据 - 使用relativedelta精确计算
        end_date = datetime.now().date()
        start_date = end_date - relativedelta(months=months)

        # 获取月度趋势数据
        trend_data = EnergyAnalysisService.get_energy_trend(
            db, user_id, schemas.AnalysisPeriod.monthly, start_date, end_date, bill_type
        )

        # 数据不足时的处理策略
        if not trend_data:
            return []

        if len(trend_data) < 2:
            # 数据极少时，使用简单阈值检测
            return EnergyAnalysisService._simple_anomaly_detection(trend_data)

        # 获取家庭信息供AI使用
        family_info = db.query(models.FamilyInfo).filter(models.FamilyInfo.user_id == user_id).first()
        family_dict = {
            "家庭人口": family_info.family_size if family_info else 1,
            "住房面积(㎡)": family_info.house_area if family_info else 100,
            "所在地区": family_info.location if family_info else "未知",
            "房龄(年)": family_info.building_age if family_info else 0
        }

        anomaly_months = []

        # 改进的异常检测逻辑：动态调整检测起始点
        min_data_points = min(3, len(trend_data))  # 至少需要2个数据点进行比较

        for i in range(1, len(trend_data)):  # 从第2个月开始检测
            current_item = trend_data[i]
            historical_data = trend_data[:i]  # 不包含当前月的历史数据

            # 只有当有足够历史数据时才使用智能检测
            if len(historical_data) >= min_data_points:
                # 1. 使用传统统计方法检测
                current_month_data = trend_data[:i+1]  # 包含当前月在内的历史数据
                statistical_result = anomaly_detection_service.comprehensive_anomaly_detection(current_month_data)

                # 2. AI辅助检测（如果启用且有足够数据）
                ai_result = None
                if use_ai and len(historical_data) >= 2:
                    try:
                        # 计算统计数据供AI参考
                        statistical_analysis = EnergyAnalysisService._calculate_stats_for_ai(
                            historical_data, current_item, statistical_result
                        )

                        ai_result = ai_anomaly_detection_service.detect_anomaly_with_ai(
                            bill_type, current_item, historical_data, family_dict, statistical_analysis
                        )
                    except Exception as e:
                        print(f"AI异常检测失败，使用统计方法: {str(e)}")
                        ai_result = None

                # 3. 综合判断逻辑
                is_abnormal, final_severity, final_confidence, final_type, final_recommendations = \
                    EnergyAnalysisService._combine_detection_results(
                        statistical_result, ai_result, use_ai
                    )

                if is_abnormal:
                    # 计算基本统计数据
                    usages = [item.usage for item in historical_data]
                    avg_usage = sum(usages) / len(usages) if usages else current_item.usage
                    deviation = ((current_item.usage - avg_usage) / avg_usage) * 100 if avg_usage > 0 else 0

                    anomaly_month = schemas.AnomalyMonthResult(
                        year=current_item.bill_date.year,
                        month=current_item.bill_date.month,
                        usage=current_item.usage,
                        amount=current_item.amount,
                        avg_usage=round(avg_usage, 2),
                        deviation=round(deviation, 2),
                        anomaly_type=final_type,
                        severity=final_severity,
                        confidence=round(final_confidence, 2),
                        recommendations=final_recommendations
                    )

                    anomaly_months.append(anomaly_month)

        # 按严重程度和时间排序
        severity_order = {"high": 3, "medium": 2, "low": 1}
        anomaly_months.sort(key=lambda x: (
            severity_order.get(x.severity, 0),
            x.year,
            x.month
        ), reverse=True)

        return anomaly_months

    @staticmethod
    def _simple_anomaly_detection(trend_data: List[schemas.EnergyTrendItem]) -> List[schemas.AnomalyMonthResult]:
        """简单异常检测，用于数据量极少的情况"""
        if not trend_data:
            return []

        anomaly_months = []

        # 对于只有1-2个月数据的情况，检查是否为极端值
        for i, item in enumerate(trend_data):
            # 简单的极端值检测：基于常识阈值
            extreme_thresholds = {
                schemas.BillType.electricity: 2000,  # 电力：超过2000度/月
                schemas.BillType.gas: 500,          # 燃气：超过500立方米/月
                schemas.BillType.water: 100         # 水费：超过100立方米/月
            }

            threshold = extreme_thresholds.get(item.bill_type, 1000)
            if item.usage > threshold:
                anomaly_month = schemas.AnomalyMonthResult(
                    year=item.bill_date.year,
                    month=item.bill_date.month,
                    usage=item.usage,
                    amount=item.amount,
                    avg_usage=item.usage,
                    deviation=0,
                    anomaly_type="extreme",
                    severity="high",
                    confidence=0.8,
                    recommendations=[f"检测到极高能耗值({item.usage:.1f})，建议检查数据准确性或用能设备"]
                )
                anomaly_months.append(anomaly_month)

        return anomaly_months

    @staticmethod
    def _calculate_stats_for_ai(
        historical_data: List[schemas.EnergyTrendItem],
        current_item: schemas.EnergyTrendItem,
        statistical_result: schemas.AnomalyDetectionResult
    ) -> Dict:
        """为AI计算统计数据"""
        if not historical_data:
            return {}

        usages = [item.usage for item in historical_data]
        avg_usage = sum(usages) / len(usages) if usages else 0
        max_usage = max(usages) if usages else 0
        min_usage = min(usages) if usages else 0

        # 计算环比
        if historical_data:
            month_over_month = ((current_item.usage - historical_data[-1].usage) / historical_data[-1].usage) * 100 if historical_data[-1].usage > 0 else 0
        else:
            month_over_month = 0

        return {
            "avg_usage": round(avg_usage, 2),
            "max_usage": round(max_usage, 2),
            "min_usage": round(min_usage, 2),
            "current_vs_avg": round(((current_item.usage - avg_usage) / avg_usage) * 100, 2) if avg_usage > 0 else 0,
            "month_over_month": round(month_over_month, 2),
            "data_points": len(historical_data),
            "statistical_detection": {
                "is_abnormal": statistical_result.is_abnormal,
                "methods": statistical_result.detection_methods,
                "confidence": statistical_result.confidence
            }
        }

    @staticmethod
    def _combine_detection_results(
        statistical_result: schemas.AnomalyDetectionResult,
        ai_result: Optional[schemas.AIAnomalyDetectionResult],
        use_ai: bool
    ) -> Tuple[bool, str, float, Optional[str], List[str]]:
        """
        结合统计方法和AI的检测结果

        Returns:
            (is_abnormal, severity, confidence, anomaly_type, recommendations)
        """
        if not use_ai or ai_result is None:
            # 仅使用统计方法
            return (
                statistical_result.is_abnormal,
                statistical_result.severity,
                statistical_result.confidence,
                statistical_result.anomaly_type,
                statistical_result.recommendations
            )

        # AI和统计方法都可用时的综合判断
        stat_abnormal = statistical_result.is_abnormal
        ai_abnormal = ai_result.is_abnormal

        # 综合判断逻辑
        if stat_abnormal and ai_abnormal:
            # 两种方法都认为是异常
            is_abnormal = True
            # 采用更高的置信度
            confidence = max(statistical_result.confidence, ai_result.confidence)
            # 采用更高的严重程度
            severity = "high" if statistical_result.severity == "high" or ai_result.severity == "high" else "medium"
            # 优先使用AI的异常类型
            anomaly_type = ai_result.abnormal_type if ai_result.abnormal_type else statistical_result.anomaly_type
            # 合并建议
            recommendations = statistical_result.recommendations + [ai_result.recommendation]

        elif stat_abnormal and not ai_abnormal:
            # 统计方法认为是异常，AI认为不是
            # 如果统计方法置信度高，仍然认为是异常
            if statistical_result.confidence > 0.7:
                is_abnormal = True
                confidence = statistical_result.confidence * 0.8  # 降低置信度
                severity = statistical_result.severity
                anomaly_type = statistical_result.anomaly_type
                recommendations = statistical_result.recommendations + [
                    f"注意：AI模型认为此变化可能是正常的。AI分析：{ai_result.reasoning[:100]}..."
                ]
            else:
                is_abnormal = False
                confidence = 0.3
                severity = "low"
                anomaly_type = None
                recommendations = ["统计方法显示可能异常，但AI模型认为是正常变化"]

        elif not stat_abnormal and ai_abnormal:
            # 统计方法认为不是异常，AI认为是异常
            # 如果AI置信度高，认为是异常
            if ai_result.confidence > 0.8:
                is_abnormal = True
                confidence = ai_result.confidence * 0.7  # 降低置信度
                severity = ai_result.severity
                anomaly_type = ai_result.abnormal_type
                recommendations = [ai_result.recommendation] + [
                    f"注意：传统统计方法未检测到异常。AI发现：{ai_result.reasoning[:100]}..."
                ]
            else:
                is_abnormal = False
                confidence = 0.4
                severity = "low"
                anomaly_type = None
                recommendations = ["AI模型检测到潜在异常，但传统统计方法未确认"]

        else:
            # 两种方法都认为不是异常
            is_abnormal = False
            confidence = 0.1
            severity = "low"
            anomaly_type = None
            recommendations = []

        return is_abnormal, severity, confidence, anomaly_type, recommendations

# 实例化服务
energy_analysis_service = EnergyAnalysisService()
