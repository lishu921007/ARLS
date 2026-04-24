<template>
  <div class="page">
    <div class="card">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;gap:12px;">
        <h2 class="section-title" style="margin:0">{{ currentId ? '编辑事项' : '新建事项' }}</h2>
        <el-button @click="closePage">关闭</el-button>
      </div>
      <el-form :model="form" label-width="120px">
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item label="通知书编号"><el-input v-model="form.notice_no" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="申请人"><el-input v-model="form.applicant" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="涉案主体"><el-input v-model="form.respondent_subject" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="行政复议事项"><el-select v-model="form.review_item" filterable clearable style="width:100%"><el-option v-for="x in dicts.review_item" :key="x.value" :label="x.label" :value="x.value" /></el-select></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="经办部门"><el-select v-model="form.handling_department" filterable clearable style="width:100%"><el-option v-for="x in dicts.department" :key="x.value" :label="x.label" :value="x.value" /></el-select></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="联系人"><el-input v-model="form.contact_name" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="联系人微信备注"><el-input v-model="form.contact_wechat_remark" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="签收日期"><el-date-picker v-model="form.received_date" value-format="YYYY-MM-DD" type="date" style="width:100%" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="实际答复时间"><el-date-picker v-model="form.actual_reply_time" value-format="YYYY-MM-DD" type="date" style="width:100%" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="交司法局时间"><el-date-picker v-model="form.judicial_bureau_date" value-format="YYYY-MM-DD" type="date" style="width:100%" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="决定时间"><el-date-picker v-model="form.decision_date" value-format="YYYY-MM-DD" type="date" style="width:100%" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="决定内容"><el-select v-model="form.decision_content" filterable clearable style="width:100%"><el-option v-for="x in dicts.decision_content" :key="x.value" :label="x.label" :value="x.value" /></el-select></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="类型"><el-select v-model="form.case_type" filterable clearable style="width:100%"><el-option v-for="x in dicts.case_type" :key="x.value" :label="x.label" :value="x.value" /></el-select></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="当前状态"><el-select v-model="form.current_status" filterable clearable style="width:100%"><el-option v-for="x in dicts.current_status" :key="x.value" :label="x.label" :value="x.value" /></el-select></el-form-item></el-col>
        </el-row>
        <el-form-item label="复议内容"><el-input type="textarea" rows="3" v-model="form.review_content" /></el-form-item>
        <el-form-item label="备注"><el-input type="textarea" rows="2" v-model="form.remark" /></el-form-item>
        <el-button type="primary" @click="save">保存</el-button>
      </el-form>
    </div>
  </div>
</template>
<script setup>
import { reactive, onMounted, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import http from '../api/http'
const route = useRoute(); const router = useRouter(); const currentId = computed(() => route.params.id)
const blankForm = () => ({ notice_no:'', applicant:'', respondent_subject:'', review_content:'', review_item:'', handling_department:'', contact_name:'', contact_wechat_remark:'', received_date:'', reply_date:'', actual_reply_time:'', judicial_bureau_date:'', decision_date:'', decision_content:'', redo_status:'', case_type:'', current_status:'待处理', remark:'' })
const form = reactive(blankForm())
const dicts = reactive({ department:[], decision_content:[], case_type:[], current_status:[], review_item:[] })
const loadDict = async(type) => (await http.get(`/config/dictionary/${type}`)).data.filter(x => x.enabled)
const loadCase = async(caseId) => {
  Object.assign(form, blankForm())
  if(!caseId) return
  const { data } = await http.get(`/cases/${caseId}`)
  Object.assign(form, blankForm(), data || {})
}
const initPage = async() => {
  const [department, decision_content, case_type, current_status, review_item, _] = await Promise.all([
    loadDict('department'),
    loadDict('decision_content'),
    loadDict('case_type'),
    loadDict('current_status'),
    loadDict('review_item'),
    loadCase(currentId.value),
  ])
  dicts.department = department
  dicts.decision_content = decision_content
  dicts.case_type = case_type
  dicts.current_status = current_status
  dicts.review_item = review_item
}
onMounted(initPage)
watch(currentId, async (newId) => { await loadCase(newId) }, { immediate: false })
const closePage = () => router.push('/cases')
const buildPayload = () => {
  const payload = { ...form }
  const nullableDateFields = ['received_date', 'reply_date', 'actual_reply_time', 'judicial_bureau_date', 'decision_date']
  nullableDateFields.forEach(key => {
    if (payload[key] === '') payload[key] = null
  })
  if (!payload.current_status) payload.current_status = '待处理'
  return payload
}
const save = async()=>{
  try {
    const payload = buildPayload()
    if(currentId.value) await http.put(`/cases/${currentId.value}`, payload)
    else await http.post('/cases', payload)
    ElMessage.success('保存成功')
    router.push('/cases')
  } catch (e) {
    const detail = e.response?.data?.detail
    const msg = Array.isArray(detail) ? detail.map(x => `${x.loc?.slice(-1)?.[0] || '字段'}: ${x.msg}`).join('；') : (detail || '保存失败，请检查填写内容')
    ElMessage.error(msg)
  }
}
</script>
