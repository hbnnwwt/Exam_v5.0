# 考试记录预览显示题目内容 - 设计文档

## 概述

在考试记录预览页面，通过行内展开方式显示每个考生的考试题目内容。

## 现状分析

- 后端 `/export-api/preview` API 已返回 `translationInfo` 和 `professionalInfo`
- 前端目前只展示了基本表格信息（考生号、状态、时间等）
- 需要在前端添加展开/收起交互，显示题目内容

## UI/UX 设计

### 交互方式
1. 每行右侧添加展开/收起按钮（眼睛图标）
2. 点击按钮或整行展开下方区域
3. 展开区域显示翻译题目和专业题目内容
4. 再次点击可收起

### 布局结构
```
| 考生号 | 考试状态 | 专业科目 | ... | 操作 |
|--------|----------|----------|-----|------|
|  01   | 已完成   | c_language |  | [展开] |
|--------|----------|------------|-----|------|
|        | 翻译题目 (题号: 1)              |
| 展开行 | -------------------------------- |
|        | 专业题目 (题号: 3) - c_language |
|--------|----------------------------------|
```

### 样式
- 展开行：浅灰色背景 `#f8f9fa`
- 题目标题：加粗，14px
- 题目内容：常规字体，支持文本和图片
- 图片：最大宽度100px缩略图显示，点击可放大

## 技术实现

### 后端（无需修改）
- API已返回题目信息：
  - `translationInfo`: { questionNumber, questionContent }
  - `professionalInfo`: { questionNumber, questionContent, subject }

### 前端修改
**文件**: `frontend/src/views/ExportView.vue`

1. 添加展开状态管理
```javascript
const expandedRows = ref(new Set())
```

2. 添加展开/收起方法
```javascript
const toggleExpand = (studentNumber) => {
  if (expandedRows.value.has(studentNumber)) {
    expandedRows.value.delete(studentNumber)
  } else {
    expandedRows.value.add(studentNumber)
  }
}
```

3. 模板修改
- 每行添加展开按钮
- 条件渲染展开区域
- 复用题目内容渲染逻辑

## 验收标准

1. 点击展开按钮显示题目内容
2. 再次点击收起题目内容
3. 文本题目正常显示
4. 图片题目显示缩略图，点击可放大
5. 翻译题目和专业题目都正确显示
