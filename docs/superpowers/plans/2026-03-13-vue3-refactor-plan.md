# Vue 3 前后端分离重构 - 实施计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将研究生复试系统从单体HTML重构为Vue 3 + Flask前后端分离架构，解决API硬编码和代码可维护性问题。

**Architecture:** 前端使用Vue 3 + Vite + Pinia，后端保持Flask，通过Vite代理和动态API配置实现跨机器访问。

**Tech Stack:** Vue 3, Vite, Pinia, Vue Router, Axios, Flask, SQLite

---

## Chunk 1: 环境搭建

### Task 1.1: 创建前端项目目录

**Files:**
- Create: `frontend/` 目录结构

- [ ] **Step 1: 创建前端目录**

```bash
mkdir -p frontend/src/{api,components,views,stores,router,utils,assets/css}
```

- [ ] **Step 2: 验证目录创建**

```bash
ls -la frontend/src/
```
Expected: 显示 api, components, views, stores, router, utils, assets 目录

---

### Task 1.2: 初始化 package.json

**Files:**
- Create: `frontend/package.json`

- [ ] **Step 1: 创建 package.json**

```json
{
  "name": "exam-frontend",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.0",
    "pinia": "^2.1.0",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "vite": "^5.0.0"
  }
}
```

- [ ] **Step 2: 验证文件创建**

```bash
cat frontend/package.json
```

---

### Task 1.3: 创建 Vite 配置

**Files:**
- Create: `frontend/vite.config.js`

- [ ] **Step 1: 创建 vite.config.js**

```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  },
  build: {
    outDir: '../backend/assets/frontend',
    emptyOutDir: true
  }
})
```

- [ ] **Step 2: 验证配置**

```bash
cat frontend/vite.config.js
```

---

### Task 1.4: 创建入口 HTML

**Files:**
- Create: `frontend/index.html`

- [ ] **Step 1: 创建 index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>研究生复试流程控制系统</title>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.js"></script>
</body>
</html>
```

- [ ] **Step 2: 验证**

```bash
cat frontend/index.html
```

---

### Task 1.5: 创建 Vue 入口文件

**Files:**
- Create: `frontend/src/main.js`
- Create: `frontend/src/App.vue`

- [ ] **Step 1: 创建 main.js**

```javascript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/css/main.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.mount('#app')
```

- [ ] **Step 2: 创建 App.vue**

```vue
<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup>
// 根组件
</script>

<style>
#app {
  width: 100%;
  height: 100vh;
}
</style>
```

- [ ] **Step 3: 验证**

```bash
cat frontend/src/main.js && echo "---" && cat frontend/src/App.vue
```

---

### Task 1.6: 创建基础 CSS

**Files:**
- Create: `frontend/src/assets/css/main.css`

- [ ] **Step 1: 创建 main.css**

```css
/* 全局样式 */
:root {
  --primary-color: #007bff;
  --success-color: #28a745;
  --warning-color: #ffc107;
  --danger-color: #dc3545;
  --light-color: #f8f9fa;
  --dark-color: #343a40;
  --border-radius: 0.25rem;
  --box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  --transition: all 0.3s ease;
}

* {
  box-sizing: border-box;
}

body {
  font-family: 'Microsoft YaHei', sans-serif;
  background-color: #f8f9fa;
  color: #333;
  line-height: 1.4;
  margin: 0;
  padding: 0;
  min-height: 100vh;
}
```

- [ ] **Step 2: 验证**

```bash
cat frontend/src/assets/css/main.css
```

---

### Task 1.7: 创建 API 配置层

**Files:**
- Create: `frontend/src/api/config.js`
- Create: `frontend/src/api/index.js`

- [ ] **Step 1: 创建 api/config.js**

```javascript
/**
 * API 配置 - 自动检测后端地址
 */

const getBaseURL = () => {
  // 开发环境使用代理
  if (import.meta.env.DEV) {
    return '/api'
  }
  // 生产环境：动态获取当前主机
  const protocol = window.location.protocol
  const host = window.location.host
  return `${protocol}//${host}`
}

export const apiConfig = {
  baseURL: getBaseURL(),
  timeout: 30000
}

export default apiConfig
```

- [ ] **Step 2: 创建 api/index.js**

```javascript
import axios from 'axios'
import { apiConfig } from './config'

