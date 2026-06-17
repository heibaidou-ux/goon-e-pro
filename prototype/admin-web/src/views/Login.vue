<template>
  <div class="login-wrapper">
    <div class="login-bg-decoration"></div>
    <div class="login-card">
      <div class="login-header">
        <div class="login-logo"><t-icon name="dashboard" size="36px" style="color:#5D8A6B" /></div>
        <h1>高岸ERP</h1>
        <p class="login-subtitle">盈隆店 · 智能管理系统</p>
      </div>

      <t-form :data="form" @submit="handleLogin" label-align="top">
        <t-form-item label="用户名">
          <t-input v-model="form.username" placeholder="请输入用户名" clearable>
            <template #prefix-icon><t-icon name="user" /></template>
          </t-input>
        </t-form-item>
        <t-form-item label="密码">
          <t-input v-model="form.password" type="password" placeholder="请输入密码">
            <template #prefix-icon><t-icon name="lock-on" /></template>
          </t-input>
        </t-form-item>
        <t-form-item>
          <t-button type="submit" theme="primary" block :loading="loading" size="large">登 录</t-button>
        </t-form-item>
      </t-form>

      <div v-if="errorMsg" class="login-error">{{ errorMsg }}</div>

      <div class="login-hint">
        <p class="hint-title">演示账号</p>
        <p>admin / admin123 （管理员）</p>
        <p>staff / staff123 （店员）</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '../services/api'

const router = useRouter()
const loading = ref(false)
const errorMsg = ref('')

const form = reactive({
  username: '',
  password: '',
})

async function handleLogin() {
  if (!form.username || !form.password) return
  loading.value = true
  errorMsg.value = ''

  try {
    const result = await authApi.login(form.username, form.password)
    if (result && result.access_token) {
      localStorage.setItem('erp_logged_in', 'true')
      localStorage.setItem('erp_user', result.user.display_name || form.username)
      localStorage.setItem('erp_user_role', result.user.role || 'admin')
      localStorage.setItem('erp_api_token', result.access_token)
      router.push('/dashboard')
    } else {
      errorMsg.value = '登录返回数据异常'
      loading.value = false
    }
  } catch (err: any) {
    errorMsg.value = err.message || '登录失败，请检查用户名密码或后端是否启动'
    loading.value = false
  }
}
</script>

<style scoped>
.login-wrapper {
  position: relative; height: 100vh; display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); overflow: hidden;
}
.login-bg-decoration {
  position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
  background: radial-gradient(circle at 30% 40%, rgba(93,138,107,0.08) 0%, transparent 50%),
              radial-gradient(circle at 70% 60%, rgba(0,168,112,0.06) 0%, transparent 50%);
  pointer-events: none;
}
.login-card {
  position: relative; width: 400px; background: rgba(255,255,255,0.97); border-radius: 16px;
  padding: 40px; box-shadow: 0 8px 40px rgba(0,0,0,0.2); z-index: 1;
}
.login-header { text-align: center; margin-bottom: 32px; }
.login-logo { margin-bottom: 12px; }
.login-header h1 {
  font-size: 28px; font-weight: 800;
  background: linear-gradient(135deg, #5D8A6B, #7BA88E);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
  letter-spacing: 2px; margin: 0;
}
.login-subtitle { font-size: 13px; color: #999; margin-top: 8px; }
.login-error { margin-top: 12px; text-align: center; font-size: 13px; color: #D54941; padding: 8px; background: #fff0f0; border-radius: 8px; }
.login-hint { margin-top: 20px; text-align: center; font-size: 12px; color: #bbb; line-height: 1.8; }
.hint-title { font-weight: 600; color: #888; margin-bottom: 4px; }
</style>
