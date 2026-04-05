import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Exam',
    component: () => import('@/views/ExamView.vue')
  },
  {
    path: '/editor',
    name: 'Editor',
    component: () => import('@/views/EditorView.vue')
  },
  {
    path: '/export',
    name: 'Export',
    component: () => import('@/views/ExportView.vue')
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/SettingsView.vue')
  },
  {
    path: '/help',
    name: 'Help',
    component: () => import('@/views/HelpView.vue')
  },
  {
    path: '/settings/ai',
    name: 'AiSettings',
    component: () => import('@/views/AiSettingsView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
