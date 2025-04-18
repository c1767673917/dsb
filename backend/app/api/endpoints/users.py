from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import get_current_active_superuser, validate_admin_role
from backend.app.services.user import UserService
from backend.app.api.schemas.user import User, UserCreate, UserUpdate, UserBrief

router = APIRouter()

@router.get("/", response_model=List[UserBrief])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(validate_admin_role)
) -> Any:
    """
    获取用户列表（需要管理员权限）
    """
    users = UserService.get_users(db, skip=skip, limit=limit)
    return users

@router.post("/", response_model=User)
def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
    current_user = Depends(get_current_active_superuser)
) -> Any:
    """
    创建新用户（需要超级管理员权限）
    """
    # 检查用户名是否已存在
    user = UserService.get_user_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    user = UserService.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已存在"
        )
    
    user = UserService.create_user(db, **user_in.dict())
    return user

@router.get("/{user_id}", response_model=User)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(validate_admin_role)
) -> Any:
    """
    根据ID获取用户信息（需要管理员权限）
    """
    user = UserService.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return user

@router.put("/{user_id}", response_model=User)
def update_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    user_in: UserUpdate,
    current_user = Depends(validate_admin_role)
) -> Any:
    """
    更新用户信息（需要管理员权限）
    """
    user = UserService.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 检查邮箱是否已被其他用户使用
    if user_in.email and user_in.email != user.email:
        existing_user = UserService.get_user_by_email(db, email=user_in.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被其他用户使用"
            )
    
    # 普通管理员不能修改超级管理员
    if user.is_superuser and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改超级管理员信息"
        )
    
    user = UserService.update_user(
        db,
        user_id=user_id,
        email=user_in.email,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        role=user_in.role,
        is_active=user_in.is_active
    )
    return user

@router.delete("/{user_id}", response_model=dict)
def delete_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    current_user = Depends(get_current_active_superuser)
) -> Any:
    """
    删除用户（需要超级管理员权限）
    """
    user = UserService.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 不能删除自己
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除当前登录用户"
        )
    
    # 删除用户
    UserService.delete_user(db, user_id=user_id)
    return {"status": "success", "message": "用户已删除"} 