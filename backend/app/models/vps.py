from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship

from backend.app.models.base import Base

class VPSServer(Base):
    __tablename__ = "vps_servers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    vmid = Column(Integer, unique=True, index=True)  # Proxmox VM ID
    node_name = Column(String)  # Proxmox 节点名称
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String)  # running, stopped, suspended
    
    # 资源配置
    cpu_cores = Column(Integer)
    memory = Column(Integer)  # MB
    disk_size = Column(Integer)  # GB
    bandwidth = Column(Integer)  # Mbps
    
    # 系统信息
    os_type = Column(String)  # linux, windows
    os_template = Column(String)  # ubuntu-20.04, debian-11, windows-2022 等
    
    # IP信息
    ip_allocation_id = Column(Integer, ForeignKey("ip_allocations.id"))
    
    # 其他信息
    notes = Column(Text, nullable=True)
    config = Column(JSON, nullable=True)  # 其他配置信息
    
    # 时间信息
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_backup_at = Column(DateTime, nullable=True)
    
    # 关系
    owner = relationship("User", back_populates="vps_servers")
    ip_allocation = relationship("IPAllocation", back_populates="vps_server")
    backups = relationship("VPSBackup", back_populates="vps_server")
    
    def __repr__(self):
        return f"<VPSServer {self.name} (VM:{self.vmid})>"

class VPSBackup(Base):
    __tablename__ = "vps_backups"
    
    id = Column(Integer, primary_key=True, index=True)
    vps_id = Column(Integer, ForeignKey("vps_servers.id"))
    backup_id = Column(String, unique=True)  # Proxmox 备份ID
    file_name = Column(String)
    file_size = Column(Float)  # MB
    notes = Column(Text, nullable=True)
    is_auto = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    vps_server = relationship("VPSServer", back_populates="backups")
    
    def __repr__(self):
        return f"<VPSBackup {self.backup_id}>" 