<template>
  <div class="page page-stack">
    <div class="hero-card">
      <div>
        <div class="hero-eyebrow">工作日 / 节假日</div>
        <h2 class="hero-title">法定日历与人工覆盖</h2>
        <div class="hero-subtitle">系统默认自动按中国法定节假日与调休判断工作日。这里的配置不是主流程依赖，而是人工覆盖兜底：只有遇到特殊情况时才需要录入。</div>
      </div>
      <div class="hero-actions">
        <el-button type="primary" @click="openCreate">新增人工覆盖</el-button>
        <el-button @click="load">刷新</el-button>
      </div>
    </div>

    <div class="queue-grid">
      <div class="info-block">
        <h4>系统判断逻辑</h4>
        <p>1）先看人工覆盖表；2）若无覆盖，再按中国法定节假日/调休自动判断；3）再兜底按周一到周五视为工作日。</p>
      </div>
      <div class="info-block">
        <h4>当前人工覆盖数量</h4>
        <p>共 {{ rows.length }} 条。建议仅在自动判断不满足实际业务时再新增，避免把主流程变成人工维护系统。</p>
      </div>
    </div>

    <div class="card">
      <h3 class="section-title">人工覆盖记录</h3>
      <el-table :data="rows" stripe>
        <el-table-column prop="day" label="日期" width="180"/>
        <el-table-column label="类型" width="120">
          <template #default="scope"><span class="status-badge" :class="scope.row.day_type === 'workday' ? 's-normal' : 's-overdue'">{{ scope.row.day_type === 'workday' ? '工作日' : '节假日' }}</span></template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="280"/>
        <el-table-column label="操作" width="180">
          <template #default="scope">
            <el-button link @click="openEdit(scope.row)">编辑</el-button>
            <el-button link type="danger" @click="removeItem(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialogVisible" title="人工覆盖配置" width="520px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="日期"><el-date-picker v-model="form.day" value-format="YYYY-MM-DD" type="date" style="width:100%" /></el-form-item>
        <el-form-item label="类型">
          <el-radio-group v-model="form.day_type">
            <el-radio label="workday">工作日</el-radio>
            <el-radio label="holiday">节假日</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注"><el-input v-model="form.remark" type="textarea" rows="3" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible=false">取消</el-button>
        <el-button type="primary" @click="submit">保存</el-button>
      </template>
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
const blankForm = () => ({ day:'', day_type:'holiday', remark:'' })
const form = reactive(blankForm())

const load = async()=>{ const { data } = await http.get('/config/holidays'); rows.value = data }
const openCreate = ()=>{ editingId.value = null; Object.assign(form, blankForm()); dialogVisible.value = true }
const openEdit = (row)=>{ editingId.value = row.id; Object.assign(form, { day: row.day, day_type: row.day_type, remark: row.remark || '' }); dialogVisible.value = true }
const submit = async()=>{
  if (editingId.value) await http.put(`/config/holidays/${editingId.value}`, form)
  else await http.post('/config/holidays', form)
  ElMessage.success('保存成功')
  dialogVisible.value = false
  load()
}
const removeItem = async(row)=>{
  await ElMessageBox.confirm(`确认删除 ${row.day} 的人工覆盖吗？`, '提示')
  await http.delete(`/config/holidays/${row.id}`)
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>
