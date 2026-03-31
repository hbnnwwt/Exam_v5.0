<template>
  <div class="subjects-page">
    <!-- 顶部导航 -->
    <header class="header">
      <div class="header-left">
        <h1>科目管理</h1>
      </div>
      <div class="header-right">
        <router-link to="/editor" class="nav-btn">题库管理</router-link>
        <router-link to="/settings" class="nav-btn">考试设置</router-link>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="main-content">
      <div class="subjects-container">
        <!-- 操作栏 -->
        <div class="toolbar">
          <button @click="openAddModal" class="add-btn">+ 添加科目</button>
        </div>

        <!-- 科目列表 -->
        <div class="subjects-list">
          <div
            v-for="subject in subjects"
            :key="subject.id"
            :class="['subject-item', { inactive: !subject.is_active }]"
          >
            <div class="subject-info">
              <div class="subject-name">{{ subject.name }}</div>
              <div class="subject-code">代码: {{ subject.code }}</div>
              <div class="subject-desc" v-if="subject.description">{{ subject.description }}</div>
            </div>
            <div class="subject-stats">
              <span class="stat-badge">{{ subject.question_count || 0 }} 题</span>
              <span :class="['status-badge', { active: subject.is_active }]">
                {{ subject.is_active ? '启用' : '禁用' }}
              </span>
            </div>
            <div class="subject-actions">
              <button @click="editSubject(subject)" class="action-btn edit">编辑</button>
              <button @click="toggleSubject(subject)" class="action-btn toggle">
                {{ subject.is_active ? '禁用' : '启用' }}
              </button>
              <button @click="deleteSubject(subject)" class="action-btn delete">删除</button>
            </div>
          </div>

          <div v-if="subjects.length === 0" class="empty-state">
            暂无科目，请添加
          </div>
        </div>
      </div>
    </main>

    <!-- 添加/编辑科目弹窗 -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>{{ isEditing ? '编辑科目' : '添加科目' }}</h3>
          <button class="modal-close" @click="closeModal">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>科目代码</label>
            <input
              v-model="formData.code"
              type="text"
              class="form-input"
              placeholder="例如: c_language"
              :disabled="isEditing"
            >
            <small class="form-hint">科目代码用于系统内部识别，建议使用英文和下划线</small>
          </div>

          <div class="form-group">
            <label>科目名称</label>
            <input
              v-model="formData.name"
              type="text"
              class="form-input"
              placeholder="例如: C语言"
            >
          </div>

          <div class="form-group">
            <label>描述</label>
            <textarea
              v-model="formData.description"
              rows="3"
              class="form-textarea"
              placeholder="请输入科目描述..."
            ></textarea>
          </div>

          <div class="form-group" v-if="isEditing">
            <label>
              <input v-model="formData.is_active" type="checkbox">
              启用此科目
            </label>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="closeModal" class="cancel-btn">取消</button>
          <button @click="saveSubject" class="save-btn">保存</button>
        </div>
      </div>
    </div>
  </div>

  <!-- 底部版权 -->
  <footer class="footer">
    <p>{{ footerCopyright || '版权所有 © 2026 北京石油化工学院 | 联系方式：wangwentong@bipt.edu.cn' }}</p>
  </footer>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useToastStore } from '@/stores/toast'
import api from '@/api'

const toast = useToastStore()

// 底部版权信息
const footerCopyright = ref('')

// 加载版权信息
const loadFooterCopyright = async () => {
  try {
    const response = await api.get('/api/header-settings')
    if (response.success && response.data && response.data.footerCopyright) {
      footerCopyright.value = response.data.footerCopyright
    }
  } catch (error) {
    console.error('加载版权信息失败:', error)
  }
}

// 科目列表
const subjects = ref([])

// 弹窗控制
const showModal = ref(false)
const isEditing = ref(false)

// 表单数据
const formData = reactive({
  id: null,
  code: '',
  name: '',
  description: '',
  is_active: true
})

// 加载科目列表
const loadSubjects = async () => {
  try {
    const response = await api.get('/api/subjects')
    if (response.success) {
      subjects.value = response.data || []
    }
  } catch (error) {
    console.error('加载科目失败:', error)
    toast.error('加载科目失败')
  }
}

// 打开添加弹窗
const openAddModal = () => {
  isEditing.value = false
  formData.id = null
  formData.code = ''
  formData.name = ''
  formData.description = ''
  formData.is_active = true
  showModal.value = true
}

// 打开编辑弹窗
const editSubject = (subject) => {
  isEditing.value = true
  formData.id = subject.id
  formData.code = subject.code
  formData.name = subject.name
  formData.description = subject.description || ''
  formData.is_active = subject.is_active
  showModal.value = true
}