const api = axios.create({
  baseURL: apiConfig.baseURL,
  timeout: apiConfig.timeout,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => config,
  error => Promise.reject(error)
)

// 响应拦截器
api.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default api
```

- [ ] **Step 3: 验证**

```bash
cat frontend/src/api/config.js && echo "---" && cat frontend/src/api/index.js
```

---

### Task 1.8: 创建路由配置

**Files:**
- Create: `frontend/src/router/index.js`

- [ ] **Step 1: 创建 router/index.js**

```javascript
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
    path: '/header-settings',
    name: 'HeaderSettings',
    component: () => import('@/views/HeaderSettingsView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
```

- [ ] **Step 2: 验证**

```bash
cat frontend/src/router/index.js
```

---

### Task 1.9: 创建占位页面组件

**Files:**
- Create: `frontend/src/views/ExamView.vue`
- Create: `frontend/src/views/EditorView.vue`
- Create: `frontend/src/views/ExportView.vue`
- Create: `frontend/src/views/SettingsView.vue`
- Create: `frontend/src/views/HeaderSettingsView.vue`

- [ ] **Step 1: 创建 ExamView.vue（占位）**

```vue
<template>
  <div class="exam-view">
    <h1>考试系统</h1>
    <p>页面迁移中...</p>
  </div>
</template>

<script setup>
// 考试主页面 - 待迁移
</script>

<style scoped>
.exam-view {
  padding: 20px;
}
</style>
```

- [ ] **Step 2: 创建其他占位页面**

EditorView.vue:
```vue
<template>
  <div class="editor-view">
    <h1>题库编辑</h1>
    <p>页面迁移中...</p>
  </div>
</template>
<script setup>
</script>
```

ExportView.vue:
```vue
<template>
  <div class="export-view">
    <h1>考试导出</h1>
    <p>页面迁移中...</p>
  </div>
</template>
<script setup>
</script>
```

SettingsView.vue:
```vue
<template>
  <div class="settings-view">
    <h1>页面设置</h1>
    <p>页面迁移中...</p>
  </div>
</template>
<script setup>
</script>
```

HeaderSettingsView.vue:
```vue
<template>
  <div class="header-settings-view">
    <h1>顶部设置</h1>
    <p>页面迁移中...</p>
  </div>
</template>
<script setup>
</script>
```

- [ ] **Step 3: 验证**

```bash
ls -la frontend/src/views/
```

---

### Task 1.10: 安装前端依赖

**Files:**
- Modify: `frontend/package.json` (添加依赖)

- [ ] **Step 1: 安装依赖**

```bash
cd frontend && npm install
```
Expected: node_modules 目录创建成功

- [ ] **Step 2: 验证安装**

```bash
ls frontend/node_modules/ | head -20
```

- [ ] **Step 3: 测试开发服务器**

```bash
cd frontend && npm run dev &
sleep 5
curl http://localhost:3000 || echo "Server may need manual check"
```

---

## Chunk 2: 后端调整

### Task 2.1: 创建 backend 目录结构

**Files:**
- Create: `backend/` 目录

- [ ] **Step 1: 创建目录**

```bash
mkdir -p backend/apis/{common,editor,exam}
```

- [ ] **Step 2: 验证**

```bash
ls -la backend/
```

---

### Task 2.2: 创建后端配置模块

**Files:**
- Create: `backend/config.py`

- [ ] **Step 1: 创建 config.py**

```python
"""
后端配置模块
"""
import os

class Config:
    """基础配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    DATABASE = os.path.join(os.path.dirname(__file__), 'assets', 'data', 'interview_system.db')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB

    # 上传配置
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'assets', 'images')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'}

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    """获取当前配置"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])
```

- [ ] **Step 2: 验证**

```bash
cat backend/config.py
```

---

### Task 2.3: 创建后端入口文件

**Files:**
- Create: `backend/app.py`

- [ ] **Step 1: 创建 app.py**

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
研究生复试系统 - Flask 后端入口
"""

import os
import sys
from flask import Flask, send_from_directory
from flask_cors import CORS

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from config import get_config

# 创建 Flask 应用
app = Flask(__name__)
app.config.from_object(get_config())

# 启用 CORS（开发环境）
if app.config['DEBUG']:
    CORS(app)

# 数据库路径
DATABASE = app.config['DATABASE']

def get_db_connection():
    """获取数据库连接"""
    import sqlite3
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# 注册 API 蓝图
try:
    from apis.exam import exam_bp
    app.register_blueprint(exam_bp, url_prefix='/exam-api')
    print("✓ 已注册考试系统 API")
except ImportError as e:
    print(f"✗ 考试系统 API 注册失败: {e}")

try:
    from apis.editor import editor_bp
    app.register_blueprint(editor_bp, url_prefix='/api')
    print("✓ 已注册题库编辑 API")
except ImportError as e:
    print(f"✗ 题库编辑 API 注册失败: {e}")

try:
    from apis.exam.export import export_bp
    app.register_blueprint(export_bp, url_prefix='/export-api')
    print("✓ 已注册导出 API")
except ImportError as e:
    print(f"✗ 导出 API 注册失败: {e}")

# 静态文件服务
@app.route('/assets/<path:filename>')
def serve_assets(filename):
    """服务静态资源"""
    return send_from_directory('assets', filename)

# 前端页面服务（生产环境）
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """服务前端页面"""
    # 如果是 API 请求，跳过
    if path.startswith(('exam-api', 'api', 'export-api')):
        return {'error': 'Not found'}, 404

    # 生产环境：返回前端构建文件
    frontend_path = os.path.join(current_dir, 'assets', 'frontend')
    if os.path.exists(frontend_path):
        if path and os.path.exists(os.path.join(frontend_path, path)):
            return send_from_directory(frontend_path, path)
        return send_from_directory(frontend_path, 'index.html')

    return {'message': 'Frontend not built'}, 404

if __name__ == '__main__':
    print("=" * 40)
    print("研究生复试系统后端")
    print(f"环境: {'开发' if app.config['DEBUG'] else '生产'}")
    print(f"地址: http://localhost:5000")
    print("=" * 40)

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )
```

- [ ] **Step 2: 验证**

```bash
cat backend/app.py
```

---

### Task 2.4: 复制现有 API 模块到 backend

**Files:**
- Copy: `apis/` → `backend/apis/`

- [ ] **Step 1: 复制 API 模块**

```bash
cp -r apis/* backend/apis/
```

- [ ] **Step 2: 验证**

```bash
ls -la backend/apis/
ls -la backend/apis/common/
ls -la backend/apis/editor/
ls -la backend/apis/exam/
```

---

### Task 2.5: 复制静态资源到 backend

**Files:**
- Copy: `assets/` → `backend/assets/`

- [ ] **Step 1: 复制资源目录**

```bash
cp -r assets backend/assets
```

- [ ] **Step 2: 验证**

```bash
ls -la backend/assets/
```

---

### Task 2.6: 添加 Flask-CORS 依赖

**Files:**
- Create: `backend/requirements.txt`

- [ ] **Step 1: 创建 requirements.txt**

```txt
flask>=2.0.0
flask-cors>=4.0.0
werkzeug>=2.0.0
gunicorn>=21.0.0
```

- [ ] **Step 2: 验证**

```bash
cat backend/requirements.txt
```

---

### Task 2.7: 测试后端启动

**Files:**
- Test: `backend/app.py`

- [ ] **Step 1: 启动后端（测试）**

```bash
cd backend && python app.py &
sleep 3
curl http://localhost:5000/exam-api/test || echo "API may need database"
```

Expected: 后端启动成功，打印配置信息

- [ ] **Step 2: 停止测试服务器**

```bash
pkill -f "python.*app.py" 2>/dev/null || echo "No process to kill"
```

---

## Chunk 3: 前端核心组件迁移

### Task 3.1: 创建 Pinia 状态管理 - 考试状态

**Files:**
- Create: `frontend/src/stores/exam.js`

- [ ] **Step 1: 创建 exam.js**

```javascript
import { defineStore } from 'pinia'
import api from '@/api'

export const useExamStore = defineStore('exam', {
  state: () => ({
    // 当前考生
    currentStudent: null,
    currentStudentInfo: null,

    // 面试流程
    currentStep: 1,
    totalSteps: 6,
    examStatus: 'ready', // ready, in_progress, completed

    // 计时器
    timer: {
      isRunning: false,
      remainingTime: 0,
      totalTime: 0
    },

    // 题目
    translationQuestion: null,
    professionalQuestion: null,

    // 步骤时间配置
    stepTimes: {
      1: 60,   // 中文自我介绍 1分钟
      2: 60,   // 英文自我介绍 1分钟
      3: 240,  // 英文翻译 4分钟
      4: 300,  // 专业问题 5分钟
      5: 540,  // 综合问答 9分钟
      6: 0     // 结束
    }
  }),

  getters: {
    stepName: (state) => {
      const names = {
        1: '中文自我介绍',
        2: '英文自我介绍',
        3: '英文翻译',
        4: '专业问题',
        5: '综合问答',
        6: '考试结束'
      }
      return names[state.currentStep] || '未知步骤'
    },

    formattedTime: (state) => {
      const minutes = Math.floor(state.timer.remainingTime / 60)
      const seconds = state.timer.remainingTime % 60
      return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
    }
  },

  actions: {
    async setStudent(studentNumber) {
      this.currentStudent = studentNumber
      try {
        const response = await api.get(`/exam-api/students/${studentNumber}`)
        if (response.success) {
          this.currentStudentInfo = response.data
        }
      } catch (error) {
        console.error('获取学生信息失败:', error)
      }
    },

    nextStep() {
      if (this.currentStep < this.totalSteps) {
        this.currentStep++
        this.startStepTimer()
      }
    },

    prevStep() {
      if (this.currentStep > 1) {
        this.currentStep--
        this.startStepTimer()
      }
    },

    startStepTimer() {
      const duration = this.stepTimes[this.currentStep] || 60
      this.timer.totalTime = duration
      this.timer.remainingTime = duration
      this.timer.isRunning = true
    },

    decrementTimer() {
      if (this.timer.remainingTime > 0) {
        this.timer.remainingTime--
      } else {
        this.timer.isRunning = false
      }
    },

    pauseTimer() {
      this.timer.isRunning = false
    },

    resumeTimer() {
      this.timer.isRunning = true
    },

    resetExam() {
      this.currentStudent = null
      this.currentStudentInfo = null
      this.currentStep = 1
      this.examStatus = 'ready'
      this.timer.isRunning = false
      this.timer.remainingTime = 0
      this.translationQuestion = null
      this.professionalQuestion = null
    }
  }
})
```

- [ ] **Step 2: 验证**

```bash
cat frontend/src/stores/exam.js
```

---

### Task 3.2: 创建 Pinia 状态管理 - 消息提示

**Files:**
- Create: `frontend/src/stores/toast.js`

- [ ] **Step 1: 创建 toast.js**

```javascript
import { defineStore } from 'pinia'

export const useToastStore = defineStore('toast', {
  state: () => ({
    messages: []
  }),

  actions: {
    show(message, type = 'info', duration = 3000) {
      const id = Date.now()
      this.messages.push({ id, message, type })

      if (duration > 0) {
        setTimeout(() => {
          this.remove(id)
        }, duration)
      }

      return id
    },

    remove(id) {
      const index = this.messages.findIndex(m => m.id === id)
      if (index > -1) {
        this.messages.splice(index, 1)
      }
    },

    success(message, duration = 3000) {
      return this.show(message, 'success', duration)
    },

    error(message, duration = 4000) {
      return this.show(message, 'error', duration)
    },

    warning(message, duration = 3500) {
      return this.show(message, 'warning', duration)
    },

    info(message, duration = 3000) {
      return this.show(message, 'info', duration)
    }
  }
})
```

- [ ] **Step 2: 验证**

```bash
cat frontend/src/stores/toast.js
```

---

### Task 3.3: 创建通用组件 - Toast

**Files:**
- Create: `frontend/src/components/Toast.vue`

- [ ] **Step 1: 创建 Toast.vue**

```vue
<template>
  <div class="toast-container">
    <TransitionGroup name="toast">
      <div
        v-for="msg in toastStore.messages"
        :key="msg.id"
        :class="['toast', `toast-${msg.type}`]"
        @click="toastStore.remove(msg.id)"
      >
        <span class="toast-icon">{{ iconMap[msg.type] }}</span>
        <span class="toast-message">{{ msg.message }}</span>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup>
import { useToastStore } from '@/stores/toast'

const toastStore = useToastStore()

const iconMap = {
  success: '✓',
  error: '✗',
  warning: '⚠',
  info: 'ℹ'
}
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.toast {
  padding: 12px 20px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
}

.toast:hover {
  transform: translateX(-5px);
}

.toast-success {
  background: #28a745;
  color: white;
}

.toast-error {
  background: #dc3545;
  color: white;
}

.toast-warning {
  background: #ffc107;
  color: #333;
}

.toast-info {
  background: #17a2b8;
  color: white;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}
</style>
```

- [ ] **Step 2: 验证**

```bash
cat frontend/src/components/Toast.vue
```

---

### Task 3.4: 创建通用组件 - Timer

**Files:**
- Create: `frontend/src/components/Timer.vue`

- [ ] **Step 1: 创建 Timer.vue**

```vue
<template>
  <div class="timer" :class="{ 'timer-warning': isWarning, 'timer-danger': isDanger }">
    <div class="timer-display">
      <span class="timer-icon">⏱</span>
      <span class="timer-time">{{ examStore.formattedTime }}</span>
    </div>
    <div class="timer-controls">
      <button
        v-if="!examStore.timer.isRunning"
        class="timer-btn start"
        @click="start"
        :disabled="examStore.timer.remainingTime === 0"
      >
        ▶ 开始
      </button>
      <button
        v-else
        class="timer-btn pause"
        @click="pause"
      >
        ⏸ 暂停
      </button>
      <button class="timer-btn reset" @click="reset">
        ↺ 重置
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { useExamStore } from '@/stores/exam'

const examStore = useExamStore()
const intervalId = ref(null)

const isWarning = computed(() => {
  return examStore.timer.remainingTime <= 60 && examStore.timer.remainingTime > 30
})

const isDanger = computed(() => {
  return examStore.timer.remainingTime <= 30
})

const start = () => {
  if (examStore.timer.remainingTime === 0) {
    examStore.startStepTimer()
  }
  examStore.resumeTimer()
  intervalId.value = setInterval(() => {
    examStore.decrementTimer()
  }, 1000)
}

const pause = () => {
  examStore.pauseTimer()
  if (intervalId.value) {
    clearInterval(intervalId.value)
    intervalId.value = null
  }
}

const reset = () => {
  pause()
  examStore.startStepTimer()
}

onUnmounted(() => {
  if (intervalId.value) {
    clearInterval(intervalId.value)
  }
})
</script>

<style scoped>
.timer {
  background: #fff;
  border-radius: 12px;
  padding: 15px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.timer-warning {
  background: #fff3cd;
  border: 2px solid #ffc107;
}

.timer-danger {
  background: #f8d7da;
  border: 2px solid #dc3545;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.timer-display {
  display: flex;
  align-items: center;
  gap: 10px;
}

.timer-icon {
  font-size: 24px;
}

.timer-time {
  font-size: 28px;
  font-weight: bold;
  font-family: monospace;
}

.timer-controls {
  display: flex;
  gap: 8px;
}

.timer-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.timer-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.timer-btn.start {
  background: #28a745;
  color: white;
}

.timer-btn.pause {
  background: #ffc107;
  color: #333;
}

.timer-btn.reset {
  background: #6c757d;
  color: white;
}

.timer-btn:hover:not(:disabled) {
  opacity: 0.9;
  transform: scale(1.02);
}
</style>
```

- [ ] **Step 2: 验证**

```bash
cat frontend/src/components/Timer.vue
```

---

### Task 3.5: 更新 App.vue 集成 Toast

**Files:**
- Modify: `frontend/src/App.vue`

- [ ] **Step 1: 更新 App.vue**

```vue
<template>
  <div id="app">
    <router-view />
    <Toast />
  </div>
</template>

<script setup>
import Toast from '@/components/Toast.vue'
</script>

<style>
#app {
  width: 100%;
  min-height: 100vh;
}
</style>
```

- [ ] **Step 2: 验证**

```bash
cat frontend/src/App.vue
```

---

## Chunk 4: 主页面迁移（核心功能）

### Task 4.1: 创建考试主页面 - 结构

**Files:**
- Modify: `frontend/src/views/ExamView.vue`

- [ ] **Step 1: 创建 ExamView.vue（完整结构）**

由于原 index.html 有约 5000 行内联 JS，这里先创建基础框架：

```vue
<template>
  <div class="exam-page">
    <!-- 顶部栏 -->
    <header class="header">
      <div class="header-content">
        <div class="header-logos">
          <img v-if="settings.instituteLogo" :src="settings.instituteLogo" class="logo" alt="学院Logo">
          <img v-if="settings.collegeLogo" :src="settings.collegeLogo" class="logo" alt="学校Logo">
        </div>
        <h1 class="header-title">{{ settings.title }}</h1>
        <div class="header-controls">
          <span v-if="examStore.currentStudent" class="current-student">
            当前考生: {{ examStore.currentStudent }}
          </span>
          <router-link to="/editor" class="nav-btn">题库管理</router-link>
          <router-link to="/export" class="nav-btn">导出</router-link>
          <router-link to="/settings" class="nav-btn">设置</router-link>
        </div>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="main-content">
      <!-- 左侧面板 - 考试流程 -->
      <aside class="left-panel" :class="{ collapsed: leftPanelCollapsed }">
        <button class="panel-toggle" @click="leftPanelCollapsed = !leftPanelCollapsed">
          {{ leftPanelCollapsed ? '▶' : '◀' }}
        </button>
        <div v-if="!leftPanelCollapsed" class="panel-content">
          <h3>面试流程</h3>
          <div class="step-list">
            <div
              v-for="step in steps"
              :key="step.id"
              :class="['step-item', { active: examStore.currentStep === step.id, completed: examStore.currentStep > step.id }]"
              @click="goToStep(step.id)"
            >
              <span class="step-number">{{ step.id }}</span>
              <span class="step-name">{{ step.name }}</span>
            </div>
          </div>
        </div>
      </aside>

      <!-- 中间内容区 -->
      <section class="center-panel">
        <!-- 考生输入区 -->
        <div v-if="!examStore.currentStudent" class="student-input-area">
          <h2>请输入考生号</h2>
          <div class="input-group">
            <input
              v-model="studentNumber"
              type="text"
              placeholder="输入考生号"
              @keyup.enter="loadStudent"
              class="student-input"
            >
            <button @click="loadStudent" class="load-btn">开始考试</button>
          </div>
        </div>

        <!-- 考试内容区 -->
        <div v-else class="exam-content">
          <div class="step-header">
            <h2>{{ examStore.stepName }}</h2>
            <Timer />
          </div>

          <!-- 步骤内容 -->
          <div class="step-content">
            <StepContent :step="examStore.currentStep" />
          </div>

          <!-- 控制按钮 -->
          <div class="step-controls">
            <button
              @click="prevStep"
              :disabled="examStore.currentStep <= 1"
              class="control-btn prev"
            >
              ◀ 上一步
            </button>
            <button @click="completeExam" class="control-btn complete">
              ✓ 完成考试
            </button>
            <button
              @click="nextStep"
              :disabled="examStore.currentStep >= examStore.totalSteps"
              class="control-btn next"
            >
              下一步 ▶
            </button>
          </div>
        </div>
      </section>

      <!-- 右侧面板 - 控制面板 -->
      <aside class="right-panel" :class="{ collapsed: rightPanelCollapsed }">
        <button class="panel-toggle" @click="rightPanelCollapsed = !rightPanelCollapsed">
          {{ rightPanelCollapsed ? '◀' : '▶' }}
        </button>
        <div v-if="!rightPanelCollapsed" class="panel-content">
          <h3>控制面板</h3>
          <!-- 控制面板内容待完善 -->
        </div>
      </aside>
    </main>

    <!-- 底部版权 -->
    <footer class="footer">
      <p>版权所有 © 2025 北京石油化工学院</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useExamStore } from '@/stores/exam'
import { useToastStore } from '@/stores/toast'
import api from '@/api'
import Timer from '@/components/Timer.vue'
import StepContent from '@/components/StepContent.vue'

const examStore = useExamStore()
const toast = useToastStore()

// 状态
const studentNumber = ref('')
const leftPanelCollapsed = ref(false)
const rightPanelCollapsed = ref(false)
const settings = ref({
  title: '研究生复试流程控制系统',
  instituteLogo: null,
  collegeLogo: null
})

// 步骤列表
const steps = [
  { id: 1, name: '中文自我介绍' },
  { id: 2, name: '英文自我介绍' },
  { id: 3, name: '英文翻译' },
  { id: 4, name: '专业问题' },
  { id: 5, name: '综合问答' },
  { id: 6, name: '考试结束' }
]

// 加载考生
const loadStudent = async () => {
  if (!studentNumber.value.trim()) {
    toast.warning('请输入考生号')
    return
  }

  try {
    const response = await api.get(`/exam-api/students/${studentNumber.value}`)
    if (response.success) {
      await examStore.setStudent(studentNumber.value)
      examStore.startStepTimer()
      toast.success(`已加载考生: ${studentNumber.value}`)
    } else {
      toast.error('考生不存在')
    }
  } catch (error) {
    toast.error('加载考生失败: ' + error.message)
  }
}

// 步骤导航
const goToStep = (stepId) => {
  if (stepId <= examStore.currentStep) {
    examStore.currentStep = stepId
    examStore.startStepTimer()
  }
}

const prevStep = () => {
  examStore.prevStep()
}

const nextStep = () => {
  examStore.nextStep()
}

const completeExam = () => {
  examStore.examStatus = 'completed'
  toast.success('考试已完成！')
  // TODO: 保存考试记录
}

// 加载设置
const loadSettings = async () => {
  try {
    const response = await api.get('/api/header-settings')
    if (response.success) {
      settings.value = response.data
    }
  } catch (error) {
    console.error('加载设置失败:', error)
  }
}

onMounted(() => {
  loadSettings()
})
</script>

<style scoped>
.exam-page {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: #f8f9fa;
}

/* 顶部栏 */
.header {
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
  padding: 15px 20px;
  flex-shrink: 0;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1400px;
  margin: 0 auto;
}

.header-logos {
  display: flex;
  gap: 15px;
}

.logo {
  height: 45px;
  object-fit: contain;
}

.header-title {
  font-size: 1.8rem;
  color: #1f2937;
  margin: 0;
}

.header-controls {
  display: flex;
  gap: 10px;
  align-items: center;
}

.current-student {
  color: #6b7280;
  font-size: 14px;
}

.nav-btn {
  padding: 8px 16px;
  background: var(--primary-color);
  color: white;
  text-decoration: none;
  border-radius: 6px;
  font-size: 14px;
  transition: opacity 0.2s;
}

.nav-btn:hover {
  opacity: 0.9;
}

/* 主内容区 */
.main-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* 侧边栏 */
.left-panel,
.right-panel {
  width: 200px;
  background: #fff;
  border-right: 1px solid #e5e7eb;
  position: relative;
  transition: width 0.3s ease;
}

.left-panel.collapsed,
.right-panel.collapsed {
  width: 40px;
}

.right-panel {
  border-right: none;
  border-left: 1px solid #e5e7eb;
}

.panel-toggle {
  position: absolute;
  top: 50%;
  width: 20px;
  height: 60px;
  background: #f0f0f0;
  border: 1px solid #ccc;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.left-panel .panel-toggle {
  right: -10px;
}

.right-panel .panel-toggle {
  left: -10px;
}

.panel-content {
  padding: 15px;
}

/* 步骤列表 */
.step-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.step-item:hover {
  background: #f3f4f6;
}

.step-item.active {
  background: var(--primary-color);
  color: white;
}

.step-item.completed {
  background: #d1fae5;
}

.step-number {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}

.step-item.active .step-number {
  background: white;
  color: var(--primary-color);
}

/* 中间内容区 */
.center-panel {
  flex: 1;
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.student-input-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
}

.input-group {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.student-input {
  padding: 12px 20px;
  font-size: 18px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  width: 300px;
}

.load-btn {
  padding: 12px 30px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
}

/* 考试内容区 */
.exam-content {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.step-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.step-content {
  flex: 1;
  overflow-y: auto;
}

.step-controls {
  display: flex;
  justify-content: center;
  gap: 20px;
  padding-top: 20px;
}

.control-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.control-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.control-btn.prev {
  background: #6c757d;
  color: white;
}

.control-btn.next {
  background: var(--primary-color);
  color: white;
}

.control-btn.complete {
  background: var(--success-color);
  color: white;
}

/* 底部 */
.footer {
  text-align: center;
  padding: 15px;
  background: #fff;
  border-top: 1px solid #e5e7eb;
  color: #6b7280;
  font-size: 14px;
}
</style>
```

- [ ] **Step 2: 验证**

```bash
cat frontend/src/views/ExamView.vue | head -100
```

---

### Task 4.2: 创建步骤内容组件

**Files:**
- Create: `frontend/src/components/StepContent.vue`

- [ ] **Step 1: 创建 StepContent.vue**

```vue
<template>
  <div class="step-content-wrapper">
    <!-- 步骤 1: 中文自我介绍 -->
    <div v-if="step === 1" class="step-intro">
      <h3>中文自我介绍</h3>
      <p>请考生用中文进行自我介绍，时间约1分钟。</p>
    </div>

    <!-- 步骤 2: 英文自我介绍 -->
    <div v-if="step === 2" class="step-intro">
      <h3>英文自我介绍</h3>
      <p>Please introduce yourself in English, about 1 minute.</p>
    </div>

    <!-- 步骤 3: 英文翻译 -->
    <div v-if="step === 3" class="step-translation">
      <h3>英文翻译</h3>
      <div v-if="examStore.translationQuestion" class="question-display">
        <div class="question-content" v-html="renderQuestion(examStore.translationQuestion)"></div>
      </div>
      <div v-else class="no-question">
        <button @click="selectQuestion('translation')" class="select-btn">
          抽取翻译题目
        </button>
      </div>
    </div>

    <!-- 步骤 4: 专业问题 -->
    <div v-if="step === 4" class="step-professional">
      <h3>专业问题</h3>
      <div v-if="examStore.professionalQuestion" class="question-display">
        <div class="question-content" v-html="renderQuestion(examStore.professionalQuestion)"></div>
      </div>
      <div v-else class="no-question">
        <button @click="selectQuestion('professional')" class="select-btn">
          抽取专业题目
        </button>
      </div>
    </div>

    <!-- 步骤 5: 综合问答 -->
    <div v-if="step === 5" class="step-qna">
      <h3>综合问答</h3>
      <p>考官可进行综合提问。</p>
    </div>

    <!-- 步骤 6: 考试结束 -->
    <div v-if="step === 6" class="step-complete">
      <h3>考试结束</h3>
      <p>感谢考生的配合！</p>
    </div>
  </div>
</template>

<script setup>
import { useExamStore } from '@/stores/exam'
import { useToastStore } from '@/stores/toast'
import api from '@/api'

const props = defineProps({
  step: {
    type: Number,
    required: true
  }
})

const examStore = useExamStore()
const toast = useToastStore()

// 渲染题目内容
const renderQuestion = (questionData) => {
  if (!questionData) return ''

  try {
    const data = typeof questionData === 'string' ? JSON.parse(questionData) : questionData
    if (Array.isArray(data)) {
      return data.map(item => {
        if (item[0] === 'txt') {
          return `<p>${item[1]}</p>`
        } else if (item[0] === 'img') {
          return `<img src="${item[1]}" alt="题目图片" style="max-width: 100%;">`
        }
        return ''
      }).join('')
    }
  } catch (e) {
    return questionData
  }

  return questionData
}

// 抽取题目
const selectQuestion = async (type) => {
  try {
    const response = await api.get(`/exam-api/questions/${type}/available`)
    if (response.success && response.data.length > 0) {
      // TODO: 显示题目选择模态框
      toast.info(`找到 ${response.data.length} 道可用题目`)
    } else {
      toast.warning('没有可用的题目')
    }
  } catch (error) {
    toast.error('获取题目失败: ' + error.message)
  }
}
</script>

<style scoped>
.step-content-wrapper {
  padding: 20px;
  background: #fff;
  border-radius: 12px;
  min-height: 300px;
}

.step-intro,
.step-qna,
.step-complete {
  text-align: center;
  padding: 40px;
}

.step-intro h3,
.step-qna h3,
.step-complete h3 {
  font-size: 1.5rem;
  margin-bottom: 15px;
}

.question-display {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.no-question {
  text-align: center;
  padding: 40px;
}

.select-btn {
  padding: 12px 30px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
}
</style>
```

- [ ] **Step 2: 验证**

```bash
cat frontend/src/components/StepContent.vue
```

---

## Chunk 5: 集成与部署

### Task 5.1: 构建前端生产版本

**Files:**
- Run: `npm run build`

- [ ] **Step 1: 构建前端**

```bash
cd frontend && npm run build
```
Expected: 输出到 `backend/assets/frontend/`

- [ ] **Step 2: 验证构建输出**

```bash
ls -la backend/assets/frontend/
```

---

### Task 5.2: 更新启动脚本

**Files:**
- Create: `run.bat`（新版启动脚本）

- [ ] **Step 1: 创建 run.bat**

```batch
@echo off
echo ====================================
echo 研究生复试系统 - 启动
echo ====================================

cd backend

REM 设置环境变量
set FLASK_ENV=production
set FLASK_DEBUG=false

REM 启动后端服务器
python_portable\python.exe app.py
```

- [ ] **Step 2: 验证**

```bash
cat run.bat
```

---

### Task 5.3: 创建构建脚本

**Files:**
- Create: `build.bat`

- [ ] **Step 1: 创建 build.bat**

```batch
@echo off
echo ====================================
echo 构建前端
echo ====================================

cd frontend

REM 检查 node_modules
if not exist "node_modules" (
    echo 安装依赖...
    npm install
)

REM 构建
echo 构建生产版本...
npm run build

echo ====================================
echo 构建完成！
echo 输出目录: backend/assets/frontend/
echo ====================================
pause
```

- [ ] **Step 2: 验证**

```bash
cat build.bat
```

---

### Task 5.4: 最终测试

**Files:**
- Test: 完整系统

- [ ] **Step 1: 启动后端**

```bash
cd backend && ../python_portable/python.exe app.py &
sleep 3
```

- [ ] **Step 2: 测试 API**

```bash
curl http://localhost:5000/exam-api/test
```
Expected: `{"success": true, ...}`

- [ ] **Step 3: 访问前端**

打开浏览器访问 `http://localhost:5000`

- [ ] **Step 4: 功能验证**

检查以下功能：
- [ ] 考生号输入
- [ ] 计时器
- [ ] 步骤切换
- [ ] 题目抽取

---

### Task 5.5: 提交代码

- [ ] **Step 1: 查看变更**

```bash
git status
```

- [ ] **Step 2: 提交**

```bash
git add .
git commit -m "feat: Vue 3 前后端分离重构

- 创建 Vue 3 + Vite 前端项目
- 实现动态 API 配置，支持跨机器访问
- 添加 Pinia 状态管理
- 创建核心组件 (Timer, Toast, StepContent)
- 迁移考试主页面
- 配置外部化

Co-Authored-By: Claude Code <noreply@anthropic.com>"
```

---

## 完成检查清单

- [ ] 前端项目结构创建完成
- [ ] 后端配置外部化
- [ ] API 地址动态配置
- [ ] 核心组件实现
- [ ] 主页面迁移完成
- [ ] 构建和启动脚本可用
- [ ] 功能测试通过

---

*创建时间: 2026-03-13*
*基于设计文档: docs/superpowers/specs/2026-03-13-vue3-refactor-design.md*
