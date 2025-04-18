<template>
  <div class="app-container">
    <el-container>
      <!-- 侧边栏 -->
      <el-aside :width="isCollapsed ? '64px' : '220px'" class="aside">
        <div class="logo">
          <img src="@/assets/logo.png" alt="Logo" v-if="!isCollapsed" />
          <img src="@/assets/logo-mini.png" alt="Logo" v-else />
        </div>
        <el-menu
          :default-active="activeMenu"
          class="el-menu-vertical"
          :collapse="isCollapsed"
          background-color="#304156"
          text-color="#fff"
          active-text-color="#409EFF"
          router
        >
          <el-menu-item index="/">
            <el-icon><el-icon-odometer /></el-icon>
            <span>控制面板</span>
          </el-menu-item>
          
          <el-menu-item index="/vps">
            <el-icon><el-icon-monitor /></el-icon>
            <span>VPS管理</span>
          </el-menu-item>
          
          <el-menu-item index="/vps/create" v-if="isOperator">
            <el-icon><el-icon-plus /></el-icon>
            <span>创建VPS</span>
          </el-menu-item>
          
          <el-submenu index="ip" v-if="isOperator">
            <template #title>
              <el-icon><el-icon-connection /></el-icon>
              <span>IP管理</span>
            </template>
            <el-menu-item index="/ippools">IP池管理</el-menu-item>
            <el-menu-item index="/ip-allocations">IP分配管理</el-menu-item>
          </el-submenu>
          
          <el-menu-item index="/users" v-if="isAdmin">
            <el-icon><el-icon-user /></el-icon>
            <span>用户管理</span>
          </el-menu-item>
          
          <el-menu-item index="/profile">
            <el-icon><el-icon-setting /></el-icon>
            <span>个人设置</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      
      <!-- 主体内容 -->
      <el-container>
        <!-- 头部 -->
        <el-header class="header">
          <div class="header-left">
            <el-button
              :icon="isCollapsed ? 'el-icon-s-unfold' : 'el-icon-s-fold'"
              @click="toggleSidebar"
              type="text"
            />
            <span class="current-route">{{ currentRoute }}</span>
          </div>
          <div class="header-right">
            <el-dropdown trigger="click" @command="handleCommand">
              <span class="user-dropdown">
                {{ username }}
                <el-icon class="el-icon-arrow-down" />
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">个人资料</el-dropdown-item>
                  <el-dropdown-item command="logout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>
        
        <!-- 主要内容 -->
        <el-main class="main">
          <router-view />
        </el-main>
        
        <!-- 页脚 -->
        <el-footer class="footer">
          PVE VPS 管理系统 &copy; {{ currentYear }}
        </el-footer>
      </el-container>
    </el-container>
  </div>
</template>

<script>
import { computed, ref } from 'vue'
import { useStore } from 'vuex'
import { useRoute, useRouter } from 'vue-router'

export default {
  name: 'Layout',
  
  setup() {
    const store = useStore()
    const route = useRoute()
    const router = useRouter()
    
    // 当前年份
    const currentYear = new Date().getFullYear()
    
    // 侧边栏折叠状态
    const isCollapsed = computed(() => store.getters['app/sidebarCollapsed'])
    
    // 用户信息
    const username = computed(() => {
      const user = store.getters['auth/currentUser']
      return user.username || ''
    })
    
    // 权限检查
    const isAdmin = computed(() => store.getters['auth/isAdmin'])
    const isOperator = computed(() => store.getters['auth/isOperator'])
    
    // 当前路由
    const currentRoute = computed(() => {
      return route.meta.title || '未知页面'
    })
    
    // 当前激活菜单
    const activeMenu = computed(() => route.path)
    
    // 切换侧边栏
    const toggleSidebar = () => {
      store.dispatch('app/toggleSidebar')
    }
    
    // 下拉菜单命令处理
    const handleCommand = (command) => {
      if (command === 'logout') {
        store.dispatch('auth/logout')
      } else if (command === 'profile') {
        router.push('/profile')
      }
    }
    
    return {
      isCollapsed,
      username,
      isAdmin,
      isOperator,
      currentRoute,
      currentYear,
      activeMenu,
      toggleSidebar,
      handleCommand
    }
  }
}
</script>

<style scoped>
.app-container {
  height: 100vh;
}

.aside {
  background-color: #304156;
  transition: width 0.3s;
  overflow: hidden;
}

.logo {
  height: 60px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #263445;
}

.logo img {
  height: 40px;
}

.el-menu-vertical:not(.el-menu--collapse) {
  width: 220px;
}

.header {
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
}

.current-route {
  margin-left: 15px;
  font-size: 16px;
  font-weight: bold;
}

.user-dropdown {
  cursor: pointer;
  display: flex;
  align-items: center;
}

.user-dropdown .el-icon-arrow-down {
  margin-left: 5px;
}

.main {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}

.footer {
  text-align: center;
  font-size: 14px;
  color: #666;
  padding: 15px 0;
  background-color: #fff;
}
</style> 