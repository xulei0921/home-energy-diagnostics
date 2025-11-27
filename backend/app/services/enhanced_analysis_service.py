import json
import os
import requests
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from typing import List, Optional
from .ai_service import AISuggestionService
from .ai_anomaly_detection import ai_anomaly_detection_service
from .. import schemas, models


class EnhancedAnalysisService:
    """增强版分析服务 - 支持多能源类型和AI智能分析"""

    def generate_analysis_and_suggestions(
        self,
        db: Session,
        user_id: int,
        bill_type: Optional[schemas.BillType] = None,
        period: schemas.AnalysisPeriod = schemas.AnalysisPeriod.monthly,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> schemas.ComprehensiveAnalysisResult:
        """
        生成智能能耗分析结果和AI节能建议 - 增强版本

        Args:
            db: 数据库会话
            user_id: 用户ID
            bill_type: 能源类型（可选，不填时分析所有类型）
            period: 分析周期
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            综合分析结果，包含多能源类型分析和AI建议
        """
        # 确定要分析的能源类型
        if bill_type:
            energy_types = [bill_type]
        else:
            energy_types = [schemas.BillType.electricity, schemas.BillType.gas, schemas.BillType.water]

        # 获取家庭信息
        family_info = db.query(models.FamilyInfo).filter(models.FamilyInfo.user_id == user_id).first()
        family_info_dict = {
            "家庭人口": family_info.family_size if family_info else 1,
            "住房面积(㎡)": family_info.house_area if family_info else 100,
            "所在地区": family_info.location if family_info else "未知",
            "房龄(年)": family_info.building_age if family_info else 10
        }

        # 收集所有能源类型的分析结果
        energy_analyses = []
        total_suggestions = []

        for energy_type in energy_types:
            try:
                # 获取单个能源类型的分析
                analysis_result = self._analyze_single_energy_type(
                    db, user_id, energy_type, period, start_date, end_date, family_info_dict
                )

                if analysis_result:
                    energy_analyses.append(analysis_result)
                    total_suggestions.extend(analysis_result.suggestions)

            except Exception as e:
                print(f"分析 {energy_type.value} 时出错: {str(e)}")
                continue

        # 生成综合AI建议（如果分析了多种能源类型）
        comprehensive_suggestions = []
        if len(energy_types) > 1 and energy_analyses:
            comprehensive_suggestions = self._generate_comprehensive_suggestions(
                energy_analyses, family_info_dict
            )
            total_suggestions.extend(comprehensive_suggestions)

        # 获取历史建议
        historical_suggestions = self._get_historical_suggestions(db, user_id, bill_type)
        all_suggestions = total_suggestions + historical_suggestions

        # 去重并限制数量
        unique_suggestions = []
        seen_titles = set()
        for suggestion in all_suggestions:
            if suggestion.suggestion_title not in seen_titles:
                unique_suggestions.append(suggestion)
                seen_titles.add(suggestion.suggestion_title)

        # 限制最多返回10条建议
        final_suggestions = unique_suggestions[:10]

        return schemas.ComprehensiveAnalysisResult(
            energy_analyses=energy_analyses,
            overall_summary=self._generate_overall_summary(energy_analyses),
            suggestions=final_suggestions,
            analysis_date=datetime.now(),
            analyzed_energy_types=[et.value for et in energy_types]
        )

    def _analyze_single_energy_type(
        self,
        db: Session,
        user_id: int,
        bill_type: schemas.BillType,
        period: schemas.AnalysisPeriod,
        start_date: Optional[date],
        end_date: Optional[date],
        family_info: dict
    ) -> Optional[schemas.EnergyTypeAnalysis]:
        """分析单个能源类型"""
        # 导入原始分析服务
        from .analysis_service import energy_analysis_service

        # 1. 获取趋势数据
        trend_data = energy_analysis_service.get_energy_trend(db, user_id, period, start_date, end_date, bill_type)
        if not trend_data:
            return None

        # 2. 计算同比环比
        comparison = energy_analysis_service.calculate_comparison(trend_data)

        # 3. 计算设备能耗占比
        latest_bill_date = trend_data[-1].bill_date
        device_consumption = energy_analysis_service.calculate_device_consumption(db, user_id, bill_type, latest_bill_date)

        # 4. 检测异常月份
        try:
            anomaly_months = energy_analysis_service.detect_anomaly_months(db, user_id, bill_type, months=12, use_ai=True)
        except Exception as e:
            print(f"AI异常检测失败，使用统计方法: {str(e)}")
            anomaly_months = []

        # 5. 生成AI分析和建议
        ai_analysis = self._generate_ai_energy_analysis(
            bill_type, trend_data, comparison, device_consumption, family_info, anomaly_months
        )

        return schemas.EnergyTypeAnalysis(
            bill_type=bill_type,
            trend_data=trend_data,
            comparison=comparison,
            device_consumption=device_consumption,
            anomaly_months=anomaly_months,
            ai_analysis=ai_analysis,
            suggestions=ai_analysis.suggestions
        )

    def _generate_ai_energy_analysis(
        self,
        bill_type: schemas.BillType,
        trend_data: List[schemas.EnergyTrendItem],
        comparison: schemas.EnergyComparison,
        device_consumption: List[schemas.DeviceEnergyConsumption],
        family_info: dict,
        anomaly_months: List[schemas.AnomalyMonthResult]
    ) -> schemas.AIEnergyAnalysis:
        """生成AI驱动的能源分析"""
        try:
            # 构建专业的分析提示词
            prompt = self._build_energy_analysis_prompt(
                bill_type, trend_data, comparison, device_consumption, family_info, anomaly_months
            )

            # 调用AI服务
            ai_service = AISuggestionService()
            response = self._call_ai_analysis_service(ai_service, prompt)

            # 解析AI响应
            ai_result = self._parse_ai_response(response)

            return schemas.AIEnergyAnalysis(
                overall_assessment=ai_result.get("assessment", "暂无评估"),
                key_insights=ai_result.get("insights", []),
                risk_level=ai_result.get("risk_level", "medium"),
                optimization_potential=ai_result.get("optimization_potential", "medium"),
                seasonal_analysis=ai_result.get("seasonal_analysis", ""),
                suggestions=self._convert_ai_suggestions(ai_result.get("suggestions", []), bill_type),
                confidence_score=ai_result.get("confidence", 0.7)
            )

        except Exception as e:
            print(f"AI分析失败: {str(e)}")
            # 返回默认分析
            return self._generate_default_analysis(bill_type, comparison)

    def _build_energy_analysis_prompt(
            self,
            bill_type: schemas.BillType,
            trend_data: List[schemas.EnergyTrendItem],
            comparison: schemas.EnergyComparison,
            device_consumption: List[schemas.DeviceEnergyConsumption],
            family_info: dict,
            anomaly_months: List[schemas.AnomalyMonthResult]
    ) -> str:
        """构建专业的能源分析提示词"""
        energy_map = {
            "electricity": "电力",
            "gas": "燃气",
            "water": "水资源"
        }
        energy_type = energy_map.get(bill_type.value if bill_type else "electricity", "电力")
        unit = "度" if bill_type == schemas.BillType.electricity else "立方米"
        # 构建趋势数据描述
        trend_desc = []
        if trend_data:
            for item in trend_data[-6:]:  # 最近6个月
                date_str = item.bill_date.strftime('%Y-%m') if item.bill_date else '未知日期'
                usage = item.usage if item.usage is not None else 0.0  # 兜底 None
                amount = item.amount if item.amount is not None else 0.0  # 兜底 None
                trend_desc.append(f"{date_str}: {usage:.1f}{unit} ({amount:.1f}元)")
        # 构建设备数据描述
        device_desc = []
        if device_consumption:
            for device in device_consumption[:3]:
                device_name = device.device_name or '未知设备'
                monthly_usage = device.monthly_usage if device.monthly_usage is not None else 0.0  # 兜底 None
                consumption = device.consumption if device.consumption is not None else 0.0  # 兜底 None（确保是数字）
                device_desc.append(
                    f"{device_name}: {monthly_usage:.1f}{unit}/月 (占比{consumption:.1f}%)")  # 加 .1f 统一格式
        # 构建异常月份描述
        anomaly_desc = []
        if anomaly_months:
            for anomaly in anomaly_months:
                year = anomaly.year if anomaly.year is not None else 0
                month = anomaly.month if anomaly.month is not None else 0  # 兜底 None
                deviation = anomaly.deviation if anomaly.deviation is not None else 0.0  # 兜底 None
                severity = anomaly.severity or '未知'
                anomaly_desc.append(f"{year}-{month:02d}: 偏差{deviation:+.1f}% ({severity}严重)")
        # 处理最新月份用量（兜底 None）
        latest_usage = 0.0
        if trend_data and trend_data[-1].usage is not None:
            latest_usage = trend_data[-1].usage
        # 处理环比/同比（兜底 None）
        usage_mom_rate = comparison.usage_mom_rate if comparison.usage_mom_rate is not None else 0.0
        usage_yoy_rate = comparison.usage_yoy_rate if comparison.usage_yoy_rate is not None else 0.0
        is_abnormal = comparison.is_abnormal if comparison.is_abnormal is not None else False
        # 处理季节
        current_month = datetime.now().month
        if trend_data and trend_data[-1].bill_date:
            current_month = trend_data[-1].bill_date.month
        season = self._get_season(current_month)
        # 处理家庭信息（兜底空字典）
        family_info = family_info or {}
        prompt = f"""
你是专业的家庭能源分析师，请基于以下数据对用户的{energy_type}使用情况进行深度分析：
## 家庭背景信息
{json.dumps(family_info, ensure_ascii=False, indent=2)}
## {energy_type}使用趋势（最近6个月）
{chr(10).join(trend_desc) if trend_desc else '暂无趋势数据'}
## 关键指标
- 最新月份用量: {latest_usage:.1f}{unit}
- 环比变化: {usage_mom_rate:+.1f}%
- 同比变化: {usage_yoy_rate:+.1f}%
- 是否异常: {'是' if is_abnormal else '否'}
- 当前季节: {season}
## 设备能耗分析
{chr(10).join(device_desc) if device_desc else '暂无设备数据'}
## 异常月份检测
{chr(10).join(anomaly_desc) if anomaly_desc else '未检测到明显异常'}
## 分析要求
请提供专业、可操作的能源分析报告，重点关注：
1. **使用模式分析**: 识别{energy_type}消费的规律和特点
2. **效率评估**: 基于家庭规模和使用习惯评估能效水平
3. **季节性影响**: 分析季节变化对{energy_type}消费的影响
4. **设备优化**: 识别高耗能设备和优化机会
5. **风险评估**: 评估潜在的能效风险和成本压力
6. **改进潜力**: 估算节能潜力和预期效果
## 输出格式
请严格按照以下JSON格式返回：
{{
    "assessment": "整体评估概述（50-100字）",
    "insights": [
        "关键发现1（具体数据支撑）",
        "关键发现2（具体数据支撑）",
        "关键发现3（具体数据支撑）"
    ],
    "risk_level": "low/medium/high",
    "optimization_potential": "low/medium/high",
    "seasonal_analysis": "季节性分析结果（50-80字）",
    "suggestions": [
        {{
            "title": "建议标题1",
            "content": "具体建议内容（包含可执行措施）",
            "priority": "high/medium/low",
            "potential_savings": "预期节能效果描述"
        }}
    ],
    "confidence": 0.0-1.0
}}
重要要求：
- 所有分析必须基于提供的数据，避免主观臆测
- 建议必须具体可执行，包含量化指标
- 优先考虑季节性因素和家庭实际情况
- 节能潜力估算要合理可信
"""
        return prompt

    def _call_ai_analysis_service(self, ai_service, prompt: str) -> str:
        """调用AI分析服务"""
        # 这里需要适配现有的AI服务接口
        api_key = os.getenv('DASHSCOPE_API_KEY')
        if not api_key:
            raise Exception("DASHSCOPE_API_KEY环境变量未设置")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": os.getenv("DEFAULT_ALI_MODEL"),
            "input": {
                "messages": [{"role": "user", "content": prompt}]
            },
            "parameters": {
                "result_format": "text",
                "temperature": 0.3,
                "max_tokens": 1500
            }
        }

        try:
            response = requests.post(
                os.getenv("ALI_BASE_URL"),
                headers=headers,
                json=data,
                timeout=60
            )
            response.raise_for_status()
            return response.text
        except Exception as e:
            raise Exception(f"AI服务调用失败: {str(e)}")

    def _parse_ai_response(self, response: str) -> dict:
        """解析AI响应"""
        try:
            # 解析通义千问API的响应格式
            response_data = json.loads(response)

            if "output" in response_data and "text" in response_data["output"]:
                text_content = response_data["output"]["text"].strip()

                # 提取JSON内容
                if "```json" in text_content:
                    start = text_content.find("```json") + 7
                    end = text_content.find("```", start)
                    if end != -1:
                        json_str = text_content[start:end].strip()
                    else:
                        json_str = text_content
                else:
                    # 直接查找JSON对象
                    start = text_content.find("{")
                    end = text_content.rfind("}")
                    if start != -1 and end != -1:
                        json_str = text_content[start:end+1]
                    else:
                        json_str = text_content

                return json.loads(json_str)
            else:
                raise Exception("API响应格式不正确")

        except Exception as e:
            print(f"AI响应解析失败: {str(e)}")
            return {}

    def _convert_ai_suggestions(self, ai_suggestions: List[dict], bill_type: Optional[schemas.BillType]) -> List[schemas.EnergySavingSuggestionResponse]:
        """转换AI建议为标准格式"""
        suggestions = []
        for i, ai_sugg in enumerate(ai_suggestions):
            try:
                suggestion = schemas.EnergySavingSuggestionResponse(
                    id=0,  # 临时ID
                    user_id=0,  # 临时用户ID
                    bill_type=bill_type or schemas.BillType.electricity,
                    suggestion_title=ai_sugg.get("title", f"节能建议{i+1}"),
                    suggestion_text=ai_sugg.get("content", ""),
                    suggestion_date=date.today(),
                    impact_rating=self._convert_priority_to_rating(ai_sugg.get("priority", "medium")),
                    is_implemented=False,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                suggestions.append(suggestion)
            except Exception as e:
                print(f"转换建议时出错: {str(e)}")
                continue

        return suggestions

    def _convert_priority_to_rating(self, priority: str) -> int:
        """将优先级转换为评级"""
        priority_map = {"high": 5, "medium": 3, "low": 1}
        return priority_map.get(priority, 3)

    def _generate_default_analysis(self, bill_type: schemas.BillType, comparison: schemas.EnergyComparison) -> schemas.AIEnergyAnalysis:
        """生成默认分析（AI服务不可用时）"""
        return schemas.AIEnergyAnalysis(
            overall_assessment=f"基于数据分析，您的{bill_type.value}使用情况{'正常' if not comparison.is_abnormal else '需要关注'}",
            key_insights=[f"环比变化: {comparison.usage_mom_rate:+.1f}%"],
            risk_level="medium",
            optimization_potential="medium",
            seasonal_analysis="暂无季节性数据",
            suggestions=[],
            confidence_score=0.5
        )

    def _generate_comprehensive_suggestions(
        self,
        energy_analyses: List[schemas.EnergyTypeAnalysis],
        family_info: dict
    ) -> List[schemas.EnergySavingSuggestionResponse]:
        """生成综合建议（多能源类型）"""
        try:
            # 构建综合分析提示词
            prompt = self._build_comprehensive_prompt(energy_analyses, family_info)

            # 调用AI服务
            response = self._call_ai_analysis_service(AISuggestionService(), prompt)
            ai_result = self._parse_ai_response(response)

            # 转换建议格式
            return self._convert_ai_suggestions(ai_result.get("suggestions", []), None)

        except Exception as e:
            print(f"生成综合建议失败: {str(e)}")
            return []

    def _build_comprehensive_prompt(
        self,
        energy_analyses: List[schemas.EnergyTypeAnalysis],
        family_info: dict
    ) -> str:
        """构建综合分析提示词"""
        # 构建各能源类型的简要分析
        energy_summaries = []
        for analysis in energy_analyses:
            energy_summaries.append(f"""
{analysis.bill_type.value}:
- 最新用量: {analysis.trend_data[-1].usage:.1f}
- 环比变化: {analysis.comparison.usage_mom_rate:+.1f}%
- 异常状态: {'是' if analysis.comparison.is_abnormal else '否'}
""")

        prompt = f"""
基于用户的多种能源使用数据，提供整体性的节能建议：

## 家庭信息
{json.dumps(family_info, ensure_ascii=False, indent=2)}

## 各能源类型概况
{chr(10).join(energy_summaries)}

## 要求
请从以下角度提供综合建议：
1. 多能源协同优化
2. 整体成本控制策略
3. 系统性能源管理
4. 跨季节调节策略

## 输出格式
{{
    "suggestions": [
        {{
            "title": "综合建议标题",
            "content": "具体建议内容",
            "priority": "high/medium/low",
            "potential_savings": "预期综合效益"
        }}
    ]
}}
"""
        return prompt

    def _generate_overall_summary(self, energy_analyses: List[schemas.EnergyTypeAnalysis]) -> str:
        """生成整体摘要"""
        if not energy_analyses:
            return "暂无数据进行分析"

        total_amount = sum(analysis.comparison.current_amount for analysis in energy_analyses)
        abnormal_count = sum(1 for analysis in energy_analyses if analysis.comparison.is_abnormal)

        summary = f"分析了{len(energy_analyses)}种能源类型，总费用{total_amount:.1f}元"
        if abnormal_count > 0:
            summary += f"，其中{abnormal_count}种能源存在异常"

        return summary

    def _get_historical_suggestions(
        self,
        db: Session,
        user_id: int,
        bill_type: Optional[schemas.BillType]
    ) -> List[schemas.EnergySavingSuggestionResponse]:
        """获取历史建议"""
        query = db.query(models.EnergySavingSuggestion).filter(
            models.EnergySavingSuggestion.user_id == user_id
        )

        if bill_type:
            query = query.filter(models.EnergySavingSuggestion.bill_type == bill_type)

        suggestions = query.order_by(
            models.EnergySavingSuggestion.created_at.desc()
        ).limit(5).all()

        result = []
        for sugg in suggestions:
            sugg_dict = {k: v for k, v in sugg.__dict__.items() if not k.startswith('_')}
            result.append(schemas.EnergySavingSuggestionResponse.model_validate(sugg_dict))

        return result

    def _get_season(self, month: int) -> str:
        """获取季节"""
        if month in [12, 1, 2]:
            return "冬季"
        elif month in [3, 4, 5]:
            return "春季"
        elif month in [6, 7, 8]:
            return "夏季"
        else:
            return "秋季"


# 实例化增强分析服务
enhanced_analysis_service = EnhancedAnalysisService()