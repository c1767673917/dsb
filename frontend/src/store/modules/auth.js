import api from '@/api'
import router from '@/router'
import { ElMessage } from 'element-plus'

const TOKEN_KEY = 'access_token'
const USER_KEY = 'user_info'

// 初始化状态
const state = {
  token: localStorage.getItem(TOKEN_KEY) || '',
  user: JSON.parse(localStorage.getItem(USER_KEY) || '{}')
}

const getters = {
  isAuthenticated: state => !!state.token,
  currentUser: state => state.user,
  userRole: state => state.user.role || '',
  isAdmin: state => state.user.role === 'admin' || state.user.is_superuser,
  isOperator: state => state.user.role === 'operator' || state.user.role === 'admin' || state.user.is_superuser
}

const actions = {
  // 登录
  async login({ commit }, credentials) {
    try {
      const response = await api.auth.login(credentials)
      commit('setToken', response.data.access_token)
      await dispatch('fetchUserInfo')
      return response
    } catch (error) {
      ElMessage.error('登录失败: ' + (error.response?.data?.detail || error.message))
      throw error
    }
  },

  // 获取当前用户信息
  async fetchUserInfo({ commit }) {
    try {
      const response = await api.auth.getCurrentUser()
      commit('setUser', response.data)
      return response
    } catch (error) {
      ElMessage.error('获取用户信息失败: ' + (error.response?.data?.detail || error.message))
      throw error
    }
  },

  // 注册
  async register({ commit }, userData) {
    try {
      const response = await api.auth.register(userData)
      return response
    } catch (error) {
      ElMessage.error('注册失败: ' + (error.response?.data?.detail || error.message))
      throw error
    }
  },

  // 修改密码
  async changePassword({ commit }, passwordData) {
    try {
      const response = await api.auth.changePassword(passwordData)
      return response
    } catch (error) {
      ElMessage.error('修改密码失败: ' + (error.response?.data?.detail || error.message))
      throw error
    }
  },

  // 退出登录
  logout({ commit }) {
    commit('clearAuth')
    router.push('/login')
  }
}

const mutations = {
  setToken(state, token) {
    state.token = token
    localStorage.setItem(TOKEN_KEY, token)
  },
  
  setUser(state, user) {
    state.user = user
    localStorage.setItem(USER_KEY, JSON.stringify(user))
  },
  
  clearAuth(state) {
    state.token = ''
    state.user = {}
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
} 