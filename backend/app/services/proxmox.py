import logging
from typing import Dict, List, Optional, Any, Union
from proxmoxer import ProxmoxAPI
from proxmoxer.core import ResourceException

from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class ProxmoxService:
    """Proxmox VE API集成服务"""
    
    def __init__(self):
        """初始化Proxmox连接"""
        try:
            # 尝试使用API令牌连接
            if settings.PVE_TOKEN_NAME and settings.PVE_TOKEN_VALUE:
                self.proxmox = ProxmoxAPI(
                    host=settings.PVE_HOST,
                    user=settings.PVE_USER,
                    token_name=settings.PVE_TOKEN_NAME,
                    token_value=settings.PVE_TOKEN_VALUE,
                    verify_ssl=False
                )
            # 使用密码连接
            else:
                self.proxmox = ProxmoxAPI(
                    host=settings.PVE_HOST,
                    user=settings.PVE_USER,
                    password=settings.PVE_PASSWORD,
                    verify_ssl=False
                )
            logger.info(f"成功连接到Proxmox服务器: {settings.PVE_HOST}")
        except Exception as e:
            logger.error(f"连接Proxmox服务器失败: {str(e)}")
            raise Exception(f"无法连接到Proxmox服务器: {str(e)}")
    
    def get_nodes(self) -> List[Dict[str, Any]]:
        """获取所有Proxmox节点"""
        try:
            return self.proxmox.nodes.get()
        except Exception as e:
            logger.error(f"获取节点列表失败: {str(e)}")
            raise Exception(f"获取节点列表失败: {str(e)}")
    
    def get_node_status(self, node: str) -> Dict[str, Any]:
        """获取指定节点的状态"""
        try:
            return self.proxmox.nodes(node).status.get()
        except Exception as e:
            logger.error(f"获取节点 {node} 状态失败: {str(e)}")
            raise Exception(f"获取节点状态失败: {str(e)}")
    
    def get_vms(self, node: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取所有虚拟机
        
        Args:
            node: 可选的节点名称，如果指定则只返回该节点上的VM
        """
        try:
            if node:
                return self.proxmox.nodes(node).qemu.get()
            
            # 如果没有指定节点，获取所有节点上的VM
            vms = []
            for node_info in self.get_nodes():
                node_name = node_info["node"]
                try:
                    node_vms = self.proxmox.nodes(node_name).qemu.get()
                    vms.extend(node_vms)
                except Exception as e:
                    logger.warning(f"获取节点 {node_name} 的VM列表失败: {str(e)}")
            
            return vms
        except Exception as e:
            logger.error(f"获取VM列表失败: {str(e)}")
            raise Exception(f"获取VM列表失败: {str(e)}")
    
    def get_vm_status(self, node: str, vmid: int) -> Dict[str, Any]:
        """获取虚拟机状态"""
        try:
            return self.proxmox.nodes(node).qemu(vmid).status.current.get()
        except Exception as e:
            logger.error(f"获取VM {vmid} 状态失败: {str(e)}")
            raise Exception(f"获取VM状态失败: {str(e)}")
    
    def get_vm_config(self, node: str, vmid: int) -> Dict[str, Any]:
        """获取虚拟机配置"""
        try:
            return self.proxmox.nodes(node).qemu(vmid).config.get()
        except Exception as e:
            logger.error(f"获取VM {vmid} 配置失败: {str(e)}")
            raise Exception(f"获取VM配置失败: {str(e)}")
    
    def start_vm(self, node: str, vmid: int) -> Dict[str, Any]:
        """启动虚拟机"""
        try:
            return self.proxmox.nodes(node).qemu(vmid).status.start.post()
        except Exception as e:
            logger.error(f"启动VM {vmid} 失败: {str(e)}")
            raise Exception(f"启动VM失败: {str(e)}")
    
    def stop_vm(self, node: str, vmid: int) -> Dict[str, Any]:
        """关闭虚拟机"""
        try:
            return self.proxmox.nodes(node).qemu(vmid).status.stop.post()
        except Exception as e:
            logger.error(f"关闭VM {vmid} 失败: {str(e)}")
            raise Exception(f"关闭VM失败: {str(e)}")
    
    def restart_vm(self, node: str, vmid: int) -> Dict[str, Any]:
        """重启虚拟机"""
        try:
            return self.proxmox.nodes(node).qemu(vmid).status.reset.post()
        except Exception as e:
            logger.error(f"重启VM {vmid} 失败: {str(e)}")
            raise Exception(f"重启VM失败: {str(e)}")
    
    def create_vm(self, node: str, vm_params: Dict[str, Any]) -> Dict[str, Any]:
        """创建新虚拟机
        
        Args:
            node: 节点名称
            vm_params: 虚拟机参数字典
        """
        try:
            return self.proxmox.nodes(node).qemu.post(**vm_params)
        except Exception as e:
            logger.error(f"创建VM失败: {str(e)}")
            raise Exception(f"创建VM失败: {str(e)}")
    
    def delete_vm(self, node: str, vmid: int) -> Dict[str, Any]:
        """删除虚拟机"""
        try:
            return self.proxmox.nodes(node).qemu(vmid).delete()
        except Exception as e:
            logger.error(f"删除VM {vmid} 失败: {str(e)}")
            raise Exception(f"删除VM失败: {str(e)}")
    
    def backup_vm(self, node: str, vmid: int, storage: str, compress: str = "zstd") -> Dict[str, Any]:
        """备份虚拟机
        
        Args:
            node: 节点名称
            vmid: 虚拟机ID
            storage: 存储名称
            compress: 压缩方式
        """
        try:
            backup_params = {
                "vmid": vmid,
                "storage": storage,
                "compress": compress,
                "mode": "snapshot"
            }
            return self.proxmox.nodes(node).vzdump.post(**backup_params)
        except Exception as e:
            logger.error(f"备份VM {vmid} 失败: {str(e)}")
            raise Exception(f"备份VM失败: {str(e)}")
    
    def get_storage_list(self, node: str) -> List[Dict[str, Any]]:
        """获取存储列表"""
        try:
            return self.proxmox.nodes(node).storage.get()
        except Exception as e:
            logger.error(f"获取存储列表失败: {str(e)}")
            raise Exception(f"获取存储列表失败: {str(e)}")
    
    def get_templates(self, node: str, storage: str) -> List[Dict[str, Any]]:
        """获取可用模板列表"""
        try:
            return self.proxmox.nodes(node).storage(storage).content.get(content="vztmpl")
        except Exception as e:
            logger.error(f"获取模板列表失败: {str(e)}")
            raise Exception(f"获取模板列表失败: {str(e)}")
    
    def get_vm_backups(self, node: str, storage: str, vmid: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取备份列表
        
        Args:
            node: 节点名称
            storage: 存储名称
            vmid: 可选的虚拟机ID，用于筛选特定VM的备份
        """
        try:
            backups = self.proxmox.nodes(node).storage(storage).content.get(content="backup")
            if vmid:
                return [b for b in backups if f"vzdump-qemu-{vmid}-" in b["volid"]]
            return backups
        except Exception as e:
            logger.error(f"获取备份列表失败: {str(e)}")
            raise Exception(f"获取备份列表失败: {str(e)}")

proxmox_service = ProxmoxService() 