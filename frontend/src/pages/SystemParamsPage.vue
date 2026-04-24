<template>
  <div class="page page-stack">
    <div class="hero-card">
      <div>
        <div class="hero-eyebrow">系统参数</div>
        <h2 class="hero-title">参数中心与审计日志</h2>
        <div class="hero-subtitle">把英文参数键翻成中文，常用参数直接卡片化编辑，避免记键名、手工输错、不知道参数是什么意思。</div>
      </div>
      <div class="hero-actions">
        <el-button type="primary" @click="saveAll">保存已修改参数</el-button>
        <el-button @click="load">刷新</el-button>
      </div>
    </div>

    <div class="panel-grid">
      <div v-for="item in visibleConfigs" :key="item.key" class="card card-soft">
        <div class="toolbar-between">
          <div>
            <h3 class="section-title" style="margin-bottom:0">{{ item.label }}</h3>
            <div class="section-subtitle">{{ item.description }}</div>
          </div>
          <span class="status-badge s-normal">{{ item.key }}</span>
        </div>
        <div style="height:14px"></div>
        <el-form label-position="top">
          <el-form-item label="当前值">
            <el-switch v-if="item.type === 'bool'" v-model="form[item.key]" />
            <el-input-number v-else-if="item.type === 'int'" v-model="form[item.key]" :min="item.min ?? 0" :step="item.step ?? 1" style="width:100%" />
            <el-input v-else v-model="form[item.key]" />
          </el-form-item>
          <div class="muted">默认/建议：{{ item.recommendation }}</div>
        </el-form>
      </div>
    </div>

    <div class="card">
      <div class="toolbar-between">
        <div>
          <h3 class="section-title" style="margin-bottom:0">全部系统参数</h3>
          <div class="section-subtitle">保留完整表格，便于排查、核对和后续扩展。</div>
        </div>
        <el-button @click="dialogVisible = true">新增参数</el-button>
      </div>
      <div style="height:12px"></div>
      <el-table :data="tableRows" stripe>
        <el-table-column prop="label" label="中文名称" width="180"/>
        <el-table-column prop="param_key" label="参数键" width="240"/>
        <el-table-column prop="param_value" label="当前值" width="160"/>
        <el-table-column prop="description" label="说明" min-width="300"/>
        <el-table-column prop="remark" label="备注" min-width="180"/>
        <el-table-column label="操作" width="140">
          <template #default="scope"><el-button link @click="openEdit(scope.row)">编辑</el-button></template>
        </el-table-column>
      </el-table>
    </div>

    <div class="card">
      <h3 class="section-title">审计日志</h3>
      <el-table :data="logs" stripe>
        <el-table-column prop="username" label="操作人" width="100"/>
        <el-table-column prop="action" label="动作" width="180"/>
        <el-table-column prop="target_type" label="对象类型" width="120"/>
        <el-table-column prop="target_id" label="对象ID" width="90"/>
        <el-table-column prop="detail" label="详情" min-width="260"/>
        <el-table-column prop="created_at" label="时间" width="180"/>
      </el-table>
    </div>

    <el-dialog v-model="dialogVisible" title="新增 / 修改系统参数" width="560px">
      <el-form :model="editForm" label-width="120px">
        <el-form-item label="参数键"><el-input v-model="editForm.param_key" /></el-form-item>
        <el-form-item label="参数值"><el-input v-model="editForm.param_value" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="editForm.remark" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible=false">取消</el-button>
        <el-button type="primary" @click="submitEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, reactive, ref, onMounted } from 'vue'
import http from '../api/http'
import { ElMessage } from 'element-plus'

const rows = ref([])
const logs = ref([])
const dialogVisible = ref(false)
const form = reactive({})
const editForm = reactive({ param_key:'', param_value:'', remark:'' })

const PARAM_META = {
  near_threshold: { label:'临期阈值', description:'剩余工作日小于等于该值时标记为“临期”。', type:'int', recommendation:'3', min:0 },
  urgent_threshold: { label:'紧急阈值', description:'剩余工作日小于等于该值时标记为“紧急”。', type:'int', recommendation:'1', min:0 },
  deadline_workdays: { label:'答复工作日时限', description:'签收日起按工作日顺延计算最晚答复日。', type:'int', recommendation:'10', min:1 },
  auto_notify_enabled: { label:'自动发送开关', description:'开启后，定时扫描时会自动把风险事项推入微信发送队列。', type:'bool', recommendation:'按需开启' },
  preview_only_mode: { label:'预览模式', description:'开启后只写入发送日志和队列，不真正向微信按回车发送。测试阶段建议开启。', type:'bool', recommendation:'建议测试时开启，验收时关闭' },
  max_retry: { label:'失败重试次数', description:'微信发送失败后的自动重试上限。', type:'int', recommendation:'3', min:0 },
  throttle_seconds: { label:'单次发送节流秒数', description:'相邻两次真实发送之间等待秒数，避免过快触发微信问题。', type:'int', recommendation:'4', min:0 },
  auto_scan_minutes: { label:'风险扫描间隔（分钟）', description:'系统自动扫描临期/紧急/超期事项并入队的周期。', type:'int', recommendation:'120', min:1 },
  queue_process_interval_seconds: { label:'队列处理间隔（秒）', description:'系统自动检查并处理一条待发送任务的周期。', type:'int', recommendation:'120', min:1 },
  wechat_window_name: { label:'微信窗口标题', description:'用于定位 Windows 微信主窗口，默认一般为“微信”。', type:'text', recommendation:'微信' },
}

const visibleConfigs = computed(() => Object.entries(PARAM_META).map(([key, meta]) => ({ key, ...meta })))
const tableRows = computed(() => rows.value.map(row => ({ ...row, label: PARAM_META[row.param_key]?.label || row.param_key, description: PARAM_META[row.param_key]?.description || '自定义参数' })))

const normalizeValue = (key, value) => {
  const meta = PARAM_META[key]
  if (!meta) return value ?? ''
  if (meta.type === 'bool') return String(value).toLowerCase() === 'true'
  if (meta.type === 'int') return Number(value)
  return value ?? ''
}
const serializeValue = (key, value) => {
  const meta = PARAM_META[key]
  if (!meta) return String(value ?? '')
  if (meta.type === 'bool') return value ? 'true' : 'false'
  return String(value ?? '')
}

const load = async()=>{
  rows.value = (await http.get('/config/params')).data
  logs.value = (await http.get('/system/audit-logs')).data
  Object.keys(form).forEach(k => delete form[k])
  for (const row of rows.value) form[row.param_key] = normalizeValue(row.param_key, row.param_value)
}
const saveAll = async()=>{
  for (const row of rows.value) {
    await http.post('/config/params', { param_key: row.param_key, param_value: serializeValue(row.param_key, form[row.param_key]), remark: row.remark || '' })
  }
  ElMessage.success('系统参数已保存；新的定时周期在服务重启后生效')
  load()
}
const openEdit = (row)=>{
  editForm.param_key = row.param_key
  editForm.param_value = row.param_value
  editForm.remark = row.remark || ''
  dialogVisible.value = true
}
const submitEdit = async()=>{
  await http.post('/config/params', editForm)
  ElMessage.success('保存成功')
  dialogVisible.value = false
  load()
}

onMounted(load)
</script>
