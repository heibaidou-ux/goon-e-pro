<template>
  <div class="login-wrapper">
    <div class="login-bg-decoration"></div>
    <div class="login-card">
      <div class="login-header">
        <div class="login-logo">
          <t-icon name="dashboard" size="36px" style="color:#0052D9" />
        </div>
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

      <div class="login-hint">
        <p class="hint-title">演示账号（密码任意）</p>
        <p>赵总（总部总经理）/ 钱副总（副总经理）</p>
        <p>张店长（店长）/ 李财务（财务）/ 王运营（总部运营）</p>
        <p>admin（系统管理员）/ 小林（店员）</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
})

function handleLogin() {
  if (!form.username || !form.password) return
  loading.value = true
  setTimeout(() => {
    loading.value = false
    localStorage.setItem('erp_logged_in', 'true')
    localStorage.setItem('erp_user', form.username)
    router.push('/dashboard')
  }, 600)
}
</script>

<style scoped>
.login-wrapper {
  position: relative;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  overflow: hidden;
}

.login-bg-decoration {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle at 30% 40%, rgba(0, 82, 217, 0.08) 0%, transparent 50%),
              radial-gradient(circle at 70% 60%, rgba(0, 168, 112, 0.06) 0%, transparent 50%);
  pointer-events: none;
}

.login-card {
  position: relative;
  width: 400px;
  background: rgba(255, 255, 255, 0.97);
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.2);
  z-index: 1;
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-logo {
  margin-bottom: 12px;
}

.login-header h1 {
  font-size: 28px;
  font-weight: 800;
  background: linear-gradient(135deg, #0052D9, #00A870);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 2px;
  margin: 0;
}

.login-subtitle {
  font-size: 13px;
  color: #999;
  margin-top: 8px;
}

.login-hint {
  margin-top: 20px;
  text-align: center;
  font-size: 12px;
  color: #bbb;
  line-height: 1.8;
}

.hint-title {
  font-weight: 600;
  color: #888;
  margin-bottom: 4px;
}
</style>
