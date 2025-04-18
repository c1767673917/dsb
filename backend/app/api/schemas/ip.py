from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, validator
import ipaddress

# IP池共享属性
class IPPoolBase(BaseModel):
    name: str
    network: str
    gateway: str
    subnet_mask: str
    dns_servers: str
    vlan_id: Optional[int] = None
    notes: Optional[str] = None
    
    @validator('network')
    def validate_network(cls, v):
        try:
            ipaddress.IPv4Network(v, strict=False)
            return v
        except:
            raise ValueError("无效的网络地址")
    
    @validator('gateway')
    def validate_gateway(cls, v):
        try:
            ipaddress.IPv4Address(v)
            return v
        except:
            raise ValueError("无效的网关地址")
    
    @validator('subnet_mask')
    def validate_subnet_mask(cls, v):
        try:
            # 验证是否为有效的子网掩码
            octets = v.split('.')
            if len(octets) != 4:
                raise ValueError()
            
            binary = ''.join([bin(int(octet))[2:].zfill(8) for octet in octets])
            if '01' in binary:  # 子网掩码中不应该有0后面跟着1
                raise ValueError()
            
            return v
        except:
            raise ValueError("无效的子网掩码")
    
    @validator('dns_servers')
    def validate_dns_servers(cls, v):
        dns_list = v.split(',')
        for dns in dns_list:
            try:
                ipaddress.IPv4Address(dns.strip())
            except:
                raise ValueError(f"无效的DNS服务器地址: {dns}")
        return v

# 创建IP池请求
class IPPoolCreate(IPPoolBase):
    is_active: bool = True

# 更新IP池请求
class IPPoolUpdate(BaseModel):
    name: Optional[str] = None
    gateway: Optional[str] = None
    dns_servers: Optional[str] = None
    vlan_id: Optional[int] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    
    @validator('gateway')
    def validate_gateway(cls, v):
        if v is not None:
            try:
                ipaddress.IPv4Address(v)
                return v
            except:
                raise ValueError("无效的网关地址")
        return v
    
    @validator('dns_servers')
    def validate_dns_servers(cls, v):
        if v is not None:
            dns_list = v.split(',')
            for dns in dns_list:
                try:
                    ipaddress.IPv4Address(dns.strip())
                except:
                    raise ValueError(f"无效的DNS服务器地址: {dns}")
        return v

# IP池响应
class IPPool(IPPoolBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# IP分配共享属性
class IPAllocationBase(BaseModel):
    ip_address: str
    ip_pool_id: int
    status: str = "available"  # available, allocated, reserved
    hostname: Optional[str] = None
    mac_address: Optional[str] = None
    notes: Optional[str] = None
    
    @validator('ip_address')
    def validate_ip_address(cls, v):
        try:
            ipaddress.IPv4Address(v)
            return v
        except:
            raise ValueError("无效的IP地址")
    
    @validator('status')
    def validate_status(cls, v):
        allowed_status = ["available", "allocated", "reserved"]
        if v not in allowed_status:
            raise ValueError(f"状态必须是以下之一: {', '.join(allowed_status)}")
        return v
    
    @validator('mac_address')
    def validate_mac_address(cls, v):
        if v is not None:
            # 简单的MAC地址格式验证
            import re
            if not re.match(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', v):
                raise ValueError("无效的MAC地址格式，应为xx:xx:xx:xx:xx:xx或xx-xx-xx-xx-xx-xx格式")
        return v

# 分配IP请求
class IPAllocationCreate(BaseModel):
    ip_address: str
    user_id: Optional[int] = None
    hostname: Optional[str] = None
    mac_address: Optional[str] = None
    notes: Optional[str] = None
    
    @validator('ip_address')
    def validate_ip_address(cls, v):
        try:
            ipaddress.IPv4Address(v)
            return v
        except:
            raise ValueError("无效的IP地址")

# 保留IP请求
class IPReservationCreate(BaseModel):
    ip_address: str
    notes: Optional[str] = None
    
    @validator('ip_address')
    def validate_ip_address(cls, v):
        try:
            ipaddress.IPv4Address(v)
            return v
        except:
            raise ValueError("无效的IP地址")

# 更新IP分配请求
class IPAllocationUpdate(BaseModel):
    hostname: Optional[str] = None
    mac_address: Optional[str] = None
    notes: Optional[str] = None
    
    @validator('mac_address')
    def validate_mac_address(cls, v):
        if v is not None:
            import re
            if not re.match(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', v):
                raise ValueError("无效的MAC地址格式，应为xx:xx:xx:xx:xx:xx或xx-xx-xx-xx-xx-xx格式")
        return v

# IP分配响应
class IPAllocation(IPAllocationBase):
    id: int
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# IP使用统计响应
class IPUsageStats(BaseModel):
    total: int
    available: int
    allocated: int
    reserved: int
    available_percentage: float
    allocated_percentage: float
    reserved_percentage: float 