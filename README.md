# 研究生复试系统

基于 Vue 3 + Flask 的前后端分离架构的研究生复试面试系统。

## 下载版本

### [Exam_v5.0-release.zip](releases/Exam_v5.0-release.zip) (15MB)
- 需先运行 `setup.bat` 安装依赖
- 需要 Node.js 18+ 构建前端
- 适合有 Python 环境的用户

### [Exam_v5.0-portable.zip](releases/Exam_v5.0-portable.zip) (53MB)
- **解压即用**，无需安装任何环境
- 包含便携版 Python
- 适合追求开箱即用的用户

## 快速开始

### Portable 版（推荐）

```bash
# 解压后直接运行
run.bat
```

### Release 版

```bash
# 1. 解压
# 2. 安装依赖
setup.bat

# 3. 启动系统
run.bat

# 4. 访问
http://localhost:5000
```

### 开发模式

```bash
# 启动双服务器（前端 3000 + 后端 5000）
dev.bat

# 前端开发服务器
http://localhost:3000

# 后端 API
http://localhost:5000
```

### 环境要求

- **Release 版**: Python 3.8+、Node.js 18+
- **Portable 版**: 无需额外安装

## 项目结构

```
Exam_v5.0/
├── frontend/              # Vue 3 前端
│   ├── src/
│   │   ├── api/           # API 调用层
│   │   ├── components/    # 通用组件
│   │   ├── views/         # 页面组件
│   │   ├── stores/        # Pinia 状态管理
│   │   └── router/        # 路由配置
│   ├── vite.config.js
│   └── package.json
│
├── backend/               # Flask 后端
│   ├── apis/              # API 模块
│   ├── tests/             # 单元测试
│   ├── assets/            # 静态资源
│   │   ├── data/          # 数据库
│   │   ├── images/        # 图片
│   │   └── logos/         # Logo
│   ├── app.py             # 入口文件
│   ├── config.py          # 配置模块
│   └── requirements.txt   # 依赖版本锁定
│
├── python_portable/       # 便携式 Python (仅 Portable 版)
├── docs/                 # 文档
│
├── run.bat                # 启动系统
├── build.bat              # 构建前端
├── build-releases.bat     # 构建发布版本
└── dev.bat                # 开发模式
```

## API 端点

| 前缀 | 用途 |
|------|------|
| `/exam-api/*` | 考试系统 API |
| `/api/*` | 题库编辑 API |
| `/export-api/*` | 导出 API |

## 核心功能

1. **面试流程控制** - 可配置的面试流程（默认6个步骤）
2. **计时器** - 每个步骤独立计时
3. **题库管理** - 翻译题和专业题管理
4. **随机抽题** - 支持随机抽取题目
5. **考试导出** - 导出考试记录和统计数据
6. **Logo设置** - 可自定义学校/学院Logo和系统标题

## 面试环节

系统支持动态配置面试步骤，默认包含：
- 中文自我介绍
- 英文自我介绍
- 英文翻译
- 专业问题
- 综合问答
- 考试结束

## 版权信息

版权所有 © 2026 北京石油化工学院
联系方式: wangwentong@bipt.edu.cn
