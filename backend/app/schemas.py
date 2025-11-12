from pydantic import BaseModel, EmailStr
from typing import Optional, List
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

# 用户模型 - 创建
class UserCreate(UserBase):
    password: str

# 用户模型 - 更新
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None

# 用户模型 - 响应
class UserResponse(UserBase):
    id: int
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
    previous_usage: Optional[float] = None
    yoy_rate: Optional[float] = None  # 同比增长率(%)
    mom_rate: Optional[float] = None  # 环比增长率(%)
    is_abnormal: bool  # 是否异常(增长率超过30%)

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

# 登录请求
class LoginRequest(BaseModel):
    username: str
    password: str

# 令牌响应
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse