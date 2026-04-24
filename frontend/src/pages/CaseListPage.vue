<template>
  <div class="page">
    <div class="card">
      <h2 class="section-title">事项列表</h2>
      <div class="toolbar">
        <el-input v-model="filters.keyword" placeholder="关键字/通知书编号/申请人/涉案主体/复议内容" style="width:320px" clearable />
        <el-input v-model="filters.notice_no" placeholder="通知书编号" style="width:180px" clearable />
        <el-input v-model="filters.applicant" placeholder="申请人" style="width:140px" clearable />
        <el-select v-model="filters.handling_department" placeholder="经办部门" style="width:150px" clearable><el-option v-for="x in dicts.department" :key="x.value" :label="x.label" :value="x.value" /></el-select>
        <el-select v-model="filters.case_type" placeholder="类型" style="width:120px" clearable><el-option v-for="x in dicts.case_type" :key="x.value" :label="x.label" :value="x.value" /></el-select>
        <el-select v-model="filters.current_status" placeholder="当前状态" style="width:120px" clearable><el-option v-for="x in dicts.current_status" :key="x.value" :label="x.label" :value="x.value" /></el-select>
        <el-select v-model="filters.decision_content" placeholder="决定内容" style="width:140px" clearable><el-option v-for="x in dicts.decision_content" :key="x.value" :label="x.label" :value="x.value" /></el-select>
        <el-select v-model="filters.warning_status" placeholder="预警状态" style="width:120px" clearable><el-option v-for="x in ['正常','临期','紧急','超期']" :key="x" :label="x.label || x" :value="x" /></el-select>
        <el-select v-model="filters.closed_status" placeholder="闭环状态" style="width:120px" clearable><el-option label="未闭环" value="open" /><el-option label="已闭环" value="closed" /></el-select>
      </div>
      <div class="toolbar">
        <el-date-picker v-model="receivedRange" type="daterange" value-format="YYYY-MM-DD" start-placeholder="签收开始" end-placeholder="签收结束" />
        <el-date-picker v-model="deadlineRange" type="daterange" value-format="YYYY-MM-DD" start-placeholder="最晚答复开始" end-placeholder="最晚答复结束" />
        <el-date-picker v-model="decisionRange" type="daterange" value-format="YYYY-MM-DD" start-placeholder="决定时间开始" end-placeholder="决定时间结束" />
        <el-button type="primary" @click="load">查询</el-button>
        <el-button @click="reset">重置</el-button>
        <el-button type="success" @click="goCreate">新建事项</el-button>
        <el-upload :show-file-list="false" :http-request="uploadImport"><el-button>一键导入</el-button></el-upload>
        <el-button @click="downloadTemplate('xlsx')">下载导入模板</el-button>
        <el-button @click="download('csv')">导出CSV</el-button>
        <el-button @click="download('xlsx')">导出Excel</el-button>
      </div>
      <el-table :data="rows" stripe>
        <el-table-column prop="seq_no" label="序号" width="90" sortable :sort-method="sortBySeqNo"/>
        <el-table-column prop="notice_no" label="通知书编号" width="180" sortable :sort-method="sortByNoticeNo"/>
        <el-table-column prop="applicant" label="申请人" width="120"/>
        <el-table-column prop="respondent_subject" label="涉案主体" min-width="160" show-overflow-tooltip/>
        <el-table-column prop="review_item" label="行政复议事项" min-width="150" show-overflow-tooltip/>
        <el-table-column prop="review_content" label="复议内容" min-width="220" show-overflow-tooltip/>
        <el-table-column prop="handling_department" label="经办部门" width="120"/>
        <el-table-column prop="received_date" label="签收日期" width="120" sortable :sort-method="sortByReceivedDate"/>
        <el-table-column prop="deadline_date" label="最晚答复日" width="120" sortable :sort-method="sortByDeadlineDate"/>
        <el-table-column prop="current_status" label="当前状态" width="100"/>
        <el-table-column label="闭环状态" width="100"><template #default="scope"><span class="status-badge" :class="scope.row.is_closed ? 's-normal' : 's-near'">{{ scope.row.is_closed ? '已闭环' : '未闭环' }}</span></template></el-table-column>
        <el-table-column label="预警状态" width="100"><template #default="scope"><span class="status-badge" :class="badgeClass(scope.row.warning_status)">{{ scope.row.warning_status }}</span></template></el-table-column>
        <el-table-column prop="remaining_workdays" label="剩余工作日" width="120" sortable :sort-method="sortByRemainingWorkdays"/>
        <el-table-column label="操作" width="320" fixed="right">
          <template #default="scope">
            <el-button link @click="view(scope.row.id)">详情/编辑</el-button>
            <el-button link @click="manualSend(scope.row.id)">手工微信</el-button>
            <el-button link @click="closeCase(scope.row.id)">标记闭环</el-button>
            <el-button link type="danger" @click="removeCase(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>
