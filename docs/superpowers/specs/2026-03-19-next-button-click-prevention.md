# 下一步按钮防连点设计文档

**项目**: 研究生复试系统
**日期**: 2026-03-19
**类型**: UI体验优化

---

## 1. 需求概述

优化"下一步"按钮的点击体验，防止用户快速连点导致跳过步骤的问题。

## 2. 设计方案

### 2.1 交互逻辑

| 状态 | 按钮文字 | 可点击 | 说明 |
|------|----------|--------|------|
| 正常 | 下一步 ▶ | ✅ | 等待用户点击 |
| 点击中 | 处理中... | ❌ | 立即禁用，1秒后恢复 |

### 2.2 实现方式

- 使用现有的 `isProcessing` 状态变量（已用于其他按钮）
- 点击时立即设置 `isProcessing = true`
- 使用 `setTimeout` 在1秒后自动恢复 `isProcessing = false`
- 按钮文字条件渲染，根据状态显示不同文字

### 2.3 代码改动

**文件**: `frontend/src/views/ExamView.vue`

```javascript
// 修改 nextStep 函数
const nextStep = () => {
  if (isProcessing.value) return  // 防止重复点击

  isProcessing.value = true  // 禁用按钮

  examStore.nextStep()
  examStore.saveProgress()

  // 1秒后恢复按钮状态
  setTimeout(() => {
    isProcessing.value = false
  }, 1000)
}
```

```html
<!-- 修改按钮绑定 -->
<button
  @click="nextStep"
  :disabled="isProcessing"
  class="next-btn">
  {{ isProcessing ? '处理中...' : '下一步 ▶' }}
</button>
```

## 3. 验收标准

- [x] 点击"下一步"后按钮立即变灰
- [x] 按钮文字变为"处理中..."
- [x] 1秒后按钮恢复正常状态
- [x] 快速连点时只执行一次
