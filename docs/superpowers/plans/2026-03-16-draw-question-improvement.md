# 抽题模块改进实现计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 改进抽题模块的UE体验：1) 优化抽题动画为2.5秒逐个扫描效果；2) 专业题科目选择改为弹窗方式

**Architecture:**
- 前端单文件修改：`frontend/src/components/StepContent.vue`
- 新增状态变量：`tempHighlightId`、`animationTimer`、`showSubjectModal`
- 动画逻辑：先开始扫描动画，同时发起API请求，动画结束后显示结果
- 弹窗逻辑：点击专业题抽取 → 科目选择弹窗 → 确定后进入抽题弹窗

**Tech Stack:** Vue 3 + Vite + Pinia

---

## 文件结构

```
frontend/src/components/
└── StepContent.vue    # 唯一修改的文件
```

---

## Task 1: 添加新的状态变量

**Files:**
- Modify: `frontend/src/components/StepContent.vue:180-200`

- [ ] **Step 1: 添加 tempHighlightId 和 animationTimer 变量**

在现有变量区域添加：
```javascript
// 动画相关 - 新增
const tempHighlightId = ref(null)   // 动画中临时高亮的题目ID
const animationTimer = ref(null)     // 动画定时器引用

// 科目选择弹窗 - 新增
const showSubjectModal = ref(false)  // 是否显示科目选择弹窗
```

- [ ] **Step 2: 添加 onUnmounted 清理逻辑**

在脚本末尾添加：
```javascript
import { onUnmounted } from 'vue'

// 组件卸载时清理定时器
onUnmounted(() => {
  if (animationTimer.value) {
    clearInterval(animationTimer.value)
  }
})
```

---

## Task 2: 修改 getQuestionColor 函数支持扫描高亮

**Files:**
- Modify: `frontend/src/components/StepContent.vue:getQuestionColor`

- [ ] **Step 1: 更新 getQuestionColor 函数**

```javascript
// 获取题目颜色 - 优先显示选中题目 > 扫描中高亮 > 已使用 > 可用
const getQuestionColor = (question, selectedId) => {
  // 1. 选中的题目 - 高亮绿色
  if (selectedId === question.id) {
    return '#198754 !important'
  }
  // 2. 扫描中高亮 - 浅绿色
  if (tempHighlightId.value === question.id) {
    return '#86efac !important'
  }
  // 3. 已使用题目 - 灰色
  if (question.is_used) {
    return '#6c757d !important'
  }
  // 4. 可用题目 - 绿色
  return '#28a745 !important'
}
```

---

## Task 3: 实现扫描动画逻辑

**Files:**
- Modify: `frontend/src/components/StepContent.vue:startDraw`

- [ ] **Step 1: 重写 startDraw 函数**

替换现有的 startDraw 函数为：

```javascript
// 开始抽取 - 扫描动画版
const startDraw = async () => {
  const availableQuestions = questions.value.filter(q => !q.is_used)
  if (availableQuestions.length === 0) {
    toast.warning('没有可用的题目')
    return
  }

  if (isDrawing.value) return  // 防止重复点击

  // 1. 立即开始扫描动画
  isDrawing.value = true
  const questionList = questions.value
  const totalDuration = 2500  // 固定2.5秒

  // 动态计算间隔：确保扫描完所有题目，总时长约2.5秒
  const interval = Math.max(100, Math.floor(totalDuration / questionList.length))

  let scanIndex = 0
  animationTimer.value = setInterval(() => {
    tempHighlightId.value = questionList[scanIndex].id
    scanIndex = (scanIndex + 1) % questionList.length
  }, interval)

  // 2. 同时发起API请求
  let url = `/exam-api/questions/${currentQuestionType.value}/random?exclude_used=true`
  if (currentQuestionType.value === 'professional' && selectedSubject.value) {
    url += `&subject=${selectedSubject.value}`
  }

  try {
    const response = await api.get(url)

    // 3. API返回后，停止扫描动画
    if (animationTimer.value) {
      clearInterval(animationTimer.value)
      animationTimer.value = null
    }

    if (!response.success || !response.data) {
      throw new Error('没有可用的题目')
    }

    const selectedQuestion = response.data

    // 4. 显示最终结果
    tempHighlightId.value = null
    selectedQuestionId.value = selectedQuestion.id

    // 更新题目状态
    const qIndex = questionList.findIndex(q => q.id === selectedQuestion.id)
    if (qIndex !== -1) {
      questionList[qIndex].is_used = true
    }

    // 计算题目编号
    const questionNumber = qIndex + 1

    // 保存题目到store
    const questionContent = selectedQuestion.content || selectedQuestion.question_data
    if (currentQuestionType.value === 'translation') {
      examStore.translationQuestion = questionContent
      examStore.currentTranslationQuestionId = selectedQuestion.id
    } else {
      examStore.professionalQuestion = questionContent
      examStore.currentProfessionalQuestionId = selectedQuestion.id
    }

    // 保存题目ID到后端
    if (examStore.currentStudent) {
      try {
        const updateData = {}
        if (currentQuestionType.value === 'translation') {
          updateData.translationQuestionId = selectedQuestion.id
          updateData.translationQuestion = selectedQuestion.content || selectedQuestion.question_data
        } else {
          updateData.professionalQuestionId = selectedQuestion.id
          updateData.professionalQuestion = selectedQuestion.content || selectedQuestion.question_data
          updateData.professionalSubject = selectedSubject.value
        }
        await api.put(`/exam-api/students/${examStore.currentStudent}`, updateData)
      } catch (error) {
        console.error('保存题目ID失败:', error)
      }
    }

    toast.success(`题目抽取成功 - 第 ${questionNumber} 题`)
    isDrawing.value = false

  } catch (error) {
    // 错误处理：停止动画，显示错误
    if (animationTimer.value) {
      clearInterval(animationTimer.value)
      animationTimer.value = null
    }
    tempHighlightId.value = null
    isDrawing.value = false
    toast.error('抽取失败: ' + error.message)
  }
}
```

