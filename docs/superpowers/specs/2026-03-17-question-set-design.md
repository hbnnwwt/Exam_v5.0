# 套题与图片题目功能设计

> **创建日期:** 2026-03-17
> **功能:** 套题（多子题）+ 图片题目支持
> **版本:** v1.1 (审查后修订)

## 1. 概述

### 1.1 目标
- 支持一个题目记录包含多个子题目（套题）
- 支持题目中包含图片
- 考试时套题一次性展示所有子题目

### 1.2 架构决策
- **方案B**: 重构 `question_data` 为题目数组格式
- **图片存储**: 后端 `static/uploads/` 目录，通过 `/uploads/xxx.png` 访问
- **数据库**: 无需改动，使用现有的 JSON 字段

---

## 2. 数据结构

### 2.1 question_data 格式

**单题（兼容旧数据）:**
```json
[["txt", "题目内容文本"]]
```

**套题（新格式）:**
```json
[
  { "content": [["txt", "子题1内容"], ["img", "/uploads/img1.png"]] },
  { "content": [["txt", "子题2内容"]] },
  { "content": [["txt", "子题3内容"], ["img", "/uploads/img2.png"]] }
]
```

**判断逻辑:**
- 如果 `question_data[0]` 有 `content` 字段 → 套题
- 否则 → 单题（兼容模式）

---

## 3. 前端设计

### 3.1 题库管理 - 添加/编辑弹窗

#### 3.1.1 题目类型选择
- 单题模式（默认）
- 套题模式（勾选切换）

#### 3.1.2 单题模式
- 文本输入框
- 图片上传按钮（可选）

#### 3.1.3 套题模式
- 子题列表：动态添加/删除/拖拽排序
- 每个子题：
  - 内容输入区域（支持多行）
  - 图片上传按钮
  - 删除按钮
  - 拖拽排序手柄
- 底部：添加子题按钮

#### 3.1.4 图片上传组件
- 支持点击选择文件
- 支持拖拽上传
- 显示图片缩略图
- 支持删除图片

### 3.2 题库管理 - 题目列表

- 套题显示标记：`套题(3题)` 格式
- 预览显示第一道子题内容

### 3.3 考试展示

- 检测题目是否为套题格式
- 套题：遍历渲染所有子题目，每道子题独立显示
- 单题：原有逻辑

---

## 4. 后端 API 设计

### 4.1 新增接口

#### POST /api/upload/image
- **功能**: 图片上传
- **请求**: multipart/form-data, 字段: file
- **响应**:
```json
{
  "success": true,
  "data": {
    "path": "/uploads/xxx.png"
  }
}
```
- **限制**:
  - 文件类型: png, jpg, jpeg, gif, webp, bmp
  - 文件大小: 最大 5MB
  - 存储路径: `backend/static/uploads/`
- **验证**: 文件类型、大小校验

#### DELETE /api/upload/image
- **功能**: 删除图片
- **请求**:
```json
{
  "path": "/uploads/xxx.png"
}
```
- **说明**: 删除题目时或编辑时清理不再使用的图片

### 4.2 修改接口

#### POST /api/questions
- **功能**: 添加题目
- **请求**: 支持套题格式
```json
{
  "type": "professional",
  "content": [
    { "content": [["txt", "子题1内容"]] },
    { "content": [["txt", "子题2内容"], ["img", "/uploads/img.png"]] }
  ],
  "subject": "python",
  "difficulty": "medium"
}
```
- **验证**:
  - `content` 数组长度不超过 50
  - 每个 content 数组非空
  - 类型值必须为 "txt" 或 "img"

#### PUT /api/questions/question/:id
- **功能**: 更新题目
- **请求**: 同上，支持套题格式，可选增加 `imagesToDelete` 字段
```json
{
  "content": [...],
  "subject": "python",
  "difficulty": "medium",
  "imagesToDelete": ["/uploads/old-img.png"]  // 可选：编辑时删除的图片
}
```

#### GET /api/questions/:type
- **功能**: 获取题目列表
- **响应**: 返回完整的 question_data，前端自行判断格式

---

## 5. 实现任务分解

### 5.1 后端
1. 新增图片上传接口 `/api/upload/image`
2. 新增图片删除接口 `/api/upload/image` (DELETE)
3. 修改题目创建/更新逻辑，支持套题格式
4. 配置静态文件访问
5. 增加内容验证规则

### 5.2 前端 - 题库管理
1. 修改 EditorView.vue 添加/编辑弹窗
   - 添加题目类型切换（单题/套题）
   - 实现子题列表管理（增删排序）
   - 实现图片上传组件
2. 修改题目列表显示，区分套题和单题
3. 修改兼容逻辑：
   - `getPreview()` 函数 - 判断套题/单题格式
   - `getContentPreview()` 函数 - 适配两种格式
   - `saveQuestion()` 函数 - 支持套题数组格式

### 5.3 前端 - 考试展示
1. 修改 StepContent.vue
   - 检测题目格式（套题 vs 单题）
   - 套题模式渲染所有子题目

---

## 6. 兼容性考虑

- 旧数据格式 `[["txt", "内容"]]` 完全兼容
- 前端通过判断 `question_data[0].content` 是否存在来区分格式
- 批量导入保持现有逻辑（导入为单题格式）

### 6.1 前端兼容函数

```javascript
// 判断是否为套题格式
const isQuestionSet = (data) => {
  return Array.isArray(data) && data.length > 0 &&
         typeof data[0] === 'object' && 'content' in data[0]
}

// 获取题目预览（兼容两种格式）
const getPreview = (question) => {
  if (!question) return ''
  try {
    const content = question.content || question.question_data
    if (!content) return ''
    const data = typeof content === 'string' ? JSON.parse(content) : content

    // 判断套题格式
    if (isQuestionSet(data)) {
      // 套题：显示第一道子题的内容
      const firstSub = data[0]?.content
      if (firstSub && firstSub[0] && firstSub[0][1]) {
        return firstSub[0][1].substring(0, 100)
      }
    } else {
      // 单题：原有逻辑
      if (data[0] && data[0][1]) {
        return data[0][1].substring(0, 100)
      }
    }
    return ''
  } catch {
    return String(question.content || question.question_data || '').substring(0, 100)
  }
}
```

---

## 7. 文件修改清单

### 后端
- `backend/app.py` - 添加静态文件路由、上传接口注册
- `backend/apis/editor/questions.py` - 修改创建/更新逻辑

### 前端
- `frontend/src/views/EditorView.vue` - 添加/编辑弹窗改造
- `frontend/src/components/StepContent.vue` - 考试展示改造
