# 考试记录预览展开显示题目内容 - 实现计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在考试记录预览页面添加行内展开功能，显示每个考生的翻译题目和专业题目内容

**Architecture:** 前端Vue组件修改，无需后端改动。后端API已返回题目信息，前端只需添加展开状态管理和展开区域渲染

**Tech Stack:** Vue 3, JavaScript

---

## 文件结构

- 修改: `frontend/src/views/ExportView.vue` - 添加展开功能和样式

---

## Chunk 1: 展开功能核心逻辑

### Task 1: 添加展开状态和相关方法

**Files:**
- Modify: `frontend/src/views/ExportView.vue`

- [ ] **Step 1: 在 script setup 中添加展开状态**

在 `const students = ref([])` 后添加：

```javascript
// 展开行状态管理
const expandedRows = ref(new Set())

// 切换展开/收起
const toggleExpand = (studentNumber) => {
  if (expandedRows.value.has(studentNumber)) {
    expandedRows.value.delete(studentNumber)
  } else {
    expandedRows.value.add(studentNumber)
  }
}

// 检查行是否展开
const isExpanded = (studentNumber) => {
  return expandedRows.value.has(studentNumber)
}
```

- [ ] **Step 2: 验证代码正确性**

检查添加的代码语法正确

---

## Chunk 2: 模板修改

### Task 2: 修改表格模板添加展开按钮和展开区域

**Files:**
- Modify: `frontend/src/views/ExportView.vue`

- [ ] **Step 1: 添加操作列到表头**

在 `</tr>` 前添加：

```html
<th>操作</th>
```

- [ ] **Step 2: 添加展开按钮到每行**

在表格行末尾 `</tr>` 前添加：

```html
<td>
  <button @click="toggleExpand(student.studentNumber)" class="expand-btn">
    {{ isExpanded(student.studentNumber) ? '收起' : '展开' }}
  </button>
</td>
```

- [ ] **Step 3: 添加展开区域**

在 `</tr>` 后添加（使用 v-if 条件渲染）：

```html
<tr v-if="isExpanded(student.studentNumber)" class="expand-row">
  <td colspan="6">
    <div class="question-details">
      <!-- 翻译题目 -->
      <div v-if="student.translationInfo" class="question-section">
        <div class="question-title">翻译题目 (题号: {{ student.translationInfo.questionNumber }})</div>
        <div class="question-content">{{ student.translationInfo.questionContent }}</div>
      </div>
      <!-- 专业题目 -->
      <div v-if="student.professionalInfo" class="question-section">
        <div class="question-title">专业题目 (题号: {{ student.professionalInfo.questionNumber }}) - {{ student.professionalInfo.subject }}</div>
        <div class="question-content">{{ student.professionalInfo.questionContent }}</div>
      </div>
    </div>
  </td>
</tr>
```

- [ ] **Step 4: 检查数据字段名称**

确认 API 返回的字段名与模板使用的一致：
- `student.translationInfo.questionNumber`
- `student.translationInfo.questionContent`
- `student.professionalInfo.questionNumber`
- `student.professionalInfo.questionContent`
- `student.professionalInfo.subject`

---

## Chunk 3: 样式添加

### Task 3: 添加展开相关样式

**Files:**
- Modify: `frontend/src/views/ExportView.vue`

- [ ] **Step 1: 添加按钮和展开行样式**

在 `<style scoped>` 中添加：

```css
.expand-btn {
  padding: 4px 12px;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.expand-btn:hover {
  background: #5a6268;
}

.expand-row {
  background: #f8f9fa;
}

.expand-row td {
  padding: 15px;
  border-bottom: 1px solid #dee2e6;
}

.question-details {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.question-section {
  background: white;
  padding: 15px;
  border-radius: 8px;
  border: 1px solid #dee2e6;
}

.question-title {
  font-weight: bold;
  font-size: 14px;
  color: #333;
  margin-bottom: 10px;
}

.question-content {
  font-size: 13px;
  color: #666;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}
```

- [ ] **Step 2: 验证样式语法正确**

检查 CSS 语法

---

## Chunk 4: 测试验证

### Task 4: 验证功能

- [ ] **Step 1: 启动前端开发服务器**

```bash
cd frontend && npm run dev
```

- [ ] **Step 2: 访问导出页面**

打开浏览器访问导出页面

- [ ] **Step 3: 测试展开功能**

1. 点击任意一行的"展开"按钮
2. 验证下方显示题目内容
3. 再次点击验证收起功能

- [ ] **Step 4: 验证显示内容**

1. 确认翻译题目显示正确
2. 确认专业题目显示正确（包含科目名称）
3. 确认题目内容显示完整

---

## 验收检查清单

- [ ] 展开按钮显示正常
- [ ] 点击展开显示题目内容
- [ ] 再次点击收起题目内容
- [ ] 翻译题目信息正确显示
- [ ] 专业题目信息正确显示（含科目）
- [ ] 样式与设计一致
- [ ] 多个考生行展开/收起互不影响