---

## Task 4: 添加 closeModal 清理逻辑

**Files:**
- Modify: `frontend/src/components/StepContent.vue:closeModal`

- [ ] **Step 1: 更新 closeModal 函数清理定时器**

```javascript
// 关闭弹窗
const closeModal = () => {
  // 清理动画定时器
  if (animationTimer.value) {
    clearInterval(animationTimer.value)
    animationTimer.value = null
  }

  showQuestionModal.value = false
  selectedQuestionId.value = null
  isDrawing.value = false
  tempHighlightId.value = null
}
```

---

## Task 5: 添加科目选择弹窗

**Files:**
- Modify: `frontend/src/components/StepContent.vue - 在template中添加弹窗`

- [ ] **Step 1: 在 template 中添加科目选择弹窗（在question-modal之前）**

```vue
<!-- 科目选择弹窗 - 新增 -->
<div v-if="showSubjectModal" class="modal-overlay" @click="closeSubjectModal">
  <div class="modal subject-modal" @click.stop>
    <div class="modal-header">
      <h3>选择专业科目</h3>
      <button class="modal-close" @click="closeSubjectModal">&times;</button>
    </div>
    <div class="subject-grid">
      <button
        v-for="subject in subjects"
        :key="subject.code"
        :class="['subject-item', { selected: selectedSubject === subject.code }]"
        @click="selectedSubject = subject.code"
      >
        {{ subject.name }}
      </button>
    </div>
    <div class="modal-footer">
      <button @click="closeSubjectModal" class="cancel-btn">取消</button>
      <button @click="confirmSubject" class="confirm-btn" :disabled="!selectedSubject">
        确定
      </button>
    </div>
  </div>
</div>
```

- [ ] **Step 2: 添加科目选择相关的处理函数**

```javascript
// 关闭科目选择弹窗
const closeSubjectModal = () => {
  showSubjectModal.value = false
  selectedSubject.value = ''
}

// 确认科目选择
const confirmSubject = () => {
  if (!selectedSubject.value) return
  showSubjectModal.value = false
  openQuestionSelection('professional')
}

// 打开专业题抽题 - 触发科目选择弹窗
const openProfessionalQuestion = () => {
  selectedSubject.value = ''
  showSubjectModal.value = true
}
```

---

## Task 6: 修改步骤4的点击行为

**Files:**
- Modify: `frontend/src/components/StepContent.vue - 步骤4区域`

- [ ] **Step 1: 修改专业题抽取按钮的点击事件**

将步骤4中的：
```vue
<button @click="openQuestionSelection('professional')" class="select-btn">
  抽取专业题目
</button>
```

改为：
```vue
<button @click="openProfessionalQuestion" class="select-btn">
  抽取专业题目
</button>
```

- [ ] **Step 2: 确保步骤4不再显示科目选择按钮区域**

移除或隐藏原来在步骤4中直接显示科目选择的代码（如果有的话）

---

## Task 7: 添加科目选择弹窗的CSS样式

**Files:**
- Modify: `frontend/src/components/StepContent.vue - style区域`

- [ ] **Step 1: 添加科目选择弹窗样式**

```css
/* 科目选择弹窗 */
.subject-modal {
  max-width: 500px;
}

.subject-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  padding: 20px;
}

.subject-item {
  padding: 20px;
  background: #f8f9fa;
  border: 2px solid #dee2e6;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.subject-item:hover {
  background: #e9ecef;
  border-color: #adb5bd;
}

.subject-item.selected {
  background: #e7f5ff;
  border-color: #007bff;
  color: #007bff;
  font-weight: bold;
}

.cancel-btn {
  padding: 10px 20px;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.cancel-btn:hover {
  background: #5a6268;
}
```

---

## Task 8: 构建和测试

**Files:**
- Build: `frontend/`

- [ ] **Step 1: 构建前端**

```bash
cd F:/code/exam/Exam_v4.0/Exam_v3.2/frontend && npm run build
```

- [ ] **Step 2: 测试抽题动画**

使用 Playwright 访问 http://localhost:5000
1. 点击"开始考试"
2. 进入步骤3（英文翻译）
3. 点击"抽取翻译题目"
4. 点击"开始抽取"
5. 验证：动画持续约2.5秒，题目依次高亮，最后停在选中题

- [ ] **Step 3: 测试专业题科目选择**

1. 进入步骤4（专业问题）
2. 点击"抽取专业题目"
3. 验证：先弹出科目选择弹窗
4. 选择科目，点击确定
5. 验证：进入抽题弹窗，显示该科目题目

---

## 验收检查清单

- [ ] 动画持续约2.5秒
- [ ] 逐个扫描效果可见（浅绿色高亮）
- [ ] API请求与动画同时进行
- [ ] 最终选中题目显示高亮绿色+放大
- [ ] 动画过程中禁用"开始抽取"按钮
- [ ] 关闭弹窗时清理定时器
- [ ] API失败时停止动画并显示错误
- [ ] 专业题先弹出科目选择弹窗
- [ ] 科目选择后才能进入抽题界面