// 关闭弹窗
const closeModal = () => {
  showModal.value = false
}

// 保存科目
const saveSubject = async () => {
  if (!formData.code || !formData.name) {
    toast.error('请填写科目代码和名称')
    return
  }

  try {
    let response
    if (isEditing.value) {
      response = await api.put(`/api/editor/subjects/${formData.id}`, {
        name: formData.name,
        description: formData.description,
        is_active: formData.is_active
      })
    } else {
      response = await api.post('/api/editor/subjects', {
        code: formData.code,
        name: formData.name,
        description: formData.description,
        is_active: formData.is_active
      })
    }

    if (response.success) {
      toast.success(isEditing.value ? '更新成功' : '添加成功')
      closeModal()
      loadSubjects()
    } else {
      toast.error(response.error || '操作失败')
    }
  } catch (error) {
    toast.error('操作失败: ' + error.message)
  }
}

// 切换科目状态
const toggleSubject = async (subject) => {
  try {
    const response = await api.post(`/api/editor/subjects/${subject.id}/toggle`)
    if (response.success) {
      toast.success(subject.is_active ? '已禁用' : '已启用')
      loadSubjects()
    } else {
      toast.error(response.error || '操作失败')
    }
  } catch (error) {
    toast.error('操作失败: ' + error.message)
  }
}

// 删除科目
const deleteSubject = async (subject) => {
  if (!confirm(`确定要删除科目"${subject.name}"吗？`)) {
    return
  }

  try {
    const response = await api.delete(`/api/editor/subjects/${subject.id}`)
    if (response.success) {
      toast.success('删除成功')
      loadSubjects()
    } else {
      toast.error(response.error || '删除失败')
    }
  } catch (error) {
    toast.error('删除失败: ' + error.message)
  }
}

onMounted(() => {
  loadSubjects()
  loadFooterCopyright()
})
</script>

<style scoped>
.subjects-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f5f5;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: #007bff;
  color: white;
}

.header h1 {
  margin: 0;
  font-size: 20px;
}

.nav-btn {
  padding: 8px 16px;
  background: rgba(255,255,255,0.2);
  color: white;
  text-decoration: none;
  border-radius: 4px;
  font-size: 14px;
  margin-left: 10px;
}

.nav-btn:hover {
  background: rgba(255,255,255,0.3);
}

.main-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.subjects-container {
  max-width: 900px;
  margin: 0 auto;
}

.toolbar {
  margin-bottom: 20px;
}

.add-btn {
  padding: 10px 20px;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.add-btn:hover {
  background: #218838;
}

.subjects-list {
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.subject-item {
  display: flex;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
  transition: background 0.2s;
}

.subject-item:hover {
  background: #f8f9fa;
}

.subject-item.inactive {
  opacity: 0.6;
}

.subject-item:last-child {
  border-bottom: none;
}

.subject-info {
  flex: 1;
}

.subject-name {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.subject-code {
  font-size: 13px;
  color: #666;
  margin-top: 4px;
}

.subject-desc {
  font-size: 13px;
  color: #999;
  margin-top: 4px;
}

.subject-stats {
  display: flex;
  gap: 10px;
  margin-right: 20px;
}

.stat-badge {
  padding: 4px 10px;
  background: #e9ecef;
  border-radius: 12px;
  font-size: 13px;
  color: #495057;
}

.status-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 13px;
  background: #dc3545;
  color: white;
}

.status-badge.active {
  background: #28a745;
}

.subject-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
}

.action-btn.edit {
  background: #007bff;
  color: white;
}

.action-btn.toggle {
  background: #ffc107;
  color: #333;
}

.action-btn.delete {
  background: #dc3545;
  color: white;
}

.empty-state {
  padding: 60px 20px;
  text-align: center;
  color: #999;
  font-size: 16px;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
  color: #333;
}

.form-input, .form-textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-textarea {
  resize: vertical;
}

.form-hint {
  display: block;
  margin-top: 5px;
  color: #999;
  font-size: 12px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 15px 20px;
  border-top: 1px solid #eee;
}

.cancel-btn {
  padding: 10px 20px;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.cancel-btn:hover {
  background: #5a6268;
}

.save-btn {
  padding: 10px 20px;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.save-btn:hover {
  background: #218838;
}

/* 底部 */
.footer {
  text-align: center;
  padding: 15px;
  background: #fff;
  border-top: 1px solid #e5e7eb;
  color: #6b7280;
  font-size: 14px;
}
</style>
