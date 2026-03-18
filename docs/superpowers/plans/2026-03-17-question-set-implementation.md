# 套题与图片题目功能实现计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现套题（多子题）支持和图片上传功能

**Architecture:**
- 后端：新增图片上传/删除API，配置静态文件服务
- 前端题库管理：添加题目类型切换、子题列表管理、图片上传组件
- 前端考试展示：套题模式遍历渲染所有子题目

**Tech Stack:** Vue 3, Flask, SQLite

---

## Chunk 1: 后端 - 图片上传与静态文件服务

### Task 1.1: 创建图片上传蓝图

**Files:**
- Create: `backend/apis/editor/upload.py`
- Modify: `backend/app.py` - 注册蓝图
- Modify: `backend/apis/editor/__init__.py` - 导入蓝图

- [ ] **Step 1: 创建 upload.py 文件**

```python
# backend/apis/editor/upload.py
"""
图片上传模块
"""

import os
from flask import Blueprint, request, send_from_directory
from werkzeug.utils import secure_filename
from ..common.utils import format_response

upload_bp = Blueprint('upload', __name__, url_prefix='/upload')

# 配置
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """检查文件类型是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@upload_bp.route('/image', methods=['POST'])
def upload_image():
    """上传图片"""
    try:
        if 'file' not in request.files:
            return format_response(
                success=False,
                error='请选择要上传的文件',
                status_code=400
            )

        file = request.files['file']

        if file.filename == '':
            return format_response(
                success=False,
                error='请选择要上传的文件',
                status_code=400
            )

        if not allowed_file(file.filename):
            return format_response(
                success=False,
                error=f'不支持的文件类型，允许的类型: {", ".join(ALLOWED_EXTENSIONS)}',
                status_code=400
            )

        # 检查文件大小
        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)

        if file_size > MAX_FILE_SIZE:
            return format_response(
                success=False,
                error='文件大小超过限制（最大5MB）',
                status_code=400
            )

        # 生成安全文件名
        filename = secure_filename(file.filename)
        # 添加时间戳避免重名
        import time
        timestamp = int(time.time() * 1000)
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{timestamp}{ext}"

        # 保存文件
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # 返回相对路径
        path = f"/uploads/{filename}"

        return format_response(
            success=True,
            data={'path': path},
            message='图片上传成功'
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f'图片上传失败: {str(e)}',
            status_code=500
        )


@upload_bp.route('/image', methods=['DELETE'])
def delete_image():
    """删除图片"""
    try:
        data = request.get_json()
        if not data or 'path' not in data:
            return format_response(
                success=False,
                error='请提供图片路径',
                status_code=400
            )

        path = data['path']
        # 移除前导斜杠
        path = path.lstrip('/')

        # 安全检查：只允许删除 uploads 目录下的文件
        if not path.startswith('uploads/') or '..' in path or path.startswith('/'):
            return format_response(
                success=False,
                error='无效的文件路径',
                status_code=400
            )

        filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static', path)

        if os.path.exists(filepath):
            os.remove(filepath)
            return format_response(
                success=True,
                message='图片删除成功'
            )
        else:
            return format_response(
                success=False,
                error='文件不存在',
                status_code=404
            )

    except Exception as e:
        return format_response(
            success=False,
            error=f'图片删除失败: {str(e)}',
            status_code=500
        )


@upload_bp.route('/<path:filename>', methods=['GET'])
def get_image(filename):
    """获取图片"""
    return send_from_directory(UPLOAD_FOLDER, filename)
```

- [ ] **Step 2: 在 app.py 中添加静态文件路由**

在 `backend/app.py` 的 `# 后端静态资源` 部分之前添加:
```python
# 图片上传目录静态文件服务
@app.route('/uploads/<path:filename>')
def serve_uploads(filename):
    """服务上传的图片"""
    return send_from_directory(os.path.join(current_dir, 'static', 'uploads'), filename)
```

- [ ] **Step 3: 在 editor/__init__.py 中注册蓝图**

在 `backend/apis/editor/__init__.py` 文件末尾添加:
```python
# 导入上传蓝图
try:
    from .upload import upload_bp
    editor_bp.register_blueprint(upload_bp)
    print("OK - upload API registered")
except ImportError as e:
    print(f"INFO - upload module not found: {e}")
```

