<template>
  <div class="page"><div class="card"><h2 class="section-title">基础字典配置</h2>
    <div class="toolbar">
      <el-select v-model="dictType" style="width:180px" @change="onTypeChange"><el-option label="经办部门" value="department"/><el-option label="决定内容" value="decision_content"/><el-option label="类型" value="case_type"/><el-option label="行政复议事项" value="review_item"/><el-option label="当前状态" value="current_status"/></el-select>
      <el-button @click="load">加载</el-button>
      <el-button type="primary" @click="openCreate">新增选项</el-button>
    </div>
    <el-table :data="rows">
      <el-table-column prop="label" label="名称"/>
      <el-table-column prop="value" label="值"/>
      <el-table-column prop="sort_order" label="排序" width="90"/>
      <el-table-column prop="enabled" label="启用" width="90"><template #default="s">{{ s.row.enabled ? '是' : '否' }}</template></el-table-column>
      <el-table-column label="操作" width="220">
        <template #default="s">
          <el-button link @click="openEdit(s.row)">编辑</el-button>
          <el-button link @click="toggleEnabled(s.row)">{{ s.row.enabled ? '停用' : '启用' }}</el-button>
          <el-button link type="danger" @click="removeItem(s.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div></div>
  <el-dialog v-model="dialogVisible" :title="editingId ? '编辑字典项' : '新增字典项'" width="520px">
    <el-form :model="form" label-width="90px">
      <el-form-item label="字典类型"><el-select v-model="form.dict_type" style="width:100%"><el-option label="经办部门" value="department"/><el-option label="决定内容" value="decision_content"/><el-option label="类型" value="case_type"/><el-option label="行政复议事项" value="review_item"/><el-option label="当前状态" value="current_status"/></el-select></el-form-item>
      <el-form-item label="显示名称"><el-input v-model="form.label" /></el-form-item>
      <el-form-item label="实际值"><el-input v-model="form.value" /></el-form-item>
      <el-form-item label="排序"><el-input-number v-model="form.sort_order" :min="0" /></el-form-item>
      <el-form-item label="启用"><el-switch v-model="form.enabled" /></el-form-item>
    </el-form>
    <template #footer><el-button @click="dialogVisible=false">取消</el-button><el-button type="primary" @click="submit">保存</el-button></template>
  </el-dialog>
</template>
<script setup>
import { reactive, ref } from 'vue'; import http from '../api/http'; import { ElMessage, ElMessageBox } from 'element-plus'
const dictType = ref('department'); const rows = ref([]); const dialogVisible = ref(false); const editingId = ref(null)
const blankForm = () => ({ dict_type: dictType.value, label:'', value:'', sort_order:0, enabled:true })
const form = reactive(blankForm())
const onTypeChange = ()=>{ form.dict_type = dictType.value; load() }
const load = async()=>{ const { data } = await http.get(`/config/dictionary/${dictType.value}`); rows.value = data }
const openCreate = ()=>{ editingId.value = null; Object.assign(form, blankForm()); dialogVisible.value = true }
const openEdit = (row)=>{ editingId.value = row.id; Object.assign(form, { dict_type: row.dict_type, label: row.label, value: row.value, sort_order: row.sort_order, enabled: row.enabled }); dialogVisible.value = true }
const submit = async()=>{ if(editingId.value) await http.put(`/config/dictionary/${editingId.value}`, form); else await http.post('/config/dictionary', form); ElMessage.success('保存成功'); dialogVisible.value=false; load() }
const toggleEnabled = async(row)=>{ await http.put(`/config/dictionary/${row.id}`, { ...row, enabled: !row.enabled }); ElMessage.success('状态已更新'); load() }
const removeItem = async(row)=>{ await ElMessageBox.confirm(`确认删除【${row.label}】吗？`, '提示'); await http.delete(`/config/dictionary/${row.id}`); ElMessage.success('已删除'); load() }
load()
</script>