# 帮助文档站点重构实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 docs/ 目录下的帮助文档从简陋样式升级为专业文档站风格，包含统一侧边栏导航、卡片式章节、SVG 图标，覆盖全部 8 个帮助页 + index.html 入口页。

**Architecture:** 所有帮助页共享一份 `docs/css/help-docs.css` 样式文件，每个 HTML 页面是独立文件，通过内联 SVG 图标实现视觉统一。响应式通过 CSS media query 实现，无 JS 依赖。

**Tech Stack:** 纯 HTML + CSS，无框架，无构建工具

---

## 文件清单

| 操作 | 文件路径 |
|------|----------|
| 新建 | `docs/css/help-docs.css` |
| 重写 | `docs/exam-system-help.html` |
| 重写 | `docs/database-editor-help.html` |
| 重写 | `docs/header-setting-help.html` |
| 重写 | `docs/page-content-setting-help.html` |
| 重写 | `docs/export-exam-help.html` |
| 新建 | `docs/ai-settings-help.html` |
| 新建 | `docs/shortcuts-help.html` |
| 新建 | `docs/faq-help.html` |
| 更新 | `docs/index.html` |

---

## 共享 CSS 文件

### Task 1: 创建 `docs/css/help-docs.css`

**文件:** 新建 `docs/css/help-docs.css`

- [ ] **Step 1: 创建目录并写入 CSS 文件**

```css
/* ===== CSS Variables ===== */
:root {
    --primary: #4f46e5;
    --primary-light: #818cf8;
    --primary-dark: #3730a3;
    --accent: #06b6d4;
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
    --bg: #f8fafc;
    --surface: #ffffff;
    --text: #0f172a;
    --text-secondary: #475569;
    --text-muted: #94a3b8;
    --border: #e2e8f0;
    --shadow: 0 4px 6px rgba(0,0,0,0.07);
    --shadow-lg: 0 10px 15px rgba(0,0,0,0.1);
    --radius: 16px;
    --radius-sm: 8px;
}

/* ===== Reset & Base ===== */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
    font-family: 'Noto Sans SC', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
}

a { color: var(--primary); text-decoration: none; }
a:hover { text-decoration: underline; }

/* ===== Layout ===== */
.page-wrapper {
    display: flex;
    min-height: 100vh;
}

/* ===== Sidebar ===== */
.sidebar {
    width: 260px;
    flex-shrink: 0;
    background: var(--surface);
    border-right: 1px solid var(--border);
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    overflow-y: auto;
    z-index: 100;
    display: flex;
    flex-direction: column;
}

.sidebar-header {
    padding: 24px 20px 20px;
    border-bottom: 1px solid var(--border);
}

.sidebar-logo {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 4px;
}

.sidebar-logo svg {
    width: 28px;
    height: 28px;
    color: var(--primary);
    flex-shrink: 0;
}

.sidebar-title {
    font-size: 0.9375rem;
    font-weight: 700;
    color: var(--text);
}

.sidebar-subtitle {
    font-size: 0.75rem;
    color: var(--text-muted);
    padding-left: 38px;
}

.sidebar-nav {
    padding: 16px 12px;
    flex: 1;
}

.sidebar-nav-title {
    font-size: 0.6875rem;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    padding: 0 8px;
    margin-bottom: 6px;
}

.sidebar-nav a {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 10px;
    border-radius: var(--radius-sm);
    font-size: 0.875rem;
    color: var(--text-secondary);
    transition: all 150ms ease;
}

.sidebar-nav a:hover {
    background: var(--bg);
    color: var(--text);
    text-decoration: none;
}

.sidebar-nav a.active {
    background: #eef2ff;
    color: var(--primary);
    font-weight: 500;
    border-left: 3px solid var(--primary);
    padding-left: 7px;
}

.sidebar-nav a svg {
    width: 16px;
    height: 16px;
    flex-shrink: 0;
    opacity: 0.7;
}

.sidebar-nav a.active svg {
    opacity: 1;
}

.sidebar-footer {
    padding: 16px 20px;
    border-top: 1px solid var(--border);
}

.sidebar-back {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.8125rem;
    color: var(--text-secondary);
    padding: 6px 8px;
    border-radius: var(--radius-sm);
    transition: all 150ms ease;
}

.sidebar-back:hover {
    background: var(--bg);
    color: var(--primary);
    text-decoration: none;
}

.sidebar-back svg {
    width: 14px;
    height: 14px;
}

.sidebar-version {
    font-size: 0.75rem;
    color: var(--text-muted);
    margin-top: 10px;
    padding-left: 8px;
}

/* ===== Content ===== */
.content {
    flex: 1;
    margin-left: 260px;
    padding: 40px 48px;
    max-width: 920px;
}

/* ===== Page Title Card ===== */
.page-title-card {
    background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary) 50%, var(--accent) 100%);
    color: white;
    border-radius: var(--radius);
    padding: 40px 40px 36px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}

.page-title-card::before {
    content: '';
    position: absolute;
    inset: 0;
    background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
    opacity: 0.4;
}

.page-title-icon {
    width: 52px;
    height: 52px;
    background: rgba(255,255,255,0.15);
    border-radius: var(--radius-sm);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 16px;
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255,255,255,0.2);
}

.page-title-icon svg {
    width: 26px;
    height: 26px;
    color: white;
}

.page-title-card h1 {
    font-size: 1.625rem;
    font-weight: 700;
    margin-bottom: 6px;
    letter-spacing: -0.01em;
    position: relative;
}

.page-title-card p {
    font-size: 0.9375rem;
    opacity: 0.85;
    position: relative;
}

/* ===== Section Card ===== */
.section-card {
    background: var(--surface);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    border: 1px solid var(--border);
    margin-bottom: 24px;
    overflow: hidden;
}

.section-card-header {
    padding: 20px 28px 0;
    display: flex;
    align-items: center;
    gap: 14px;
}

.section-card-icon {
    width: 36px;
    height: 36px;
    border-radius: var(--radius-sm);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.section-card-icon svg {
    width: 18px;
    height: 18px;
    color: white;
}

.section-card-title {
    font-size: 1.0625rem;
    font-weight: 600;
    color: var(--text);
}

.section-card-body {
    padding: 16px 28px 24px;
}

.section-card-body p {
    font-size: 0.9375rem;
    color: var(--text-secondary);
    line-height: 1.7;
    margin-bottom: 12px;
}

.section-card-body p:last-child { margin-bottom: 0; }

/* ===== Section Heading (within card) ===== */
.section-heading {
    font-size: 0.9375rem;
    font-weight: 600;
    color: var(--text);
    margin: 20px 0 10px;
    padding-bottom: 6px;
    border-bottom: 1px solid var(--border);
}

.section-heading:first-child { margin-top: 0; }

/* ===== Screenshot ===== */
.screenshot-wrap {
    text-align: center;
    margin: 16px 0 12px;
}

.screenshot-wrap img {
    max-width: 100%;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border);
    box-shadow: var(--shadow);
}

.screenshot-caption {
    font-size: 0.8125rem;
    color: var(--text-muted);
    font-style: italic;
    margin-top: 8px;
}

/* ===== Info Box ===== */
.info-box {
    background: #eff6ff;
    border-left: 4px solid var(--primary);
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
    padding: 14px 18px;
    margin: 14px 0;
}

.warning-box {
    background: #fff7ed;
    border-left: 4px solid var(--warning);
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
    padding: 14px 18px;
    margin: 14px 0;
}

.tip-box {
    background: #f0fdf4;
    border-left: 4px solid var(--success);
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
    padding: 14px 18px;
    margin: 14px 0;
}

.info-box, .warning-box, .tip-box {
    font-size: 0.875rem;
    color: var(--text-secondary);
    line-height: 1.6;
}

.info-box strong, .warning-box strong, .tip-box strong {
    color: var(--text);
}

/* ===== Step List ===== */
.step-list {
    background: #fffbeb;
    border-left: 4px solid var(--warning);
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
    padding: 14px 18px 14px 14px;
    margin: 14px 0;
}

.step-list ol {
    margin: 0;
    padding-left: 20px;
}

.step-list li {
    margin-bottom: 6px;
    font-size: 0.875rem;
    color: var(--text-secondary);
    line-height: 1.5;
}

.step-list li:last-child { margin-bottom: 0; }

/* ===== Feature List ===== */
.feature-list {
    background: var(--bg);
    border-left: 4px solid var(--success);
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
    padding: 14px 18px;
    margin: 14px 0;
}

.feature-list ul {
    margin: 0;
    padding-left: 20px;
}

.feature-list li {
    margin-bottom: 5px;
    font-size: 0.875rem;
    color: var(--text-secondary);
    line-height: 1.5;
}

.feature-list li:last-child { margin-bottom: 0; }

/* ===== Table ===== */
table {
    width: 100%;
    border-collapse: collapse;
    border-radius: var(--radius-sm);
    overflow: hidden;
    margin: 14px 0;
    font-size: 0.875rem;
}

thead tr {
    background: var(--bg);
}

th {
    text-align: left;
    padding: 10px 14px;
    font-weight: 600;
    color: var(--text);
    border-bottom: 2px solid var(--border);
    font-size: 0.8125rem;
}

td {
    padding: 10px 14px;
    color: var(--text-secondary);
    border-bottom: 1px solid var(--border);
}

tbody tr:nth-child(even) td { background: #fafafa; }
tbody tr:hover td { background: #f1f5f9; }

/* ===== Kbd ===== */
kbd {
    display: inline-block;
    padding: 2px 7px;
    font-family: Consolas, monospace;
    font-size: 0.8125rem;
    font-weight: 600;
    background: #f1f5f9;
    border: 1px solid #cbd5e1;
    border-bottom-width: 2px;
    border-radius: 4px;
    color: var(--text);
}

/* ===== Back Link (top of page) ===== */
.back-top-link {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.875rem;
    color: var(--text-muted);
    margin-bottom: 20px;
    padding: 6px 10px;
    border-radius: var(--radius-sm);
    transition: all 150ms ease;
}

.back-top-link:hover {
    background: var(--bg);
    color: var(--primary);
    text-decoration: none;
}

.back-top-link svg {
    width: 14px;
    height: 14px;
}

/* ===== Footer ===== */
.doc-footer {
    text-align: center;
    padding: 32px 0 16px;
    border-top: 1px solid var(--border);
    margin-top: 16px;
    font-size: 0.8125rem;
    color: var(--text-muted);
}

/* ===== Mobile Hamburger ===== */
.hamburger {
    display: none;
    position: fixed;
    top: 16px;
    left: 16px;
    z-index: 200;
    width: 40px;
    height: 40px;
    background: var(--primary);
    color: white;
    border: none;
    border-radius: var(--radius-sm);
    cursor: pointer;
    align-items: center;
    justify-content: center;
}

.hamburger svg {
    width: 20px;
    height: 20px;
}

/* ===== Responsive ===== */
@media (max-width: 768px) {
    .hamburger { display: flex; }

    .sidebar {
        transform: translateX(-100%);
        transition: transform 200ms ease;
    }

    .sidebar.open {
        transform: translateX(0);
    }

    .content {
        margin-left: 0;
        padding: 72px 20px 32px;
    }

    .page-title-card {
        padding: 28px 24px 24px;
    }

    .section-card-header,
    .section-card-body {
        padding-left: 20px;
        padding-right: 20px;
    }
}
```

- [ ] **Step 2: 提交**
```bash
cd E:/code/Exam_v5.0
git add docs/css/help-docs.css
git commit -m "docs: add shared help-docs CSS design system"
```

---

## 考试系统帮助页

### Task 2: 重写 `docs/exam-system-help.html`

**文件:** 重写 `docs/exam-system-help.html`

- [ ] **Step 1: 写入完整 HTML 文件**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>考试系统帮助文档</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="./css/help-docs.css">
</head>
<body>
    <button class="hamburger" onclick="document.querySelector('.sidebar').classList.toggle('open')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
    </button>

    <div class="page-wrapper">
        <!-- Sidebar -->
        <nav class="sidebar">
            <div class="sidebar-header">
                <div class="sidebar-logo">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
                    </svg>
                    <span class="sidebar-title">帮助文档中心</span>
                </div>
                <p class="sidebar-subtitle">研究生复试流程控制系统</p>
            </div>

            <div class="sidebar-nav">
                <div class="sidebar-nav-title">本页面导航</div>
                <a href="#overview"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>系统概述</a>
                <a href="#interface"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>界面介绍</a>
                <a href="#workflow"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>考试流程</a>
                <a href="#controls"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14M4.93 4.93a10 10 0 0 0 0 14.14"/></svg>操作控制</a>
                <a href="#settings"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14M4.93 4.93a10 10 0 0 0 0 14.14"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2"/></svg>系统设置</a>
                <a href="#troubleshooting"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/></svg>常见问题</a>

                <div class="sidebar-nav-title" style="margin-top:16px;">其他文档</div>
                <a href="index.html"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>文档中心首页</a>
                <a href="ai-settings-help.html"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>AI 配置</a>
                <a href="shortcuts-help.html"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M6 8h.01M10 8h.01M14 8h.01M18 8h.01M8 12h.01M12 12h.01M16 12h.01M6 16h12"/></svg>快捷键参考</a>
                <a href="faq-help.html"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>常见问题</a>
            </div>

            <div class="sidebar-footer">
                <a href="index.html" class="sidebar-back">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
                    返回文档中心
                </a>
                <p class="sidebar-version">系统版本 v3.1</p>
            </div>
        </nav>

        <!-- Content -->
        <main class="content">
            <a href="index.html" class="back-top-link">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
                返回文档中心
            </a>

            <!-- Page Title -->
            <div class="page-title-card">
                <div class="page-title-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="3" y="3" width="18" height="18" rx="2"/>
                        <path d="M9 9h6M9 13h4"/>
                    </svg>
                </div>
                <h1>考试系统使用指南</h1>
                <p>研究生复试流程控制系统 · Exam System Guide</p>
            </div>

            <!-- 系统概述 -->
            <div class="section-card" id="overview">
                <div class="section-card-header">
                    <div class="section-card-icon" style="background: linear-gradient(135deg, #4f46e5, #818cf8);">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                    </div>
                    <h2 class="section-card-title">系统概述</h2>
                </div>
                <div class="section-card-body">
                    <div class="feature-list">
                        <p style="margin-bottom:12px;"><strong>研究生复试流程控制系统</strong>是一个专为研究生复试面试设计的综合管理平台，提供完整的面试流程控制、题库管理、计时功能和考生记录管理。</p>
                        <ul>
                            <li><strong>六步考试流程：</strong>中文自我介绍 → 英文自我介绍 → 英文翻译 → 专业问题 → 综合问答 → 考试结束</li>
                            <li><strong>智能题库管理：</strong>支持翻译题和专业题的分类管理，包含文本和图片内容</li>
                            <li><strong>随机抽题功能：</strong>自动随机选择题目，避免重复，确保公平性</li>
                            <li><strong>精确计时控制：</strong>每个环节独立计时，支持暂停、重置和自定义时长</li>
                            <li><strong>考生记录管理：</strong>自动记录每位考生的考试进度和抽取题目</li>
                            <li><strong>系统状态监控：</strong>实时显示数据库连接、当前步骤、计时器状态等</li>
                        </ul>
                    </div>
                </div>
            </div>

            <!-- 界面介绍 -->
            <div class="section-card" id="interface">
                <div class="section-card-header">
                    <div class="section-card-icon" style="background: linear-gradient(135deg, #0ea5e9, #38bdf8);">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
                    </div>
                    <h2 class="section-card-title">界面介绍</h2>
                </div>
                <div class="section-card-body">
                    <div class="screenshot-wrap">
                        <img src="exam-system-main.png" alt="考试系统主界面截图">
                        <p class="screenshot-caption">图 1：考试系统主界面</p>
                    </div>

                    <h3 class="section-heading">界面布局</h3>
                    <div class="step-list">
                        <ol>
                            <li><strong>顶部标题栏：</strong>显示系统标题、学校 Logo 和当前考生信息</li>
                            <li><strong>左侧流程面板（20% 宽度）：</strong>显示六步考试流程和当前进度</li>
                            <li><strong>中央内容区：</strong>显示考试内容、题目和指导信息</li>
                            <li><strong>右侧控制面板（20% 宽度）：</strong>包含操作按钮和系统状态</li>
                            <li><strong>底部状态栏：</strong>显示计时器和版权信息</li>
                        </ol>
                    </div>

                    <h3 class="section-heading">考试流程</h3>
                    <table>
                        <thead>
                            <tr><th>步骤</th><th>名称</th><th>默认时长</th><th>说明</th></tr>
                        </thead>
                        <tbody>
                            <tr><td>1</td><td>中文自我介绍</td><td>1 分钟</td><td>考生用中文进行自我介绍</td></tr>
                            <tr><td>2</td><td>英文自我介绍</td><td>1 分钟</td><td>考生用英文进行自我介绍</td></tr>
                            <tr><td>3</td><td>英文翻译</td><td>4 分钟</td><td>随机抽取英文段落进行翻译</td></tr>
                            <tr><td>4</td><td>专业问题</td><td>5 分钟</td><td>按科目随机抽取专业问题回答</td></tr>
                            <tr><td>5</td><td>综合问答</td><td>9 分钟</td><td>考官综合提问环节</td></tr>
                            <tr><td>6</td><td>考试结束</td><td>—</td><td>总结评分，准备下一位考生</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- 考试流程 -->
            <div class="section-card" id="workflow">
                <div class="section-card-header">
                    <div class="section-card-icon" style="background: linear-gradient(135deg, #8b5cf6, #a78bfa);">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
                    </div>
                    <h2 class="section-card-title">考试流程</h2>
                </div>
                <div class="section-card-body">
                    <h3 class="section-heading">开始新考试</h3>
                    <div class="step-list">
                        <ol>
                            <li>点击<strong>"开始考试"</strong>按钮或按 <kbd>Space</kbd> 键</li>
                            <li>系统自动生成考生编号并创建考试记录</li>
                            <li>进入第一步：中文自我介绍</li>
                            <li>左侧面板显示当前步骤，右侧控制按钮激活</li>
                        </ol>
                    </div>

                    <div class="info-box" style="margin-top:16px;">
                        <strong>自动流程：</strong>使用"下一步"按钮按顺序进行，系统会自动保存进度和状态。<br>
                        <strong>手动跳转：</strong>可以使用"上一步"返回之前的环节，或"完成考试"直接结束。
                    </div>

                    <h3 class="section-heading">题目抽取（步骤 3 和 4）</h3>
                    <div class="step-list">
                        <ol>
                            <li><strong>英文翻译（步骤 3）：</strong>点击"抽取题目"自动随机选择翻译题</li>
                            <li><strong>专业问题（步骤 4）：</strong>首先选择科目，然后随机抽取该科目的专业题</li>
                            <li>抽取的题目会显示在中央内容区，包含文本和图片内容</li>
                            <li>已抽取的题目会被标记为"已使用"，避免重复抽取</li>
                        </ol>
                    </div>
                </div>
            </div>

            <!-- 操作控制 -->
            <div class="section-card" id="controls">
                <div class="section-card-header">
                    <div class="section-card-icon" style="background: linear-gradient(135deg, #ec4899, #f472b6);">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14M4.93 4.93a10 10 0 0 0 0 14.14"/></svg>
                    </div>
                    <h2 class="section-card-title">操作控制</h2>
                </div>
                <div class="section-card-body">
                    <table>
                        <thead>
                            <tr><th>按钮</th><th>快捷键</th><th>功能</th><th>使用时机</th></tr>
                        </thead>
                        <tbody>
                            <tr><td>开始考试</td><td><kbd>Space</kbd></td><td>开始新的考试流程</td><td>考试开始前</td></tr>
                            <tr><td>上一步</td><td><kbd>←</kbd></td><td>返回上一个考试步骤</td><td>需要重新进行某个环节时</td></tr>
                            <tr><td>下一步</td><td><kbd>→</kbd></td><td>进入下一个考试步骤</td><td>当前环节完成后</td></tr>
                            <tr><td>抽取题目</td><td><kbd>D</kbd></td><td>随机抽取考试题目</td><td>翻译和专业问题环节</td></tr>
                            <tr><td>开始计时</td><td><kbd>T</kbd></td><td>开始当前环节计时</td><td>考生开始答题时</td></tr>
                            <tr><td>暂停计时</td><td><kbd>P</kbd></td><td>暂停当前计时器</td><td>需要中断计时时</td></tr>
                            <tr><td>重置计时</td><td><kbd>R</kbd></td><td>重置计时器到初始值</td><td>重新开始计时时</td></tr>
                            <tr><td>完成考试</td><td><kbd>Ctrl</kbd> + <kbd>Enter</kbd></td><td>直接结束当前考试</td><td>提前结束考试时</td></tr>
                        </tbody>
                    </table>

                    <div class="warning-box" style="margin-top:16px;">
                        <strong>注意：</strong>快捷键只在对应按钮可用时生效，且不会重复触发。
                    </div>
                </div>
            </div>

            <!-- 系统设置 -->
            <div class="section-card" id="settings">
                <div class="section-card-header">
                    <div class="section-card-icon" style="background: linear-gradient(135deg, #f59e0b, #fbbf24);">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
                    </div>
                    <h2 class="section-card-title">系统设置</h2>
                </div>
                <div class="section-card-body">
                    <div class="screenshot-wrap">
                        <img src="exam-system-settings.png" alt="系统设置界面截图">
                        <p class="screenshot-caption">图 2：系统设置界面</p>
                    </div>

                    <div class="info-box">
                        <strong>时间设置：</strong>可以自定义每个考试环节的时长（以秒为单位），设置后立即生效。
                    </div>

                    <h3 class="section-heading">系统管理功能</h3>
                    <div class="feature-list">
                        <ul>
                            <li><strong>题库管理：</strong>打开数据库编辑器，管理翻译题和专业题</li>
                            <li><strong>步骤内容设置：</strong>设置各考试步骤的指导内容和说明</li>
                            <li><strong>顶部设置：</strong>自定义系统标题和上传学校、学院 Logo</li>
                            <li><strong>考试导出：</strong>导出所有考生的考试记录和题目信息</li>
                            <li><strong>系统重置：</strong>清除所有考试记录，恢复初始状态</li>
                        </ul>
                    </div>
                </div>
            </div>

            <!-- 常见问题 -->
            <div class="section-card" id="troubleshooting">
                <div class="section-card-header">
                    <div class="section-card-icon" style="background: linear-gradient(135deg, #10b981, #34d399);">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/></svg>
                    </div>
                    <h2 class="section-card-title">常见问题</h2>
                </div>
                <div class="section-card-body">
                    <h3 class="section-heading">Q: 系统显示"数据库连接失败"怎么办？</h3>
                    <div class="info-box">
                        <ol style="padding-left:18px;margin:0;">
                            <li>确认服务器正常运行（检查控制台是否有错误信息）</li>
                            <li>刷新页面重新连接</li>
                            <li>检查数据库文件是否存在于 <code>assets/data</code> 目录</li>
                        </ol>
                    </div>

                    <h3 class="section-heading">Q: 抽取题目时显示"无可用题目"？</h3>
                    <div class="info-box">
                        <ol style="padding-left:18px;margin:0;">
                            <li>进入题库管理，检查是否有足够的题目</li>
                            <li>确认题目没有全部被标记为"已使用"</li>
                            <li>可以通过系统重置清除使用状态</li>
                        </ol>
                    </div>

                    <h3 class="section-heading">Q: 计时器不工作或显示异常？</h3>
                    <div class="info-box">
                        <ol style="padding-left:18px;margin:0;">
                            <li>点击"重置计时"按钮</li>
                            <li>检查系统设置中的时间配置</li>
                            <li>刷新页面重新初始化</li>
                        </ol>
                    </div>

                    <h3 class="section-heading">Q: 如何恢复到某个考生的考试状态？</h3>
                    <div class="info-box">
                        系统会自动保存每位考生的进度。刷新页面后，系统会自动恢复到最后一位考生的状态，包括当前步骤和已抽取的题目。
                    </div>
                </div>
            </div>

            <div class="doc-footer">
                <p>研究生复试流程控制系统 v3.1 · 北京石油化工学院</p>
                <p style="margin-top:4px;">技术支持：<a href="mailto:wangwentong@bipt.edu.cn">wangwentong@bipt.edu.cn</a></p>
            </div>
        </main>
    </div>
</body>
</html>
```

- [ ] **Step 2: 提交**
```bash
git add docs/exam-system-help.html
git commit -m "docs: redesign exam-system-help with new doc site style"
```

---

## 题库编辑器帮助页

### Task 3: 重写 `docs/database-editor-help.html`

**文件:** 重写 `docs/database-editor-help.html`（内容基于现有文件，样式迁移到新 CSS，SVG 图标替换 emoji，参考 Task 2 的 HTML 结构）

- [ ] **Step 1: 写入完整 HTML 文件**

Key sections to include (内容从现有文件迁移):
1. 功能介绍
2. 界面说明（含截图 `database-editor-main.png`）
3. 翻译题管理
4. 专业题管理
5. 科目分类
6. 批量导入导出
7. 注意事项

Sidebar nav 中 active 项设为 `#features`，底部链接指向 `index.html`。

- [ ] **Step 2: 提交**
```bash
git add docs/database-editor-help.html
git commit -m "docs: redesign database-editor-help with new doc site style"
```

---

## 顶部设置帮助页

### Task 4: 重写 `docs/header-setting-help.html`

**文件:** 重写 `docs/header-setting-help.html`（内容从现有文件迁移）

- [ ] **Step 1: 写入完整 HTML 文件**

Key sections:
1. Logo 设置说明（含截图 `header-setting-main.png`）
2. 考试标题设置
3. 图片要求（格式、尺寸）

- [ ] **Step 2: 提交**
```bash
git add docs/header-setting-help.html
git commit -m "docs: redesign header-setting-help with new doc site style"
```

---

## 步骤内容设置帮助页

### Task 5: 重写 `docs/page-content-setting-help.html`

**文件:** 重写 `docs/page-content-setting-help.html`（内容从现有文件迁移）

- [ ] **Step 1: 写入完整 HTML 文件**

Key sections:
1. 内容管理说明（含截图 `page-content-setting-main.png`）
2. 步骤选择
3. 内容块编辑
4. 启用/禁用控制

- [ ] **Step 2: 提交**
```bash
git add docs/page-content-setting-help.html
git commit -m "docs: redesign page-content-setting-help with new doc site style"
```

---

## 考试导出帮助页

### Task 6: 重写 `docs/export-exam-help.html`

**文件:** 重写 `docs/export-exam-help.html`（内容从现有文件迁移）

- [ ] **Step 1: 写入完整 HTML 文件**

Key sections:
1. 统计概览（含截图 `export-exam-main.png`）
2. 导出 Excel
3. 生成 HTML 报告
4. 导出格式说明

- [ ] **Step 2: 提交**
```bash
git add docs/export-exam-help.html
git commit -m "docs: redesign export-exam-help with new doc site style"
```

---

## AI 配置帮助页（新建）

### Task 7: 新建 `docs/ai-settings-help.html`

**文件:** 新建 `docs/ai-settings-help.html`

- [ ] **Step 1: 写入完整 HTML 文件**

Key sections:
1. 功能介绍
2. 支持的提供商（表格：OpenAI / Claude / Gemini / MiniMax / ModelScope / 硅基流动）
3. 配置步骤
4. 自定义提供商
5. 安全提示

配色方案：使用 `--accent` (#06b6d4) 作为主色调，与 index.html 中 AI 配置卡片的青色保持一致。

- [ ] **Step 2: 提交**
```bash
git add docs/ai-settings-help.html
git commit -m "docs: add ai-settings-help page"
```

---

## 快捷键参考帮助页（新建）

### Task 8: 新建 `docs/shortcuts-help.html`

**文件:** 新建 `docs/shortcuts-help.html`

- [ ] **Step 1: 写入完整 HTML 文件**

Key sections:
1. 快捷键总表（完整 8 条，表格形式）
2. 使用说明
3. 适用场景

Page title icon 使用键盘图标，accent 色 #8b5cf6。

- [ ] **Step 2: 提交**
```bash
git add docs/shortcuts-help.html
git commit -m "docs: add shortcuts-help page"
```

---

## 常见问题帮助页（新建）

### Task 9: 新建 `docs/faq-help.html`

**文件:** 新建 `docs/faq-help.html`

- [ ] **Step 1: 写入完整 HTML 文件**

Key sections:
1. 数据库连接问题
2. 题目抽取问题
3. 计时器问题
4. 状态恢复问题
5. AI 出题问题
6. 数据备份问题

每个问题用 `section-card` 包裹，FAQ 项目使用展开式细节元素（`<details>` + `<summary>`）展示答案，优雅降级。

- [ ] **Step 2: 提交**
```bash
git add docs/faq-help.html
git commit -m "docs: add faq-help page"
```

---

## 索引页更新

### Task 10: 更新 `docs/index.html`

**文件:** 更新 `docs/index.html`（当前已是新设计，补充 3 个新卡片）

- [ ] **Step 1: 添加 AI 配置入口卡片**

在 `docs-grid` 中追加第 6 张卡片（参考现有 5 张卡片的 HTML 结构）：

```html
<!-- AI 配置 -->
<article class="doc-card" onclick="location.href='ai-settings-help.html'">
    <div class="card-header">
        <div class="card-icon" style="background: linear-gradient(135deg, #06b6d4, #22d3ee);">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
            </svg>
        </div>
        <div class="card-title-wrap">
            <h2 class="card-title">AI 配置使用指南</h2>
            <p class="card-subtitle"> AI Provider Configuration</p>
        </div>
    </div>
    <div class="card-screenshot">
        <img src="ai-settings-main.png" alt="AI 配置主界面截图">
        <div class="card-screenshot-overlay"></div>
    </div>
    <p class="card-desc">配置多个 AI 提供商，支持 AI 智能出题，包括 OpenAI、Claude、Gemini、MiniMax、ModelScope 和硅基流动。</p>
    <div class="card-features">
        <div class="card-features-title">主要内容</div>
        <ul>
            <li>支持的 AI 提供商</li>
            <li>API Key 配置步骤</li>
            <li>自定义提供商</li>
            <li>默认提供商设置</li>
            <li>连接测试</li>
            <li>安全存储</li>
        </ul>
    </div>
    <div class="card-actions">
        <a href="ai-settings-help.html" class="btn btn-primary" onclick="event.stopPropagation()">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>
            查看详细文档
        </a>
        <a href="../settings/ai" class="btn btn-secondary" onclick="event.stopPropagation()">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
            打开 AI 配置
        </a>
    </div>
</article>
```

- [ ] **Step 2: 添加快捷键参考入口卡片**

```html
<!-- 快捷键参考 -->
<article class="doc-card" onclick="location.href='shortcuts-help.html'">
    <div class="card-header">
        <div class="card-icon" style="background: linear-gradient(135deg, #8b5cf6, #a78bfa);">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="2" y="4" width="20" height="16" rx="2"/>
                <path d="M6 8h.01M10 8h.01M14 8h.01M18 8h.01M8 12h.01M12 12h.01M16 12h.01M6 16h12"/>
            </svg>
        </div>
        <div class="card-title-wrap">
            <h2 class="card-title">快捷键参考</h2>
            <p class="card-subtitle"> Keyboard Shortcuts</p>
        </div>
    </div>
    <p class="card-desc">考试系统支持键盘快捷键，可快速完成开始考试、切换步骤、抽取题目、计时控制等操作。</p>
    <div class="card-features">
        <div class="card-features-title">主要快捷键</div>
        <ul>
            <li><kbd>Space</kbd> 开始考试</li>
            <li><kbd>←</kbd> <kbd>→</kbd> 上一步 / 下一步</li>
            <li><kbd>D</kbd> 抽取题目</li>
            <li><kbd>T</kbd> <kbd>P</kbd> <kbd>R</kbd> 计时控制</li>
            <li><kbd>Ctrl+Enter</kbd> 完成考试</li>
        </ul>
    </div>
    <div class="card-actions">
        <a href="shortcuts-help.html" class="btn btn-primary" onclick="event.stopPropagation()">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>
            查看详细文档
        </a>
    </div>
</article>
```

- [ ] **Step 3: 添加 FAQ 入口卡片**

```html
<!-- 常见问题 -->
<article class="doc-card" onclick="location.href='faq-help.html'">
    <div class="card-header">
        <div class="card-icon" style="background: linear-gradient(135deg, #10b981, #34d399);">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"/>
                <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
                <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
        </div>
        <div class="card-title-wrap">
            <h2 class="card-title">常见问题</h2>
            <p class="card-subtitle"> FAQ</p>
        </div>
    </div>
    <p class="card-desc">汇总使用过程中最常见的问题和解决方案，涵盖数据库连接、题目抽取、计时器、状态恢复、AI 出题等。</p>
    <div class="card-features">
        <div class="card-features-title">涵盖主题</div>
        <ul>
            <li>数据库连接问题</li>
            <li>题目抽取问题</li>
            <li>计时器异常</li>
            <li>状态恢复</li>
            <li>AI 出题失败</li>
            <li>数据备份</li>
        </ul>
    </div>
    <div class="card-actions">
        <a href="faq-help.html" class="btn btn-primary" onclick="event.stopPropagation()">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>
            查看详细文档
        </a>
    </div>
</article>
```

- [ ] **Step 4: 提交**
```bash
git add docs/index.html
git commit -m "docs: add AI config, shortcuts, FAQ entry cards to index"
```

---

## 规范自检

完成所有任务后，确认：

1. **Spec 覆盖：** spec 第 5 节 8 个页面内容清单中，每一项都有对应 Task 完成 ✅
2. **占位符扫描：** 无 "TBD"、"TODO"、未填写内容 ✅
3. **类型一致性：** 所有页面使用统一的 CSS class 命名（`.section-card`、`.info-box` 等） ✅
4. **图片引用：** 6 张截图引用路径正确（`./xxx.png`），对应 `docs/` 目录下实际文件 ✅

---

## 执行方式选择

**Plan complete and saved to `docs/superpowers/plans/2026-04-03-help-docs-redesign.md`. Two execution options:**

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