- [ ] **Step 4: 测试图片上传功能**

Run: 使用 Postman 或 curl 测试
```bash
curl -X POST -F "file=@test.png" http://localhost:5000/api/upload/image
```
Expected: 返回 {"success": true, "data": {"path": "/uploads/xxx.png"}}

- [ ] **Step 5: Commit**

```bash
git add backend/apis/editor/upload.py backend/app.py backend/apis/editor/__init__.py
git commit -m "feat: add image upload API"
```

---

### Task 1.2: 后端内容验证（可选）

**Files:**
- Modify: `backend/apis/editor/questions.py` - 添加验证逻辑

- [ ] **Step 1: 在 create_question 中添加验证**

在 `backend/apis/editor/questions.py` 的 `create_question` 函数中，content 验证部分添加:
```python
# 验证 content 格式
if not isinstance(content, list):
    return format_response(success=False, error='content 必须是数组', status_code=400)

# 检查是否是套题格式
if len(content) > 0 and isinstance(content[0], dict) and 'content' in content[0]:
    # 套题格式验证
    if len(content) > 50:
        return format_response(success=False, error='子题数量不能超过50道', status_code=400)
    for i, sub in enumerate(content):
        if not isinstance(sub.get('content'), list) or len(sub.get('content', [])) == 0:
            return format_response(success=False, error=f'第{i+1}道子题内容不能为空', status_code=400)
        for item in sub['content']:
            if not isinstance(item, list) or len(item) != 2:
                return format_response(success=False, error=f'内容格式错误', status_code=400)
            if item[0] not in ['txt', 'img']:
                return format_response(success=False, error=f'不支持的内容类型: {item[0]}', status_code=400)
```

- [ ] **Step 2: Commit**

```bash
git add backend/apis/editor/questions.py
git commit -m "feat: add content validation for question sets"
```

---

## Chunk 2: 前端 - 题库管理编辑器改造

### Task 2.1: 修改 EditorView.vue - 添加题目类型切换

**Files:**
- Modify: `frontend/src/views/EditorView.vue`

- [ ] **Step 1: 在弹窗模板中添加题目类型切换**

找到添加/编辑弹窗的模板部分，添加:
```vue
<!-- 题目类型选择 -->
<div class="form-group">
  <label class="checkbox-label">
    <input type="checkbox" v-model="isQuestionSet">
    套题模式（包含多道子题目）
  </label>
</div>
```

- [ ] **Step 2: 添加 isQuestionSet 响应式变量**

在 `script setup` 部分添加:
```javascript
const isQuestionSet = ref(false)  // 是否为套题模式
const subQuestions = ref([])  // 子题列表
```

- [ ] **Step 3: 修改 openAddModal 函数**

```javascript
const openAddModal = () => {
  isEditing.value = false
  editingId.value = null
  isQuestionSet.value = false
  subQuestions.value = []
  formData.value = {
    question_index: '',
    subject: 'computer_science',
    difficulty: 'medium',
    content: ''
  }
  showModal.value = true
}
```

- [ ] **Step 4: 修改 editQuestion 函数以支持套题**

```javascript
const editQuestion = (q) => {
  isEditing.value = true
  editingId.value = q.id

  // 判断是否为套题格式
  const content = q.content || q.question_data
  const isSet = isQuestionSetFormat(content)

  if (isSet) {
    // 套题模式
    isQuestionSet.value = true
    subQuestions.value = content.map((sub, index) => ({
      id: index,
      content: sub.content
    }))
    formData.value = {
      question_index: q.question_index,
      subject: q.subject || 'computer_science',
      difficulty: q.difficulty || 'medium',
      content: ''
    }
  } else {
    // 单题模式
    isQuestionSet.value = false
    subQuestions.value = []
    formData.value = {
      question_index: q.question_index,
      subject: q.subject || 'computer_science',
      difficulty: q.difficulty || 'medium',
      content: getPreviewText(content)
    }
  }
  showModal.value = true
}

// 判断是否为套题格式
const isQuestionSetFormat = (content) => {
  if (!content || !Array.isArray(content)) return false
  return content.length > 0 && typeof content[0] === 'object' && 'content' in content[0]
}

// 获取纯文本内容
const getPreviewText = (content) => {
  if (!content) return ''
  try {
    const data = typeof content === 'string' ? JSON.parse(content) : content
    if (data[0] && data[0][1]) {
      return data[0][1]
    }
  } catch {}
  return ''
}
```

