<template>
  <div class="page analytics-page">
    <div class="hero-card">
      <div>
        <div class="hero-eyebrow">统计分析</div>
        <h2 class="hero-title">行政复议答复事项全局概览</h2>
        <div class="hero-subtitle">默认展示全部有效事项；可按部门、类型、状态、预警与签收时间范围筛选。</div>
      </div>
      <div class="hero-actions">
        <el-button type="primary" @click="load">更新统计</el-button>
        <el-button @click="reset">重置筛选</el-button>
      </div>
    </div>

    <div class="card analytics-filter-card">
      <div class="filter-grid">
        <el-select v-model="filters.handling_department" placeholder="经办部门" clearable>
          <el-option v-for="x in dicts.department" :key="x.value" :label="x.label" :value="x.value" />
        </el-select>
        <el-select v-model="filters.case_type" placeholder="类型" clearable>
          <el-option v-for="x in dicts.case_type" :key="x.value" :label="x.label" :value="x.value" />
        </el-select>
        <el-select v-model="filters.current_status" placeholder="当前状态" clearable>
          <el-option v-for="x in dicts.current_status" :key="x.value" :label="x.label" :value="x.value" />
        </el-select>
        <el-select v-model="filters.warning_status" placeholder="预警状态" clearable>
          <el-option v-for="x in ['正常','临期','紧急','超期']" :key="x" :label="x" :value="x" />
        </el-select>
        <el-date-picker v-model="receivedRange" type="daterange" value-format="YYYY-MM-DD" start-placeholder="签收开始" end-placeholder="签收结束" />
      </div>
    </div>

    <div class="kpi-row">
      <div class="kpi-analytics kpi-neutral">
        <div class="kpi-label">总件数</div><div class="kpi-value">{{ stats.total || 0 }}</div>
      </div>
      <div class="kpi-analytics kpi-mist">
        <div class="kpi-label">本季度件数</div><div class="kpi-value">{{ stats.quarter_count || 0 }}</div>
      </div>
      <div class="kpi-analytics kpi-warn">
        <div class="kpi-label">临期件数</div><div class="kpi-value">{{ stats.near_count || 0 }}</div>
      </div>
      <div class="kpi-analytics kpi-urgent">
        <div class="kpi-label">紧急件数</div><div class="kpi-value">{{ stats.urgent_count || 0 }}</div>
      </div>
      <div class="kpi-analytics kpi-danger">
        <div class="kpi-label">超期件数</div><div class="kpi-value">{{ stats.overdue_count || 0 }}</div>
      </div>
      <div class="kpi-analytics kpi-green">
        <div class="kpi-label">已闭环件数</div><div class="kpi-value">{{ stats.closed_count || 0 }}</div>
      </div>
    </div>

    <div class="chart-grid">
      <div class="card chart-card">
        <div class="chart-header"><span>季度分布</span><span class="chart-hint">点击柱子可下钻</span></div>
        <div ref="quarterChart" class="chart-box"></div>
      </div>
      <div class="card chart-card">
        <div class="chart-header"><span>类型分布</span><span class="chart-hint">点击扇区可下钻</span></div>
        <div ref="typeChart" class="chart-box"></div>
      </div>
      <div class="card chart-card">
        <div class="chart-header"><span>经办部门分布</span><span class="chart-hint">点击柱子可下钻</span></div>
        <div ref="deptChart" class="chart-box"></div>
      </div>
      <div class="card chart-card">
        <div class="chart-header"><span>预警状态分布</span><span class="chart-hint">点击扇区可下钻</span></div>
        <div ref="warningChart" class="chart-box"></div>
      </div>
    </div>

    <div class="card detail-card">
      <div class="detail-header">
        <div>
          <div class="detail-title">统计明细</div>
          <div class="detail-subtitle">{{ drillTitle ? `当前下钻：${drillTitle}` : '未选择图表维度时，默认展示当前筛选条件下的最近事项。' }}</div>
        </div>
        <el-button v-if="drillTitle" @click="clearDrill">清除下钻</el-button>
      </div>
      <el-table :data="drillRows" stripe>
        <el-table-column prop="seq_no" label="序号" width="70"/>
        <el-table-column prop="notice_no" label="通知书编号" width="180"/>
        <el-table-column prop="applicant" label="申请人" width="120"/>
        <el-table-column prop="handling_department" label="经办部门" width="120"/>
        <el-table-column prop="case_type" label="类型" width="100"/>
        <el-table-column prop="current_status" label="当前状态" width="110"/>
        <el-table-column prop="warning_status" label="预警状态" width="100"/>
        <el-table-column prop="received_date" label="签收日期" width="110"/>
        <el-table-column prop="deadline_date" label="最晚答复日" width="110"/>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, reactive, nextTick } from 'vue'
