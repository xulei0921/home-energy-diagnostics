import json
from datetime import datetime, timedelta, date

from sqlalchemy import extract, case, func
from sqlalchemy.orm import Session
from typing import List, Tuple, Optional
import numpy as np
from . import data_processing
from .. import schemas, models
from .ai_service import AISuggestionService


class EnergyAnalysisService:
    @staticmethod
    def get_energy_trend(
        db: Session,
        user_id: int,
        period: schemas.AnalysisPeriod,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        bill_type: Optional[schemas.BillType] = None,
        # limit: int = 12
    ) -> List[schemas.EnergyTrendItem]:
        """获取能耗趋势数据"""

        analysis_start_date, analysis_end_date = data_processing.get_date_range_for_period(period, start_date, end_date)

        if period == schemas.AnalysisPeriod.monthly:
            if bill_type is None:
                bills = db.query(models.EnergyBill).filter(
                    models.EnergyBill.user_id == user_id,
                    models.EnergyBill.bill_date >= analysis_start_date,
                    models.EnergyBill.bill_date <= analysis_end_date
                ).order_by(models.EnergyBill.bill_date.desc()).all()

            else:
                bills = db.query(models.EnergyBill).filter(
                    models.EnergyBill.user_id == user_id,
                    models.EnergyBill.bill_type == bill_type,
                    models.EnergyBill.bill_date >= analysis_start_date,
                    models.EnergyBill.bill_date <= analysis_end_date
                ).order_by(models.EnergyBill.bill_date.desc()).all()

            bills.reverse()

            trend_data = [
                schemas.EnergyTrendItem(
                    bill_type=bill.bill_type,
                    bill_date=bill.bill_date,
                    usage=bill.usage,
                    amount=bill.amount
                ) for bill in bills
            ]
            return trend_data

        # elif period == schemas.AnalysisPeriod.quarter:
        #     year = date.today().year
        #     quarter_expr = case(
        #         [
        #             (extract('month', models.EnergyBill.bill_date).between(1, 3), 1),
        #             (extract('month', models.EnergyBill.bill_date).between(4, 6), 2),
        #             (extract('month', models.EnergyBill.bill_date).between(7, 9), 3),
        #             (extract('month', models.EnergyBill.bill_date).between(10, 12), 4),
        #         ],
        #         else_ = 0
        #     ).label('quarter')
        #
        #     # 单次查询所有季度汇总
        #     if bill_type is None:
        #         quarter_data = db.query(
        #             quarter_expr,
        #             func.sum(models.EnergyBill.usage).label('total_usage'),
        #             func.sum(models.EnergyBill.amount).label('total_cost'),
        #         ).filter(
        #             models.EnergyBill.user_id == user_id,
        #             extract('year', models.EnergyBill.bill_date) == year
        #         ).group_by(
        #             quarter_expr
        #         ).order_by(
        #             quarter_expr
        #         ).all()
        #     else:
        #         quarter_data = db.query(
        #             quarter_expr,
        #             func.sum(models.EnergyBill.usage).label('total_usage'),
        #             func.sum(models.EnergyBill.amount).label('total_cost'),
        #         ).filter(
        #             models.EnergyBill.user_id == user_id,
        #             models.EnergyBill.bill_type == bill_type,
        #             extract('year', models.EnergyBill.bill_date) == year
        #         ).group_by(
        #             quarter_expr
        #         ).order_by(
        #             quarter_expr
        #         ).all()
        #
        #     trend_data = [
        #         schemas.EnergyTrendItem(
        #             bill_type=bill.bill_type,
        #             bill_date=bill.bill_date,
        #             usage=bill.usage,
        #             amount=bill.amount
        #         ) for bill in quarter_data
        #     ]
        #     return trend_data

        # 按账单日期降序排序，取最近limit条
        # if bill_type is None:
        #     bills = db.query(models.EnergyBill).filter(
        #         models.EnergyBill.user_id == user_id
        #     ).order_by(models.EnergyBill.bill_date.desc()).limit(limit).all()
        #
        # else:
        #     bills = db.query(models.EnergyBill).filter(
        #         models.EnergyBill.user_id == user_id,
        #         models.EnergyBill.bill_type == bill_type
        #     ).order_by(models.EnergyBill.bill_date.desc()).limit(limit).all()

        # 反转顺序（按时间升序）
        # bills.reverse()
        #
        # trend_data = [
        #     schemas.EnergyTrendItem(
        #         bill_type=bill.bill_type,
        #         bill_date=bill.bill_date,
        #         usage=bill.usage,
        #         amount=bill.amount,
        #         month=bill.bill_date.strftime("%Y-%m")
        #     ) for bill in bills
        # ]
        # return trend_data

    @staticmethod
    def calculate_comparison(trend_data: List[schemas.EnergyTrendItem]) -> schemas.EnergyComparison:
        """计算同比、环比增长率，判断是否异常"""
        if not trend_data:
            return schemas.EnergyComparison(
                current_usage=0,
                previous_usage=None,
                yoy_rate=None,
                mom_rate=None,
                is_abnormal=False
            )

        # 当前最新数据
        current = trend_data[-1]
        current_usage = current.usage

        # 环比（与上一个月比较）
        mom_rate = None
        previous_usage = None
        if len(trend_data) >= 2:
            previous = trend_data[-2]
            previous_usage = previous.usage
            mom_rate = ((current_usage - previous_usage) / previous_usage) * 100 if previous_usage != 0 else 0

        # 同比（与去年同月比较）
        yoy_rate = None
        current_year = current.bill_date.year
        current_month = current.bill_date.month
        for item in trend_data[:-1]:  # 排除当前月
            if item.bill_date.year == current_year - 1 and item.bill_date.month == current_month:
                yoy_rate = ((current_usage - item.usage) / item.usage) * 100 if item.usage != 0 else 0
                break

        # 判断是否异常（增长率超过30%）
        is_abnormal = abs(mom_rate) > 30 if mom_rate else False

        return schemas.EnergyComparison(
            current_usage=current_usage,
            previous_usage=previous_usage,
            yoy_rate=round(yoy_rate, 2) if yoy_rate else None,
            mom_rate=round(mom_rate, 2) if mom_rate else None,
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

    def generate_analysis_and_suggestions(
        self,
        db: Session,
        user_id: int,
        bill_type: schemas.BillType
    ) -> schemas.AnalysisResult:
        """生成完整的能耗分析结果和AI节能建议"""
        # 1. 获取趋势数据
        trend_data = self.get_energy_trend(db, user_id, bill_type)
        if not trend_data:
            return schemas.AnalysisResult(
                trend_data=[],
                comparison=schemas.EnergyComparison(current_usage=0, previous_usage=None, yoy_rate=None, mom_rate=None, is_abnormal=False),
                device_consumption=[],
                suggestions=[]
            )

        # 2. 计算同比环比
        comparison = self.calculate_comparison(trend_data)

        # 3. 计算设备能耗占比
        latest_bill_date = trend_data[-1].bill_date
        device_consumption = self.calculate_device_consumption(db, user_id, bill_type, latest_bill_date)

        # 4. 获取家庭信息
        family_info = db.query(models.FamilyInfo).filter(models.FamilyInfo.user_id == user_id).first()
        family_info_dict = {
            "家庭人口": family_info.family_size if family_info else 1,
            "住房面积(㎡)": family_info.house_area if family_info else None,
            "所在地区": family_info.location if family_info else None,
            "房龄(年)": family_info.building_age if family_info else None
        }

        # 5. 构建趋势分析文本
        trend_analysis = f"""
        最近{len(trend_data)}个月{bill_type.value}使用情况:
        - 最新月份 ({latest_bill_date.strftime("%Y-%m")}) 用量: {trend_data[-1].usage} {'度' if bill_type == schemas.BillType.electricity else '立方米'}, 费用: {trend_data[-1].amount}元
        - 环比变化: {comparison.mom_rate}% (上月用量: {comparison.previous_usage})
        - 同比变化: {comparison.yoy_rate}% (去年同月用量)
        """

        # 6. 构建设备能耗占比文本
        device_text = "高耗能设备TOP3: \n"
        for i, device in enumerate(device_consumption[:3], 1):
            device_text += f"- {device.device_name}: 月能耗{device.monthly_usage} {'度' if bill_type == schemas.BillType.electricity else '立方米'}, 占比{device.consumption}%\n"

        # 7. 调用AI生成建议
        ai_service = AISuggestionService()
        suggestion_text = ai_service.generate_suggestion(
            bill_type=bill_type,
            trend_analysis=trend_analysis,
            device_consumption=device_text,
            family_info=family_info_dict,
            abnormal=comparison.is_abnormal
        )

        # print(suggestion_text)

        response_data = json.loads(suggestion_text)
        text_content = response_data.get("output", {}).get("text", "")
        parsed_text = json.loads(text_content)

        # print(parsed_text)

        # 8. 保存建议到数据库
        # suggestion = models.EnergySavingSuggestion(
        #     user_id=user_id,
        #     bill_type=bill_type,
        #     suggestion_text=suggestion_text,
        #     suggestion_date=datetime.now().date(),
        #     impact_rating=3 if comparison.is_abnormal else 2
        # )
        # db.add(suggestion)
        # db.commit()
        # db.refresh(suggestion)

        for suggestion in parsed_text['suggestions']:
            # 检查是否已存在类似建议
            existing = db.query(models.EnergySavingSuggestion).filter(
                models.EnergySavingSuggestion.suggestion_title == suggestion["suggestion_title"],
                models.EnergySavingSuggestion.user_id == user_id
            ).first()

            if not existing:
                db_suggestion = models.EnergySavingSuggestion(
                    user_id=user_id,
                    bill_type=bill_type,
                    suggestion_title=suggestion['suggestion_title'],
                    suggestion_text=suggestion['suggestion_text'],
                    suggestion_date=datetime.now().date(),
                    impact_rating=3 if comparison.is_abnormal else 2
                )
                db.add(db_suggestion)
        db.commit()
        db.refresh(db_suggestion)

        # 9. 获取历史建议（最近3条）
        db_suggestions = db.query(models.EnergySavingSuggestion).filter(
            models.EnergySavingSuggestion.user_id == user_id,
            models.EnergySavingSuggestion.bill_type == bill_type
        ).order_by(models.EnergySavingSuggestion.created_at.desc()).limit(3).all()

        suggestions = []
        for sugg in db_suggestions:
            # 提取字段字典（排除ORM内部属性，如_sa_instance_state）
            sugg_dict = {k: v for k, v in sugg.__dict__.items() if not k.startswith('_')}
            # 用字典创建Pydantic模型
            suggestions.append(schemas.EnergySavingSuggestionResponse.model_validate(sugg_dict))

        return schemas.AnalysisResult(
            trend_data=trend_data,
            comparison=comparison,
            device_consumption=device_consumption,
            suggestions=suggestions
        )

# 实例化服务
energy_analysis_service = EnergyAnalysisService()
