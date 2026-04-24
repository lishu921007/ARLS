<template>
  <div class="page page-stack">
    <div class="hero-card">
      <div>
        <div class="hero-eyebrow">负责人映射</div>
        <h2 class="hero-title">负责人规则与微信映射</h2>
        <div class="hero-subtitle">这里配置经办部门、类型与负责人的对应关系。后续自动提醒、手工微信都会用到这里的规则。</div>
      </div>
      <div class="hero-actions">
        <el-button type="primary" @click="openCreate">新增映射</el-button>
        <el-button @click="load">刷新</el-button>
      </div>
    </div>

    <div class="card">
      <el-table :data="rows" stripe>
        <el-table-column prop="rule_name" label="规则名称" min-width="160"/>
        <el-table-column prop="handling_department" label="经办部门" width="140"/>
        <el-table-column prop="case_type" label="类型" width="120"/>
        <el-table-column prop="contact_name" label="联系人" width="120"/>
        <el-table-column prop="contact_wechat_remark" label="联系人微信备注" min-width="140"/>
        <el-table-column prop="primary_name" label="主负责人" width="120"/>
        <el-table-column prop="primary_wechat_remark" label="主负责人微信备注" min-width="140"/>
        <el-table-column prop="backup_name" label="备用负责人" width="120"/>
        <el-table-column prop="enabled" label="启用" width="90"><template #default="s">{{ s.row.enabled ? '是' : '否' }}</template></el-table-column>
        <el-table-column label="操作" width="220">
          <template #default="s">
            <el-button link @click="openEdit(s.row)">编辑</el-button>
            <el-button link @click="toggleEnabled(s.row)">{{ s.row.enabled ? '停用' : '启用' }}</el-button>
            <el-button link type="danger" @click="removeItem(s.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑负责人映射' : '新增负责人映射'" width="760px">
      <el-form :model="form" label-width="120px">
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item label="规则名称"><el-input v-model="form.rule_name" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="经办部门"><el-select v-model="form.handling_department" clearable filterable placeholder="请选择经办部门" style="width:100%"><el-option v-for="x in dicts.department" :key="x.value" :label="x.label" :value="x.value" /></el-select></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="类型"><el-select v-model="form.case_type" clearable filterable placeholder="请选择类型" style="width:100%"><el-option v-for="x in dicts.case_type" :key="x.value" :label="x.label" :value="x.value" /></el-select></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="联系人姓名"><el-input v-model="form.contact_name" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="联系人微信备注"><el-input v-model="form.contact_wechat_remark" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="主负责人姓名"><el-input v-model="form.primary_name" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="主负责人微信备注"><el-input v-model="form.primary_wechat_remark" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="备用负责人姓名"><el-input v-model="form.backup_name" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="备用微信备注"><el-input v-model="form.backup_wechat_remark" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="预警天数"><el-input-number v-model="form.warning_days" :min="1" style="width:100%" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="启用"><el-switch v-model="form.enabled" /></el-form-item></el-col>
        </el-row>
        <el-form-item label="备注"><el-input type="textarea" rows="2" v-model="form.remark" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialogVisible=false">取消</el-button><el-button type="primary" @click="submit">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import http from '../api/http'
import { ElMessage, ElMessageBox } from 'element-plus'

const rows = ref([])
const dialogVisible = ref(false)
const editingId = ref(null)
const dicts = reactive({ department: [], case_type: [] })
const blankForm = () => ({ rule_name:'', handling_department:'', case_type:'', contact_name:'', contact_wechat_remark:'', primary_name:'', primary_wechat_remark:'', backup_name:'', backup_wechat_remark:'', warning_days:3, enabled:true, remark:'' })
const form = reactive(blankForm())
const cleanPayload = () => ({
  rule_name: form.rule_name,
  handling_department: form.handling_department || null,
  case_type: form.case_type || null,
  contact_name: form.contact_name || null,
  contact_wechat_remark: form.contact_wechat_remark || null,
  primary_name: form.primary_name || null,
  primary_wechat_remark: form.primary_wechat_remark || null,
  backup_name: form.backup_name || null,
  backup_wechat_remark: form.backup_wechat_remark || null,
  warning_days: form.warning_days || 3,
  enabled: !!form.enabled,
  remark: form.remark || null,
})
const loadDict = async(type) => (await http.get(`/config/dictionary/${type}`)).data
const load = async()=>{ const { data } = await http.get('/config/mappings'); rows.value = data }
const initDicts = async()=>{ dicts.department = await loadDict('department'); dicts.case_type = await loadDict('case_type') }
const openCreate = ()=>{ editingId.value=null; Object.assign(form, blankForm()); dialogVisible.value=true }
const openEdit = (row)=>{ editingId.value=row.id; Object.assign(form, blankForm(), cleanRow(row)); dialogVisible.value=true }
const cleanRow = (row)=> ({
  rule_name: row.rule_name || '', handling_department: row.handling_department || '', case_type: row.case_type || '', contact_name: row.contact_name || '', contact_wechat_remark: row.contact_wechat_remark || '', primary_name: row.primary_name || '', primary_wechat_remark: row.primary_wechat_remark || '', backup_name: row.backup_name || '', backup_wechat_remark: row.backup_wechat_remark || '', warning_days: row.warning_days || 3, enabled: !!row.enabled, remark: row.remark || ''
})
const submit = async()=>{
  try {
    const payload = cleanPayload()
    if(editingId.value) await http.put(`/config/mappings/${editingId.value}`, payload)
    else await http.post('/config/mappings', payload)
    ElMessage.success('保存成功')
    dialogVisible.value=false
    await load()
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || '保存失败，请检查表单内容')
  }
}
const toggleEnabled = async(row)=>{ await http.put(`/config/mappings/${row.id}`, { enabled: !row.enabled }); ElMessage.success('状态已更新'); load() }
const removeItem = async(row)=>{ await ElMessageBox.confirm(`确认删除【${row.rule_name}】吗？`, '提示'); await http.delete(`/config/mappings/${row.id}`); ElMessage.success('已删除'); load() }
onMounted(async()=>{ await Promise.all([initDicts(), load()]) })
</script>
