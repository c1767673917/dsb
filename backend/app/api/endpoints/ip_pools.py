from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import validate_admin_role, validate_operator_role
from backend.app.services.ip_manager import IPManagerService
from backend.app.api.schemas.ip import (
    IPPool, IPPoolCreate, IPPoolUpdate,
    IPAllocation, IPAllocationCreate, IPAllocationUpdate,
    IPReservationCreate, IPUsageStats
)

router = APIRouter()

@router.get("/", response_model=List[IPPool])
def read_ip_pools(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(validate_operator_role)
) -> Any:
    """
    获取IP池列表（需要操作员权限）
    """
    ip_pools = IPManagerService.get_ip_pools(db, skip=skip, limit=limit)
    return ip_pools

@router.post("/", response_model=IPPool)
def create_ip_pool(
    *,
    db: Session = Depends(get_db),
    ip_pool_in: IPPoolCreate,
    current_user = Depends(validate_admin_role)
) -> Any:
    """
    创建新IP池（需要管理员权限）
    """
    ip_pool = IPManagerService.create_ip_pool(
        db,
        name=ip_pool_in.name,
        network=ip_pool_in.network,
        gateway=ip_pool_in.gateway,
        subnet_mask=ip_pool_in.subnet_mask,
        dns_servers=ip_pool_in.dns_servers,
        vlan_id=ip_pool_in.vlan_id,
        notes=ip_pool_in.notes
    )
    return ip_pool

@router.get("/{ip_pool_id}", response_model=IPPool)
def read_ip_pool(
    ip_pool_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(validate_operator_role)
) -> Any:
    """
    根据ID获取IP池信息（需要操作员权限）
    """
    ip_pool = IPManagerService.get_ip_pool_by_id(db, ip_pool_id=ip_pool_id)
    if not ip_pool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="IP池不存在"
        )
    return ip_pool

@router.put("/{ip_pool_id}", response_model=IPPool)
def update_ip_pool(
    *,
    db: Session = Depends(get_db),
    ip_pool_id: int,
    ip_pool_in: IPPoolUpdate,
    current_user = Depends(validate_admin_role)
) -> Any:
    """
    更新IP池信息（需要管理员权限）
    """
    ip_pool = IPManagerService.get_ip_pool_by_id(db, ip_pool_id=ip_pool_id)
    if not ip_pool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="IP池不存在"
        )
    
    # 更新字段
    if ip_pool_in.name is not None:
        ip_pool.name = ip_pool_in.name
    if ip_pool_in.gateway is not None:
        ip_pool.gateway = ip_pool_in.gateway
    if ip_pool_in.dns_servers is not None:
        ip_pool.dns_servers = ip_pool_in.dns_servers
    if ip_pool_in.vlan_id is not None:
        ip_pool.vlan_id = ip_pool_in.vlan_id
    if ip_pool_in.notes is not None:
        ip_pool.notes = ip_pool_in.notes
    if ip_pool_in.is_active is not None:
        ip_pool.is_active = ip_pool_in.is_active
    
    db.commit()
    db.refresh(ip_pool)
    return ip_pool

@router.get("/{ip_pool_id}/allocations", response_model=List[IPAllocation])
def read_ip_allocations(
    ip_pool_id: int,
    db: Session = Depends(get_db),
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(validate_operator_role)
) -> Any:
    """
    获取IP池内的IP分配列表（需要操作员权限）
    """
    ip_pool = IPManagerService.get_ip_pool_by_id(db, ip_pool_id=ip_pool_id)
    if not ip_pool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="IP池不存在"
        )
    
    ip_allocations = IPManagerService.get_ip_allocations(
        db, ip_pool_id=ip_pool_id, status=status, skip=skip, limit=limit
    )
    return ip_allocations

@router.get("/{ip_pool_id}/stats", response_model=IPUsageStats)
def get_ip_usage_stats(
    ip_pool_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(validate_operator_role)
) -> Any:
    """
    获取IP池的使用统计（需要操作员权限）
    """
    ip_pool = IPManagerService.get_ip_pool_by_id(db, ip_pool_id=ip_pool_id)
    if not ip_pool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="IP池不存在"
        )
    
    stats = IPManagerService.get_ip_usage_statistics(db, ip_pool_id=ip_pool_id)
    return stats 