import * as echarts from 'echarts'
import http from '../api/http'

const stats = ref({})
const quarterChart = ref()
const typeChart = ref()
const deptChart = ref()
const warningChart = ref()
const chartInstances = reactive({ quarter: null, type: null, dept: null, warning: null })
const dicts = reactive({ department: [], case_type: [], current_status: [] })
const filters = reactive({ handling_department:'', case_type:'', current_status:'', warning_status:'' })
const receivedRange = ref([])
const drillRows = ref([])
const drillTitle = ref('')

const queryParams = () => ({
  ...filters,
  received_start: receivedRange.value?.[0],
  received_end: receivedRange.value?.[1],
})

const loadDict = async(type) => (await http.get(`/config/dictionary/${type}`)).data
const initDicts = async()=>{
  const [department, caseType, currentStatus] = await Promise.all([
    loadDict('department'),
    loadDict('case_type'),
    loadDict('current_status'),
  ])
  dicts.department = department
  dicts.case_type = caseType
  dicts.current_status = currentStatus
}

const ensureChart = (key, dom) => {
  if (!chartInstances[key]) chartInstances[key] = echarts.init(dom)
  return chartInstances[key]
}

const buildBarOption = (title, rows, color) => ({
  color: [color],
  grid: { left: 36, right: 16, top: 24, bottom: 28 },
  tooltip: { trigger: 'axis' },
  xAxis: {
    type: 'category',
    data: rows.map(x => x.name),
    axisLine: { lineStyle: { color: '#d8e1e6' } },
    axisLabel: { color: '#607080' }
  },
  yAxis: {
    type: 'value',
    splitLine: { lineStyle: { color: '#edf2f5' } },
    axisLabel: { color: '#607080' }
  },
  series: [{
    type: 'bar',
    barWidth: 28,
    borderRadius: [8,8,0,0],
    data: rows.map(x => x.value)
  }]
})

const buildPieOption = (rows, colors) => ({
  color: colors,
  tooltip: { trigger: 'item' },
  legend: { bottom: 0, textStyle: { color: '#607080' } },
  series: [{
    type: 'pie',
    radius: ['42%', '68%'],
    center: ['50%', '44%'],
    itemStyle: { borderColor: '#fff', borderWidth: 2 },
    label: { color: '#4d5b68' },
    data: rows,
  }]
})

const loadDrill = async(kind, name) => {
  const params = { ...queryParams() }
  if(kind === 'quarter') {
    const [yearPart, qPart] = name.split('Q')
    const year = yearPart
    const quarter = Number(qPart)
    const startMonth = (quarter - 1) * 3 + 1
    const endMonth = startMonth + 2
    params.received_start = `${year}-${String(startMonth).padStart(2,'0')}-01`
    params.received_end = `${year}-${String(endMonth).padStart(2,'0')}-31`
  }
  if(kind === 'type' && name !== '未填') params.case_type = name
  if(kind === 'department' && name !== '未填') params.handling_department = name
  if(kind === 'warning') params.warning_status = name
  const { data } = await http.get('/cases', { params })
  drillRows.value = data
  drillTitle.value = `${kind} / ${name}`
}

const loadDefaultDrill = async() => {
  const { data } = await http.get('/cases', { params: queryParams() })
  drillRows.value = data.slice(0, 20)
  if (!drillTitle.value) drillTitle.value = ''
}

const clearDrill = async() => {
  drillTitle.value = ''
  await loadDefaultDrill()
}

