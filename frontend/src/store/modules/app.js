// 初始化状态
const state = {
  sidebarCollapsed: false,
  loading: false,
  notifications: []
}

const getters = {
  sidebarCollapsed: state => state.sidebarCollapsed,
  isLoading: state => state.loading,
  notifications: state => state.notifications
}

const actions = {
  toggleSidebar({ commit }) {
    commit('TOGGLE_SIDEBAR')
  },
  
  setLoading({ commit }, isLoading) {
    commit('SET_LOADING', isLoading)
  },
  
  addNotification({ commit }, notification) {
    commit('ADD_NOTIFICATION', notification)
  },
  
  removeNotification({ commit }, id) {
    commit('REMOVE_NOTIFICATION', id)
  },
  
  clearNotifications({ commit }) {
    commit('CLEAR_NOTIFICATIONS')
  }
}

const mutations = {
  TOGGLE_SIDEBAR(state) {
    state.sidebarCollapsed = !state.sidebarCollapsed
  },
  
  SET_LOADING(state, isLoading) {
    state.loading = isLoading
  },
  
  ADD_NOTIFICATION(state, notification) {
    state.notifications.push({
      id: new Date().getTime(),
      ...notification
    })
  },
  
  REMOVE_NOTIFICATION(state, id) {
    state.notifications = state.notifications.filter(n => n.id !== id)
  },
  
  CLEAR_NOTIFICATIONS(state) {
    state.notifications = []
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
} 