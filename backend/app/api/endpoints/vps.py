from typing import Any, List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user, validate_admin_role, validate_operator_role
from backend.app.services.vps_manager import VPSManagerService
from backend.app.api.schemas.vps import (
    VPSServer, VPSServerCreate, VPSServerUpdate, VPSServerBrief,
    VPSBackup, VPSBackupCreate, VPSStatusUpdate
)
from backend.app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[VPSServerBrief])
def read_vps_servers(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取VPS服务器列表
    """
    # 管理员和操作员可以查看所有VPS
    if current_user.role in ["admin", "operator"] or current_user.is_superuser:
        vps_servers = VPSManagerService.get_all_vps(db, skip=skip, limit=limit)
    # 普通用户只能查看自己的VPS
    else:
        vps_servers = VPSManagerService.get_vps_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    
    return vps_servers

@router.post("/", response_model=VPSServer)
def create_vps(
    *,
    db: Session = Depends(get_db),
    vps_in: VPSServerCreate,
    current_user: User = Depends(validate_operator_role)
) -> Any:
    """
    创建新VPS服务器（需要操作员权限）
    """
    try:
        # 创建VPS，使用当前操作员作为用户
        vps_server = VPSManagerService.create_vps(
            db,
            user_id=current_user.id,
            name=vps_in.name,
            node_name=vps_in.node_name,
            cpu_cores=vps_in.cpu_cores,
            memory=vps_in.memory,
            disk_size=vps_in.disk_size,
            os_type=vps_in.os_type,
            os_template=vps_in.os_template,
            ip_allocation_id=vps_in.ip_allocation_id,
            ip_pool_id=vps_in.ip_pool_id,
            bandwidth=vps_in.bandwidth,
            notes=vps_in.notes,
            config=vps_in.config
        )
        return vps_server
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{vps_id}", response_model=VPSServer)
def read_vps(
    vps_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    根据ID获取VPS服务器信息
    """
    vps_server = VPSManagerService.get_vps_by_id(db, vps_id=vps_id)
    if not vps_server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="VPS服务器不存在"
        )
    
    # 普通用户只能查看自己的VPS
    if current_user.role not in ["admin", "operator"] and not current_user.is_superuser:
        if vps_server.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限查看此VPS服务器"
            )
    
    return vps_server

@router.put("/{vps_id}", response_model=VPSServer)
def update_vps(
    *,
    db: Session = Depends(get_db),
    vps_id: int,
    vps_in: VPSServerUpdate,
    current_user: User = Depends(validate_operator_role)
) -> Any:
    """
    更新VPS服务器信息（需要操作员权限）
    """
    vps_server = VPSManagerService.get_vps_by_id(db, vps_id=vps_id)
    if not vps_server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="VPS服务器不存在"
        )
    
    # 更新字段
    if vps_in.name is not None:
        vps_server.name = vps_in.name
    if vps_in.cpu_cores is not None:
        vps_server.cpu_cores = vps_in.cpu_cores
    if vps_in.memory is not None:
        vps_server.memory = vps_in.memory
    if vps_in.disk_size is not None:
        vps_server.disk_size = vps_in.disk_size
    if vps_in.bandwidth is not None:
        vps_server.bandwidth = vps_in.bandwidth
    if vps_in.notes is not None:
        vps_server.notes = vps_in.notes
    if vps_in.config is not None:
        vps_server.config = vps_in.config
    
    db.commit()
    db.refresh(vps_server)
    return vps_server

@router.delete("/{vps_id}")
def delete_vps(
    vps_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(validate_admin_role)
) -> Dict[str, Any]:
    """
    删除VPS服务器（需要管理员权限）
    """
    vps_server = VPSManagerService.get_vps_by_id(db, vps_id=vps_id)
    if not vps_server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="VPS服务器不存在"
        )
    
    try:
        result = VPSManagerService.delete_vps(db, vps_id=vps_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{vps_id}/start", response_model=VPSStatusUpdate)
def start_vps(
    vps_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    启动VPS服务器
    """
    vps_server = VPSManagerService.get_vps_by_id(db, vps_id=vps_id)
    if not vps_server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="VPS服务器不存在"
        )
    
    # 普通用户只能操作自己的VPS
    if current_user.role not in ["admin", "operator"] and not current_user.is_superuser:
        if vps_server.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限操作此VPS服务器"
            )
    
    try:
        vps_server = VPSManagerService.start_vps(db, vps_id=vps_id)
        return {"id": vps_server.id, "name": vps_server.name, "status": vps_server.status}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{vps_id}/stop", response_model=VPSStatusUpdate)
def stop_vps(
    vps_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    关闭VPS服务器
    """
    vps_server = VPSManagerService.get_vps_by_id(db, vps_id=vps_id)
    if not vps_server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="VPS服务器不存在"
        )
    
    # 普通用户只能操作自己的VPS
    if current_user.role not in ["admin", "operator"] and not current_user.is_superuser:
        if vps_server.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限操作此VPS服务器"
            )
    
    try:
        vps_server = VPSManagerService.stop_vps(db, vps_id=vps_id)
        return {"id": vps_server.id, "name": vps_server.name, "status": vps_server.status}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{vps_id}/restart", response_model=VPSStatusUpdate)
def restart_vps(
    vps_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    重启VPS服务器
    """
    vps_server = VPSManagerService.get_vps_by_id(db, vps_id=vps_id)
    if not vps_server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="VPS服务器不存在"
        )
    
    # 普通用户只能操作自己的VPS
    if current_user.role not in ["admin", "operator"] and not current_user.is_superuser:
        if vps_server.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限操作此VPS服务器"
            )
    
    try:
        vps_server = VPSManagerService.restart_vps(db, vps_id=vps_id)
        return {"id": vps_server.id, "name": vps_server.name, "status": vps_server.status}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{vps_id}/backup", response_model=VPSBackup)
def create_vps_backup(
    *,
    db: Session = Depends(get_db),
    vps_id: int,
    backup_in: VPSBackupCreate,
    current_user: User = Depends(validate_operator_role)
) -> Any:
    """
    创建VPS备份（需要操作员权限）
    """
    vps_server = VPSManagerService.get_vps_by_id(db, vps_id=vps_id)
    if not vps_server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="VPS服务器不存在"
        )
    
    try:
        backup = VPSManagerService.create_backup(
            db, 
            vps_id=vps_id, 
            storage=backup_in.storage,
            is_auto=backup_in.is_auto,
            notes=backup_in.notes
        )
        return backup
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{vps_id}/backups", response_model=List[VPSBackup])
def read_vps_backups(
    vps_id: int,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取VPS备份列表
    """
    vps_server = VPSManagerService.get_vps_by_id(db, vps_id=vps_id)
    if not vps_server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="VPS服务器不存在"
        )
    
    # 普通用户只能查看自己的VPS备份
    if current_user.role not in ["admin", "operator"] and not current_user.is_superuser:
        if vps_server.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限查看此VPS服务器的备份"
            )
    
    backups = VPSManagerService.get_vps_backups(db, vps_id=vps_id, skip=skip, limit=limit)
    return backups

@router.post("/update-status")
def update_vps_status(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(validate_operator_role)
) -> Dict[str, str]:
    """
    更新所有VPS状态（异步任务，需要操作员权限）
    """
    background_tasks.add_task(VPSManagerService.update_vps_status, db)
    return {"status": "success", "message": "VPS状态更新任务已启动"} 