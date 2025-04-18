<template>
  <div class="dashboard-container">
    <h1 class="page-title">控制面板</h1>
    
    <!-- 系统状态卡片 -->
    <el-row :gutter="20">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="status-card">
          <template #header>
            <div class="card-header">
              <span>VPS服务器</span>
              <el-icon><el-icon-monitor /></el-icon>
            </div>
          </template>
          <div class="card-value">{{ stats.totalVPS }}</div>
          <div class="card-detail">
            <div>
              <span class="detail-label">运行中:</span>
              <span class="detail-value running">{{ stats.runningVPS }}</span>
            </div>
            <div>
              <span class="detail-label">已停止:</span>
              <span class="detail-value stopped">{{ stats.stoppedVPS }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="status-card">
          <template #header>
            <div class="card-header">
              <span>IP地址</span>
              <el-icon><el-icon-connection /></el-icon>
            </div>
          </template>
          <div class="card-value">{{ stats.totalIPs }}</div>
          <div class="card-detail">
            <div>
              <span class="detail-label">已分配:</span>
              <span class="detail-value used">{{ stats.allocatedIPs }}</span>
            </div>
            <div>
              <span class="detail-label">可用:</span>
              <span class="detail-value available">{{ stats.availableIPs }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="status-card">
          <template #header>
            <div class="card-header">
              <span>用户数量</span>
              <el-icon><el-icon-user /></el-icon>
            </div>
          </template>
          <div class="card-value">{{ stats.totalUsers }}</div>
          <div class="card-detail">
            <div>
              <span class="detail-label">管理员:</span>
              <span class="detail-value">{{ stats.adminUsers }}</span>
            </div>
            <div>
              <span class="detail-label">普通用户:</span>
              <span class="detail-value">{{ stats.regularUsers }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="status-card">
          <template #header>
            <div class="card-header">
              <span>备份数量</span>
              <el-icon><el-icon-document-copy /></el-icon>
            </div>
          </template>
          <div class="card-value">{{ stats.totalBackups }}</div>
          <div class="card-detail">
            <div>
              <span class="detail-label">自动备份:</span>
              <span class="detail-value">{{ stats.autoBackups }}</span>
            </div>
            <div>
              <span class="detail-label">手动备份:</span>
              <span class="detail-value">{{ stats.manualBackups }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 快速操作区 -->
    <el-card class="quick-actions-card">
      <template #header>
        <div class="card-header">
          <span>快速操作</span>
        </div>
      </template>
      <div class="quick-actions">
        <el-button
          type="primary"
          icon="el-icon-plus"
          @click="$router.push('/vps/create')"
          v-if="isOperator"
        >
          创建VPS
        </el-button>
        
        <el-button
          type="success"
          icon="el-icon-refresh"
          @click="refreshVPSStatus"
          v-if="isOperator"
          :loading="refreshing"
        >
          刷新VPS状态
        </el-button>
        
        <el-button
          type="warning"
          icon="el-icon-connection"
          @click="$router.push('/ip-allocations')"
          v-if="isOperator"
        >
          管理IP
        </el-button>
        
        <el-button
          type="info"
          icon="el-icon-document"
          @click="$router.push('/vps')"
        >
          VPS列表
        </el-button>
      </div>
    </el-card>
    
    <!-- 我的VPS列表 -->
    <el-card class="my-vps-card">
      <template #header>
        <div class="card-header">
          <span>我的VPS服务器</span>
          <el-button
            type="primary"
            size="small"
            @click="$router.push('/vps')"
          >
            查看全部
          </el-button>
        </div>
      </template>
      
      <el-table
        :data="myVPSList"
        stripe
        v-loading="loading"
      >
        <el-table-column prop="name" label="名称" width="180" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="scope">
            <el-tag
              :type="getStatusType(scope.row.status)"
              size="small"
            >
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="ip_address" label="IP地址" width="150" />
        <el-table-column prop="os_template" label="系统模板" width="150" />
        <el-table-column prop="cpu_cores" label="CPU" width="80" />
        <el-table-column prop="memory" label="内存" width="100">
          <template #default="scope">
            {{ (scope.row.memory / 1024).toFixed(1) }} GB
          </template>
        </el-table-column>
        <el-table-column label="操作">
          <template #default="scope">
            <el-button
              size="small"
              type="primary"
              @click="$router.push(`/vps/${scope.row.id}`)"
            >
              详情
            </el-button>
            <el-button
              size="small"
              type="success"
              v-if="scope.row.status !== 'running'"
              @click="startVPS(scope.row.id)"
              :loading="actionLoading[scope.row.id]?.start"
            >
              启动
            </el-button>
            <el-button
              size="small"
              type="warning"
              v-if="scope.row.status === 'running'"
              @click="stopVPS(scope.row.id)"
              :loading="actionLoading[scope.row.id]?.stop"
            >
              停止
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="empty-data" v-if="myVPSList.length === 0">
        <el-empty description="暂无VPS服务器" />
        <el-button
          type="primary"
          @click="$router.push('/vps/create')"
          v-if="isOperator"
        >
          创建新VPS
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'

export default {
  name: 'Dashboard',
  
  setup() {
    const store = useStore()
    const loading = ref(false)
    const refreshing = ref(false)
    const actionLoading = reactive({})
    
    // 统计数据
    const stats = reactive({
      totalVPS: 0,
      runningVPS: 0,
      stoppedVPS: 0,
      totalIPs: 0,
      allocatedIPs: 0,
      availableIPs: 0,
      totalUsers: 0,
      adminUsers: 0,
      regularUsers: 0,
      totalBackups: 0,
      autoBackups: 0,
      manualBackups: 0
    })
    
    // 我的VPS列表
    const myVPSList = ref([])
    
    // 权限检查
    const isOperator = computed(() => store.getters['auth/isOperator'])
    
    // 获取状态类型
    const getStatusType = (status) => {
      switch (status) {
        case 'running':
          return 'success'
        case 'stopped':
          return 'danger'
        case 'suspended':
          return 'warning'
        default:
          return 'info'
      }
    }
    
    // 获取状态文本
    const getStatusText = (status) => {
      switch (status) {
        case 'running':
          return '运行中'
        case 'stopped':
          return '已停止'
        case 'suspended':
          return '已挂起'
        case 'creating':
          return '创建中'
        case 'failed':
          return '失败'
        default:
          return status
      }
    }
    
    // 加载我的VPS列表
    const loadMyVPSList = async () => {
      loading.value = true
      
      try {
        const response = await store.dispatch('vps/getVPSList')
        
        // 最多显示5个VPS
        myVPSList.value = response.data.slice(0, 5)
        
        // 更新统计数据
        const allVPS = response.data
        stats.totalVPS = allVPS.length
        stats.runningVPS = allVPS.filter(vps => vps.status === 'running').length
        stats.stoppedVPS = allVPS.filter(vps => vps.status === 'stopped').length
      } catch (error) {
        console.error('加载VPS列表失败:', error)
        ElMessage.error('加载VPS列表失败')
      } finally {
        loading.value = false
      }
    }
    
    // 刷新VPS状态
    const refreshVPSStatus = async () => {
      refreshing.value = true
      
      try {
        await store.dispatch('vps/updateVPSStatus')
        await loadMyVPSList()
        ElMessage.success('VPS状态已更新')
      } catch (error) {
        console.error('更新VPS状态失败:', error)
        ElMessage.error('更新VPS状态失败')
      } finally {
        refreshing.value = false
      }
    }
    
    // 启动VPS
    const startVPS = async (id) => {
      if (!actionLoading[id]) {
        actionLoading[id] = reactive({})
      }
      
      actionLoading[id].start = true
      
      try {
        await store.dispatch('vps/startVPS', id)
        await loadMyVPSList()
        ElMessage.success('VPS已启动')
      } catch (error) {
        console.error(`启动VPS ${id} 失败:`, error)
        ElMessage.error('启动VPS失败')
      } finally {
        actionLoading[id].start = false
      }
    }
    
    // 停止VPS
    const stopVPS = async (id) => {
      if (!actionLoading[id]) {
        actionLoading[id] = reactive({})
      }
      
      actionLoading[id].stop = true
      
      try {
        await store.dispatch('vps/stopVPS', id)
        await loadMyVPSList()
        ElMessage.success('VPS已停止')
      } catch (error) {
        console.error(`停止VPS ${id} 失败:`, error)
        ElMessage.error('停止VPS失败')
      } finally {
        actionLoading[id].stop = false
      }
    }
    
    // 加载统计数据
    const loadStatistics = async () => {
      try {
        // 通常会从API获取统计数据
        // 这里使用模拟数据
        stats.totalIPs = 254
        stats.allocatedIPs = 78
        stats.availableIPs = 176
        stats.totalUsers = 25
        stats.adminUsers = 3
        stats.regularUsers = 22
        stats.totalBackups = 120
        stats.autoBackups = 90
        stats.manualBackups = 30
      } catch (error) {
        console.error('加载统计数据失败:', error)
      }
    }
    
    onMounted(() => {
      loadMyVPSList()
      loadStatistics()
    })
    
    return {
      stats,
      myVPSList,
      loading,
      refreshing,
      actionLoading,
      isOperator,
      getStatusType,
      getStatusText,
      refreshVPSStatus,
      startVPS,
      stopVPS
    }
  }
}
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
}

.status-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-value {
  font-size: 36px;
  font-weight: bold;
  text-align: center;
  color: #303133;
  margin: 15px 0;
}

.card-detail {
  font-size: 14px;
  color: #606266;
}

.detail-label {
  display: inline-block;
  width: 70px;
}

.detail-value {
  font-weight: bold;
}

.detail-value.running,
.detail-value.available {
  color: #67c23a;
}

.detail-value.stopped,
.detail-value.used {
  color: #f56c6c;
}

.quick-actions-card,
.my-vps-card {
  margin-bottom: 20px;
}

.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.empty-data {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
}

.empty-data .el-button {
  margin-top: 20px;
}
</style> 