const render = async()=>{
  await nextTick()
  const quarter = ensureChart('quarter', quarterChart.value)
  const type = ensureChart('type', typeChart.value)
  const dept = ensureChart('dept', deptChart.value)
  const warning = ensureChart('warning', warningChart.value)

  quarter.setOption(buildBarOption('季度分布', stats.value.by_quarter || [], '#8aa39f'), true)
  type.setOption(buildPieOption(stats.value.by_type || [], ['#95aca7','#b4c7c2','#d3ddd8','#e7eeeb','#c9bba7']), true)
  dept.setOption(buildBarOption('经办部门分布', stats.value.by_department || [], '#8fa8b9'), true)
  warning.setOption(buildPieOption(stats.value.by_warning || [], ['#b8c8bf','#e7c985','#ddab7c','#d9867c']), true)

  quarter.off('click'); type.off('click'); dept.off('click'); warning.off('click')
  quarter.on('click', params => loadDrill('quarter', params.name))
  type.on('click', params => loadDrill('type', params.name))
  dept.on('click', params => loadDrill('department', params.name))
  warning.on('click', params => loadDrill('warning', params.name))
}

const load = async()=>{
  const { data } = await http.get('/dashboard', { params: queryParams() })
  stats.value = data
  await render()
  if (!drillTitle.value) await loadDefaultDrill()
}

const reset = async()=>{
  Object.assign(filters,{ handling_department:'', case_type:'', current_status:'', warning_status:'' })
  receivedRange.value=[]
  drillTitle.value=''
  await load()
}

onMounted(async()=>{
  await initDicts()
  await load()
})
</script>

<style scoped>
.analytics-page{display:flex;flex-direction:column;gap:16px}
.hero-card{display:flex;justify-content:space-between;align-items:flex-end;gap:16px;background:linear-gradient(135deg,#f7faf8,#eef4f5);border:1px solid #e5ecef;border-radius:24px;padding:24px 26px;box-shadow:0 12px 30px rgba(53,75,91,.05)}
.hero-eyebrow{font-size:12px;color:#7b8b97;letter-spacing:.08em;text-transform:uppercase;margin-bottom:8px}
.hero-title{margin:0;font-size:28px;color:#22303c;font-weight:700}
.hero-subtitle{margin-top:8px;color:#6c7c88;font-size:14px}
.hero-actions{display:flex;gap:10px;flex-wrap:wrap}
.analytics-filter-card{padding:16px 18px;border-radius:20px}
.filter-grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px}
.kpi-row{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:14px}
.kpi-analytics{padding:18px;border-radius:20px;border:1px solid #ebeff2;box-shadow:0 10px 24px rgba(53,75,91,.04)}
.kpi-label{font-size:13px;color:#6d7d89}
.kpi-value{font-size:32px;line-height:1.15;font-weight:700;color:#263340;margin-top:8px}
.kpi-neutral{background:linear-gradient(180deg,#fff,#f7f9fa)}
.kpi-mist{background:linear-gradient(180deg,#f5f8fb,#edf4f8)}
.kpi-warn{background:linear-gradient(180deg,#fff9ef,#fff4df)}
.kpi-urgent{background:linear-gradient(180deg,#fff7f0,#ffefdf)}
.kpi-danger{background:linear-gradient(180deg,#fff4f1,#ffe7e1)}
.kpi-green{background:linear-gradient(180deg,#f3faf7,#e9f5ef)}
.chart-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}
.chart-card{border-radius:22px;padding:16px 18px 12px}
.chart-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;font-size:16px;font-weight:600;color:#2a3744}
.chart-hint{font-size:12px;color:#8a98a4;font-weight:400}
.chart-box{height:320px}
.detail-card{border-radius:22px}
.detail-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;gap:16px}
.detail-title{font-size:18px;font-weight:700;color:#273440}
.detail-subtitle{font-size:13px;color:#7b8a96;margin-top:4px}
@media (max-width: 1200px){
  .filter-grid,.kpi-row,.chart-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
  .hero-card{flex-direction:column;align-items:flex-start}
}
</style>