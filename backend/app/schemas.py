from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from enum import Enum

# 账单类型枚举
class BillType(str, Enum):
    electricity = "electricity"
    gas = "gas"
    water = "water"

# 设备类型枚举
class DeviceType(str, Enum):
    electricity = "electricity"
    gas = "gas"
    water = "water"

# 新增分析时间段枚举
class AnalysisPeriod(str, Enum):
    monthly = "monthly"    # 月度
    quarter = "quarter"    # 季度
    annual = "annual"      # 年度
    custom = "custom"      # 自定义

# 用户模型 - 基础
class UserBase(BaseModel):
    username: str
    email: EmailStr
    phone: Optional[str] = None

# 用户模型 - 创建
class UserCreate(UserBase):
    password: str

# 用户模型 - 更新
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None

# 用户模型 - 响应
class UserResponse(UserBase):
    id: int
    avatar: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 家庭信息模型 - 基础
class FamilyInfoBase(BaseModel):
    family_size: Optional[int] = 1
    house_area: Optional[float] = None
    location: Optional[str] = None
    building_age: Optional[int] = None

# 家庭信息 - 创建
class FamilyInfoCreate(FamilyInfoBase):
    pass

# 家庭信息 - 修改
class FamilyInfoUpdate(BaseModel):
    family_size: Optional[int] = None
    house_area: Optional[float] = None
    location: Optional[str] = None
    building_age: Optional[int] = None

# 家庭信息 - 响应
class FamilyInfoResponse(FamilyInfoBase):
    id: int
    user_id: int


# 设备模型 - 基础
class DeviceBase(BaseModel):
    device_type: DeviceType
    name: str
    power_rating: Optional[float] = None
    usage_hours_per_day: Optional[float] = None
    efficiency_rating: Optional[str] = None
    purchase_year: Optional[int] = None
    notes: Optional[str] = None

# 设备模型 - 创建
class DeviceCreate(DeviceBase):
    pass

# 设备模型 - 更新
class DeviceUpdate(BaseModel):
    device_type: Optional[DeviceType] = None
    name: Optional[str] = None
    power_rating: Optional[float] = None
    usage_hours_per_day: Optional[float] = None
    efficiency_rating: Optional[str] = None
    purchase_year: Optional[int] = None
    notes: Optional[str] = None

