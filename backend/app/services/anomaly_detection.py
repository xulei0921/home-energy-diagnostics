import numpy as np
import statistics
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from sqlalchemy.orm import Session
from .. import models, schemas

# 尝试导入scipy，如果不可用则使用numpy的统计函数
try:
    from scipy import stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    # 创建一个简单的替代函数
    class SimpleStats:
        @staticmethod
        def linregress(x, y):
            """简单的线性回归实现"""
            n = len(x)
            if n < 2:
                return (0, 0, 0, 1, 0)

            x_mean, y_mean = np.mean(x), np.mean(y)
            xy_mean = np.mean(x * y)
            x2_mean = np.mean(x * x)

            # 计算斜率
            slope = (xy_mean - x_mean * y_mean) / (x2_mean - x_mean * x_mean) if (x2_mean - x_mean * x_mean) != 0 else 0

            # 计算截距
            intercept = y_mean - slope * x_mean

            # 计算相关系数
            if np.std(x) == 0 or np.std(y) == 0:
                r_value = 0
            else:
                r_value = np.corrcoef(x, y)[0, 1] if len(np.corrcoef(x, y)) > 1 else 0

            # 简单的p值和标准误差估算
            p_value = 0.05 if abs(r_value) > 0.5 else 0.5
            std_err = np.std(y) / np.sqrt(n) if n > 0 else 0

            return (slope, intercept, r_value, p_value, std_err)

    stats = SimpleStats()


