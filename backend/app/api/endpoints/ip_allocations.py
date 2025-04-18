from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user, validate_admin_role, validate_operator_role
from backend.app.services.ip_manager import IPManagerService
from backend.app.api.schemas.ip import (
    IPAllocation, IPAllocationCreate, IPAllocationUpdate,
    IPReservationCreate
)
from backend.app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[IPAllocation])
def read_ip_allocations(
    db: Session = Depends(get_db),
    status: Optional[str] = None,
    ip_pool_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(validate_operator_role)
) -> Any:
    """
    获取IP分配列表（需要操作员权限）
    """
    ip_allocations = IPManagerService.get_ip_allocations(
        db, ip_pool_id=ip_pool_id, status=status, skip=skip, limit=limit
    )
    return ip_allocations

@router.post("/allocate", response_model=IPAllocation)
def allocate_ip(
    *,
    db: Session = Depends(get_db),
    allocation_in: IPAllocationCreate,
    current_user: User = Depends(validate_operator_role)
) -> Any:
    """
    分配指定IP地址（需要操作员权限）
    """
    try:
        ip_allocation = IPManagerService.allocate_ip(
            db,
            ip_address=allocation_in.ip_address,
            user_id=allocation_in.user_id,
            hostname=allocation_in.hostname,
            mac_address=allocation_in.mac_address,
            notes=allocation_in.notes
        )
        return ip_allocation
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/reserve", response_model=IPAllocation)
def reserve_ip(
    *,
    db: Session = Depends(get_db),
    reservation_in: IPReservationCreate,
    current_user: User = Depends(validate_operator_role)
) -> Any:
    """
    保留指定IP地址（需要操作员权限）
    """
    try:
        ip_allocation = IPManagerService.reserve_ip(
            db,
            ip_address=reservation_in.ip_address,
            notes=reservation_in.notes
        )
        return ip_allocation
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/release/{ip_address}", response_model=IPAllocation)
def release_ip(
    ip_address: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(validate_operator_role)
) -> Any:
    """
    释放指定IP地址（需要操作员权限）
    """
    try:
        ip_allocation = IPManagerService.release_ip(db, ip_address=ip_address)
        return ip_allocation
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{ip_address}", response_model=IPAllocation)
def read_ip_allocation(
    ip_address: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    根据IP地址获取分配信息
    """
    ip_allocation = IPManagerService.get_ip_allocation_by_ip(db, ip_address=ip_address)
    if not ip_allocation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"IP地址 {ip_address} 不存在"
        )
    
    # 普通用户只能查看自己的IP
    if current_user.role not in ["admin", "operator"] and not current_user.is_superuser:
        if ip_allocation.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限查看此IP分配信息"
            )
    
    return ip_allocation

@router.put("/{ip_address}", response_model=IPAllocation)
def update_ip_allocation(
    *,
    db: Session = Depends(get_db),
    ip_address: str,
    update_in: IPAllocationUpdate,
    current_user: User = Depends(validate_operator_role)
) -> Any:
    """
    更新IP分配信息（需要操作员权限）
    """
    ip_allocation = IPManagerService.get_ip_allocation_by_ip(db, ip_address=ip_address)
    if not ip_allocation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"IP地址 {ip_address} 不存在"
        )
    
    # 更新字段
    if update_in.hostname is not None:
        ip_allocation.hostname = update_in.hostname
    if update_in.mac_address is not None:
        ip_allocation.mac_address = update_in.mac_address
    if update_in.notes is not None:
        ip_allocation.notes = update_in.notes
    
    db.commit()
    db.refresh(ip_allocation)
    return ip_allocation 