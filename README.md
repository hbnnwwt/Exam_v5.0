# 研究生复试系统

基于 Vue 3 + Flask 的前后端分离架构的研究生复试面试系统。

## 下载版本

### [Exam_v5.0-portable.zip](https://github.com/hbnnwwt/Exam_v5.0/releases/download/v1.0.8/Exam_v5.0-portable.zip) (54MB)
- **解压即用**，无需安装任何环境
- 包含便携版 Python
- 适合追求开箱即用的用户

### [Exam_v5.0-release.zip](https://github.com/hbnnwwt/Exam_v5.0/releases/download/v1.0.8/Exam_v5.0-release.zip) (2MB)
- 需先运行 `setup.bat` 安装依赖
- 需要 Node.js 18+ 构建前端
- 适合有 Python 环境的用户

### [Exam_v5.0-Source.zip](https://github.com/hbnnwwt/Exam_v5.0/releases/download/v1.0.8/Exam_v5.0-Source.zip) (67MB)
- 完整源码

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
3. **题库管理** - 翻译题和专业题管理，支持批量导入
4. **随机抽题** - 支持随机抽取题目
5. **考试导出** - 导出考试记录和统计数据（Excel / PDF / HTML）
6. **Logo设置** - 可自定义学校/学院Logo和系统标题
7. **AI 智能出题** - 基于 AI 自动生成翻译题和专业问题，支持套题模式和批量生成
8. **多 AI Provider** - 支持 OpenAI / Claude / Gemini / MiniMax / ModelScope / SiliconFlow 等
9. **庄重面试风 UI** - 专业、沉稳的视觉设计，深石板灰 + 金色强调色

## 更新日志

### v1.0.8 (2026-04-02)
- **安全修复**：移除所有硬编码 API Key，配置文件不再包含敏感信息
- **AI 智能出题**：支持单题生成、套题生成、批量生成三种模式
- **AI 候选结果**：生成多个候选答案，标注差异（基础 / 应用 / 深度）
- **多 Provider 管理**：支持配置多个 AI 服务商，一键切换默认 Provider
- **UI 全面优化**：AI 设置页 / 导出页 / 设置页统一使用设计令牌系统

### v1.0.7 (2026-04-01)
- 考生面试界面全新设计
- 庄重面试风 UI 配色
- 金色高亮步骤卡片
- 平滑过渡动画效果

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
