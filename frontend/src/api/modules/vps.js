export default (request) => ({
  // 获取VPS列表
  getVPSList(params = {}) {
    return request({
      url: '/vps',
      method: 'get',
      params
    })
  },
  
  // 获取单个VPS详情
  getVPS(id) {
    return request({
      url: `/vps/${id}`,
      method: 'get'
    })
  },
  
  // 创建VPS
  createVPS(data) {
    return request({
      url: '/vps',
      method: 'post',
      data
    })
  },
  
  // 更新VPS
  updateVPS(id, data) {
    return request({
      url: `/vps/${id}`,
      method: 'put',
      data
    })
  },
  
  // 删除VPS
  deleteVPS(id) {
    return request({
      url: `/vps/${id}`,
      method: 'delete'
    })
  },
  
  // 启动VPS
  startVPS(id) {
    return request({
      url: `/vps/${id}/start`,
      method: 'post'
    })
  },
  
  // 停止VPS
  stopVPS(id) {
    return request({
      url: `/vps/${id}/stop`,
      method: 'post'
    })
  },
  
  // 重启VPS
  restartVPS(id) {
    return request({
      url: `/vps/${id}/restart`,
      method: 'post'
    })
  },
  
  // 创建VPS备份
  createBackup(id, data) {
    return request({
      url: `/vps/${id}/backup`,
      method: 'post',
      data
    })
  },
  
  // 获取VPS备份列表
  getBackupList(id, params = {}) {
    return request({
      url: `/vps/${id}/backups`,
      method: 'get',
      params
    })
  },
  
  // 更新所有VPS状态
  updateVPSStatus() {
    return request({
      url: '/vps/update-status',
      method: 'post'
    })
  }
}) 