from typing import Any
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.config import settings
from backend.app.core.security import create_access_token, get_current_user
from backend.app.services.user import UserService
from backend.app.api.schemas.user import Token, User, UserCreate, ChangePassword

router = APIRouter()

@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2密码流程获取访问令牌
    """
    user = UserService.authenticate_user(
        db, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            data={"sub": user.username, "user_id": user.id},
            expires_delta=access_token_expires
        ),
        "token_type": "bearer"
    }

@router.post("/register", response_model=User)
def register_user(*, db: Session = Depends(get_db), user_in: UserCreate) -> Any:
    """
    注册新用户
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
    
    # 创建新用户（普通用户无法创建超级管理员）
    user_in_dict = user_in.dict()
    user_in_dict["is_superuser"] = False
    user = UserService.create_user(db, **user_in_dict)
    return user

@router.post("/change-password", response_model=User)
def change_password(
    *,
    db: Session = Depends(get_db),
    password_in: ChangePassword,
    current_user = Depends(get_current_user)
) -> Any:
    """
    修改当前用户密码
    """
    # 验证旧密码
    user = UserService.authenticate_user(
        db, username=current_user.username, password=password_in.old_password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码不正确"
        )
    
    # 修改密码
    user = UserService.change_password(db, user_id=current_user.id, new_password=password_in.new_password)
    return user

@router.get("/me", response_model=User)
def read_users_me(current_user = Depends(get_current_user)) -> Any:
    """
    获取当前用户信息
    """
    return current_user 