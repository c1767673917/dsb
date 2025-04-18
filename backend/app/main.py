import logging
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend.app.api.api import api_router
from backend.app.core.config import settings
from backend.app.core.database import engine, get_db
from backend.app.models.base import Base
from backend.app.services.user import UserService

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(filename="app.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(api_router, prefix=settings.API_V1_STR)

# 初始化超级管理员账户
@app.on_event("startup")
async def create_superuser():
    """初始化应用时创建超级管理员账户（如果不存在）"""
    logger.info("检查超级管理员账户...")
    db = next(get_db())
    try:
        # 检查admin用户是否存在
        admin = UserService.get_user_by_username(db, username="admin")
        if not admin:
            # 创建管理员账户
            UserService.create_user(
                db=db,
                username="admin",
                email="admin@example.com",
                password="admin123",  # 初始密码
                first_name="管理员",
                last_name="",
                role="admin",
                is_active=True,
                is_superuser=True
            )
            logger.info("已创建超级管理员账户")
        else:
            logger.info("超级管理员账户已存在")
    except Exception as e:
        logger.error(f"创建超级管理员账户失败: {str(e)}")

# 健康检查路由
@app.get("/health")
def health_check():
    """健康检查端点"""
    return {"status": "ok"}

@app.get("/")
def root():
    """根路由重定向到API文档"""
    return {"message": "欢迎使用PVE VPS管理系统API", "docs": "/docs"} 