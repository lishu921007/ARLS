<template>
  <div class="page page-stack">
    <div class="hero-card">
      <div>
        <div class="hero-eyebrow">风险专页</div>
        <h2 class="hero-title">临期 / 紧急 / 超期驾驶舱</h2>
        <div class="hero-subtitle">把风险事项从普通表格里拎出来，优先显示今日最需要处理的部分。超期永远排在最前面。</div>
      </div>
      <div class="hero-actions">
        <el-radio-group v-model="level" @change="load">
          <el-radio-button label="全部" />
          <el-radio-button label="临期" />
          <el-radio-button label="紧急" />
          <el-radio-button label="超期" />
        </el-radio-group>
        <el-button @click="load">刷新</el-button>
      </div>
    </div>

    <div class="risk-board">
      <div class="risk-card near">
        <div class="title">临期</div>
        <div class="value">{{ nearCount }}</div>
        <div class="desc">接近时限，适合提前催办、补材料、做内部提醒，避免滑入紧急和超期。</div>
        <div class="footer">建议：提前 1~3 个工作日完成催办。</div>
      </div>
      <div class="risk-card urgent">
        <div class="title">紧急</div>
        <div class="value">{{ urgentCount }}</div>
        <div class="desc">已进入高优先级处理区，应当天推进，确保经办部门和负责人都已收到提醒。</div>
        <div class="footer">建议：当天闭环处理进展。</div>
      </div>
      <div class="risk-card overdue">
        <div class="title">超期</div>
        <div class="value">{{ overdueCount }}</div>
        <div class="desc">最高风险区，需要单独盯办。页面内默认按剩余工作日与最晚答复日优先排序。</div>
        <div class="footer">建议：逐条核实原因并形成处置说明。</div>
      </div>
    </div>

    <div class="card">
      <div class="toolbar-between">
        <div>
          <h3 class="section-title" style="margin-bottom:0">风险事项清单</h3>
          <div class="section-subtitle">当前筛选：{{ level }}。支持直接手工发送提醒和进入详情处理。</div>
        </div>
        <div class="muted">共 {{ rows.length }} 条</div>
      </div>
      <div style="height:12px"></div>
      <el-table :data="rows" stripe class="compact-table">
        <el-table-column prop="notice_no" label="通知书编号" min-width="180"/>
        <el-table-column prop="applicant" label="申请人" width="120"/>
        <el-table-column prop="handling_department" label="经办部门" width="140"/>
        <el-table-column prop="deadline_date" label="最晚答复日" width="130"/>
        <el-table-column label="预警状态" width="110">
          <template #default="scope"><span class="status-badge" :class="badgeClass(scope.row.warning_status)">{{ scope.row.warning_status }}</span></template>
        </el-table-column>
        <el-table-column prop="remaining_workdays" label="剩余工作日" width="120"/>
        <el-table-column prop="current_status" label="当前状态" width="120"/>
        <el-table-column prop="contact_name" label="联系人" width="120"/>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="scope">
            <el-button link @click="view(scope.row.id)">详情</el-button>
            <el-button link @click="manualSend(scope.row.id)">手工微信</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import http from '../api/http'

const router = useRouter()
const level = ref('全部')
const rows = ref([])
const badgeClass = s => s==='超期'?'s-overdue':s==='紧急'?'s-urgent':s==='临期'?'s-near':'s-normal'
const load = async()=>{
  const params = level.value === '全部' ? {} : { warning_status: level.value }
  const { data } = await http.get('/cases', { params })
  rows.value = data.filter(x => ['临期','紧急','超期'].includes(x.warning_status))
}
const nearCount = computed(()=> rows.value.filter(x=>x.warning_status==='临期').length)
const urgentCount = computed(()=> rows.value.filter(x=>x.warning_status==='紧急').length)
const overdueCount = computed(()=> rows.value.filter(x=>x.warning_status==='超期').length)
const view = id => router.push(`/cases/${id}`)
const manualSend = async(id)=>{
  await http.post(`/notify/case/${id}/manual`)
  ElMessage.success('已进入发送队列')
}
onMounted(load)
</script>
