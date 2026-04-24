<template>
  <div class="layout">
    <aside class="sidebar">
      <div class="brand">行政复议事项系统</div>
      <el-menu :default-active="$route.path" router background-color="transparent">
        <el-menu-item index="/">首页仪表盘</el-menu-item>
        <el-menu-item index="/cases">事项列表</el-menu-item>
        <el-menu-item index="/cases/new">新建事项</el-menu-item>
        <el-menu-item index="/warnings">临期/紧急/超期</el-menu-item>
        <el-menu-item index="/analytics">统计分析</el-menu-item>
        <el-menu-item index="/dictionary">基础字典</el-menu-item>
        <el-menu-item index="/workdays">工作日/节假日</el-menu-item>
        <el-menu-item index="/mappings">负责人映射</el-menu-item>
        <el-menu-item index="/wechat-logs">微信发送日志</el-menu-item>
        <el-menu-item index="/wechat-test">微信测试</el-menu-item>
        <el-menu-item index="/system-params">系统参数</el-menu-item>
        <el-menu-item index="/backup">备份恢复</el-menu-item>
      </el-menu>
    </aside>
    <main class="main">
      <router-view />
    </main>
  </div>
</template>
