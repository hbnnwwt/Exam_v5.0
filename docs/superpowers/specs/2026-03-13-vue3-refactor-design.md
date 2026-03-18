# 研究生复试系统 - Vue 3 前后端分离重构设计文档

## 1. 背景与目标

### 1.1 现状问题

| 问题 | 描述 | 影响 |
|------|------|------|
| 前端代码臃肿 | `index.html` 5971行，约5000行内联JS | 难以维护、调试困难 |
| API地址硬编码 | 使用 `http://localhost:5000` | 无法跨机器访问 |
| 安全配置不当 | SECRET_KEY 硬编码，debug=True | 安全隐患 |
| 状态管理混乱 | 使用全局变量管理状态 | 难以追踪、容易出错 |

### 1.2 目标

- **可维护性**：代码模块化，职责分离
- **可扩展性**：易于添加新功能
- **跨机器访问**：支持网络部署
- **安全性**：配置外部化，生产环境安全

## 2. 技术选型

| 组件 | 技术栈 | 理由 |
|------|--------|------|
| 前端框架 | Vue 3 | 学习曲线平缓、中文文档丰富 |
| 构建工具 | Vite | 启动快、HMR快、Vue官方推荐 |
| 状态管理 | Pinia | Vue 3官方推荐、TypeScript友好 |
| 路由 | Vue Router | Vue生态标准路由方案 |
| HTTP客户端 | Axios | 功能完善、拦截器支持 |
| 后端 | Flask | 保持现有技术栈 |
| CSS | 保持现有 | 避免过度改动 |

## 3. 目录结构

```
Exam_v3.2/
├── backend/                        # 后端 (Flask)
│   ├── app.py                      # Flask入口
│   ├── config.py                   # 配置管理
│   ├── apis/                       # API模块（保持现有结构）
│   │   ├── __init__.py
│   │   ├── common/
│   │   │   ├── database.py
│   │   │   └── utils.py
│   │   ├── editor/
│   │   │   ├── __init__.py
│   │   │   ├── questions.py
│   │   │   └── subjects.py
│   │   └── exam/
│   │       ├── __init__.py
│   │       ├── exam_flow.py
│   │       ├── students.py
│   │       └── questions.py
│   ├── assets/                     # 静态资源（后端服务）
│   │   ├── data/
│   │   ├── images/
│   │   └── logos/
│   └── requirements.txt
│
├── frontend/                       # 前端 (Vue 3 + Vite)
│   ├── src/
│   │   ├── main.js                 # 入口
│   │   ├── App.vue                 # 根组件
│   │   ├── api/                    # API调用层
│   │   │   ├── index.js            # API统一封装
│   │   │   └── config.js           # API配置
│   │   ├── components/             # 通用组件
│   │   │   ├── Timer.vue           # 计时器
│   │   │   ├── Toast.vue           # 消息提示
│   │   │   ├── Modal.vue           # 模态框
│   │   │   ├── Header.vue          # 顶部栏
│   │   │   └── ProgressBar.vue     # 进度条
│   │   ├── views/                  # 页面组件
│   │   │   ├── ExamView.vue        # 考试主页面
│   │   │   ├── EditorView.vue      # 题库编辑
│   │   │   ├── ExportView.vue      # 导出页面
│   │   │   ├── SettingsView.vue    # 页面设置
│   │   │   └── HeaderSettingsView.vue # 顶部设置
│   │   ├── stores/                 # 状态管理 (Pinia)
│   │   │   ├── exam.js             # 考试状态
│   │   │   ├── students.js         # 学生状态
│   │   │   └── toast.js            # 消息状态
│   │   ├── router/                 # 路由配置
│   │   │   └── index.js
│   │   ├── utils/                  # 工具函数
│   │   │   └── helpers.js
│   │   └── assets/                 # 前端静态资源
│   │       └── css/
│   │           ├── main.css
│   │           ├── progress.css
│   │           └── modern-ui.css
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
│
├── python_portable/                # 便携式Python（保持）
├── run_portable.bat                # 启动脚本（更新）
├── build.bat                       # 构建脚本（新增）
└── README.md
```

## 4. 核心组件设计

### 4.1 API配置层

```javascript
// frontend/src/api/config.js
const getBaseURL = () => {
  // 开发环境使用代理，生产环境使用相对路径
  if (import.meta.env.DEV) {
    return '/api'
  }
  // 生产环境：动态获取当前主机
  const protocol = window.location.protocol
  const host = window.location.host
  return `${protocol}//${host}/api`
}

export const apiConfig = {
  baseURL: getBaseURL(),
  timeout: 10000
}
```

### 4.2 状态管理 (Pinia)

```javascript
// frontend/src/stores/exam.js
import { defineStore } from 'pinia'

export const useExamStore = defineStore('exam', {
  state: () => ({
    currentStudent: null,
    currentStep: 1,
    examStatus: 'ready',
    timer: {
      isRunning: false,
      remainingTime: 0,
      totalTime: 0
    }
  }),

  actions: {
    setStudent(studentNumber) {
      this.currentStudent = studentNumber
    },

    startTimer(duration) {
      this.timer.isRunning = true
      this.timer.totalTime = duration
      this.timer.remainingTime = duration
    }
  }
})
```

### 4.3 后端配置

```python
# backend/config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    DATABASE = 'assets/data/interview_system.db'

class ProductionConfig(Config):
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG = True
```

## 5. 迁移策略

### 5.1 阶段一：环境搭建
1. 创建 `frontend/` 目录
2. 初始化 Vite + Vue 3 项目
3. 配置 Vite 代理

### 5.2 阶段二：后端调整
1. 创建 `backend/` 目录
2. 移动 Flask 应用
3. 添加 CORS 支持
4. 配置外部化

### 5.3 阶段三：前端迁移
1. 提取内联 JS 到 Vue 组件
2. 实现状态管理
3. 配置路由

### 5.4 阶段四：集成测试
1. 本地测试
2. 构建生产版本
3. 更新启动脚本

## 6. 风险与缓解

| 风险 | 缓解措施 |
|------|----------|
| 功能回归 | 逐页面迁移，每步验证 |
| 学习成本 | 提供代码注释和文档 |
| 部署复杂度 | 保持便携式部署方式 |

## 7. 预期成果

- 前端代码从 5971 行拆分为 ~20 个模块化文件
- API 地址自动适配，支持跨机器访问
- 安全配置外部化
- 保持便携式部署能力

---

*创建时间: 2026-03-13*
*作者: Claude Code*
