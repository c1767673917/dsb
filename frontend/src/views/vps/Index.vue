<template>
  <div class="vps-list-container">
    <div class="page-header">
      <h1 class="page-title">VPS服务器管理</h1>
      <div class="header-actions">
        <el-button
          type="primary"
          icon="el-icon-plus"
          @click="$router.push('/vps/create')"
          v-if="isOperator"
        >
          创建新VPS
        </el-button>
        <el-button
          type="success"
          icon="el-icon-refresh"
          @click="refreshVPSList"
          :loading="refreshing"
        >
          刷新
        </el-button>
      </div>
    </div>
    
    <!-- 搜索过滤 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部" clearable>
            <el-option label="运行中" value="running" />
            <el-option label="已停止" value="stopped" />
            <el-option label="已挂起" value="suspended" />
            <el-option label="创建中" value="creating" />
            <el-option label="失败" value="failed" />
          </el-select>
        </el-form-item>
        <el-form-item label="系统模板">
          <el-select v-model="filterForm.osTemplate" placeholder="全部" clearable>
            <el-option v-for="template in osTemplates" :key="template" :label="template" :value="template" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="filterForm.keyword" placeholder="VPS名称/IP/备注" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleFilter">搜索</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- VPS列表 -->
    <el-card class="vps-table-card">
      <el-table
        :data="filteredVPSList"
        stripe
        style="width: 100%"
        v-loading="loading"
        @sort-change="handleSortChange"
      >
        <el-table-column prop="name" label="VPS名称" sortable="custom" min-width="150">
          <template #default="scope">
            <el-link
              type="primary"
              @click="$router.push(`/vps/${scope.row.id}`)"
            >
              {{ scope.row.name }}
            </el-link>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="120" sortable="custom">
          <template #default="scope">
            <el-tag
              :type="getStatusType(scope.row.status)"
              size="small"
            >
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="ip_address" label="IP地址" min-width="140" />
        
        <el-table-column prop="os_template" label="系统模板" min-width="140" sortable="custom" />
        
        <el-table-column label="资源配置" min-width="200">
          <template #default="scope">
            <div>
              <el-tooltip content="CPU核心数" placement="top">
                <span class="resource-item">
                  <i class="el-icon-cpu"></i> {{ scope.row.cpu_cores }} 核
                </span>
              </el-tooltip>
              
              <el-tooltip content="内存大小" placement="top">
                <span class="resource-item">
                  <i class="el-icon-coin"></i> {{ (scope.row.memory / 1024).toFixed(1) }} GB
                </span>
              </el-tooltip>
              
              <el-tooltip content="存储空间" placement="top">
                <span class="resource-item">
                  <i class="el-icon-folder"></i> {{ scope.row.disk_size }} GB
                </span>
              </el-tooltip>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="创建时间" min-width="180" sortable="custom">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" fixed="right" min-width="240">
          <template #default="scope">
            <el-button-group v-if="!actionLoading[scope.row.id]?.any">
              <el-button
                size="small"
                type="primary"
                @click="$router.push(`/vps/${scope.row.id}`)"
                icon="el-icon-view"
              >
                详情
              </el-button>
              
              <el-button
                size="small"
                type="success"
                v-if="scope.row.status !== 'running'"
                @click="startVPS(scope.row.id)"
                icon="el-icon-video-play"
              >
                启动
              </el-button>
              
              <el-button
                size="small"
                type="warning"
                v-if="scope.row.status === 'running'"
                @click="stopVPS(scope.row.id)"
                icon="el-icon-video-pause"
              >
                停止
              </el-button>
              
              <el-button
                size="small"
                type="info"
                v-if="scope.row.status === 'running'"
                @click="restartVPS(scope.row.id)"
                icon="el-icon-refresh"
              >
                重启
              </el-button>
              
              <el-button
                size="small"
                type="danger"
                @click="showDeleteConfirm(scope.row)"
                icon="el-icon-delete"
                v-if="isOperator"
              >
                删除
              </el-button>
            </el-button-group>
            
            <el-button
              v-else
              size="small"
              loading
            >
              操作中...
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          background
          layout="total, sizes, prev, pager, next, jumper"
          :total="totalVPS"
          :page-size="pageSize"
          :current-page="currentPage"
          :page-sizes="[10, 20, 50, 100]"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- 删除确认对话框 -->
    <el-dialog
      title="确认删除"
      v-model="deleteDialogVisible"
      width="30%"
    >
      <span>
        您确定要删除VPS <strong>{{ vpsToDelete?.name }}</strong> 吗？此操作将永久删除该VPS服务器及其所有数据，且不可恢复。
      </span>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="deleteDialogVisible = false">取消</el-button>
          <el-button type="danger" @click="confirmDelete" :loading="deleting">确认删除</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useStore } from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'
import { format } from 'date-fns'

