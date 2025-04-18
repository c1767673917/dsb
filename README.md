# PVE VPS 管理系统

这是一个针对 Proxmox Virtual Environment (PVE) 的综合管理系统，提供自动化的 VPS 部署、IP 管理和多用户管理界面等功能。

## 主要功能

1. **IP 地址管理**
   - 自动 IP 分配与跟踪
   - 网段 IP 池管理
   - IP 使用监控与报告
   - IP 预留与释放

2. **VPS 自动化**
   - 自动化 VPS 配置流程
   - 资源分配管理
   - 多操作系统模板支持
   - 自动备份解决方案

3. **操作系统安装**
   - 自动化操作系统安装脚本
   - 主流 Linux 和 Windows 支持
   - 自定义模板管理
   - 安装后配置选项

4. **管理界面**
   - 用户友好的 Web 仪表盘
   - 实时监控功能
   - 资源使用统计
   - 基于角色的权限管理

## 技术规格

- RESTful API 集成
- 安全身份验证
- 日志记录和审计
- 可扩展架构
- 兼容最新版 PVE

## 安装指南

1. 克隆仓库
```
git clone https://github.com/yourusername/pve-vps-management.git
cd pve-vps-management
```

2. 安装依赖
```
pip install -r requirements.txt
```

3. 配置环境变量
```
cp .env.example .env
# 编辑 .env 文件以适应您的环境
```

4. 初始化数据库
```
python scripts/init_db.py
```

5. 启动服务
```
python manage.py runserver
```

## 架构

该系统采用前后端分离的架构:
- 后端: Python FastAPI
- 前端: Vue.js
- 数据库: PostgreSQL
- PVE 交互: Proxmoxer Python 库

## 许可证

MIT 