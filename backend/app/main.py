from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from .api import users, family, bills, devices, analysis, suggestion
from .database import engine, Base

# 创建数据库表
Base.metadata.create_all(bind=engine)

load_dotenv()

app = FastAPI(
    title="家庭能耗体检与节能建议系统",
    version="2.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:0921"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(users.router, prefix="/api/users", tags=["用户"])
app.include_router(family.router, prefix="/api/family", tags=["家庭信息"])
app.include_router(bills.router, prefix="/api/bills", tags=["能耗账单"])
app.include_router(devices.router, prefix="/api/devices", tags=["设备"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["能耗分析"])
app.include_router(suggestion.router, prefix="/api/suggestion", tags=["节能建议"])

@app.get("/")
async def root():
    return {"message": "家庭能耗体检与节能建议系统 API 2.0"}