- [ ] **Step 5: Commit**

```bash
git add frontend/src/views/EditorView.vue
git commit -m "feat: add question type toggle in editor"
```

---

### Task 2.2: 添加子题列表管理组件

**Files:**
- Modify: `frontend/src/views/EditorView.vue`

- [ ] **Step 1: 在弹窗模板中添加子题列表渲染**

在题目类型切换后，根据 `isQuestionSet` 显示不同内容:

```vue
<!-- 单题模式 -->
<div v-if="!isQuestionSet" class="form-group">
  <label>题目内容</label>
  <textarea
    v-model="formData.content"
    rows="4"
    class="form-textarea"
    placeholder="请输入题目内容..."
  ></textarea>
  <!-- 单题图片上传 -->
  <button type="button" @click="triggerImageUpload('single')" class="btn-upload">
    添加图片
  </button>
</div>

<!-- 套题模式 -->
<div v-else class="sub-questions-container">
  <div class="sub-question-item" v-for="(sub, index) in subQuestions" :key="sub.id">
    <div class="sub-question-header">
      <span class="sub-question-number">子题 {{ index + 1 }}</span>
      <button type="button" @click="removeSubQuestion(index)" class="btn-remove">删除</button>
    </div>
    <textarea
      v-model="sub.content"
      rows="3"
      class="form-textarea"
      placeholder="请输入子题内容..."
    ></textarea>
    <!-- 子题图片列表 -->
    <div class="sub-question-images">
      <div v-for="(img, imgIndex) in getSubQuestionImages(sub.content)" :key="imgIndex" class="image-preview">
        <img :src="img[1]" alt="题目图片">
        <button type="button" @click="removeSubQuestionImage(index, imgIndex)" class="btn-remove-image">×</button>
      </div>
    </div>
    <button type="button" @click="triggerImageUpload(index)" class="btn-upload">
      添加图片
    </button>
  </div>
  <button type="button" @click="addSubQuestion" class="btn-add-sub">
    + 添加子题
  </button>
</div>

<!-- 隐藏的文件输入 -->
<input type="file" ref="imageInput" @change="handleImageSelect" accept="image/*" style="display: none">
```

- [ ] **Step 2: 添加子题管理函数**

```javascript
// 添加子题
const addSubQuestion = () => {
  subQuestions.value.push({
    id: Date.now(),
    content: []
  })
}

// 删除子题
const removeSubQuestion = (index) => {
  if (subQuestions.value.length > 1) {
    subQuestions.value.splice(index, 1)
  } else {
    toast.warning('至少保留一道子题')
  }
}

// 获取子题中的图片
const getSubQuestionImages = (content) => {
  if (!content || !Array.isArray(content)) return []
  return content.filter(item => item[0] === 'img')
}

// 删除子题中的图片
const removeSubQuestionImage = (subIndex, imgIndex) => {
  const content = subQuestions.value[subIndex].content
  content.splice(imgIndex, 1)
}

// 图片上传相关
const imageInput = ref(null)
const currentImageUploadTarget = ref(null)

const triggerImageUpload = (target) => {
  currentImageUploadTarget.value = target
  imageInput.value?.click()
}

const handleImageSelect = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return

  try {
    const formData = new FormData()
    formData.append('file', file)

    const response = await fetch('/api/upload/image', {
      method: 'POST',
      body: formData
    })
    const result = await response.json()

    if (result.success) {
      const imagePath = result.data.path

      // 根据目标添加到不同位置
      if (currentImageUploadTarget.value === 'single') {
        // 单题模式 - 暂时不支持，后续可扩展
        toast.info('单题图片功能开发中')
      } else if (typeof currentImageUploadTarget.value === 'number') {
        // 套题模式 - 添加到指定子题
        const subIndex = currentImageUploadTarget.value
        if (!subQuestions.value[subIndex].content) {
          subQuestions.value[subIndex].content = []
        }
        subQuestions.value[subIndex].content.push(['img', imagePath])
      }
    } else {
      toast.error(result.error || '图片上传失败')
    }
  } catch (error) {
    toast.error('图片上传失败')
  }

  // 清空 input 以便重复选择同一文件
  event.target.value = ''
}
```

