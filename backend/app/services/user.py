from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from jose import jwt
from passlib.context import CryptContext

from backend.app.models.user import User
from backend.app.core.config import settings

# 密码哈希处理
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    """用户服务"""
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """通过ID获取用户"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """通过用户名获取用户"""
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """通过邮箱获取用户"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """获取用户列表"""
        return db.query(User).offset(skip).limit(limit).all()
    
    @staticmethod
    def create_user(
        db: Session, 
        username: str, 
        email: str, 
        password: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        role: str = "user",
        is_active: bool = True,
        is_superuser: bool = False
    ) -> User:
        """创建新用户"""
        hashed_password = pwd_context.hash(password)
        db_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            first_name=first_name,
            last_name=last_name,
            role=role,
            is_active=is_active,
            is_superuser=is_superuser
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def update_user(
        db: Session,
        user_id: int,
        email: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Optional[User]:
        """更新用户信息"""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return None
        
        if email is not None:
            user.email = email
        if first_name is not None:
            user.first_name = first_name
        if last_name is not None:
            user.last_name = last_name
        if role is not None:
            user.role = role
        if is_active is not None:
            user.is_active = is_active
        
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def change_password(db: Session, user_id: int, new_password: str) -> Optional[User]:
        """修改用户密码"""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return None
        
        user.hashed_password = pwd_context.hash(new_password)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """删除用户"""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return False
        
        db.delete(user)
        db.commit()
        return True
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """用户认证"""
        user = UserService.get_user_by_username(db, username)
        if not user:
            return None
        if not user.is_active:
            return None
        if not pwd_context.verify(password, user.hashed_password):
            return None
        return user
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt 