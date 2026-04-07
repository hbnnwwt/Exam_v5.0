# 帮助文档入口链接总结

本文档总结了系统帮助文档的结构和入口链接。

## 📚 帮助文档结构

### 体系 A：Vue SPA 内嵌帮助（主帮助系统）

| 文件 | 路由 | 说明 |
|------|------|------|
| `frontend/src/views/HelpView.vue` | `/help` | 系统内帮助页面，包含搜索、滚动导航、8 个章节 |

**章节内容：**
1. 快速上手（3 步引导）
2. 考试流程（六步面试流程、抽题、下一考生）
3. 题库管理（添加/编辑/删除/搜索）
4. 考试设置（步骤设置、Logo 设置、步骤内容设置）
5. AI 配置（6 提供商、自定义提供商、测试连接）
6. 数据导出（Excel、HTML 报告）
7. 快捷键参考（8 个快捷键）
8. 常见问题（7 个 FAQ）

### 体系 B：静态 HTML 文档（深度文档）

| 文件 | 说明 |
|------|------|
| `docs/index.html` | 文档中心首页（卡片式导航） |
| `docs/exam-system-help.html` | 考试系统架构概述（技术栈、路由、数据流程） |
| `docs/database-editor-help.html` | 题库编辑器使用指南（详细） |
| `docs/ai-settings-help.html` | AI 配置使用指南（详细） |
| `docs/page-content-setting-help.html` | 考试设置使用指南（详细，含步骤设置和 Logo 设置） |
| `docs/export-exam-help.html` | 考试导出使用指南（详细） |

### 已删除的冗余文档

以下文档因与 HelpView.vue 内容高度重复已被删除：

| 文件 | 删除原因 |
|------|----------|
| `docs/shortcuts-help.html` | 与 HelpView "快捷键参考" 章节重复 95% |
| `docs/faq-help.html` | 与 HelpView "常见问题" 章节重复 85% |

> 注：`docs/ai-settings-help.html` 已恢复为深度文档，保留在静态文档体系中。

### 截图文件

| 文件 | 用途 |
|------|------|
| `docs/exam-system-main.png` | 考试系统主界面 |
| `docs/exam-system-settings.png` | 系统设置界面 |
| `docs/database-editor-main.png` | 数据库编辑器主界面 |
| `docs/database-editor-professional.png` | 专业题管理界面 |
| `docs/database-editor-edit.png` | 题目编辑界面 |
| `docs/header-setting-main.png` | 顶部设置主界面 |
| `docs/page-content-setting-main.png` | 步骤内容设置主界面 |
| `docs/page-content-setting-edit.png` | 内容编辑界面 |
| `docs/export-exam-main.png` | 考试导出主界面 |

## 🔗 访问路径

### Vue SPA 页面（所有入口指向 `/help`）

| 来源页面 | 链接方式 | 代码位置 |
|----------|----------|----------|
| ExamView | `<a href="/help" target="_blank">` | 顶部导航 |
| EditorView | `<router-link to="/help">` | 顶部导航 |
| SettingsView | `<router-link to="/help">` | 顶部导航 |
| ExportView | `<router-link to="/help">` | 顶部导航 |

### 静态文档访问

| 来源 | 目标 |
|------|------|
| HelpView.vue 顶部"详细文档中心"按钮 | `docs/index.html` |
| docs/index.html 卡片 | 各 `*-help.html` 文件 |
| 各 `*-help.html` 侧边栏 | 文档中心首页 + 其他文档交叉链接 |

## 🎯 文档定位

| 文档 | 定位 | 适合人群 |
|------|------|----------|
| `/help` (HelpView) | 快速参考，日常使用 | 所有用户 |
| `docs/index.html` | 文档中心索引 | 需要深入学习的用户 |
| `exam-system-help.html` | 架构概述 | 技术人员、管理员 |
| `database-editor-help.html` | 题库管理详细指南 | 题库管理员 |
| `ai-settings-help.html` | AI 配置详细指南 | 系统管理员 |
| `page-content-setting-help.html` | 考试设置详细指南（步骤+Logo） | 系统管理员 |
| `export-exam-help.html` | 导出功能详细指南 | 需要导出数据的用户 |

## 🔄 维护说明

### 更新帮助内容
1. **日常操作指南** → 更新 `HelpView.vue`
2. **深度技术文档** → 更新 `docs/` 下对应 HTML 文件
3. **截图更新** → 替换 `docs/` 或 `frontend/src/assets/` 中的图片

### 添加新的帮助入口
1. 在目标 Vue 页面添加 `<router-link to="/help">` 或 `<a href="/help" target="_blank">`
2. 保持样式一致性
3. 测试链接功能

## ✅ 测试清单

- [x] 所有 Vue 页面帮助按钮指向 `/help`
- [x] HelpView 顶部"详细文档中心"指向 `docs/index.html`
- [x] docs/index.html 卡片链接正确
- [x] 各静态文档侧边栏交叉链接正确
- [x] 已删除文档的引用已清理
- [x] 截图文件正确加载

## 📞 技术支持

如需添加更多帮助入口或修改现有链接，请参考本文档的实现方式，保持一致的用户体验和技术标准。

---
**文档版本**: v1.1  
**最后更新**: 2026年4月3日  
**维护者**: 王文通 (wangwentong@bipt.edu.cn)
