import { createRouter, createWebHistory } from 'vue-router'
import LoginPage from '../pages/LoginPage.vue'
import MainLayout from '../layouts/MainLayout.vue'
import DashboardPage from '../pages/DashboardPage.vue'
import CaseListPage from '../pages/CaseListPage.vue'
import CaseFormPage from '../pages/CaseFormPage.vue'
import WarningPage from '../pages/WarningPage.vue'
import AnalyticsPage from '../pages/AnalyticsPage.vue'
import DictionaryPage from '../pages/DictionaryPage.vue'
import WorkdayPage from '../pages/WorkdayPage.vue'
import MappingPage from '../pages/MappingPage.vue'
import WechatLogsPage from '../pages/WechatLogsPage.vue'
import WechatTestPage from '../pages/WechatTestPage.vue'
import SystemParamsPage from '../pages/SystemParamsPage.vue'
import BackupPage from '../pages/BackupPage.vue'

const routes = [
  { path: '/login', component: LoginPage },
  { path: '/', component: MainLayout, children: [
    { path: '', component: DashboardPage },
    { path: 'cases', component: CaseListPage },
    { path: 'cases/new', component: CaseFormPage },
    { path: 'cases/:id', component: CaseFormPage, props: true },
    { path: 'warnings/:level?', component: WarningPage },
    { path: 'analytics', component: AnalyticsPage },
    { path: 'dictionary', component: DictionaryPage },
    { path: 'workdays', component: WorkdayPage },
    { path: 'mappings', component: MappingPage },
    { path: 'wechat-logs', component: WechatLogsPage },
    { path: 'wechat-test', component: WechatTestPage },
    { path: 'system-params', component: SystemParamsPage },
    { path: 'backup', component: BackupPage },
  ]}
]
const router = createRouter({ history: createWebHistory(), routes })
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.path !== '/login' && !token) next('/login')
  else next()
})
export default router
