# 抽题模块改进设计文档

**日期**: 2026-03-16
**主题**: 抽题模块UE优化

## 1. 需求概述

对抽题模块进行以下改进：

1. **优化抽题动画** - 改为2-3秒的逐个扫描效果
2. **已抽取题目显示** - 保持当前方式（已有实现）
3. **专业题科目选择** - 改为分两步弹窗方式

## 2. 当前实现分析

### 2.1 抽题动画
- 当前：简单的加载动画，持续时间短（约1秒）
- 问题：动画太快，用户感知不强

### 2.2 专业题科目选择
- 当前：在主内容区直接显示科目选择按钮
- 问题：不够直观，应该用弹窗

## 3. 设计方案

### 3.1 抽题动画改进（修正版）

**效果描述**：逐个扫描效果 - 依次高亮每个题目，最后停在选中题

**核心改进**：
1. **先动画 + 同时发API请求** - 减少等待感知
2. **动态计算扫描间隔** - 固定2.5秒，间隔 = 2500ms / 题目数量，最小100ms
3. **添加 tempHighlightId 变量** - 跟踪扫描中高亮的题目
4. **添加清理逻辑** - 防止内存泄漏

**技术实现**：
```javascript
// 新增状态变量
const tempHighlightId = ref(null)   // 动画中临时高亮的题目ID
const animationTimer = ref(null)     // 动画定时器引用

const startDraw = async () => {
  // 防止重复点击
  if (availableCount.value === 0 || isDrawing.value) return

  // 1. 立即开始动画
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

  // 2. 同时发起API请求（不等待）
  const fetchPromise = api.get(url)

  try {
    // 3. 等待API响应
    const response = await fetchPromise

    // 4. API返回后，停止扫描动画
    if (animationTimer.value) {
      clearInterval(animationTimer.value)
      animationTimer.value = null
    }

    if (!response.success || !response.data) {
      throw new Error('没有可用的题目')
    }

    const selectedQuestion = response.data

    // 5. 显示最终结果
    tempHighlightId.value = null
    selectedQuestionId.value = selectedQuestion.id

    // 6. 更新题目状态
    const qIndex = questionList.findIndex(q => q.id === selectedQuestion.id)
    if (qIndex !== -1) {
      questionList[qIndex].is_used = true
    }

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

**组件卸载清理**：
```javascript
import { onUnmounted } from 'vue'

onUnmounted(() => {
  if (animationTimer.value) {
    clearInterval(animationTimer.value)
  }
})
```

**颜色定义**：
| 状态 | 颜色代码 | 说明 |
|------|----------|------|
| 可用题目 | `#28a745` (绿色) | 未被抽过的题目 |
| 扫描中高亮 | `#86efac` (浅绿色) | 动画过程中临时高亮 |
| 已使用题目 | `#6c757d` (灰色) | 已被抽过 |
| 最终选中 | `#198754` (高亮绿) + 放大 | 动画停止时的选中题 |

### 3.2 专业题科目选择弹窗

**交互流程**：
```
用户点击"抽取专业题目"按钮
    ↓
弹出"选择科目"弹窗
    ↓
用户点击科目 → 点击"确定"
    ↓
关闭科目弹窗，打开抽题弹窗
    ↓
进行抽题流程
```

**状态变量**：
```javascript
// 新增：科目选择弹窗
const showSubjectModal = ref(false)

// 现有变量复用
const showQuestionModal = ref(false)  // 抽题弹窗
const selectedSubject = ref('')       // 选中的科目
```

**弹窗结构**：
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

**科目选择处理函数**：
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

### 3.3 已抽取题目显示（保持现有实现）

当前实现已满足需求：
- 从API获取题目时包含 `is_used` 字段
- 前端根据 `is_used` 显示不同颜色
- 统计信息显示：总计、已使用、可用

## 4. 边界情况处理

| 场景 | 处理方式 |
|------|----------|
| 动画中关闭弹窗 | 在 closeModal 中清理 animationTimer |
| API请求失败 | 停止动画，显示错误提示 |
| 题目已全部使用 | isDrawing 前检查 availableCount，禁用抽取按钮 |
| 快速连续点击 | isDrawing 检查 + 按钮 disabled 属性 |
| 重新打开弹窗 | API返回最新的 is_used 状态（后端已保存） |
| 题目数<5 | interval 最小100ms，保证至少扫描5轮 |

## 5. 数据流设计

### 5.1 组件状态

```
StepContent.vue
├── 题目相关
│   ├── questions: 题目列表
│   ├── selectedQuestionId: 当前选中的题目ID
│   └── tempHighlightId: 动画中临时高亮的题目ID（新增）
├── 科目相关
│   ├── showSubjectModal: 是否显示科目选择弹窗（新增）
│   ├── showQuestionModal: 是否显示抽题弹窗
│   └── selectedSubject: 选中的科目代码
└── 动画相关
    ├── isDrawing: 是否正在抽取
    └── animationTimer: 动画定时器引用（新增）
```

### 5.2 交互流程

```
1. 用户点击"抽取翻译题目"
   → openQuestionSelection('translation')
   → 直接打开抽题弹窗

2. 用户点击"抽取专业题目"
   → openProfessionalQuestion()
   → showSubjectModal = true
   → 显示科目选择弹窗

3. 用户选择科目并确定
   → confirmSubject()
   → showSubjectModal = false
   → openQuestionSelection('professional')
   → showQuestionModal = true

4. 用户点击"开始抽取"
   → startDraw()
   → 立即开始扫描动画 + 同时发起API请求
   → 动画2.5秒后，使用API返回结果显示最终结果
```

## 6. 验收标准

### 6.1 抽题动画
- [ ] 动画持续约2.5秒
- [ ] 逐个扫描效果可见（题目依次浅绿色高亮）
- [ ] API请求与动画同时进行，减少等待感知
- [ ] 最终停在选中的题目上，显示高亮绿色+放大
- [ ] 动画过程中禁用"开始抽取"按钮
- [ ] 动画中关闭弹窗，状态正确重置（无内存泄漏）
- [ ] API请求失败时，动画停止并显示错误提示

### 6.2 专业题科目选择
- [ ] 点击"抽取专业题目"先弹出科目选择弹窗
- [ ] 科目选择后才能进入抽题界面
- [ ] 取消科目选择返回主界面
- [ ] 已选科目可再次更改

### 6.3 已抽取题目显示
- [ ] 已使用题目显示为灰色
- [ ] 可用题目显示为绿色
- [ ] 统计信息正确

## 7. 影响范围

- **修改文件**：`frontend/src/components/StepContent.vue`
- **无后端改动**：所有功能通过前端实现
- **向后兼容**：现有API无需修改
