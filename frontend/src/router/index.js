import { createRouter, createWebHistory } from 'vue-router'
import store from '../store'

// 懒加载路由组件
const Login = () => import('../views/Login.vue')
const Layout = () => import('../views/layout/Layout.vue')
const Dashboard = () => import('../views/Dashboard.vue')
const UserManagement = () => import('../views/users/UserManagement.vue')
const IPPoolList = () => import('../views/ippool/IPPoolList.vue')
const IPAllocationList = () => import('../views/ippool/IPAllocationList.vue')
const VPSList = () => import('../views/vps/VPSList.vue')
const VPSDetail = () => import('../views/vps/VPSDetail.vue')
const CreateVPS = () => import('../views/vps/CreateVPS.vue')
const UserProfile = () => import('../views/users/UserProfile.vue')
const NotFound = () => import('../views/NotFound.vue')

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: Layout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: Dashboard,
        meta: { title: '控制面板' }
      },
      {
        path: 'users',
        name: 'UserManagement',
        component: UserManagement,
        meta: { title: '用户管理', requiresAdmin: true }
      },
      {
        path: 'ippools',
        name: 'IPPoolList',
        component: IPPoolList,
        meta: { title: 'IP池管理', requiresOperator: true }
      },
      {
        path: 'ip-allocations',
        name: 'IPAllocationList',
        component: IPAllocationList,
        meta: { title: 'IP分配管理', requiresOperator: true }
      },
      {
        path: 'vps',
        name: 'VPSList',
        component: VPSList,
        meta: { title: 'VPS服务器列表' }
      },
      {
        path: 'vps/:id',
        name: 'VPSDetail',
        component: VPSDetail,
        meta: { title: 'VPS详情' },
        props: true
      },
      {
        path: 'vps/create',
        name: 'CreateVPS',
        component: CreateVPS,
        meta: { title: '创建VPS', requiresOperator: true }
      },
      {
        path: 'profile',
        name: 'UserProfile',
        component: UserProfile,
        meta: { title: '个人资料' }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// 全局导航守卫
router.beforeEach((to, from, next) => {
  const isAuthenticated = store.getters['auth/isAuthenticated']
  const userRole = store.getters['auth/userRole']
  
  // 需要认证的路由
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!isAuthenticated) {
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }
    
    // 需要管理员权限的路由
    if (to.matched.some(record => record.meta.requiresAdmin)) {
      if (userRole !== 'admin' && userRole !== 'superuser') {
        next({ name: 'Dashboard' })
        return
      }
    }
    
    // 需要操作员权限的路由
    if (to.matched.some(record => record.meta.requiresOperator)) {
      if (userRole !== 'admin' && userRole !== 'operator' && userRole !== 'superuser') {
        next({ name: 'Dashboard' })
        return
      }
    }
  }
  
  // 已登录用户访问登录页，重定向到首页
  if (to.name === 'Login' && isAuthenticated) {
    next({ name: 'Dashboard' })
    return
  }
  
  next()
})

export default router 