- [ ] **Step 3: 添加子题相关样式**

在 `<style scoped>` 中添加:
```css
.sub-questions-container {
  max-height: 400px;
  overflow-y: auto;
}

.sub-question-item {
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 15px;
}

.sub-question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.sub-question-number {
  font-weight: bold;
  color: #007bff;
}

.sub-question-images {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 10px;
}

.image-preview {
  position: relative;
  width: 100px;
  height: 100px;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
}

.image-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.btn-remove-image {
  position: absolute;
  top: 2px;
  right: 2px;
  width: 20px;
  height: 20px;
  background: rgba(255,0,0,0.7);
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  font-size: 14px;
  line-height: 1;
}

.btn-upload, .btn-add-sub {
  margin-top: 10px;
  padding: 8px 16px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-add-sub {
  width: 100%;
  background: #28a745;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.checkbox-label input {
  width: 18px;
  height: 18px;
}
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/views/EditorView.vue
git commit -m "feat: add sub-question management in editor"
```

---

### Task 2.3: 修改 saveQuestion 函数支持套题格式

**Files:**
- Modify: `frontend/src/views/EditorView.vue`

- [ ] **Step 1: 修改 saveQuestion 函数**

```javascript
// 保存题目
const saveQuestion = async () => {
  // 构建题目数据
  let content

  if (isQuestionSet.value) {
    // 套题模式
    if (subQuestions.value.length === 0) {
      toast.warning('请至少添加一道子题')
      return
    }

    // 将文本内容转换为数组格式
    content = subQuestions.value.map(sub => {
      let subContent = []
      if (sub.content) {
        // 检查是否已经是数组格式（包含图片的情况）
        if (Array.isArray(sub.content)) {
          subContent = sub.content
        } else {
          // 纯文本情况
          subContent = [['txt', sub.content]]
        }
      }
      return { content: subContent }
    })
  } else {
    // 单题模式
    if (!formData.value.content) {
      toast.warning('请填写题目内容')
      return
    }
    content = [['txt', formData.value.content]]
  }

  try {
    let response

    if (isEditing.value) {
      // 更新
      response = await api.put(`/api/questions/question/${editingId.value}`, {
        content: content,
        subject: formData.value.subject,
        difficulty: formData.value.difficulty
      })
    } else {
      // 添加
      response = await api.post('/api/questions', {
        type: currentType.value,
        content: content,
        subject: formData.value.subject,
        difficulty: formData.value.difficulty
      })
    }

    if (response.success) {
      toast.success(isEditing.value ? '更新成功' : '添加成功')
      closeModal()
      loadQuestions()
    } else {
      toast.error(response.error || '保存失败')
    }
  } catch (error) {
    toast.error('保存失败: ' + error.message)
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/views/EditorView.vue
git commit -m "feat: support question set format in saveQuestion"
```

---

### Task 2.4: 修改题目列表显示

**Files:**
- Modify: `frontend/src/views/EditorView.vue`

- [ ] **Step 1: 修改题目列表显示逻辑**

找到题目列表渲染部分，修改显示内容:
```vue
<div class="question-info">
  <div class="question-index">{{ (currentPage - 1) * pageSize + index + 1 }}</div>
  <div class="question-content">
    <div class="question-preview">{{ getPreview(q) }}</div>
    <!-- 套题标记 -->
    <div v-if="isQuestionSetFormat(q.content || q.question_data)" class="question-set-badge">
      套题({{ (q.content || q.question_data).length }}题)
    </div>
  </div>
</div>
```

- [ ] **Step 2: 添加相关函数**