# 设备模型 - 响应
class DeviceResponse(DeviceBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 设备使用记录模型 - 基础
class DeviceUsageBase(BaseModel):
    device_id: int
    usage_date: date
    usage_hours: float
    notes: Optional[str] = None

# 设备使用记录模型 - 创建
class DeviceUsageCreate(DeviceUsageBase):
    pass

# 设备使用记录模型 - 更新
class DeviceUsageUpdate(BaseModel):
    usage_date: Optional[date] = None
    usage_hours: Optional[float] = None
    notes: Optional[str] = None

# 设备使用记录模型 - 响应
class DeviceUsageResponse(DeviceUsageBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 能耗账单模型 - 基础
class EnergyBillBase(BaseModel):
    bill_type: BillType
    bill_date: date
    amount: float
    usage: float
    unit_price: float
    notes: Optional[str] = None

# 能耗账单模型 - 创建
class EnergyBillCreate(EnergyBillBase):
    pass

# 能耗账单模型 - 更新
class EnergyBillUpdate(BaseModel):
    bill_type: Optional[BillType] = None
    bill_date: Optional[date] = None
    amount: Optional[float] = None
    usage: Optional[float] = None
    unit_price: Optional[float] = None
    notes: Optional[str] = None

# 能耗账单模型 - 响应
class EnergyBillResponse(EnergyBillBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

# 分页账单模型 - 响应
class PaginatedBillResponse(BaseModel):
    """分页账单响应模型"""
    items: List[EnergyBillResponse]  # 当前页的账单列表
    total: int  # 总记录数
    page: int # 当前页码
    page_size: int  # 每页数量
    total_pages: int  # 总页数

    class Config:
        from_attributes = True

class PaginatedDeviceResponse(BaseModel):
    """分页设备响应模型"""
    items: List[DeviceResponse]  # 当前页的设备列表
    total: int  # 总记录数
    page: int  # 当前页码
    page_size: int  # 每页数量
    total_pages: int  # 总页数

    class Config:
        from_attributes = True

class PaginatedDeviceUsageResponse(BaseModel):
    """分页设备使用记录模型"""
    items: List[DeviceUsageResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

# 节能建议模型 - 基础
class EnergySavingSuggestionBase(BaseModel):
    bill_type: BillType
    suggestion_title: str
    suggestion_text: str
    suggestion_date: date
    impact_rating: Optional[int] = None
    is_implemented: Optional[bool] = False

# 节能建议模型 - 创建
class EnergySavingSuggestionCreate(EnergySavingSuggestionBase):
    pass

# 节能建议模型 - 更新
class EnergySavingSuggestionUpdate(BaseModel):
    bill_type: Optional[BillType] = None
    suggestion_title: Optional[str] = None
    suggestion_text: Optional[str] = None
    suggestion_date: Optional[date] = None
    impact_rating: Optional[int] = None
    is_implemented: Optional[bool] = None

# 节能建议模型 - 响应
class EnergySavingSuggestionResponse(EnergySavingSuggestionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

# 分析结构响应
class EnergyTrendItem(BaseModel):
    bill_type: BillType
    bill_date: date
    usage: float
    amount: float
    year: Optional[str] = None
    month: Optional[str] = None

class EnergyComparison(BaseModel):
    current_usage: float
    current_amount: float
    current_unit_price: float
    previous_usage: Optional[float] = None
    previous_amount: Optional[float] = None
    previous_unit_price: Optional[float] = None
    usage_yoy_rate: Optional[float] = None  # 用电量同比增长率(%)
    usage_mom_rate: Optional[float] = None  # 用电量环比增长率(%)
    amount_yoy_rate: Optional[float] = None # 能耗费用同比增长率(%)
    amount_mom_rate: Optional[float] = None # 能耗费用环比增长率(%)
    unit_price_yoy_rate: Optional[float] = None # 能耗单价同比增长率(%)
    unit_price_mom_rate: Optional[float] = None # 能耗单价环比增长率(%)
    is_abnormal: bool  # 是否异常(使用智能异常检测算法)

class AnomalyDetectionResult(BaseModel):
    """异常检测结果模型"""
    is_abnormal: bool  # 是否异常
    anomaly_type: Optional[str] = None  # 异常类型: trend, seasonal, statistical, traditional
    severity: str  # 严重程度: low, medium, high
    confidence: float  # 置信度 0-1
    detection_methods: List[str] = []  # 检测方法列表
    recommendations: List[str] = []  # 异常处理建议
    statistical_thresholds: Optional[Dict[str, float]] = None  # 统计阈值
    trend_analysis: Optional[Dict[str, Any]] = None  # 趋势分析结果

class AnomalyMonthResult(BaseModel):
    """异常月份检测结果"""
    year: int  # 年份
    month: int  # 月份
    usage: float  # 当月用量
    amount: float  # 当月费用
    avg_usage: float  # 历史平均用量
    deviation: float  # 偏差百分比
    anomaly_type: Optional[str] = None  # 异常类型
    severity: str  # 严重程度: low, medium, high
    confidence: float  # 置信度
    recommendations: List[str] = []  # 处理建议

class AIAnomalyDetectionResult(BaseModel):
    """AI异常检测结果模型"""
    is_abnormal: bool  # AI判断是否异常
    abnormal_type: Optional[str] = None  # AI判断的异常类型
    severity: str  # 严重程度: low, medium, high
    confidence: float  # AI判断的置信度 0-1
    reasoning: str  # AI的推理过程
    possible_explanations: List[str] = []  # AI提供的可能解释
    recommendation: str  # AI给出的建议
    ai_model_used: str  # 使用的AI模型
    api_timestamp: datetime  # API调用时间

class DeviceEnergyConsumption(BaseModel):
    device_id: int
    device_name: str
    consumption: float  # 能耗占比(%)
    monthly_usage: float  # 月能耗(度/立方米)

class AnalysisResult(BaseModel):
    trend_data: List[EnergyTrendItem]
    comparison: EnergyComparison
    device_consumption: List[DeviceEnergyConsumption]
    suggestions: List[EnergySavingSuggestionResponse]

class AIEnergyAnalysis(BaseModel):
    """AI能源分析结果"""
    overall_assessment: str  # 整体评估
    key_insights: List[str]  # 关键发现
    risk_level: str  # 风险等级: low/medium/high
    optimization_potential: str  # 优化潜力: low/medium/high
    seasonal_analysis: str  # 季节性分析
    suggestions: List[EnergySavingSuggestionResponse]  # AI生成的建议
    confidence_score: float  # 置信度 0-1

class EnergyTypeAnalysis(BaseModel):
    """单个能源类型的分析结果"""
    bill_type: BillType  # 能源类型
    trend_data: List[EnergyTrendItem]  # 趋势数据
    comparison: EnergyComparison  # 同比环比分析
    device_consumption: List[DeviceEnergyConsumption]  # 设备能耗
    anomaly_months: List[AnomalyMonthResult]  # 异常月份
    ai_analysis: AIEnergyAnalysis  # AI分析结果
    suggestions: List[EnergySavingSuggestionResponse]  # 节能建议

class ComprehensiveAnalysisResult(BaseModel):
    """综合分析结果（支持多能源类型）"""
    energy_analyses: List[EnergyTypeAnalysis]  # 各能源类型分析
    overall_summary: str  # 整体摘要
    suggestions: List[EnergySavingSuggestionResponse]  # 综合建议
    analysis_date: datetime  # 分析时间
    analyzed_energy_types: List[str]  # 已分析的能源类型

class LatestCostItem(BaseModel):
    bill_type: BillType
    amount: float  # 花费金额
    percentage: float  # 占总花费的百分比

class LatestCostResponse(BaseModel):
    total_amount: float  # 总花费
    items: list[LatestCostItem]  # 总类型花费详情
    month: str  # 月份 (格式: YYYY-MM)

    class Config:
        from_attributes = True

# 登录请求
class LoginRequest(BaseModel):
    username: str
    password: str

# 令牌响应
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse