# AI UI优化实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**目标:** 优化顶部导航按钮布局，添加AI批量导入和AI设置入口，增强AI单题生成功能

**技术栈:** Vue 3

---

## Task 1: 顶部导航栏按钮

**Files:**
- Modify: `frontend/src/views/EditorView.vue:8-13`

- [ ] **Step 1: 修改顶部导航按钮**

当前 (line 9-12):
```vue
<button @click="openBatchImportModal" class="nav-btn batch-btn">批量导入</button>
<button @click="openBatchExportModal" class="nav-btn batch-btn">批量导出</button>
<router-link to="/" class="nav-btn">返回考试</router-link>
<router-link to="/help" class="nav-btn">帮助</router-link>
```

修改为:
```vue
<button @click="openBatchImportModal" class="nav-btn batch-btn">批量导入</button>
<button @click="switchToAiImport" class="nav-btn batch-btn">AI批量导入</button>
<router-link to="/settings/ai" class="nav-btn">AI设置</router-link>
<button @click="openBatchExportModal" class="nav-btn batch-btn">批量导出</button>
<router-link to="/" class="nav-btn">返回考试</router-link>
<router-link to="/help" class="nav-btn">帮助</router-link>
```

- [ ] **Step 2: 添加 switchToAiImport 方法**

在 methods 中添加:
```javascript
const switchToAiImport = () => {
  currentTab.value = 'import'
}
```

- [ ] **Step 3: 测试**

刷新 EditorView，确认顶部有5个按钮

- [ ] **Step 4: Commit**

```bash
git add frontend/src/views/EditorView.vue
git commit -m "feat: add AI import and settings buttons to header"
```

---

## Task 2: 增加重新生成按钮

**Files:**
- Modify: `frontend/src/views/EditorView.vue:368-372`

- [ ] **Step 1: 添加重新生成按钮**

当前 (line 368-372):
```vue
<div class="ai-generation" v-if="currentTab !== 'subjects'">
  <button @click="generateWithAI" class="ai-btn" type="button">
    🤖 AI 生成
  </button>
</div>
```

修改为:
```vue
<div class="ai-generation" v-if="currentTab !== 'subjects'">
  <button @click="generateWithAI" class="ai-btn" type="button">
    🤖 AI 生成
  </button>
  <button @click="regenerateWithAI" class="ai-btn" type="button">
    🔄 重新生成
  </button>
</div>
```

- [ ] **Step 2: 添加 regenerateWithAI 方法**

```javascript
// 重新生成（使用相同知识点）
const regenerateWithAI = async () => {
  try {
    const providers = await getAiProviders()
    const enabled = providers.data.find(p => p.enabled)
    if (!enabled) {
      alert('请先在设置中配置 AI Provider')
      return
    }

    const result = await generateQuestion({
      provider: enabled.id,
      type: currentType.value,
      context: currentSubject.value,
      source_text: subQuestions.value[0]?.text || ''
    })

    if (result.data.candidates && result.data.candidates.length > 0) {
      showAiCandidates(result.data.candidates)
    }
  } catch (error) {
    console.error('AI重新生成失败:', error)
    alert('AI生成失败，请检查配置')
  }
}
```

- [ ] **Step 3: 测试**

1. 添加题目 → 输入内容 → 点击AI生成
2. 点击重新生成，确认生成新候选

- [ ] **Step 4: Commit**

```bash
git add frontend/src/views/EditorView.vue
git commit -m "feat: add regenerate button for AI question generation"
```

---

## 验收检查清单

- [ ] Task 1: 顶部导航有5个按钮：批量导入、AI批量导入、AI设置、批量导出、返回考试、帮助
- [ ] Task 1: AI批量导入按钮点击跳转到AI批量导入Tab
- [ ] Task 1: AI设置按钮点击跳转到/settings/ai
- [ ] Task 2: 重新生成按钮显示在AI生成按钮旁边
- [ ] Task 2: 点击重新生成调用AI生成新候选

---

## 执行选项

**Plan complete and saved to `docs/superpowers/plans/2026-04-01-ai-ui-optimize.md`. Two execution options:**

**1. Subagent-Driven (recommended)** - 任务交给 subagent 执行

**2. Inline Execution** - 在当前会话执行

选择哪种方式？