export default {
  name: 'VPSList',
  
  setup() {
    const store = useStore()
    const loading = ref(false)
    const refreshing = ref(false)
    const actionLoading = reactive({})
    const vpsList = ref([])
    const osTemplates = ref([])
    
    // 分页相关
    const currentPage = ref(1)
    const pageSize = ref(10)
    const totalVPS = ref(0)
    
    // 排序
    const sortBy = ref('created_at')
    const sortOrder = ref('descending')
    
    // 过滤表单
    const filterForm = reactive({
      status: '',
      osTemplate: '',
      keyword: ''
    })
    
    // 删除相关
    const deleteDialogVisible = ref(false)
    const vpsToDelete = ref(null)
    const deleting = ref(false)
    
    // 计算属性：过滤后的VPS列表
    const filteredVPSList = computed(() => {
      return vpsList.value.filter(vps => {
        // 状态过滤
        if (filterForm.status && vps.status !== filterForm.status) {
          return false
        }
        
        // 系统模板过滤
        if (filterForm.osTemplate && vps.os_template !== filterForm.osTemplate) {
          return false
        }
        
        // 关键词过滤
        if (filterForm.keyword) {
          const keyword = filterForm.keyword.toLowerCase()
          return vps.name.toLowerCase().includes(keyword) ||
                 (vps.ip_address && vps.ip_address.toLowerCase().includes(keyword)) ||
                 (vps.notes && vps.notes.toLowerCase().includes(keyword))
        }
        
        return true
      })
    })
    
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
    
    // 格式化日期
    const formatDate = (dateString) => {
      try {
        return format(new Date(dateString), 'yyyy-MM-dd HH:mm:ss')
      } catch (error) {
        return dateString
      }
    }
    
    // 加载VPS列表
    const loadVPSList = async () => {
      loading.value = true
      
      try {
        const response = await store.dispatch('vps/getVPSList')
        vpsList.value = response.data
        totalVPS.value = vpsList.value.length
        
        // 提取所有操作系统模板
        const templates = new Set()
        vpsList.value.forEach(vps => {
          if (vps.os_template) {
            templates.add(vps.os_template)
          }
        })
        osTemplates.value = Array.from(templates)
      } catch (error) {
        console.error('加载VPS列表失败:', error)
        ElMessage.error('加载VPS列表失败')
      } finally {
        loading.value = false
      }
    }
    
    // 刷新VPS列表
    const refreshVPSList = async () => {
      refreshing.value = true
      
      try {
        await loadVPSList()
        ElMessage.success('VPS列表已刷新')
      } catch (error) {
        console.error('刷新VPS列表失败:', error)
      } finally {
        refreshing.value = false
      }
    }
    
    // 处理过滤
    const handleFilter = () => {
      currentPage.value = 1
    }
    
    // 重置过滤
    const resetFilter = () => {
      Object.keys(filterForm).forEach(key => {
        filterForm[key] = ''
      })
      currentPage.value = 1
    }
    
    // 更改每页显示数量
    const handleSizeChange = (val) => {
      pageSize.value = val
      currentPage.value = 1
    }
    
    // 更改当前页
    const handleCurrentChange = (val) => {
      currentPage.value = val
    }
    
    // 处理排序变化
    const handleSortChange = (sortParams) => {
      if (sortParams.prop) {
        sortBy.value = sortParams.prop
        sortOrder.value = sortParams.order
      } else {
        sortBy.value = 'created_at'
        sortOrder.value = 'descending'
      }
    }
    
    // 启动VPS
    const startVPS = async (id) => {
      if (!actionLoading[id]) {
        actionLoading[id] = reactive({})
      }
      
      actionLoading[id].any = true
      
      try {
        await store.dispatch('vps/startVPS', id)
        await refreshVPSList()
        ElMessage.success('VPS已启动')
      } catch (error) {
        console.error(`启动VPS ${id} 失败:`, error)
        ElMessage.error('启动VPS失败')
      } finally {
        actionLoading[id].any = false
      }
    }
    
    // 停止VPS
    const stopVPS = async (id) => {
      if (!actionLoading[id]) {
        actionLoading[id] = reactive({})
      }
      
      actionLoading[id].any = true
      
      try {
        await store.dispatch('vps/stopVPS', id)
        await refreshVPSList()
        ElMessage.success('VPS已停止')
      } catch (error) {
        console.error(`停止VPS ${id} 失败:`, error)
        ElMessage.error('停止VPS失败')
      } finally {
        actionLoading[id].any = false
      }
    }
    
    // 重启VPS
    const restartVPS = async (id) => {
      if (!actionLoading[id]) {
        actionLoading[id] = reactive({})
      }
      
      actionLoading[id].any = true
      
      try {
        await store.dispatch('vps/restartVPS', id)
        await refreshVPSList()
        ElMessage.success('VPS已重启')
      } catch (error) {
        console.error(`重启VPS ${id} 失败:`, error)
        ElMessage.error('重启VPS失败')
      } finally {
        actionLoading[id].any = false
      }
    }
    
    // 显示删除确认
    const showDeleteConfirm = (vps) => {
      vpsToDelete.value = vps
      deleteDialogVisible.value = true
    }
    
    // 确认删除
    const confirmDelete = async () => {
      if (!vpsToDelete.value) return
      
      deleting.value = true
      
      try {
        await store.dispatch('vps/deleteVPS', vpsToDelete.value.id)
        deleteDialogVisible.value = false
        await refreshVPSList()
        ElMessage.success('VPS已删除')
      } catch (error) {
        console.error('删除VPS失败:', error)
        ElMessage.error('删除VPS失败')
      } finally {
        deleting.value = false
      }
    }
    
    onMounted(() => {
      loadVPSList()
    })
    
    return {
      vpsList,
      filteredVPSList,
      loading,
      refreshing,
      actionLoading,
      osTemplates,
      currentPage,
      pageSize,
      totalVPS,
      filterForm,
      deleteDialogVisible,
      vpsToDelete,
      deleting,
      isOperator,
      getStatusType,
      getStatusText,
      formatDate,
      refreshVPSList,
      handleFilter,
      resetFilter,
      handleSizeChange,
      handleCurrentChange,
      handleSortChange,
      startVPS,
      stopVPS,
      restartVPS,
      showDeleteConfirm,
      confirmDelete
    }
  }
}
</script>

<style scoped>
.vps-list-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.filter-card {
  margin-bottom: 20px;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
}

.vps-table-card {
  margin-bottom: 20px;
}

.resource-item {
  margin-right: 15px;
  display: inline-flex;
  align-items: center;
}

.resource-item i {
  margin-right: 5px;
}

.pagination-container {
  text-align: right;
  margin-top: 20px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
}
</style> 