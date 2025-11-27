
import json
import requests
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from dotenv import load_dotenv
from .. import schemas

# 加载环境变量
load_dotenv()

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
DASHSCOPE_MODEL = os.getenv("DEFAULT_ALI_MODEL")
DASHSCOPE_API_URL = os.getenv("ALI_BASE_URL")

# 验证必需的环境变量
if not DASHSCOPE_API_KEY:
    raise Exception("DASHSCOPE_API_KEY环境变量未设置")
if not DASHSCOPE_MODEL:
    raise Exception("DEFAULT_ALI_MODEL环境变量未设置")
if not DASHSCOPE_API_URL:
    raise Exception("ALI_BASE_URL环境变量未设置")


class AIAnomalyDetectionService:
    """AI辅助异常检测服务 - 结合通义千问大模型"""

    def __init__(self):
        self.api_timeout = 30  # API调用超时时间
        self.max_retries = 2   # 最大重试次数

    def _build_anomaly_detection_prompt(
        self,
        bill_type: schemas.BillType,
        current_month_data: schemas.EnergyTrendItem,
        historical_data: List[schemas.EnergyTrendItem],
        family_info: Dict,
        statistical_analysis: Dict
    ) -> str:
        """
        构建AI异常检测的提示词

        Args:
            bill_type: 能源类型
            current_month_data: 当月数据
            historical_data: 历史数据
            family_info: 家庭信息
            statistical_analysis: 统计分析结果

        Returns:
            构建好的提示词
        """
        energy_type_map = {
            "electricity": "电力",
            "gas": "燃气",
            "water": "水资源"
        }
        energy_type_str = energy_type_map[bill_type.value]
        energy_unit = "度" if bill_type == schemas.BillType.electricity else "立方米"

        # 构建历史数据摘要
        history_summary = []
        for i, data in enumerate(historical_data[-6:]):  # 最近6个月
            history_summary.append(
                f"{data.bill_date.strftime('%Y-%m')}: {data.usage:.1f}{energy_unit} ({data.amount:.1f}元)"
            )

        # 计算简单的环比数据
        if len(historical_data) >= 1:
            prev_month = historical_data[-1]
            month_over_month = ((current_month_data.usage - prev_month.usage) / prev_month.usage) * 100 if prev_month.usage > 0 else 0
        else:
            month_over_month = 0

        # 获取季节性信息
        current_month = current_month_data.bill_date.month
        current_season = self._get_season(current_month)

        # 分析历史数据的季节性模式
        seasonal_pattern = self._analyze_seasonal_pattern(historical_data)

        prompt = f"""
你是一位专业的家庭能耗分析专家，请帮我判断以下能耗数据是否异常。

## 基本信息
- 能源类型：{energy_type_str}
- 分析月份：{current_month_data.bill_date.strftime('%Y-%m')} ({current_season})
- 当月用量：{current_month_data.usage:.1f}{energy_unit}
- 当月费用：{current_month_data.amount:.1f}元
- 环比变化：{month_over_month:+.1f}%

## 季节性分析
- 当前季节：{current_season}
- 历史季节模式：{seasonal_pattern}

## 家庭背景
{json.dumps(family_info, ensure_ascii=False, indent=2)}

## 历史数据（最近6个月）
{chr(10).join(history_summary)}

## 统计分析结果
{json.dumps(statistical_analysis, ensure_ascii=False, indent=2)}

## 季节性判断标准
对于{energy_type_str}消费，请特别注意以下季节性规律：

**电力消费季节性特点：**
- 夏季（6-8月）：空调制冷需求增加，用电量通常上升15-30%
- 冬季（12-2月）：取暖设备使用，用电量通常上升10-25%
- 春季（3-5月）：气温适中，用电量相对较低
- 秋季（9-11月）：气温适中，用电量相对较低

**燃气消费季节性特点：**
- 冬季（12-2月）：取暖需求旺盛，燃气用量通常上升40-60%
- 夏季（6-8月）：燃气用量最低
- 春秋季：燃气用量适中

**水资源季节性特点：**
- 夏季：洗澡、洗衣等用水需求增加，用水量通常上升10-20%
- 冬季：用水量相对稳定

## 详细分析要求
请基于以下维度进行深入分析：

1. **季节性合理性分析**：对比当前季节与历史同期的差异
2. **数值异常性**：与历史数据相比是否出现显著偏离
3. **家庭规模匹配度**：结合{family_info.get('家庭人口', '未知')}人、{family_info.get('住房面积(㎡)', '未知')}㎡判断
4. **设备使用模式**：考虑季节性设备（空调、取暖器）的使用影响
5. **地理位置因素**：结合{family_info.get('所在地区', '未知')}地区的气候特点

## 特别关注点
- 当前处于{current_season}，这是{energy_type_str}消费的{self._get_seasonal_characteristic(current_season, bill_type)}季节
- 如果{current_month_data.bill_date.strftime('%m')}月的用量与历史同期相比差异超过{self._get_seasonal_threshold(current_season, bill_type)}%，需要重点分析

## 输出格式
请严格按照以下JSON格式输出，直接返回JSON对象：

{{
    "is_abnormal": true/false,
    "abnormal_type": "数值异常/季节异常/业务异常/无异常",
    "severity": "high/medium/low",
    "confidence": 0.0-1.0,
    "reasoning": "详细分析原因，必须包含季节性对比分析",
    "possible_explanations": ["可能的原因1（必须包含季节性因素）", "可能的原因2"],
    "recommendation": "针对性的处理建议（必须包含季节性应对措施）"
}}

## 分析重点
1. 必须详细分析当前季节对{energy_type_str}消费的影响
2. 对比同季节的历史数据，而非简单对比相邻月份
3. recommendation中必须包含针对当前季节的具体建议
4. reasoning必须明确说明季节性因素的影响程度

重要：只返回JSON对象本身，不要用```json```包裹，确保JSON格式完全正确。
"""
        return prompt

    def _get_season(self, month: int) -> str:
        """获取季节描述"""
        if month in [12, 1, 2]:
            return "冬季"
        elif month in [3, 4, 5]:
            return "春季"
        elif month in [6, 7, 8]:
            return "夏季"
        else:
            return "秋季"

    def _analyze_seasonal_pattern(self, historical_data: List[schemas.EnergyTrendItem]) -> str:
        """分析历史数据的季节性模式"""
        if not historical_data:
            return "无历史数据"

        # 按季节分组分析
        seasonal_data = {
            "春季": [],
            "夏季": [],
            "秋季": [],
            "冬季": []
        }

        for item in historical_data:
            season = self._get_season(item.bill_date.month)
            seasonal_data[season].append(item.usage)

        patterns = []
        for season, usages in seasonal_data.items():
            if usages:
                avg_usage = sum(usages) / len(usages)
                patterns.append(f"{season}平均{avg_usage:.1f}")

        return "、".join(patterns) if patterns else "数据不足"

    def _get_seasonal_characteristic(self, season: str, energy_type: schemas.BillType) -> str:
        """获取季节特征描述"""
        characteristics = {
            ("春季", "electricity"): "用电需求较低的",
            ("春季", "gas"): "燃气需求适中的",
            ("春季", "water"): "用水需求稳定的",
            ("夏季", "electricity"): "空调用电高负荷的",
            ("夏季", "gas"): "燃气需求最低的",
            ("夏季", "water"): "用水需求增加的",
            ("秋季", "electricity"): "用电需求适中的",
            ("秋季", "gas"): "燃气需求适中的",
            ("秋季", "water"): "用水需求稳定的",
            ("冬季", "electricity"): "取暖用电增加的",
            ("冬季", "gas"): "取暖燃气高负荷的",
            ("冬季", "water"): "用水需求稳定的",
        }
        # 处理可能的字符串输入
        energy_value = energy_type.value if hasattr(energy_type, 'value') else str(energy_type)
        return characteristics.get((season, energy_value), "季节变化明显的")

    def _get_seasonal_threshold(self, season: str, energy_type: schemas.BillType) -> str:
        """获取季节性判断阈值"""
        thresholds = {
            ("春季", "electricity"): "15",
            ("春季", "gas"): "20",
            ("春季", "water"): "10",
            ("夏季", "electricity"): "20",
            ("夏季", "gas"): "15",
            ("夏季", "water"): "15",
            ("秋季", "electricity"): "15",
            ("秋季", "gas"): "20",
            ("秋季", "water"): "10",
            ("冬季", "electricity"): "20",
            ("冬季", "gas"): "25",
            ("冬季", "water"): "10",
        }
        # 处理可能的字符串输入
        energy_value = energy_type.value if hasattr(energy_type, 'value') else str(energy_type)
        return thresholds.get((season, energy_value), "20")

    def detect_anomaly_with_ai(
        self,
        bill_type: schemas.BillType,
        current_month_data: schemas.EnergyTrendItem,
        historical_data: List[schemas.EnergyTrendItem],
        family_info: Optional[Dict] = None,
        statistical_analysis: Optional[Dict] = None
    ) -> schemas.AIAnomalyDetectionResult:
        """
        使用AI检测异常

        Args:
            bill_type: 能源类型
            current_month_data: 当月数据
            historical_data: 历史数据
            family_info: 家庭信息
            statistical_analysis: 统计分析结果

        Returns:
            AI异常检测结果
        """
        # 默认值处理
        if family_info is None:
            family_info = {"家庭人口": 1, "住房面积": 100}
        if statistical_analysis is None:
            statistical_analysis = {"method": "ai_only"}

        # 构建提示词
        prompt = self._build_anomaly_detection_prompt(
            bill_type, current_month_data, historical_data, family_info, statistical_analysis
        )

        # 调用AI API
        try:
            ai_response = self._call_ai_api(prompt)

            # 解析AI响应
            result_data = json.loads(ai_response)

            return schemas.AIAnomalyDetectionResult(
                is_abnormal=result_data.get("is_abnormal", False),
                abnormal_type=result_data.get("abnormal_type", "无异常"),
                severity=result_data.get("severity", "low"),
                confidence=result_data.get("confidence", 0.0),
                reasoning=result_data.get("reasoning", ""),
                possible_explanations=result_data.get("possible_explanations", []),
                recommendation=result_data.get("recommendation", ""),
                ai_model_used=DASHSCOPE_MODEL,
                api_timestamp=datetime.now()
            )

        except Exception as e:
            # AI调用失败时的降级处理
            print(f"AI异常检测调用失败: {str(e)}")
            return schemas.AIAnomalyDetectionResult(
                is_abnormal=False,
                abnormal_type="检测失败",
                severity="low",
                confidence=0.0,
                reasoning=f"AI服务暂时不可用: {str(e)}",
                possible_explanations=["AI服务异常"],
                recommendation="建议使用统计方法进行异常检测或稍后重试",
                ai_model_used="failed",
                api_timestamp=datetime.now()
            )

    def _call_ai_api(self, prompt: str) -> str:
        """
        调用通义千问API

        Args:
            prompt: 提示词

        Returns:
            AI响应内容
        """
        headers = {
            "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": DASHSCOPE_MODEL,
            "input": {
                "messages": [{"role": "user", "content": prompt}]
            },
            "parameters": {
                "result_format": "text",
                "temperature": 0.3,  # 降低随机性，提高判断一致性
                "top_p": 0.8,
                "max_tokens": 1000
            }
        }

        for attempt in range(self.max_retries + 1):
            try:
                response = requests.post(
                    DASHSCOPE_API_URL,
                    headers=headers,
                    json=data,
                    timeout=self.api_timeout
                )
                response.raise_for_status()

                # 解析通义千问API的响应格式
                response_data = response.json()

                # 提取output.text字段中的内容
                if "output" in response_data and "text" in response_data["output"]:
                    text_content = response_data["output"]["text"].strip()
                else:
                    raise Exception("API响应格式不正确，缺少output.text字段")

                # 多种方式尝试提取JSON内容
                json_str = ""

                # 方式1：处理 ```json 标记
                if "```json" in text_content:
                    start = text_content.find("```json") + 7
                    end = text_content.find("```", start)
                    if end != -1:
                        json_str = text_content[start:end].strip()
                else:
                    # 方式2：直接查找JSON对象
                    # 找到第一个 { 和最后一个 }
                    start = text_content.find("{")
                    end = text_content.rfind("}")
                    if start != -1 and end != -1 and start < end:
                        json_str = text_content[start:end+1].strip()

                # 如果没找到，尝试其他方法
                if not json_str:
                    # 方式3：使用正则表达式匹配JSON对象
                    import re
                    json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
                    matches = re.findall(json_pattern, text_content, re.DOTALL)
                    if matches:
                        # 取最长的匹配（通常是最完整的JSON对象）
                        json_str = max(matches, key=len)

                if not json_str:
                    raise Exception(f"无法从响应中提取JSON内容: {text_content}")

                # 清理JSON字符串中的特殊字符
                json_str = json_str.replace('\n', ' ').replace('\r', '').replace('\t', ' ')

                # 验证JSON格式
                try:
                    parsed_json = json.loads(json_str)
                except json.JSONDecodeError as json_error:
                    # 尝试修复常见的JSON问题
                    try:
                        # 移除可能的尾部逗号
                        json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
                        # 尝试再次解析
                        parsed_json = json.loads(json_str)
                    except:
                        raise Exception(f"JSON解析失败: {str(json_error)}\n提取的JSON: {json_str}")

                # 确保包含必要字段
                required_fields = ["is_abnormal", "abnormal_type", "severity", "confidence"]
                missing_fields = [field for field in required_fields if field not in parsed_json]
                if missing_fields:
                    # 尝试从文本中推测缺失的字段
                    if "is_abnormal" in missing_fields:
                        # 如果文本中包含"异常"字样，设为true，否则false
                        parsed_json["is_abnormal"] = "异常" in text_content and "无异常" not in text_content
                    if "abnormal_type" in missing_fields:
                        parsed_json["abnormal_type"] = "业务异常" if parsed_json.get("is_abnormal") else "无异常"
                    if "severity" in missing_fields:
                        parsed_json["severity"] = "medium" if parsed_json.get("is_abnormal") else "low"
                    if "confidence" in missing_fields:
                        parsed_json["confidence"] = 0.7 if parsed_json.get("is_abnormal") else 0.3

                return json.dumps(parsed_json, ensure_ascii=False)  # 重新序列化为字符串

            except requests.exceptions.Timeout:
                if attempt == self.max_retries:
                    raise Exception("API调用超时")
                continue

            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries:
                    raise Exception(f"API调用失败: {str(e)}")
                continue

            except json.JSONDecodeError as e:
                if attempt == self.max_retries:
                    # 记录原始响应以便调试
                    original_response = response_data if 'response_data' in locals() else "未知"
                    raise Exception(f"AI响应JSON格式错误: {str(e)}\n提取的JSON: {json_str}\n原始响应: {original_response}")
                continue

            except Exception as e:
                if attempt == self.max_retries:
                    raise Exception(f"处理AI响应时出错: {str(e)}")
                continue

        raise Exception("AI调用失败")

    def batch_detect_anomalies(
        self,
        bill_type: schemas.BillType,
        trend_data: List[schemas.EnergyTrendItem],
        family_info: Optional[Dict] = None
    ) -> List[schemas.AIAnomalyDetectionResult]:
        """
        批量检测异常月份

        Args:
            bill_type: 能源类型
            trend_data: 趋势数据
            family_info: 家庭信息

        Returns:
            异常检测结果列表
        """
        if len(trend_data) < 2:
            return []

        results = []

        # 只检测最近的几个月（避免API调用过多）
        recent_months = min(6, len(trend_data))
        start_index = len(trend_data) - recent_months

        for i in range(start_index, len(trend_data)):
            current_data = trend_data[i]
            historical_data = trend_data[:i]

            if not historical_data:
                continue

            # 进行简单的统计分析
            statistical_analysis = self._calculate_simple_stats(historical_data, current_data)

            # AI检测
            ai_result = self.detect_anomaly_with_ai(
                bill_type, current_data, historical_data, family_info, statistical_analysis
            )

            results.append(ai_result)

        return results

    def _calculate_simple_stats(
        self,
        historical_data: List[schemas.EnergyTrendItem],
        current_data: schemas.EnergyTrendItem
    ) -> Dict:
        """计算简单的统计数据供AI参考"""
        if not historical_data:
            return {}

        usages = [item.usage for item in historical_data]
        avg_usage = sum(usages) / len(usages) if usages else 0
        max_usage = max(usages) if usages else 0
        min_usage = min(usages) if usages else 0

        # 计算环比
        if historical_data:
            month_over_month = ((current_data.usage - historical_data[-1].usage) / historical_data[-1].usage) * 100 if historical_data[-1].usage > 0 else 0
        else:
            month_over_month = 0

        return {
            "avg_usage": round(avg_usage, 2),
            "max_usage": round(max_usage, 2),
            "min_usage": round(min_usage, 2),
            "current_vs_avg": round(((current_data.usage - avg_usage) / avg_usage) * 100, 2) if avg_usage > 0 else 0,
            "month_over_month": round(month_over_month, 2),
            "data_points": len(historical_data)
        }


# 实例化服务
ai_anomaly_detection_service = AIAnomalyDetectionService()