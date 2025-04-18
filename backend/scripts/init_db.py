import logging
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from sqlalchemy.orm import Session

from backend.app.core.database import engine, get_db
from backend.app.models.base import Base
from backend.app.models.user import User
from backend.app.models.ip import IPPool, IPAllocation
from backend.app.models.vps import VPSServer, VPSBackup
from backend.app.services.user import UserService
from backend.app.services.ip_manager import IPManagerService
from backend.app.core.config import settings

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def init_db():
    """初始化数据库"""
    logger.info("正在创建数据库表...")
    
    # 删除现有表格（谨慎使用）
    # Base.metadata.drop_all(bind=engine)
    
    # 创建表格
    Base.metadata.create_all(bind=engine)
    logger.info("数据库表创建完成")

def create_initial_data(db: Session):
    """创建初始数据"""
    # 创建管理员用户
    logger.info("正在创建超级管理员用户...")
    try:
        admin = UserService.get_user_by_username(db, username="admin")
        if not admin:
            admin = UserService.create_user(
                db=db,
                username="admin",
                email="admin@example.com",
                password="admin123",
                first_name="管理员",
                last_name="",
                role="admin",
                is_active=True,
                is_superuser=True
            )
            logger.info("超级管理员创建成功")
        else:
            logger.info("超级管理员已存在")
    except Exception as e:
        logger.error(f"创建超级管理员失败: {str(e)}")
    
    # 创建示例IP池
    logger.info("正在创建示例IP池...")
    try:
        ip_pool = db.query(IPPool).filter(IPPool.name == "默认网段").first()
        if not ip_pool:
            IPManagerService.create_ip_pool(
                db=db,
                name="默认网段",
                network="192.168.1.0",
                gateway="192.168.1.1",
                subnet_mask="255.255.255.0",
                dns_servers="8.8.8.8,8.8.4.4",
                notes="示例IP池"
            )
            logger.info("示例IP池创建成功")
        else:
            logger.info("示例IP池已存在")
    except Exception as e:
        logger.error(f"创建示例IP池失败: {str(e)}")
    
    logger.info("初始数据创建完成")

if __name__ == "__main__":
    # 初始化数据库
    init_db()
    
    # 创建初始数据
    db = next(get_db())
    create_initial_data(db)
    logger.info("数据库初始化完成") 