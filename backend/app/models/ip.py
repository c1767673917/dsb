from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from backend.app.models.base import Base

class IPPool(Base):
    __tablename__ = "ip_pools"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    network = Column(String)  # 例如 "192.168.1.0/24"
    gateway = Column(String)
    subnet_mask = Column(String)
    dns_servers = Column(String)  # 逗号分隔的DNS服务器列表
    vlan_id = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    ip_allocations = relationship("IPAllocation", back_populates="ip_pool")
    
    def __repr__(self):
        return f"<IPPool {self.name} ({self.network})>"

class IPAllocation(Base):
    __tablename__ = "ip_allocations"
    
    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String, unique=True, index=True)
    ip_pool_id = Column(Integer, ForeignKey("ip_pools.id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String)  # available, allocated, reserved
    hostname = Column(String, nullable=True)
    mac_address = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    ip_pool = relationship("IPPool", back_populates="ip_allocations")
    user = relationship("User", back_populates="ip_allocations")
    vps_server = relationship("VPSServer", back_populates="ip_allocation", uselist=False)
    
    def __repr__(self):
        return f"<IPAllocation {self.ip_address} ({self.status})>" 