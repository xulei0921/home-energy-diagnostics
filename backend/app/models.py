from sqlalchemy import Column, Integer, String, Float, Enum, Date, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

Base = declarative_base()

class BillType(str, enum.Enum):
    electricity = "electricity"
    gas = "gas"
    water = "water"

class DeviceType(str, enum.Enum):
    electricity = "electricity"
    gas = "gas"
    water = "water"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关联表
    family_info = relationship("FamilyInfo", back_populates="user", cascade="all, delete-orphan")
    energy_bills = relationship("EnergyBill", back_populates="user", cascade="all, delete-orphan")
    devices = relationship("Device", back_populates="user", cascade="all, delete-orphan")
    suggestions = relationship("EnergySavingSuggestion", back_populates="user", cascade="all, delete-orphan")

class FamilyInfo(Base):
    __tablename__ = "family_info"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    family_size = Column(Integer, default=1)
    house_area = Column(Float)
    location = Column(String(100))
    building_age = Column(Integer)

    user = relationship("User", back_populates="family_info")

class EnergyBill(Base):
    __tablename__ = "energy_bills"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    bill_type = Column(Enum(BillType), nullable=False)
    bill_date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    usage = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="energy_bills")

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    device_type = Column(Enum(DeviceType), nullable=False)
    name = Column(String(100), nullable=False)
    power_rating = Column(Float)  # 功率/流量额定值
    usage_hours_per_day = Column(Float)  # 平均每天使用小时数
    efficiency_rating = Column(String(20))  # 能效等级
    purchase_year = Column(Integer)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="devices")
    usage_records = relationship("DeviceUsage", back_populates="device", cascade="all, delete-orphan")

class DeviceUsage(Base):
    __tablename__ = "device_usage"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False)
    usage_date = Column(Date, nullable=False)
    usage_hours = Column(Float, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    device = relationship("Device", back_populates="usage_records")

class EnergySavingSuggestion(Base):
    __tablename__ = "energy_saving_suggestions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    bill_type = Column(Enum(BillType), nullable=False)
    suggestion_title = Column(String(255), nullable=False)
    suggestion_text = Column(Text, nullable=False)
    suggestion_date = Column(Date, nullable=False)
    impact_rating = Column(Integer, default=0)  # 影响程度评分(1-5)
    is_implemented = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="suggestions")