class AnomalyDetectionService:
    """智能异常检测服务 - 使用多种统计方法和机器学习算法"""

    @staticmethod
    def calculate_statistical_threshold(
        historical_data: List[float],
        method: str = "iqr",
        sensitivity: float = 1.5
    ) -> Tuple[float, float]:
        """
        基于历史数据计算动态阈值 - 修复版本

        Args:
            historical_data: 历史能耗数据
            method: 计算方法 ("iqr", "zscore", "modified_zscore")
            sensitivity: 敏感度参数，值越小越敏感

        Returns:
            (lower_threshold, upper_threshold): 上下阈值
        """
        if len(historical_data) < 3:
            # 数据不足时使用默认阈值
            return (-30.0, 30.0)

        # 修复：使用更鲁棒的变化率计算方法
        changes = []
        for i in range(1, len(historical_data)):
            if historical_data[i-1] != 0:
                change = ((historical_data[i] - historical_data[i-1]) / historical_data[i-1]) * 100
                changes.append(change)

        if len(changes) < 2:
            return (-30.0, 30.0)

        if method == "iqr":
            # 四分位距方法 - 修复异常值污染问题
            q1 = np.percentile(changes, 25)
            q3 = np.percentile(changes, 75)
            iqr = q3 - q1

            # 修复：设置合理的阈值边界
            base_threshold = 20.0  # 基础阈值20%
            iqr_threshold = sensitivity * iqr

            # 使用较大值作为阈值，避免过于敏感
            final_threshold = max(base_threshold, iqr_threshold)
            lower_threshold = q1 - final_threshold
            upper_threshold = q3 + final_threshold

            # 限制阈值范围，避免极端情况
            lower_threshold = max(lower_threshold, -50.0)  # 最小-50%
            upper_threshold = min(upper_threshold, 50.0)   # 最大+50%

        elif method == "zscore":
            # Z-score方法
            mean_change = np.mean(changes)
            std_change = np.std(changes)

            # 修复：使用固定标准差倍数，避免阈值过大
            base_threshold = 25.0  # 基础阈值25%
            std_threshold = sensitivity * std_change
            final_threshold = max(base_threshold, std_threshold)

            lower_threshold = mean_change - final_threshold
            upper_threshold = mean_change + final_threshold

            # 限制阈值范围
            lower_threshold = max(lower_threshold, -50.0)
            upper_threshold = min(upper_threshold, 50.0)

        elif method == "modified_zscore":
            # 修正Z-score方法（对异常值更鲁棒）
            median_change = np.median(changes)
            mad = np.median(np.abs(changes - median_change))

            if mad == 0:
                return (-20.0, 20.0)  # MAD为0时的默认阈值

            # 修复：调整计算方式
            base_threshold = 20.0
            mad_threshold = sensitivity * mad / 0.6745
            final_threshold = max(base_threshold, mad_threshold)

            lower_threshold = median_change - final_threshold
            upper_threshold = median_change + final_threshold

            # 限制阈值范围
            lower_threshold = max(lower_threshold, -50.0)
            upper_threshold = min(upper_threshold, 50.0)

        else:
            # 默认固定阈值
            return (-30.0, 30.0)

        return (lower_threshold, upper_threshold)

    @staticmethod
    def detect_seasonal_anomaly(
        trend_data: List[schemas.EnergyTrendItem],
        seasonal_window: int = 3
    ) -> bool:
        """
        检测季节性异常（考虑周期性模式）

        Args:
            trend_data: 趋势数据
            seasonal_window: 季节窗口（月数）

        Returns:
            bool: 是否存在季节性异常
        """
        if len(trend_data) < seasonal_window * 2:
            return False

        # 当前值
        current_usage = trend_data[-1].usage
        current_month = trend_data[-1].bill_date.month

        # 获取相同季节的历史数据
        seasonal_data = []
        for item in trend_data[:-1]:
            if abs(item.bill_date.month - current_month) <= 1:  # 相邻月份
                seasonal_data.append(item.usage)

        if len(seasonal_data) < 2:
            return False

        # 计算季节性基准
        seasonal_mean = np.mean(seasonal_data)
        seasonal_std = np.std(seasonal_data)

        # 检查是否偏离季节性模式
        if seasonal_std == 0:
            return False

        z_score = abs(current_usage - seasonal_mean) / seasonal_std
        return z_score > 2.0  # 2倍标准差外认为异常

    @staticmethod
    def calculate_trend_anomaly(
        trend_data: List[schemas.EnergyTrendItem],
        min_window: int = 6
    ) -> Dict[str, any]:
        """
        基于趋势变化检测异常

        Args:
            trend_data: 趋势数据
            min_window: 最小窗口大小

        Returns:
            Dict: 异常检测结果
        """
        if len(trend_data) < min_window:
            return {
                "is_trend_abnormal": False,
                "trend_direction": "stable",
                "trend_strength": 0,
                "confidence": 0
            }

        # 提取用量数据
        usages = [item.usage for item in trend_data]

        # 计算趋势强度（线性回归斜率）
        x = np.arange(len(usages))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, usages)

        # 趋势方向判断
        if abs(slope) < std_err * 2:
            trend_direction = "stable"
            trend_strength = 0
        elif slope > 0:
            trend_direction = "increasing"
            trend_strength = slope / np.mean(usages) * 100  # 相对强度（百分比）
        else:
            trend_direction = "decreasing"
            trend_strength = abs(slope) / np.mean(usages) * 100

        # 判断趋势是否异常
        is_trend_abnormal = (
            abs(r_value) > 0.7 and  # 强相关性
            abs(trend_strength) > 15 and  # 趋势强度超过15%
            p_value < 0.05  # 统计显著性
        )

        return {
            "is_trend_abnormal": is_trend_abnormal,
            "trend_direction": trend_direction,
            "trend_strength": abs(trend_strength),
            "confidence": abs(r_value)
        }

    @staticmethod
    def comprehensive_anomaly_detection(
        trend_data: List[schemas.EnergyTrendItem]
    ) -> schemas.AnomalyDetectionResult:
        """
        综合异常检测（结合多种方法）

        Args:
            trend_data: 能耗趋势数据

        Returns:
            AnomalyDetectionResult: 综合异常检测结果
        """
        if len(trend_data) < 2:
            return schemas.AnomalyDetectionResult(
                is_abnormal=False,
                anomaly_type=None,
                severity="low",
                confidence=0,
                detection_methods=[],
                recommendations=[]
            )

        # 1. 传统环比异常检测
        current_usage = trend_data[-1].usage
        previous_usage = trend_data[-2].usage if len(trend_data) >= 2 else None

        traditional_abnormal = False
        traditional_rate = 0
        if previous_usage and previous_usage != 0:
            traditional_rate = ((current_usage - previous_usage) / previous_usage) * 100
            traditional_abnormal = abs(traditional_rate) > 30

        # 2. 统计阈值异常检测
        usages = [item.usage for item in trend_data]
        lower_threshold, upper_threshold = AnomalyDetectionService.calculate_statistical_threshold(
            usages, method="iqr", sensitivity=1.5
        )

        statistical_abnormal = False
        if previous_usage and previous_usage != 0:
            current_rate = traditional_rate
            statistical_abnormal = current_rate < lower_threshold or current_rate > upper_threshold

        # 3. 季节性异常检测
        seasonal_abnormal = AnomalyDetectionService.detect_seasonal_anomaly(trend_data)

        # 4. 趋势异常检测
        trend_result = AnomalyDetectionService.calculate_trend_anomaly(trend_data)

        # 5. 综合判断
        detection_methods = []
        anomaly_scores = []

        if traditional_abnormal:
            detection_methods.append("traditional")
            anomaly_scores.append(0.6)

        if statistical_abnormal:
            detection_methods.append("statistical")
            anomaly_scores.append(0.8)

        if seasonal_abnormal:
            detection_methods.append("seasonal")
            anomaly_scores.append(0.7)

        if trend_result["is_trend_abnormal"]:
            detection_methods.append("trend")
            anomaly_scores.append(0.9)

        # 修复：改进的综合异常判定逻辑
        if len(detection_methods) == 0:
            is_abnormal = False
        elif len(detection_methods) == 1:
            # 单一方法检测到异常时，降低阈值要求
            method = detection_methods[0]
            score = anomaly_scores[0]

            # 传统检测或统计检测单独就足够
            if method in ["traditional", "statistical"] and score >= 0.6:
                is_abnormal = True
            # 季节性或趋势检测需要更高置信度
            elif method in ["seasonal", "trend"] and score >= 0.8:
                is_abnormal = True
            else:
                is_abnormal = False
        else:
            # 多种方法都检测到异常，直接判定为异常
            is_abnormal = True

        # 异常类型和严重程度
        anomaly_type = None
        severity = "low"
        confidence = 0

        if is_abnormal:
            confidence = np.mean(anomaly_scores)

            if trend_result["is_trend_abnormal"]:
                anomaly_type = "trend"
                severity = "high" if trend_result["trend_strength"] > 25 else "medium"
            elif seasonal_abnormal:
                anomaly_type = "seasonal"
                severity = "medium"
            elif statistical_abnormal:
                anomaly_type = "statistical"
                severity = "medium" if confidence > 0.7 else "low"
            else:
                anomaly_type = "traditional"
                severity = "low"

        # 生成针对性的建议
        recommendations = AnomalyDetectionService._generate_anomaly_recommendations(
            anomaly_type, severity, traditional_rate, trend_result
        )

        return schemas.AnomalyDetectionResult(
            is_abnormal=is_abnormal,
            anomaly_type=anomaly_type,
            severity=severity,
            confidence=round(confidence, 2),
            detection_methods=detection_methods,
            recommendations=recommendations,
            statistical_thresholds={
                "lower_threshold": round(lower_threshold, 2),
                "upper_threshold": round(upper_threshold, 2)
            },
            trend_analysis=trend_result
        )

    @staticmethod
    def _generate_anomaly_recommendations(
        anomaly_type: Optional[str],
        severity: str,
        rate_change: float,
        trend_result: Dict[str, any]
    ) -> List[str]:
        """根据异常类型生成针对性建议"""
        recommendations = []

        if anomaly_type == "trend":
            if trend_result["trend_direction"] == "increasing":
                recommendations.append("检测到持续增长的能耗趋势，建议检查设备效率和使用习惯")
                if severity == "high":
                    recommendations.append("能耗增长趋势明显，建议立即进行设备能效评估")
                    recommendations.append("考虑升级老旧设备或调整使用模式以控制成本")
                else:
                    recommendations.append("建议制定阶段性节能目标，逐步优化能源使用")
            else:
                recommendations.append("检测到能耗下降趋势，继续保持当前的节能措施")
                recommendations.append("可进一步优化，建立长期的节能管理机制")

        elif anomaly_type == "seasonal":
            recommendations.append("检测到季节性能耗异常，请注意季节变化对能耗的影响")
            recommendations.append("建议调整季节性设备的使用策略")
            if severity == "high":
                recommendations.append("季节性变化显著，建议制定季节性能耗管理预案")
            else:
                recommendations.append("适度调整设备使用时间和温度设置")

        elif anomaly_type == "statistical":
            if rate_change > 0:
                recommendations.append(f"能耗增长{abs(rate_change):.1f}%超出正常范围，建议检查异常高耗能设备")
                if abs(rate_change) > 50:
                    recommendations.append("能耗异常增长，建议立即检查设备故障或泄漏问题")
                else:
                    recommendations.append("建议排查高耗能设备的使用频率和效率")
            else:
                recommendations.append(f"能耗下降{abs(rate_change):.1f}%，节能效果显著")
                recommendations.append("可记录当前的节能措施，作为后续参考")

        elif anomaly_type == "traditional":
            recommendations.append("检测到能耗变化，建议关注最近的用能行为变化")
            recommendations.append("回顾近期是否有新增设备或使用习惯改变")

        # 通用建议
        if severity == "high":
            recommendations.append("异常程度较高，建议详细排查并制定改善计划")
            recommendations.append("考虑请专业人员进行能源审计，找出潜在问题")
        elif severity == "medium":
            recommendations.append("建议持续监测并采取适当的节能措施")
            recommendations.append("建立定期能耗检查习惯，及时发现问题")

        return recommendations

    @staticmethod
    def get_user_consumption_pattern(
        db: Session,
        user_id: int,
        bill_type: schemas.BillType,
        months: int = 12
    ) -> Dict[str, any]:
        """
        获取用户个人能耗模式用于个性化异常检测

        Args:
            db: 数据库会话
            user_id: 用户ID
            bill_type: 能源类型
            months: 分析的月数

        Returns:
            Dict: 用户能耗模式信息
        """
        # 获取历史数据
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=months * 30)

        bills = db.query(models.EnergyBill).filter(
            models.EnergyBill.user_id == user_id,
            models.EnergyBill.bill_type == bill_type,
            models.EnergyBill.bill_date >= start_date,
            models.EnergyBill.bill_date <= end_date
        ).order_by(models.EnergyBill.bill_date).all()

        if len(bills) < 3:
            return {
                "avg_monthly_usage": 0,
                "usage_variance": 0,
                "stability_score": 0,
                "seasonal_pattern": "unknown",
                "personal_baseline": 0
            }

        usages = [bill.usage for bill in bills]

        # 计算个人基线和变异系数
        avg_usage = np.mean(usages)
        std_usage = np.std(usages)
        cv = std_usage / avg_usage if avg_usage > 0 else 0

        # 稳定性评分（0-1，1表示非常稳定）
        stability_score = 1 - min(cv, 1)

        # 季节性模式分析
        monthly_averages = {}
        for bill in bills:
            month = bill.bill_date.month
            if month not in monthly_averages:
                monthly_averages[month] = []
            monthly_averages[month].append(bill.usage)

        # 计算各月平均值
        seasonal_avg = {month: np.mean(values) for month, values in monthly_averages.items()}

        # 判断季节性模式
        if len(seasonal_avg) >= 3:
            seasonal_values = list(seasonal_avg.values())
            seasonal_std = np.std(seasonal_values)
            seasonal_mean = np.mean(seasonal_values)
            seasonal_cv = seasonal_std / seasonal_mean if seasonal_mean > 0 else 0

            if seasonal_cv > 0.3:
                seasonal_pattern = "strong"
            elif seasonal_cv > 0.15:
                seasonal_pattern = "moderate"
            else:
                seasonal_pattern = "weak"
        else:
            seasonal_pattern = "unknown"

        return {
            "avg_monthly_usage": round(avg_usage, 2),
            "usage_variance": round(std_usage, 2),
            "stability_score": round(stability_score, 2),
            "seasonal_pattern": seasonal_pattern,
            "personal_baseline": round(avg_usage, 2),
            "monthly_averages": {k: round(v, 2) for k, v in seasonal_avg.items()}
        }


# 实例化服务
anomaly_detection_service = AnomalyDetectionService()