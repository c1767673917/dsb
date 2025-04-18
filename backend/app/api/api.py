from fastapi import APIRouter

from backend.app.api.endpoints import auth, users, ip_pools, ip_allocations, vps

api_router = APIRouter()

# 认证路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])

# 用户管理路由
api_router.include_router(users.router, prefix="/users", tags=["用户管理"])

# IP池管理路由
api_router.include_router(ip_pools.router, prefix="/ip-pools", tags=["IP池管理"])

# IP分配管理路由
api_router.include_router(ip_allocations.router, prefix="/ip-allocations", tags=["IP分配管理"])

# VPS管理路由
api_router.include_router(vps.router, prefix="/vps", tags=["VPS管理"]) 