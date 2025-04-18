export default (request) => ({
  // 用户登录
  login(credentials) {
    const formData = new FormData()
    formData.append('username', credentials.username)
    formData.append('password', credentials.password)
    
    return request({
      url: '/auth/login',
      method: 'post',
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },
  
  // 用户注册
  register(userData) {
    return request({
      url: '/auth/register',
      method: 'post',
      data: userData
    })
  },
  
  // 获取当前用户信息
  getCurrentUser() {
    return request({
      url: '/auth/me',
      method: 'get'
    })
  },
  
  // 修改密码
  changePassword(passwordData) {
    return request({
      url: '/auth/change-password',
      method: 'post',
      data: passwordData
    })
  }
}) 