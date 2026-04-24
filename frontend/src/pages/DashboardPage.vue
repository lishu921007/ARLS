<template>
  <div class="page dashboard-layout">
    <div class="hero-card">
      <div>
        <div class="hero-eyebrow">首页仪表盘</div>
        <h2 class="hero-title">行政复议答复事项总览</h2>
        <div class="hero-subtitle">把总量、风险、闭环与结构分布放在同一屏里。重点先看超期与紧急，再看部门和类型的结构分布。</div>
      </div>
      <div class="hero-actions">
        <el-button type="primary" @click="load">刷新仪表盘</el-button>
        <el-button @click="$router.push('/warnings')">查看风险专页</el-button>
        <el-button @click="$router.push('/analytics')">进入统计分析</el-button>
      </div>
    </div>

    <div class="kpi-grid">
      <div class="kpi-card kpi-dark">
        <div class="label">总件数</div>
        <div class="value">{{ stats.total || 0 }}</div>
        <div class="hint">当前有效事项总量</div>
      </div>
      <div class="kpi-card kpi-mist">
        <div class="label">本季度新增</div>
        <div class="value">{{ stats.quarter_count || 0 }}</div>
        <div class="hint">用于观察阶段性工作压力</div>
      </div>
      <div class="kpi-card kpi-warn">
        <div class="label">临期件数</div>
        <div class="value">{{ stats.near_count || 0 }}</div>
        <div class="hint">接近时限，建议提前催办</div>
      </div>
      <div class="kpi-card kpi-urgent">
        <div class="label">紧急件数</div>
        <div class="value">{{ stats.urgent_count || 0 }}</div>
        <div class="hint">需要优先处理</div>
      </div>
      <div class="kpi-card kpi-danger">
        <div class="label">超期件数</div>
        <div class="value">{{ stats.overdue_count || 0 }}</div>
        <div class="hint">最优先处置风险</div>
      </div>
    </div>

    <div class="metric-strip">
      <div class="metric-panel">
        <div class="metric-panel-title">风险总览</div>
        <div class="metric-panel-subtitle">系统优先关注临期 / 紧急 / 超期三类事项。</div>
        <div class="list-clean">
          <div class="list-item"><div><strong>风险件合计</strong><span>临期 + 紧急 + 超期</span></div><em>{{ riskTotal }}</em></div>
          <div class="list-item"><div><strong>已闭环件数</strong><span>已办结 / 已终止等闭环状态</span></div><em>{{ stats.closed_count || 0 }}</em></div>
          <div class="list-item"><div><strong>风险占比</strong><span>帮助判断当前压力是否集中</span></div><em>{{ riskRate }}</em></div>
        </div>
      </div>
      <div class="metric-panel">
        <div class="metric-panel-title">处理建议</div>
        <div class="metric-panel-subtitle">按优先级给出直观建议。</div>
        <div class="list-clean">
          <div class="list-item"><div><strong>第一优先</strong><span>超期事项逐条清理</span></div><em>{{ stats.overdue_count || 0 }}</em></div>
          <div class="list-item"><div><strong>第二优先</strong><span>紧急事项当天推进</span></div><em>{{ stats.urgent_count || 0 }}</em></div>
          <div class="list-item"><div><strong>第三优先</strong><span>临期事项提前提醒</span></div><em>{{ stats.near_count || 0 }}</em></div>
        </div>
      </div>
      <div class="metric-panel">
        <div class="metric-panel-title">结构观察</div>
        <div class="metric-panel-subtitle">快速识别主要部门与类型。</div>
        <div class="list-clean">
          <div class="list-item"><div><strong>主要经办部门</strong><span>{{ topDepartment?.name || '暂无' }}</span></div><em>{{ topDepartment?.value || 0 }}</em></div>
          <div class="list-item"><div><strong>主要类型</strong><span>{{ topType?.name || '暂无' }}</span></div><em>{{ topType?.value || 0 }}</em></div>
          <div class="list-item"><div><strong>主要状态</strong><span>{{ topStatus?.name || '暂无' }}</span></div><em>{{ topStatus?.value || 0 }}</em></div>
        </div>
      </div>
    </div>

    <div class="card card-soft">
      <div class="toolbar-between">
        <div>
          <h3 class="section-title" style="margin-bottom:0">统计概览</h3>
          <div class="section-subtitle">用更清爽的摘要视图替代纯表格堆叠。</div>
        </div>
      </div>
      <div class="panel-grid" style="margin-top:16px">
        <div class="info-block">
          <h4>经办部门分布</h4>
          <table class="summary-table">
            <thead><tr><th>部门</th><th>数量</th></tr></thead>
            <tbody>
              <tr v-for="item in topRows(stats.by_department, 6)" :key="`dept-${item.name}`"><td>{{ item.name }}</td><td>{{ item.value }}</td></tr>
            </tbody>
          </table>
        </div>
        <div class="info-block">
          <h4>类型分布</h4>
          <table class="summary-table">
            <thead><tr><th>类型</th><th>数量</th></tr></thead>
            <tbody>
              <tr v-for="item in topRows(stats.by_type, 6)" :key="`type-${item.name}`"><td>{{ item.name }}</td><td>{{ item.value }}</td></tr>
            </tbody>
          </table>
        </div>
        <div class="info-block">
          <h4>当前状态分布</h4>
          <table class="summary-table">
            <thead><tr><th>状态</th><th>数量</th></tr></thead>
            <tbody>
              <tr v-for="item in topRows(stats.by_status, 6)" :key="`status-${item.name}`"><td>{{ item.name }}</td><td>{{ item.value }}</td></tr>
            </tbody>
          </table>
        </div>
        <div class="info-block">
          <h4>预警级别分布</h4>
          <table class="summary-table">
            <thead><tr><th>级别</th><th>数量</th></tr></thead>
            <tbody>
              <tr v-for="item in topRows(stats.by_warning, 6)" :key="`warning-${item.name}`"><td>{{ item.name }}</td><td>{{ item.value }}</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import http from '../api/http'

const stats = ref({})
const load = async()=>{
  const { data } = await http.get('/dashboard')
  stats.value = data
}
const topRows = (rows = [], limit = 5) => [...rows].sort((a,b)=>b.value-a.value).slice(0, limit)
const topDepartment = computed(()=> topRows(stats.value.by_department, 1)[0])
const topType = computed(()=> topRows(stats.value.by_type, 1)[0])
const topStatus = computed(()=> topRows(stats.value.by_status, 1)[0])
const riskTotal = computed(()=> (stats.value.near_count || 0) + (stats.value.urgent_count || 0) + (stats.value.overdue_count || 0))
const riskRate = computed(()=> {
  const total = stats.value.total || 0
  if (!total) return '0%'
  return `${Math.round((riskTotal.value / total) * 100)}%`
})

onMounted(load)
</script>
