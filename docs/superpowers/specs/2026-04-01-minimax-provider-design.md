# MiniMax AI Provider 支持设计

**项目**: 研究生复试面试系统
**日期**: 2026-04-01
**范围**: AI 配置模块 - MiniMax Provider 支持

---

## 设计目标

- 在 AI 配置页添加 MiniMax 内置 Provider
- 支持用户配置 API Key 和自定义模型名称
- 后端支持调用 MiniMax API 生成题目

---

## 当前状态

- 现有内置 Provider: OpenAI, Claude, Gemini
- AI 生成返回模拟数据（待实现真实 API 调用）

---

## 设计方案

### 1. 前端 - AI 配置页

**文件**: `frontend/src/views/AiSettingsView.vue`

添加 MiniMax 到内置 Provider 列表:
```javascript
const builtInProviders = ['openai', 'claude', 'gemini', 'minimax']
```

MiniMax 卡片显示:
- 名称: MiniMax
- 状态: 未启用/已启用
- 设置项: API Key, Base URL, 默认模型

### 2. 后端 - AI 生成

**文件**: `backend/apis/ai/generate.py`

添加 MiniMax API 调用:
- 端点: `https://api.minimaxi.com/anthropic/v1/messages`
- API 格式: Anthropic Messages API (原生)
- 模型: 用户自定义（默认 MiniMax-M2.7）

---

## 验收标准

- [ ] 前端显示 MiniMax 卡片
- [ ] 可配置 API Key 和模型
- [ ] AI 生成时调用 MiniMax API