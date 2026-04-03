# 帮助文档站点重构设计规范

**日期：** 2026-04-03
**状态：** 已批准

---

## 1. 概念与愿景

将帮助文档中心从"简陋的说明文本"升级为"专业的文档站点"。参考 GitBook / Notion 文档风格——左侧固定导航、右侧内容区、清晰的视觉层次。让用户在阅读帮助时感受到系统的专业性和用心程度。

---

## 2. 设计语言

### 配色
| Token | 色值 | 用途 |
|-------|------|------|
| `--primary` | #4f46e5 | 主按钮、章节标题下划线、激活导航 |
| `--accent` | #06b6d4 | AI 配置专属色 |
| `--success` | #10b981 | Tip 提示框 |
| `--warning` | #f59e0b | 注意提示框 |
| `--danger` | #ef4444 | 警告提示框 |
| `--bg` | #f8fafc | 页面背景 |
| `--surface` | #ffffff | 卡片背景 |
| `--text` | #0f172a | 主文本 |
| `--text-secondary` | #475569 | 副文本 |
| `--text-muted` | #94a3b8 | 辅助文本 |
| `--border` | #e2e8f0 | 边框 |

### 字体
- 主字体：Noto Sans SC（正文）
- 英文字体：Inter（UI 元素）
- 代码字体：Consolas / monospace

### 圆角 & 阴影
- 卡片：radius 16px，shadow: `0 4px 6px rgba(0,0,0,0.07)`
- 按钮：radius 8px
- 输入框：radius 8px

### 图标
- 全部使用 Lucide SVG 内联图标（viewBox="0 0 24 24"）
- 尺寸：标题图标 48px / 卡片图标 36px / 导航图标 18px
- 不使用 emoji

---

## 3. 页面结构

### 所有帮助页通用布局

```
┌─────────────────────────────────────────────────────────┐
│  ┌──────────┐  ┌──────────────────────────────────────┐  │
│  │ Sidebar  │  │         Content Area                 │  │
│  │  (240px) │  │                                      │  │
│  │          │  │  [Page Title Card]                   │  │
│  │  Logo    │  │                                      │  │
│  │  Nav     │  │  [Section Card 1]                    │  │
│  │  Links   │  │                                      │  │
│  │          │  │  [Section Card 2]                    │  │
│  │  Version │  │                                      │  │
│  └──────────┘  │  ...                                 │  │
│                └──────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Sidebar（左侧固定栏，240px）
- 顶部：图标 + "帮助文档中心" 标题
- 导航：当前页面各章节的锚点链接
- 激活状态：左侧有 3px 主色边框 + 浅紫背景
- 底部：系统版本 v3.1
- 返回首页：`← 返回文档中心` 链接

### 内容区
- max-width: 860px，右侧留白
- 每个章节 = 一张白色卡片
- 卡片内：章节标题（带左侧竖线颜色）+ 内容

### 响应式
- < 768px：Sidebar 隐藏，显示 hamburger 按钮，点击展开抽屉

---

## 4. 组件

### 提示框（3种）
```
.info-box   → 蓝色左边框  (#17a2b8)，浅蓝背景
.warning-box → 红色左边框 (#dc3545)，浅红背景
.tip-box    → 绿色左边框  (#28a745)，浅绿背景
```

### 截图展示
- 居中，max-width: 100%
- 圆角 8px，1px 边框，投影
- 下方 caption：斜体，灰色，text-sm

### 步骤列表
- 浅黄背景 (#fff3cd)，黄色左边框 (#ffc107)
- 有序列表样式

### 功能列表
- 浅灰背景 (#f8f9fa)，绿色左边框 (#28a745)

### 表格
- 100% 宽度，圆角，斑马纹（奇偶行背景不同）
- 表头：浅灰背景 + 粗体

### 快捷键标签
- `<kbd>` 样式：浅灰背景，4px 圆角，等宽字体，深色边框（底部 1px）

### 导航栏链接
- `<a>` 标签，跳转到页面内锚点
- hover：有背景色 + 主色文字

---

## 5. 8 个页面内容清单

### 5.1 exam-system-help.html（考试系统）
- 系统概述
- 界面布局说明（含截图 exam-system-main.png）
- 六步考试流程详解（表格）
- 操作控制（表格：按钮/快捷键/功能）
- 系统设置（含截图 exam-system-settings.png）
- 常见问题

### 5.2 database-editor-help.html（题库编辑器）
- 功能介绍
- 界面说明（含截图 database-editor-main.png）
- 翻译题管理
- 专业题管理
- 科目分类
- 批量导入导出
- 注意事项

### 5.3 header-setting-help.html（顶部设置）
- Logo 设置说明（含截图 header-setting-main.png）
- 考试标题设置
- 图片要求（格式、尺寸）

### 5.4 page-content-setting-help.html（步骤内容设置）
- 内容管理说明（含截图 page-content-setting-main.png）
- 步骤选择
- 内容块编辑
- 启用/禁用控制

### 5.5 export-exam-help.html（考试导出）
- 统计概览（含截图 export-exam-main.png）
- 导出 Excel
- 生成 HTML 报告
- 导出格式说明

### 5.6 ai-settings-help.html（AI 配置）【新增】
- 功能介绍
- 支持的提供商（表格：OpenAI/Claude/Gemini/MiniMax/ModelScope/硅基流动）
- 配置步骤
- 自定义提供商
- 安全提示

### 5.7 shortcuts-help.html（快捷键参考）【新增】
- 快捷键总表（完整 8 条）
- 使用说明
- 适用场景

### 5.8 faq-help.html（常见问题）【新增】
- 数据库连接问题
- 题目抽取问题
- 计时器问题
- 状态恢复问题
- AI 出题问题
- 数据备份问题

### 5.9 index.html（更新）
- 补充 AI 配置入口卡片
- 补充快捷键参考入口卡片
- 补充 FAQ 入口卡片
- 其他 5 个入口保持现有新设计风格

---

## 6. 技术约束

- 纯 HTML + CSS（无 JavaScript 依赖，sidebar 响应式用 CSS media query 实现）
- 图片路径：`./xxx.png`（与 HTML 文件同目录）
- 所有 SVG 图标内联嵌入（不依赖外部 CDN）
- Google Fonts 通过 CDN 引入（Noto Sans SC + Inter）
- 兼容现代浏览器（Chrome / Firefox / Safari / Edge 最近 2 个版本
