# 研究生复试系统

基于 Vue 3 + Flask 的前后端分离架构的研究生复试面试系统。

## 下载版本

### [Exam_v5.0-portable.zip](https://github.com/hbnnwwt/Exam_v5.0/releases/download/v1.0.10/Exam_v5.0-portable.zip) (54MB)
- **解压即用**，无需安装任何环境
- 包含便携版 Python
- 适合追求开箱即用的用户

### [Exam_v5.0-release.zip](https://github.com/hbnnwwt/Exam_v5.0/releases/download/v1.0.10/Exam_v5.0-release.zip) (2MB)
- 需先运行 `setup.bat` 安装依赖
- 需要 Node.js 18+ 构建前端
- 适合有 Python 环境的用户

### [Exam_v5.0-Source.zip](https://github.com/hbnnwwt/Exam_v5.0/releases/download/v1.0.10/Exam_v5.0-Source.zip) (67MB)
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

### AI Key 配置

系统支持三种方式配置 AI Provider Key，优先级依次为：**环境变量 > 数据库 > JSON 模板**。

#### 方式一：环境变量（推荐，生产部署用）

复制 `env.example` 为 `.env`，填入真实 Key：

```env
MINIMAX_API_KEY=sk-cp-xxx
SILICONFLOW_API_KEY=sk-xxx
```

环境变量会覆盖数据库和 JSON 模板中的配置。

#### 方式二：UI 配置（便携场景用）

启动系统后访问 **AI 设置** 页面，直接在界面填写 Key。配置保存到本地数据库，换电脑不丢失。

#### 方式三：JSON 模板（仅默认配置，无 Key）

`backend/apis/config/ai_providers.json` 包含各 Provider 的默认 base_url 和模型名，但不含真实 Key。新用户首次使用需先配置 Key。

#### 安全说明

- `env.example` 已包含所有 Provider 的环境变量说明
- 发布包（release/portable）**不包含** `interview_system.db` 和 `ai_providers.json`，不会泄露真实 Key
- 切勿将包含真实 Key 的 `ai_providers.json` 提交到 GitHub

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
├── docs/                  # 静态帮助文档 (HTML + 截图)
├── python_portable/       # 便携式 Python (仅 Portable 版)
│
├── run.bat                # 启动系统
├── build.bat              # 构建前端
├── build-release.bat     # 构建发布版本 (release + portable)
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
10. **双体系帮助文档** - Vue SPA 快速参考（`/help`）+ 静态 HTML 深度文档（`docs/`）

## 帮助文档

系统提供两层帮助文档：

| 入口 | 路由/路径 | 定位 |
|------|----------|------|
| 内嵌帮助 | `/help` | 快速参考，8 章节覆盖日常操作 |
| 文档中心 | `docs/index.html` | 深度文档，含详细截图和技术架构 |

所有页面顶部导航均设有帮助入口。

## 更新日志

### v1.0.10 (2026-04-07)
- **帮助文档体系重构**：新增 Vue SPA 内嵌帮助（`/help`），8 章节快速参考
- **深度文档完善**：静态 HTML 帮助页全面接入截图（考试设置/题库管理/AI配置/导出）
- **HeaderSettingsView.vue 已移除**：功能合并到统一设置页面
- **新增 build-release.bat**：一键构建 release/portable 双版本

### v1.0.9 (2026-04-02)
- **API Key 安全存储**：新增 `api_keys` 数据库表，Key 从环境变量/数据库/JSON 三层递进读取
- **Key 泄露防护**：API 接口不再返回 Key 明文，只返回 `hasApiKey` 布尔标志
- **测试连接优化**：测试连接支持自动读取已有 Key，无需重复填写
- **env.example**：新增环境变量配置模板，部署更安全便捷

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
