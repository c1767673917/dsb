import axios from 'axios'
import auth from './modules/auth'
import users from './modules/users'
import ipPools from './modules/ipPools'
import ipAllocations from './modules/ipAllocations'
import vps from './modules/vps'
import router from '@/router'
import store from '@/store'
import { ElMessage } from 'element-plus'

// 创建axios实例
const request = axios.create({
  baseURL: process.env.VUE_APP_API_URL || 'http://localhost:8000/api/v1',
  timeout: 10000
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    // 添加认证令牌
    const token = store.state.auth.token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // 设置加载状态
    store.dispatch('app/setLoading', true)
    
    return config
  },
  error => {
    store.dispatch('app/setLoading', false)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    store.dispatch('app/setLoading', false)
    return response
  },
  error => {
    store.dispatch('app/setLoading', false)
    
    const response = error.response
    
    // 未授权，清除token，跳转到登录页
    if (response && response.status === 401) {
      store.dispatch('auth/logout')
      router.push('/login')
      ElMessage.error('会话已过期，请重新登录')
    } 
    // 服务器错误
    else if (response && response.status >= 500) {
      ElMessage.error('服务器错误，请稍后再试')
    }
    // 其他客户端错误
    else if (response && response.data) {
      const message = response.data.detail || '操作失败'
      ElMessage.error(message)
    } 
    // 网络错误
    else {
      ElMessage.error('网络错误，请检查您的网络连接')
    }
    
    return Promise.reject(error)
  }
)

export default {
  auth: auth(request),
  users: users(request),
  ipPools: ipPools(request),
  ipAllocations: ipAllocations(request),
  vps: vps(request)
} 