<script setup>
import { reactive, ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import http from '../api/http'

const router = useRouter()
const rows = ref([])
const receivedRange = ref([])
const deadlineRange = ref([])
const decisionRange = ref([])
const dicts = reactive({ department: [], case_type: [], current_status: [], decision_content: [] })
const filters = reactive({ keyword:'', notice_no:'', applicant:'', handling_department:'', case_type:'', current_status:'', decision_content:'', warning_status:'', closed_status:'' })

const queryParams = () => ({
  ...filters,
  received_start: receivedRange.value?.[0],
  received_end: receivedRange.value?.[1],
  deadline_start: deadlineRange.value?.[0],
  deadline_end: deadlineRange.value?.[1],
  decision_start: decisionRange.value?.[0],
  decision_end: decisionRange.value?.[1],
})

const normalizeNumber = value => {
  if (value === null || value === undefined || value === '') return Number.MAX_SAFE_INTEGER
  const num = Number(value)
  return Number.isNaN(num) ? Number.MAX_SAFE_INTEGER : num
}

const normalizeDate = value => {
  if (!value) return Number.MAX_SAFE_INTEGER
  const ts = new Date(value).getTime()
  return Number.isNaN(ts) ? Number.MAX_SAFE_INTEGER : ts
}

const normalizeText = value => String(value ?? '').trim().toLowerCase()

const sortBySeqNo = (a, b) => normalizeNumber(a.seq_no) - normalizeNumber(b.seq_no)
const sortByNoticeNo = (a, b) => normalizeText(a.notice_no).localeCompare(normalizeText(b.notice_no), 'zh-CN', { numeric: true, sensitivity: 'base' })
const sortByReceivedDate = (a, b) => normalizeDate(a.received_date) - normalizeDate(b.received_date)
const sortByDeadlineDate = (a, b) => normalizeDate(a.deadline_date) - normalizeDate(b.deadline_date)
const sortByRemainingWorkdays = (a, b) => normalizeNumber(a.remaining_workdays) - normalizeNumber(b.remaining_workdays)

const load = async()=>{
  const { data } = await http.get('/cases', { params: queryParams() })
  rows.value = data
}
const loadDict = async(type) => (await http.get(`/config/dictionary/${type}`)).data
const initDicts = async()=>{
  dicts.department = await loadDict('department')
  dicts.case_type = await loadDict('case_type')
  dicts.current_status = await loadDict('current_status')
  dicts.decision_content = await loadDict('decision_content')
}
const reset = ()=>{
  Object.assign(filters, { keyword:'', notice_no:'', applicant:'', handling_department:'', case_type:'', current_status:'', decision_content:'', warning_status:'', closed_status:'' })
  receivedRange.value=[]
  deadlineRange.value=[]
  decisionRange.value=[]
  load()
}
const goCreate = ()=> router.push('/cases/new')
const view = id => router.push(`/cases/${id}`)
const badgeClass = s => s==='超期'?'s-overdue':s==='紧急'?'s-urgent':s==='临期'?'s-near':'s-normal'
const manualSend = async (id)=>{ try { const { data } = await http.post(`/notify/case/${id}/manual`); ElMessage.success(`已创建发送任务 #${data.id}`) } catch (e) { ElMessage.error(e?.response?.data?.detail || '发送任务创建失败') } }
const closeCase = async (id)=>{ await http.post(`/cases/${id}/close`); ElMessage.success('已闭环'); load() }
const removeCase = async(id)=>{ await ElMessageBox.confirm('确认删除该事项吗？', '提示'); await http.delete(`/cases/${id}`); ElMessage.success('已删除'); load() }
const download = async(format) => { const res = await http.get('/cases/export', { params: { format, ...queryParams() }, responseType:'blob' }); const a = document.createElement('a'); const url = URL.createObjectURL(res.data); a.href = url; a.download = `cases.${format === 'xlsx' ? 'xlsx' : 'csv'}`; a.click(); URL.revokeObjectURL(url) }
const uploadImport = async({ file })=>{
  const fd = new FormData()
  fd.append('file', file)
  const { data } = await http.post('/cases/import', fd, { headers:{ 'Content-Type':'multipart/form-data' } })
  if(data.errors?.length){
    ElMessage.warning(`导入成功 ${data.imported} 条，失败 ${data.errors.length} 条，首条错误：第${data.errors[0].line}行 ${data.errors[0].reason}`)
  } else {
    ElMessage.success(`导入成功：${data.imported} 条`)
  }
  load()
}
const downloadTemplate = async(format) => { const res = await http.get('/cases/import-template', { params:{ format }, responseType:'blob' }); const a = document.createElement('a'); const url = URL.createObjectURL(res.data); a.href = url; a.download = `case_import_template.${format}`; a.click(); URL.revokeObjectURL(url) }

onMounted(async()=>{ await Promise.all([initDicts(), load()]) })
</script>
