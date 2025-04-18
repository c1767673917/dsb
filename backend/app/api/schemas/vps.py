from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, validator, Field
from .ip import IPAllocation

# VPS服务器共享属性
class VPSServerBase(BaseModel):
    name: str
    node_name: str
    cpu_cores: int = Field(..., gt=0)
    memory: int = Field(..., gt=0)  # MB
    disk_size: int = Field(..., gt=0)  # GB
    os_type: str
    os_template: str
    bandwidth: int = 1000  # Mbps
    notes: Optional[str] = None
    
    @validator('os_type')
    def validate_os_type(cls, v):
        allowed_types = ["linux", "windows"]
        if v not in allowed_types:
            raise ValueError(f"操作系统类型必须是以下之一: {', '.join(allowed_types)}")
        return v

# 创建VPS请求
class VPSServerCreate(VPSServerBase):
    ip_allocation_id: Optional[int] = None
    ip_pool_id: Optional[int] = None
    config: Optional[Dict[str, Any]] = None

# 更新VPS请求
class VPSServerUpdate(BaseModel):
    name: Optional[str] = None
    cpu_cores: Optional[int] = Field(None, gt=0)
    memory: Optional[int] = Field(None, gt=0)  # MB
    disk_size: Optional[int] = Field(None, gt=0)  # GB
    bandwidth: Optional[int] = None  # Mbps
    notes: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

# VPS响应
class VPSServer(VPSServerBase):
    id: int
    vmid: int
    user_id: int
    status: str
    ip_allocation_id: int
    ip_allocation: Optional[IPAllocation] = None
    config: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    last_backup_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

# VPS服务器简略信息
class VPSServerBrief(BaseModel):
    id: int
    name: str
    vmid: int
    node_name: str
    status: str
    os_type: str
    os_template: str
    ip_address: Optional[str] = None
    
    class Config:
        orm_mode = True

# VPS备份共享属性
class VPSBackupBase(BaseModel):
    vps_id: int
    backup_id: str
    file_name: str
    file_size: float  # MB
    notes: Optional[str] = None
    is_auto: bool = True

# 创建备份请求
class VPSBackupCreate(BaseModel):
    storage: str = "local"
    notes: Optional[str] = None
    is_auto: bool = False

# VPS备份响应
class VPSBackup(VPSBackupBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

# VPS状态更新响应
class VPSStatusUpdate(BaseModel):
    id: int
    name: str
    status: str 