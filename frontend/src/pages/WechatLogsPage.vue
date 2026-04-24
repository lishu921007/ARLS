<template>
<div class="page page-stack">
  <div class="hero-card">
    <div>
      <div class="hero-eyebrow">微信发送日志</div>
      <h2 class="hero-title">发送记录与人工确认</h2>
      <div class="hero-subtitle">这里区分“预览”“真实发送”“人工确认”三层状态，避免出现看起来成功、其实没真的发出去的误解。</div>
    </div>
    <div class="hero-actions"><el-button @click="load">刷新</el-button></div>
  </div>
  <div class="card">
    <el-table :data="rows" stripe>
      <el-table-column prop="id" label="ID" width="70"/>
      <el-table-column prop="event_type" label="事件类型" width="100"/>
      <el-table-column prop="notice_no" label="通知书编号" width="160"/>
      <el-table-column prop="receiver_wechat_remark" label="接收人" width="120"/>
      <el-table-column prop="message_summary" label="消息摘要" min-width="280" show-overflow-tooltip/>
      <el-table-column label="程序状态" width="120">
        <template #default="scope"><span class="status-badge" :class="statusClass(scope.row.send_status)">{{ statusLabel(scope.row.send_status) }}</span></template>
      </el-table-column>
      <el-table-column prop="sent_at" label="真实发送时间" width="180"/>
      <el-table-column label="人工确认" width="110">
        <template #default="scope"><span class="status-badge" :class="scope.row.send_confirmed ? 's-normal' : 's-near'">{{ scope.row.send_confirmed ? '已确认' : '未确认' }}</span></template>
      </el-table-column>
      <el-table-column prop="confirmed_at" label="确认时间" width="180"/>
      <el-table-column prop="retry_count" label="重试次数" width="90"/>
      <el-table-column prop="final_send_result" label="执行结果" min-width="220" show-overflow-tooltip/>
      <el-table-column label="操作" width="120">
        <template #default="scope">
          <el-button v-if="scope.row.send_status === 'success' && !scope.row.send_confirmed" link type="primary" @click="confirmLog(scope.row)">确认已发送</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import http from '../api/http'
import { ElMessage } from 'element-plus'
const rows = ref([])
const load = async()=>{ const { data } = await http.get('/notify/logs'); rows.value = data }
const confirmLog = async(row)=>{ await http.post(`/notify/logs/${row.id}/confirm`); ElMessage.success('已确认并记录时间'); load() }
const statusLabel = (s)=> s === 'preview' ? '预览未发' : s === 'success' ? '发送成功' : '发送失败'
const statusClass = (s)=> s === 'preview' ? 's-near' : s === 'success' ? 's-normal' : 's-overdue'
onMounted(load)
</script>
