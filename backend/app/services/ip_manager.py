import ipaddress
import logging
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session

from backend.app.models.ip import IPPool, IPAllocation
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class IPManagerService:
    """IP地址管理服务"""
    
    @staticmethod
    def create_ip_pool(
        db: Session,
        name: str,
        network: str,
        gateway: str,
        subnet_mask: str,
        dns_servers: str,
        vlan_id: Optional[int] = None,
        notes: Optional[str] = None
    ) -> IPPool:
        """创建IP地址池"""
        try:
            # 验证网络参数
            net = ipaddress.IPv4Network(f"{network}/{subnet_mask}", strict=False)
            
            # 创建IP池
            ip_pool = IPPool(
                name=name,
                network=str(net),
                gateway=gateway,
                subnet_mask=subnet_mask,
                dns_servers=dns_servers,
                vlan_id=vlan_id,
                notes=notes
            )
            db.add(ip_pool)
            db.commit()
            db.refresh(ip_pool)
            
            # 创建该网络内的所有IP记录
            ip_list = list(net.hosts())
            
            # 排除网关
            try:
                gateway_ip = ipaddress.IPv4Address(gateway)
                if gateway_ip in ip_list:
                    ip_list.remove(gateway_ip)
            except ValueError:
                logger.warning(f"无效的网关地址: {gateway}")
            
            # 批量创建IP分配记录
            for ip in ip_list:
                ip_allocation = IPAllocation(
                    ip_address=str(ip),
                    ip_pool_id=ip_pool.id,
                    status="available"
                )
                db.add(ip_allocation)
            
            db.commit()
            return ip_pool
            
        except Exception as e:
            db.rollback()
            logger.error(f"创建IP池失败: {str(e)}")
            raise Exception(f"创建IP池失败: {str(e)}")
    
    @staticmethod
    def get_available_ip(db: Session, ip_pool_id: Optional[int] = None) -> Optional[IPAllocation]:
        """获取一个可用的IP地址"""
        query = db.query(IPAllocation).filter(IPAllocation.status == "available")
        
        if ip_pool_id:
            query = query.filter(IPAllocation.ip_pool_id == ip_pool_id)
        
        return query.first()
    
    @staticmethod
    def allocate_ip(
        db: Session, 
        ip_address: str, 
        user_id: Optional[int] = None,
        hostname: Optional[str] = None,
        mac_address: Optional[str] = None,
        notes: Optional[str] = None
    ) -> IPAllocation:
        """分配指定的IP地址"""
        ip_allocation = db.query(IPAllocation).filter(IPAllocation.ip_address == ip_address).first()
        
        if not ip_allocation:
            raise Exception(f"IP地址 {ip_address} 不存在")
        
        if ip_allocation.status != "available":
            raise Exception(f"IP地址 {ip_address} 已被分配，当前状态: {ip_allocation.status}")
        
        ip_allocation.status = "allocated"
        ip_allocation.user_id = user_id
        ip_allocation.hostname = hostname
        ip_allocation.mac_address = mac_address
        ip_allocation.notes = notes
        
        db.commit()
        db.refresh(ip_allocation)
        return ip_allocation
    
    @staticmethod
    def reserve_ip(
        db: Session, 
        ip_address: str, 
        notes: Optional[str] = None
    ) -> IPAllocation:
        """保留指定的IP地址"""
        ip_allocation = db.query(IPAllocation).filter(IPAllocation.ip_address == ip_address).first()
        
        if not ip_allocation:
            raise Exception(f"IP地址 {ip_address} 不存在")
        
        if ip_allocation.status != "available":
            raise Exception(f"IP地址 {ip_address} 已被分配或保留，当前状态: {ip_allocation.status}")
        
        ip_allocation.status = "reserved"
        ip_allocation.notes = notes
        
        db.commit()
        db.refresh(ip_allocation)
        return ip_allocation
    
    @staticmethod
    def release_ip(db: Session, ip_address: str) -> IPAllocation:
        """释放指定的IP地址"""
        ip_allocation = db.query(IPAllocation).filter(IPAllocation.ip_address == ip_address).first()
        
        if not ip_allocation:
            raise Exception(f"IP地址 {ip_address} 不存在")
        
        if ip_allocation.status == "available":
            raise Exception(f"IP地址 {ip_address} 已经是可用状态")
        
        ip_allocation.status = "available"
        ip_allocation.user_id = None
        ip_allocation.hostname = None
        ip_allocation.mac_address = None
        ip_allocation.notes = None
        
        db.commit()
        db.refresh(ip_allocation)
        return ip_allocation
    
    @staticmethod
    def get_ip_usage_statistics(db: Session, ip_pool_id: Optional[int] = None) -> Dict[str, Any]:
        """获取IP使用统计信息"""
        query = db.query(IPAllocation)
        
        if ip_pool_id:
            query = query.filter(IPAllocation.ip_pool_id == ip_pool_id)
        
        total = query.count()
        available = query.filter(IPAllocation.status == "available").count()
        allocated = query.filter(IPAllocation.status == "allocated").count()
        reserved = query.filter(IPAllocation.status == "reserved").count()
        
        return {
            "total": total,
            "available": available,
            "allocated": allocated,
            "reserved": reserved,
            "available_percentage": round((available / total) * 100, 2) if total > 0 else 0,
            "allocated_percentage": round((allocated / total) * 100, 2) if total > 0 else 0,
            "reserved_percentage": round((reserved / total) * 100, 2) if total > 0 else 0
        }
    
    @staticmethod
    def get_ip_pools(db: Session, skip: int = 0, limit: int = 100) -> List[IPPool]:
        """获取IP池列表"""
        return db.query(IPPool).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_ip_allocations(
        db: Session, 
        ip_pool_id: Optional[int] = None,
        status: Optional[str] = None,
        user_id: Optional[int] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[IPAllocation]:
        """获取IP分配列表"""
        query = db.query(IPAllocation)
        
        if ip_pool_id:
            query = query.filter(IPAllocation.ip_pool_id == ip_pool_id)
        
        if status:
            query = query.filter(IPAllocation.status == status)
        
        if user_id:
            query = query.filter(IPAllocation.user_id == user_id)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_ip_pool_by_id(db: Session, ip_pool_id: int) -> Optional[IPPool]:
        """通过ID获取IP池"""
        return db.query(IPPool).filter(IPPool.id == ip_pool_id).first()
    
    @staticmethod
    def get_ip_allocation_by_ip(db: Session, ip_address: str) -> Optional[IPAllocation]:
        """通过IP地址获取分配记录"""
        return db.query(IPAllocation).filter(IPAllocation.ip_address == ip_address).first() 