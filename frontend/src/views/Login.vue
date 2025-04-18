<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h2>PVE VPS 管理系统</h2>
        <p>欢迎登录</p>
      </div>
      
      <el-form ref="loginForm" :model="loginForm" :rules="loginRules" class="login-form">
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="用户名"
            prefix-icon="el-icon-user"
            type="text"
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            placeholder="密码"
            prefix-icon="el-icon-lock"
            :type="passwordVisible ? 'text' : 'password'"
            @keyup.enter="handleLogin"
          >
            <template #suffix>
              <el-icon
                :class="passwordVisible ? 'el-icon-view' : 'el-icon-hide'"
                @click="passwordVisible = !passwordVisible"
              />
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button
            :loading="loading"
            type="primary"
            class="login-button"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="register-link">
        <a href="javascript:;" @click="showRegisterDialog = true">还没有账号？立即注册</a>
      </div>
    </div>
    
    <!-- 注册对话框 -->
    <el-dialog title="注册新账户" v-model="showRegisterDialog" width="400px">
      <el-form
        ref="registerForm"
        :model="registerForm"
        :rules="registerRules"
        label-position="top"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="registerForm.username" placeholder="请输入用户名" />
        </el-form-item>
        
        <el-form-item label="电子邮箱" prop="email">
          <el-input v-model="registerForm.email" placeholder="请输入电子邮箱" />
        </el-form-item>
        
        <el-form-item label="姓" prop="last_name">
          <el-input v-model="registerForm.last_name" placeholder="请输入姓" />
        </el-form-item>
        
        <el-form-item label="名" prop="first_name">
          <el-input v-model="registerForm.first_name" placeholder="请输入名" />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="registerForm.password"
            placeholder="请输入密码"
            :type="registerPasswordVisible ? 'text' : 'password'"
          >
            <template #suffix>
              <el-icon
                :class="registerPasswordVisible ? 'el-icon-view' : 'el-icon-hide'"
                @click="registerPasswordVisible = !registerPasswordVisible"
              />
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            placeholder="请再次输入密码"
            :type="registerConfirmPasswordVisible ? 'text' : 'password'"
          >
            <template #suffix>
              <el-icon
                :class="registerConfirmPasswordVisible ? 'el-icon-view' : 'el-icon-hide'"
                @click="registerConfirmPasswordVisible = !registerConfirmPasswordVisible"
              />
            </template>
          </el-input>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showRegisterDialog = false">取消</el-button>
          <el-button type="primary" :loading="registerLoading" @click="handleRegister">注册</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { reactive, ref } from 'vue'
import { useStore } from 'vuex'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

export default {
  name: 'Login',
  
  setup() {
    const store = useStore()
    const route = useRoute()
    const router = useRouter()
    
    // 登录表单相关
    const loginForm = reactive({
      username: '',
      password: ''
    })
    
    const passwordVisible = ref(false)
    const loading = ref(false)
    const loginFormRef = ref(null)
    
    const loginRules = reactive({
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, message: '密码长度不能少于6个字符', trigger: 'blur' }
      ]
    })
    
    const handleLogin = async () => {
      if (!loginFormRef.value) return
      
      await loginFormRef.value.validate(async (valid) => {
        if (!valid) return
        
        loading.value = true
        
        try {
          await store.dispatch('auth/login', loginForm)
          
          // 登录成功，跳转到首页或重定向页面
          const redirectPath = route.query.redirect || '/'
          router.push(redirectPath)
          
          ElMessage.success('登录成功')
        } catch (error) {
          console.error('登录失败:', error)
        } finally {
          loading.value = false
        }
      })
    }
    
    // 注册表单相关
    const showRegisterDialog = ref(false)
    const registerPasswordVisible = ref(false)
    const registerConfirmPasswordVisible = ref(false)
    const registerLoading = ref(false)
    const registerFormRef = ref(null)
    
    const registerForm = reactive({
      username: '',
      email: '',
      first_name: '',
      last_name: '',
      password: '',
      confirmPassword: '',
      role: 'user'
    })
    
    const validateConfirmPassword = (rule, value, callback) => {
      if (value !== registerForm.password) {
        callback(new Error('两次输入的密码不一致'))
      } else {
        callback()
      }
    }
    
    const registerRules = reactive({
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 3, message: '用户名长度不能少于3个字符', trigger: 'blur' }
      ],
      email: [
        { required: true, message: '请输入电子邮箱', trigger: 'blur' },
        { type: 'email', message: '请输入正确的电子邮箱格式', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, message: '密码长度不能少于6个字符', trigger: 'blur' }
      ],
      confirmPassword: [
        { required: true, message: '请再次输入密码', trigger: 'blur' },
        { validator: validateConfirmPassword, trigger: 'blur' }
      ]
    })
    
    const handleRegister = async () => {
      if (!registerFormRef.value) return
      
      await registerFormRef.value.validate(async (valid) => {
        if (!valid) return
        
        registerLoading.value = true
        
        try {
          // 移除确认密码字段
          const { confirmPassword, ...registrationData } = registerForm
          
          await store.dispatch('auth/register', registrationData)
          
          ElMessage.success('注册成功，请登录')
          showRegisterDialog.value = false
          
          // 自动填充登录表单
          loginForm.username = registerForm.username
          loginForm.password = ''
          
          // 重置注册表单
          registerForm.username = ''
          registerForm.email = ''
          registerForm.first_name = ''
          registerForm.last_name = ''
          registerForm.password = ''
          registerForm.confirmPassword = ''
        } catch (error) {
          console.error('注册失败:', error)
        } finally {
          registerLoading.value = false
        }
      })
    }
    
    return {
      // 登录相关
      loginForm,
      loginRules,
      loginFormRef,
      passwordVisible,
      loading,
      handleLogin,
      
      // 注册相关
      showRegisterDialog,
      registerForm,
      registerRules,
      registerFormRef,
      registerPasswordVisible,
      registerConfirmPasswordVisible,
      registerLoading,
      handleRegister
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f0f2f5;
  background-image: url('@/assets/login-bg.jpg');
  background-size: cover;
  background-position: center;
}

.login-card {
  width: 350px;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  background-color: rgba(255, 255, 255, 0.95);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h2 {
  margin: 0;
  font-size: 24px;
  color: #333;
}

.login-header p {
  margin-top: 10px;
  color: #666;
}

.login-form {
  margin-bottom: 20px;
}

.login-button {
  width: 100%;
}

.register-link {
  text-align: center;
  margin-top: 15px;
  font-size: 14px;
}

.register-link a {
  color: #409eff;
  text-decoration: none;
}

.register-link a:hover {
  text-decoration: underline;
}
</style> 