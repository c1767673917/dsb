import logging
import random
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from sqlalchemy.orm import Session

from backend.app.models.vps import VPSServer, VPSBackup
from backend.app.models.ip import IPAllocation
from backend.app.services.proxmox import proxmox_service
from backend.app.services.ip_manager import IPManagerService
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class VPSManagerService:
    """VPS服务器管理服务"""
    
    @staticmethod
    def create_vps(
        db: Session,
        user_id: int,
        name: str,
        node_name: str,
        cpu_cores: int,
        memory: int,
        disk_size: int,
        os_type: str,
        os_template: str,
        ip_allocation_id: Optional[int] = None,
        ip_pool_id: Optional[int] = None,
        bandwidth: int = 1000,
        notes: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> VPSServer:
        """创建新的VPS服务器
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            name: VPS名称
            node_name: Proxmox节点名称
            cpu_cores: CPU核心数
            memory: 内存大小(MB)
            disk_size: 磁盘大小(GB)
            os_type: 操作系统类型(linux, windows)
            os_template: 操作系统模板
            ip_allocation_id: IP分配ID
            ip_pool_id: IP池ID，如果没有提供ip_allocation_id则从此池中分配
            bandwidth: 带宽(Mbps)
            notes: 备注
            config: 其他配置
        """
        try:
            # 获取可用的VMID
            vmid = VPSManagerService._get_next_vmid(db)
            
            # 确保IP地址分配
            ip_allocation = None
            if ip_allocation_id:
                ip_allocation = db.query(IPAllocation).filter(IPAllocation.id == ip_allocation_id).first()
                if not ip_allocation or ip_allocation.status != "available":
                    raise Exception("指定的IP地址不可用")
            elif ip_pool_id:
                ip_allocation = IPManagerService.get_available_ip(db, ip_pool_id)
                if not ip_allocation:
                    raise Exception(f"IP池中没有可用的IP地址")
            else:
                ip_allocation = IPManagerService.get_available_ip(db)
                if not ip_allocation:
                    raise Exception("没有可用的IP地址")
            
            # 分配IP
            ip_allocation = IPManagerService.allocate_ip(
                db, 
                ip_allocation.ip_address,
                user_id=user_id,
                hostname=name
            )
            
            # 准备Proxmox VM创建参数
            ip_pool = db.query(IPPool).filter(IPPool.id == ip_allocation.ip_pool_id).first()
            if not ip_pool:
                raise Exception("找不到IP池信息")
            
            # 创建VPS记录
            vps_server = VPSServer(
                name=name,
                vmid=vmid,
                node_name=node_name,
                user_id=user_id,
                status="creating",
                cpu_cores=cpu_cores,
                memory=memory,
                disk_size=disk_size,
                bandwidth=bandwidth,
                os_type=os_type,
                os_template=os_template,
                ip_allocation_id=ip_allocation.id,
                notes=notes,
                config=config or {}
            )
            db.add(vps_server)
            db.commit()
            db.refresh(vps_server)
            
            # 准备网络配置
            net_config = {
                "ip": f"{ip_allocation.ip_address}/{VPSManagerService._convert_subnet_mask_to_cidr(ip_pool.subnet_mask)}",
                "gw": ip_pool.gateway,
                "nameserver": ip_pool.dns_servers.split(",")[0]
            }
            
            # 构建VM创建参数
            vm_params = {
                "vmid": vmid,
                "name": name,
                "cores": cpu_cores,
                "memory": memory,
                "storage": "local-lvm",  # 这里应该根据实际情况配置存储
                "net0": f"virtio,bridge=vmbr0",
                "ipconfig0": f"ip={net_config['ip']},gw={net_config['gw']}",
                "nameserver": net_config['nameserver'],
                "ostype": "l26" if os_type == "linux" else "win10"
            }
            
            if os_type == "linux":
                # 对于Linux系统，使用克隆或模板
                if "ubuntu" in os_template or "debian" in os_template:
                    vm_params["clone"] = f"template-{os_template}"
                else:
                    vm_params["template"] = f"template-{os_template}"
            else:
                # 对于Windows系统，通常使用ISO安装
                vm_params["ide2"] = f"local:iso/windows-{os_template}.iso,media=cdrom"
                vm_params["boot"] = "d"
            
            # 创建VM
            try:
                result = proxmox_service.create_vm(node_name, vm_params)
                
                # 更新状态
                vps_server.status = "stopped"
                db.commit()
                
                # 启动VM
                proxmox_service.start_vm(node_name, vmid)
                vps_server.status = "running"
                db.commit()
                
                return vps_server
            except Exception as e:
                # 发生错误，释放IP并标记VPS为失败状态
                IPManagerService.release_ip(db, ip_allocation.ip_address)
                vps_server.status = "failed"
                db.commit()
                raise Exception(f"创建VM失败: {str(e)}")
            
        except Exception as e:
            db.rollback()
            logger.error(f"创建VPS失败: {str(e)}")
            raise Exception(f"创建VPS失败: {str(e)}")
    
    @staticmethod
    def delete_vps(db: Session, vps_id: int) -> Dict[str, Any]:
        """删除VPS服务器"""
        vps_server = db.query(VPSServer).filter(VPSServer.id == vps_id).first()
        if not vps_server:
            raise Exception(f"找不到ID为 {vps_id} 的VPS服务器")
        
        try:
            # 先关闭VM
            if vps_server.status == "running":
                proxmox_service.stop_vm(vps_server.node_name, vps_server.vmid)
            
            # 删除VM
            result = proxmox_service.delete_vm(vps_server.node_name, vps_server.vmid)
            
            # 释放IP
            if vps_server.ip_allocation_id:
                ip_allocation = db.query(IPAllocation).filter(IPAllocation.id == vps_server.ip_allocation_id).first()
                if ip_allocation:
                    IPManagerService.release_ip(db, ip_allocation.ip_address)
            
            # 删除VPS记录
            db.delete(vps_server)
            db.commit()
            
            return {"status": "success", "message": f"VPS {vps_server.name} 已成功删除"}
        except Exception as e:
            db.rollback()
            logger.error(f"删除VPS失败: {str(e)}")
            raise Exception(f"删除VPS失败: {str(e)}")
    
    @staticmethod
    def start_vps(db: Session, vps_id: int) -> VPSServer:
        """启动VPS服务器"""
        vps_server = db.query(VPSServer).filter(VPSServer.id == vps_id).first()
        if not vps_server:
            raise Exception(f"找不到ID为 {vps_id} 的VPS服务器")
        
        if vps_server.status == "running":
            return vps_server
        
        try:
            proxmox_service.start_vm(vps_server.node_name, vps_server.vmid)
            vps_server.status = "running"
            db.commit()
            return vps_server
        except Exception as e:
            logger.error(f"启动VPS失败: {str(e)}")
            raise Exception(f"启动VPS失败: {str(e)}")
    
    @staticmethod
    def stop_vps(db: Session, vps_id: int) -> VPSServer:
        """关闭VPS服务器"""
        vps_server = db.query(VPSServer).filter(VPSServer.id == vps_id).first()
        if not vps_server:
            raise Exception(f"找不到ID为 {vps_id} 的VPS服务器")
        
        if vps_server.status == "stopped":
            return vps_server
        
        try:
            proxmox_service.stop_vm(vps_server.node_name, vps_server.vmid)
            vps_server.status = "stopped"
            db.commit()
            return vps_server
        except Exception as e:
            logger.error(f"关闭VPS失败: {str(e)}")
            raise Exception(f"关闭VPS失败: {str(e)}")
    
    @staticmethod
    def restart_vps(db: Session, vps_id: int) -> VPSServer:
        """重启VPS服务器"""
        vps_server = db.query(VPSServer).filter(VPSServer.id == vps_id).first()
        if not vps_server:
            raise Exception(f"找不到ID为 {vps_id} 的VPS服务器")
        
        try:
            proxmox_service.restart_vm(vps_server.node_name, vps_server.vmid)
            vps_server.status = "running"
            db.commit()
            return vps_server
        except Exception as e:
            logger.error(f"重启VPS失败: {str(e)}")
            raise Exception(f"重启VPS失败: {str(e)}")
    
    @staticmethod
    def create_backup(db: Session, vps_id: int, storage: str = "local", is_auto: bool = False, notes: Optional[str] = None) -> VPSBackup:
        """创建VPS备份"""
        vps_server = db.query(VPSServer).filter(VPSServer.id == vps_id).first()
        if not vps_server:
            raise Exception(f"找不到ID为 {vps_id} 的VPS服务器")
        
        try:
            result = proxmox_service.backup_vm(vps_server.node_name, vps_server.vmid, storage)
            
            # 这里假设结果中包含备份ID和文件名等信息
            # 实际实现中，可能需要等待备份完成并获取详细信息
            backup = VPSBackup(
                vps_id=vps_id,
                backup_id=f"{vps_server.vmid}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                file_name=f"vzdump-qemu-{vps_server.vmid}-{datetime.now().strftime('%Y_%m_%d-%H_%M_%S')}.vma.zst",
                file_size=0,  # 这里需要实际获取文件大小
                notes=notes,
                is_auto=is_auto
            )
            db.add(backup)
            
            # 更新VPS最后备份时间
            vps_server.last_backup_at = datetime.utcnow()
            
            db.commit()
            db.refresh(backup)
            return backup
        except Exception as e:
            db.rollback()
            logger.error(f"创建备份失败: {str(e)}")
            raise Exception(f"创建备份失败: {str(e)}")
    
    @staticmethod
    def get_vps_by_id(db: Session, vps_id: int) -> Optional[VPSServer]:
        """通过ID获取VPS服务器"""
        return db.query(VPSServer).filter(VPSServer.id == vps_id).first()
    
    @staticmethod
    def get_vps_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[VPSServer]:
        """获取用户的VPS服务器列表"""
        return db.query(VPSServer).filter(VPSServer.user_id == user_id).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_all_vps(db: Session, skip: int = 0, limit: int = 100) -> List[VPSServer]:
        """获取所有VPS服务器列表"""
        return db.query(VPSServer).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_vps_backups(db: Session, vps_id: int, skip: int = 0, limit: int = 100) -> List[VPSBackup]:
        """获取VPS备份列表"""
        return db.query(VPSBackup).filter(VPSBackup.vps_id == vps_id).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_vps_status(db: Session) -> None:
        """更新所有VPS状态"""
        vps_servers = db.query(VPSServer).all()
        
        for vps in vps_servers:
            try:
                status = proxmox_service.get_vm_status(vps.node_name, vps.vmid)
                vps.status = status["status"]
            except Exception as e:
                logger.warning(f"无法更新VPS {vps.id} 状态: {str(e)}")
        
        db.commit()
    
    @staticmethod
    def _get_next_vmid(db: Session) -> int:
        """获取下一个可用的VMID"""
        try:
            # 从Proxmox获取当前使用的VMID列表
            vms = []
            for node in proxmox_service.get_nodes():
                try:
                    node_vms = proxmox_service.get_vms(node["node"])
                    vms.extend(node_vms)
                except:
                    pass
            
            used_vmids = set(vm["vmid"] for vm in vms)
            
            # 寻找可用的VMID（通常从100开始）
            vmid = 100
            while vmid in used_vmids:
                vmid += 1
            
            return vmid
        except Exception as e:
            # 如果无法从Proxmox获取，尝试从数据库获取最大值
            max_vmid = db.query(VPSServer).order_by(VPSServer.vmid.desc()).first()
            return (max_vmid.vmid + 1) if max_vmid else 100
    
    @staticmethod
    def _convert_subnet_mask_to_cidr(subnet_mask: str) -> int:
        """将子网掩码转换为CIDR表示法"""
        mask_octets = subnet_mask.split('.')
        binary_mask = ''
        for octet in mask_octets:
            binary_mask += bin(int(octet))[2:].zfill(8)
        return binary_mask.count('1') 