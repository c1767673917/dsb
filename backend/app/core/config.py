import os
from typing import Optional, Dict, Any, List
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Proxmox VPS 管理系统"
    API_V1_STR: str = "/api/v1"
    
    # 数据库配置
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "password")
    DB_NAME: str = os.getenv("DB_NAME", "pve_manager")
    DATABASE_URL: str = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # Proxmox配置
    PVE_HOST: str = os.getenv("PVE_HOST", "proxmox.example.com")
    PVE_USER: str = os.getenv("PVE_USER", "root@pam")
    PVE_PASSWORD: str = os.getenv("PVE_PASSWORD", "")
    PVE_TOKEN_NAME: Optional[str] = os.getenv("PVE_TOKEN_NAME")
    PVE_TOKEN_VALUE: Optional[str] = os.getenv("PVE_TOKEN_VALUE")
    
    # 安全配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_secret_key_here")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # CORS设置
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    CORS_ORIGINS: List[str] = [FRONTEND_URL]
    
    # 网络配置
    IP_RANGE_START: str = os.getenv("IP_RANGE_START", "192.168.1.1")
    IP_RANGE_END: str = os.getenv("IP_RANGE_END", "192.168.1.254")
    SUBNET_MASK: str = os.getenv("SUBNET_MASK", "255.255.255.0")
    GATEWAY: str = os.getenv("GATEWAY", "192.168.1.1")
    DNS_SERVERS: str = os.getenv("DNS_SERVERS", "8.8.8.8,8.8.4.4")
    
    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR: str = os.getenv("LOG_DIR", "./logs")
    
    # 系统用户角色
    ROLES = {
        "admin": "管理员",
        "operator": "操作员",
        "user": "普通用户",
        "guest": "访客"
    }
    
    # 操作系统模板配置
    OS_TEMPLATES = {
        "linux": {
            "ubuntu": ["20.04", "22.04"], 
            "debian": ["10", "11"],
            "centos": ["7", "8", "9"],
            "rocky": ["8", "9"],
            "alma": ["8", "9"],
        },
        "windows": {
            "windows": ["2019", "2022"]
        }
    }
    
    # VPS默认配置
    DEFAULT_VPS_CONFIG = {
        "cpu": 1,
        "memory": 1024,
        "disk": 10,
        "bandwidth": 1000,
    }
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings() 