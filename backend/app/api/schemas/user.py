from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator

# 共享属性
class UserBase(BaseModel):
    username: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = "user"
    is_active: Optional[bool] = True

# 创建用户请求
class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    is_superuser: Optional[bool] = False
    
    @validator('role')
    def validate_role(cls, v):
        allowed_roles = ["admin", "operator", "user", "guest"]
        if v not in allowed_roles:
            raise ValueError(f"角色必须是以下之一: {', '.join(allowed_roles)}")
        return v

# 更新用户请求
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    
    @validator('role')
    def validate_role(cls, v):
        if v is not None:
            allowed_roles = ["admin", "operator", "user", "guest"]
            if v not in allowed_roles:
                raise ValueError(f"角色必须是以下之一: {', '.join(allowed_roles)}")
        return v

# 修改密码请求
class ChangePassword(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6)

# 用户响应
class User(UserBase):
    id: int
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# 用户简略信息
class UserBrief(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    
    class Config:
        orm_mode = True

# 登录请求
class Login(BaseModel):
    username: str
    password: str

# 令牌响应
class Token(BaseModel):
    access_token: str
    token_type: str

# 令牌数据
class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None 