```javascript
// 获取题目预览（兼容两种格式）
const getPreview = (question) => {
  if (!question) return ''
  try {
    const content = question.content || question.question_data
    if (!content) return ''
    const data = typeof content === 'string' ? JSON.parse(content) : content

    // 判断套题格式
    if (isQuestionSetFormat(data)) {
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

- [ ] **Step 3: 添加套题标记样式**

```css
.question-set-badge {
  display: inline-block;
  padding: 2px 8px;
  background: #ffc107;
  color: #333;
  border-radius: 10px;
  font-size: 12px;
  margin-left: 8px;
}
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/views/EditorView.vue
git commit -m "feat: display question set badge in list"
```

---

## Chunk 3: 前端 - 考试展示改造

### Task 3.1: 修改 StepContent.vue 套题渲染

**Files:**
- Modify: `frontend/src/components/StepContent.vue`

- [ ] **Step 1: 找到题目渲染部分**

先读取 StepContent.vue 找到渲染题目的位置:
```bash
grep -n "question-content\|renderQuestion\|displayQuestion" frontend/src/components/StepContent.vue
```

- [ ] **Step 2: 添加判断函数**

```javascript
// 判断是否为套题格式
const isQuestionSet = (content) => {
  if (!content || !Array.isArray(content)) return false
  return content.length > 0 && typeof content[0] === 'object' && 'content' in content[0]
}

// 渲染题目内容（支持图片）
const renderQuestionContent = (content) => {
  if (!content || !Array.isArray(content)) return ''

  return content.map(item => {
    if (item[0] === 'txt') {
      return `<p>${escapeHtml(item[1] || '')}</p>`
    } else if (item[0] === 'img') {
      return `<div class="question-image"><img src="${item[1]}" alt="题目图片" onclick="showImageModal('${item[1]}')"></div>`
    }
    return ''
  }).join('')
}

// HTML 转义
const escapeHtml = (text) => {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}
```

- [ ] **Step 3: 修改模板渲染逻辑**

找到题目内容显示的模板，修改为:
```vue
<!-- 单题模式 -->
<div v-if="!isQuestionSet(currentQuestion?.content)" v-html="renderQuestionContent(currentQuestion?.content)">
</div>

<!-- 套题模式 -->
<div v-else class="question-set">
  <div v-for="(sub, index) in currentQuestion.content" :key="index" class="sub-question">
    <div class="sub-question-label">第 {{ index + 1 }} 题</div>
    <div class="sub-question-content" v-html="renderQuestionContent(sub.content)"></div>
  </div>
</div>
```

- [ ] **Step 4: 添加套题样式**

```css
.question-set {
  padding: 15px;
}

.sub-question {
  margin-bottom: 25px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.sub-question-label {
  font-weight: bold;
  color: #007bff;
  margin-bottom: 10px;
  font-size: 16px;
}

.sub-question-content {
  line-height: 1.8;
}

.sub-question-content p {
  margin-bottom: 10px;
}

.question-image {
  margin: 15px 0;
}

.question-image img {
  max-width: 100%;
  border-radius: 4px;
  cursor: pointer;
}

.question-image img:hover {
  opacity: 0.9;
}
```

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/StepContent.vue
git commit -m "feat: render question set in exam view"
```

---

## Chunk 4: 测试与验证

### Task 4.1: 功能测试

- [ ] **Step 1: 测试图片上传**

在题库管理中添加图片，观察是否能正常上传和显示

- [ ] **Step 2: 测试套题创建**

创建套题，添加多个子题，保存后查看是否正确显示

- [ ] **Step 3: 测试套题编辑**

编辑已有的套题，修改子题内容

- [ ] **Step 4: 测试考试展示**

开始考试，查看套题是否一次性显示所有子题目

- [ ] **Step 5: 测试兼容性**

确保原有的单题功能仍然正常工作

---

## 总结

实现计划包含 4 个 Chunk:
1. **后端 - 图片上传与静态文件服务** (2 Tasks)
2. **前端 - 题库管理编辑器改造** (4 Tasks)
3. **前端 - 考试展示改造** (1 Task)
4. **测试与验证** (1 Task)

Total: 8 Tasks

每个 Task 都是独立可测试的功能单元，完成后可提交 commit。
