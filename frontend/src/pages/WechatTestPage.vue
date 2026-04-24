<template>
  <div class="page page-stack">
    <div class="hero-card">
      <div>
        <div class="hero-eyebrow">微信自动发送</div>
        <h2 class="hero-title">自动发送状态、测试与队列</h2>
        <div class="hero-subtitle">这里不只是单条测试，还能看自动发送开关、预览模式、失败任务和待发送队列，方便你做完整验收。</div>
      </div>
      <div class="hero-actions">
        <el-button type="primary" @click="submit">发送测试</el-button>
        <el-button @click="processOnce">立即处理一条队列</el-button>
        <el-button @click="load">刷新状态</el-button>
      </div>
    </div>

    <div class="kpi-grid" style="grid-template-columns:repeat(4,minmax(0,1fr))">
      <div class="kpi-card kpi-green"><div class="label">自动发送</div><div class="value" style="font-size:22px">{{ status.runtime?.auto_notify_enabled ? '已开启' : '已关闭' }}</div><div class="hint">定时扫描是否自动入队</div></div>
      <div class="kpi-card kpi-warn"><div class="label">预览模式</div><div class="value" style="font-size:22px">{{ status.runtime?.preview_only_mode ? '开启' : '关闭' }}</div><div class="hint">开启时不真实发送</div></div>
      <div class="kpi-card kpi-mist"><div class="label">待发送队列</div><div class="value">{{ status.pending_count || 0 }}</div><div class="hint">状态为 pending</div></div>
      <div class="kpi-card kpi-danger"><div class="label">失败任务</div><div class="value">{{ status.failed_count || 0 }}</div><div class="hint">建议逐条排查并重试</div></div>
    </div>

    <div class="queue-grid">
      <div class="card">
        <h3 class="section-title">发送测试</h3>
        <el-alert v-if="status.host_os && status.host_os !== 'Windows'" :title="`当前服务运行在 ${status.host_os} 环境，微信桌面自动化仅支持 Windows 客户端，因此真实发送会失败。`" type="error" :closable="false" style="margin-bottom:16px" />
        <el-alert v-else-if="status.runtime?.preview_only_mode" title="当前系统处于预览模式：会写入队列和日志，但不会真实发送到微信。要做真实测试，请先到系统参数里关闭预览模式。" type="warning" :closable="false" style="margin-bottom:16px" />
        <el-form :model="form" label-width="120px">
          <el-form-item label="接收人姓名"><el-input v-model="form.receiver_name" /></el-form-item>
          <el-form-item label="微信备注名"><el-input v-model="form.receiver_wechat_remark" /></el-form-item>
          <el-form-item label="消息内容"><el-input type="textarea" rows="5" v-model="form.message_content" /></el-form-item>
          <el-form-item label="仅预览"><el-switch v-model="form.preview_only" /></el-form-item>
        </el-form>
      </div>
      <div class="card">
        <h3 class="section-title">当前运行说明</h3>
        <div class="list-clean">
          <div class="list-item"><div><strong>运行环境</strong><span>当前服务实际运行所在系统</span></div><em style="font-size:16px">{{ status.host_os || '-' }}</em></div>
          <div class="list-item"><div><strong>微信窗口标题</strong><span>用于定位 Windows 微信主窗口</span></div><em style="font-size:16px">{{ status.runtime?.wechat_window_name || '微信' }}</em></div>
          <div class="list-item"><div><strong>失败重试次数</strong><span>任务失败后的自动重试上限</span></div><em>{{ status.runtime?.max_retry ?? '-' }}</em></div>
          <div class="list-item"><div><strong>发送节流秒数</strong><span>相邻两次发送之间等待时间</span></div><em>{{ status.runtime?.throttle_seconds ?? '-' }}</em></div>
        </div>
        <div style="height:12px"></div>
        <div class="info-block">
          <h4>测试建议</h4>
          <p>如果当前运行环境不是 Windows，那么真实发送不会成功；此时只能做预览联调，或者把服务部署到 Windows 本机再测真实发送。</p>
        </div>
      </div>
    </div>

    <div class="card">
      <h3 class="section-title">发送队列</h3>
      <el-table :data="queueRows" stripe>
        <el-table-column prop="id" label="ID" width="70"/>
        <el-table-column prop="event_type" label="事件类型" width="100"/>
        <el-table-column prop="target_wechat_remark" label="目标备注名" width="140"/>
        <el-table-column prop="status" label="状态" width="110"/>
        <el-table-column prop="retry_count" label="重试" width="80"/>
        <el-table-column prop="message_content" label="消息内容" min-width="300" show-overflow-tooltip/>
        <el-table-column prop="error_message" label="错误信息" min-width="260" show-overflow-tooltip/>
        <el-table-column label="操作" width="160">
          <template #default="scope">
            <el-button link @click="retry(scope.row)" v-if="scope.row.status === 'failed' || scope.row.status === 'cancelled'">重试</el-button>
            <el-button link type="danger" @click="cancel(scope.row)" v-if="scope.row.status === 'pending'">取消</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import http from '../api/http'
import { ElMessage } from 'element-plus'

const form = reactive({ receiver_name:'张三', receiver_wechat_remark:'张三', message_content:'您好，这是一条测试消息。收到后可忽略。', preview_only:true })
const status = ref({ runtime:{} })
const queueRows = ref([])
const load = async()=>{
  status.value = (await http.get('/notify/status')).data
  queueRows.value = (await http.get('/notify/queue')).data
  form.preview_only = status.value.runtime?.preview_only_mode ?? true
}
const submit = async()=>{ try { await http.post('/notify/test', form); ElMessage.success('已进入发送队列'); load() } catch (e) { ElMessage.error(e?.response?.data?.detail || '测试任务创建失败') } }
const processOnce = async()=>{ await http.post('/notify/queue/process-once'); ElMessage.success('已触发处理一条队列'); load() }
const retry = async(row)=>{ await http.post(`/notify/queue/${row.id}/retry`); ElMessage.success('已重置为待发送'); load() }
const cancel = async(row)=>{ await http.post(`/notify/queue/${row.id}/cancel`); ElMessage.success('已取消'); load() }

onMounted(load)
</script>
