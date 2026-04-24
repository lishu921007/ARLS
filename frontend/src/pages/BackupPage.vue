<template>
  <div class="page page-stack">
    <div class="hero-card">
      <div>
        <div class="hero-eyebrow">备份恢复</div>
        <h2 class="hero-title">数据库备份与恢复中心</h2>
        <div class="hero-subtitle">除了手工一键备份，已经补上了“从已有备份恢复”和“上传数据库文件恢复”。恢复前系统会先自动做一次安全备份。</div>
      </div>
      <div class="hero-actions">
        <el-button type="primary" @click="backup">一键备份数据库</el-button>
        <el-upload :show-file-list="false" :http-request="uploadRestore"><el-button>上传数据库并恢复</el-button></el-upload>
        <el-button @click="load">刷新列表</el-button>
      </div>
    </div>

    <div class="queue-grid">
      <div class="info-block"><h4>恢复前保护</h4><p>每次执行恢复时，系统都会先把当前线上数据库再备份一份，避免误恢复后无法撤回。</p></div>
      <div class="info-block"><h4>支持方式</h4><p>支持从历史备份记录直接恢复，也支持上传外部 .db 文件后立即恢复。</p></div>
    </div>

    <div class="card">
      <h3 class="section-title">备份列表</h3>
      <el-table :data="rows" stripe>
        <el-table-column prop="file_name" label="备份文件" min-width="260"/>
        <el-table-column prop="file_path" label="路径" min-width="360"/>
        <el-table-column prop="remark" label="备注" width="220"/>
        <el-table-column prop="created_at" label="时间" width="180"/>
        <el-table-column label="操作" width="140">
          <template #default="scope">
            <el-button link type="danger" @click="restore(scope.row)">恢复此备份</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import http from '../api/http'
import { ElMessage, ElMessageBox } from 'element-plus'

const rows = ref([])
const load = async()=>{ const { data } = await http.get('/system/backups'); rows.value = data }
const backup = async()=>{ await http.post('/system/backup'); ElMessage.success('备份成功'); load() }
const restore = async(row)=>{
  await ElMessageBox.confirm(`确认用【${row.file_name}】恢复数据库吗？系统会先自动备份当前数据库。`, '恢复确认', { type:'warning' })
  const { data } = await http.post(`/system/restore/${row.id}`)
  ElMessage.success(`恢复成功，已自动生成恢复前备份：${data.pre_restore_backup}`)
  load()
}
const uploadRestore = async({ file })=>{
  const fd = new FormData()
  fd.append('file', file)
  const { data } = await http.post('/system/restore-upload', fd, { headers:{ 'Content-Type':'multipart/form-data' } })
  ElMessage.success(`上传并恢复成功，来源：${data.restored_from}`)
  load()
}

onMounted(load)
</script>
