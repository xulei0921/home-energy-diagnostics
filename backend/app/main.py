from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from starlette.staticfiles import StaticFiles

from .api import users, family, bills, devices, analysis, suggestion
from .database import engine, Base
from pathlib import Path

# 创建数据库表
Base.metadata.create_all(bind=engine)
# 项目根目录
BASE_DIR = Path(__file__).parent.parent

load_dotenv()

app = FastAPI(
    title="家庭能耗体检与节能建议系统",
    version="2.0.0"
)

STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
# 定义图片存储目录 (绝对路径，避免相对路径混乱)
IMAGE_DIR = BASE_DIR / "static" / "images"
# 确保目录存在 (不存在则自动创建，包括多级目录)
IMAGE_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:921"],
    allow_origins=["*"],
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