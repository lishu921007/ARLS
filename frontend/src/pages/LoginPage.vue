<template>
  <div class="login-wrap">
    <div class="card login-card">
      <h2 class="section-title">登录系统</h2>
      <el-form @submit.prevent="submit" :model="form" label-position="top">
        <el-form-item label="用户名"><el-input v-model="form.username" /></el-form-item>
        <el-form-item label="密码"><el-input type="password" show-password v-model="form.password" /></el-form-item>
        <el-button type="primary" @click="submit" style="width:100%">登录</el-button>
        <p style="color:#7b8895">默认账号：admin / admin123</p>
      </el-form>
    </div>
  </div>
</template>
<script setup>
import { reactive } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../api/http'
import { useRouter } from 'vue-router'
const router = useRouter()
const form = reactive({ username: 'admin', password: 'admin123' })
const submit = async () => {
  try { const { data } = await http.post('/auth/login', form); localStorage.setItem('token', data.token); localStorage.setItem('username', data.username); router.push('/') }
  catch (e) { ElMessage.error(e.response?.data?.detail || '登录失败') }
}
</script>
