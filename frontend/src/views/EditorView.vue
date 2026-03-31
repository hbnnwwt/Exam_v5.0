<template>
  <div class="editor-page">
    <!-- 顶部导航 -->
    <header class="header">
      <div class="header-left">
        <h1>题库管理</h1>
      </div>
      <div class="header-right">
        <button @click="openBatchImportModal" class="nav-btn batch-btn">批量导入</button>
        <button @click="openBatchExportModal" class="nav-btn batch-btn">批量导出</button>
        <router-link to="/" class="nav-btn">返回考试</router-link>
        <router-link to="/help" class="nav-btn">帮助</router-link>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="main-content">
      <!-- 左侧边栏 -->
      <aside class="sidebar">
        <!-- 题目类型Tab -->
        <div class="sidebar-section">
          <div class="tab-buttons">
            <button
              :class="['tab-btn', { active: currentTab === 'translation' }]"
              @click="switchTab('translation')"
            >
              翻译题目
            </button>
            <button
              :class="['tab-btn', { active: currentTab === 'professional' }]"
              @click="switchTab('professional')"
            >
              专业题目
            </button>
            <button
              :class="['tab-btn', { active: currentTab === 'subjects' }]"
              @click="switchTab('subjects')"
            >
              科目管理
            </button>
          </div>
        </div>

        <!-- 科目筛选（仅专业题目时显示） -->
        <div class="sidebar-section" v-if="currentTab === 'professional'">
          <h3>科目筛选</h3>
          <select v-model="selectedSubject" class="subject-select">
            <option value="">全部科目</option>
            <option v-for="subject in subjects" :key="subject.value" :value="subject.value">
              {{ subject.label }}
            </option>
          </select>
        </div>

        <!-- 添加题目按钮（仅题目列表时显示） -->
        <div class="sidebar-section" v-if="currentTab !== 'subjects'">
          <button @click="openAddModal" class="add-btn">+ 添加题目</button>
        </div>

        <!-- 统计信息（仅题目列表时显示） -->
        <div class="sidebar-section stats" v-if="currentTab !== 'subjects'">
          <h3>统计信息</h3>
          <div class="stat-item">
            <span class="stat-label">题目总数</span>
            <span class="stat-value">{{ totalQuestions }}</span>
          </div>
        </div>
      </aside>

      <!-- 题目列表 -->
      <section class="content" v-if="currentTab !== 'subjects'">
        <div class="toolbar">
          <input
            v-model="searchKeyword"
            type="text"
            placeholder="搜索题目..."
            class="search-input"
          >
        </div>

        <div class="question-list">
          <!-- 批量操作工具栏 -->
          <div class="batch-toolbar" v-if="filteredQuestions.length > 0">
            <label class="select-all">
              <input
                type="checkbox"
                :checked="selectedQuestions.length === filteredQuestions.length && filteredQuestions.length > 0"
                :indeterminate="selectedQuestions.length > 0 && selectedQuestions.length < filteredQuestions.length"
                @change="toggleSelectAll"
              >
              全选
            </label>
            <span class="selected-count" v-if="selectedQuestions.length > 0">
              已选择 {{ selectedQuestions.length }} 项
            </span>
            <div class="batch-actions" v-if="selectedQuestions.length > 0">
              <button @click="batchDelete" class="batch-btn delete">批量删除</button>
              <button @click="openBatchSubjectModal" class="batch-btn" v-if="currentTab === 'professional'">批量修改科目</button>
            </div>
          </div>

          <div
            v-for="(q, index) in filteredQuestions"
            :key="q.id"
            :class="['question-item', { selected: selectedQuestions.includes(q.id) }]"
          >
            <input
              type="checkbox"
              class="question-checkbox"
              :checked="selectedQuestions.includes(q.id)"
              @click.stop
              @change="toggleSelectQuestion(q.id)"
            >
            <div class="question-index">{{ (currentPage - 1) * pageSize + index + 1 }}</div>
            <div class="question-content" @click="selectQuestion(q)">
              <!-- 套题：默认展开显示所有子题 -->
              <div v-if="isQuestionSetFormat(q.content || q.question_data)" class="question-set-list">
                <div v-for="(sub, subIdx) in (q.content || q.question_data)" :key="subIdx" class="question-set-item">
                  <span class="sub-label">{{ subIdx + 1 }}.</span>
                  <span class="sub-content">{{ getSubPreview(sub.content).text }}</span>
                  <span v-if="getSubPreview(sub.content).images.length > 0" class="sub-images">
                    <img v-for="(img, imgIdx) in getSubPreview(sub.content).images" :key="imgIdx" :src="img" class="preview-thumb">
                  </span>
                </div>
              </div>
              <!-- 单题：显示原有内容 -->
              <div v-else class="question-preview">
                {{ getPreviewText(q.content || q.question_data) }}
                <span v-if="getQuestionImages(q.content || q.question_data).length > 0" class="sub-images">
                  <img v-for="(img, imgIdx) in getQuestionImages(q.content || q.question_data)" :key="imgIdx" :src="img" class="preview-thumb">
                </span>
              </div>
              <div class="question-meta">
                <span class="meta-tag" v-if="currentTab === 'professional'">{{ q.subject }}</span>
              </div>
            </div>
            <div class="question-actions">
              <button @click.stop="editQuestion(q)" class="action-btn edit">编辑</button>
              <button @click.stop="deleteQuestion(q)" class="action-btn delete">删除</button>
            </div>
          </div>

          <div v-if="filteredQuestions.length === 0" class="empty-state">
            暂无题目，请添加
          </div>

          <!-- 分页组件 -->
          <div class="pagination" v-if="totalQuestions > pageSize">
            <button
              class="page-btn"
              :disabled="currentPage <= 1"
              @click="changePage(currentPage - 1)"
            >
              上一页
            </button>
            <span class="page-info">{{ currentPage }} / {{ Math.ceil(totalQuestions / pageSize) }}</span>
            <button
              class="page-btn"
              :disabled="currentPage >= Math.ceil(totalQuestions / pageSize)"
              @click="changePage(currentPage + 1)"
            >
              下一页
            </button>
          </div>
        </div>
      </section>

      <!-- 科目管理内容 -->
      <section class="content" v-if="currentTab === 'subjects'">
        <div class="subjects-manager">
          <div class="subjects-toolbar">
            <button @click="openSubjectModal()" class="add-btn">+ 添加科目</button>
          </div>
          <div class="subjects-list">
            <div
              v-for="subject in subjectList"
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
              <div class="subject-actions" v-if="!isVirtualSubject(subject)">
                <button @click="editSubject(subject)" class="action-btn edit">编辑</button>
                <button @click="toggleSubject(subject)" class="action-btn toggle">
                  {{ subject.is_active ? '禁用' : '启用' }}
                </button>
                <button @click="deleteSubject(subject)" class="action-btn delete">删除</button>
              </div>
              <div class="subject-actions" v-else>
                <span class="subject-tip">仅题库中存在，建议先建科目</span>
              </div>
            </div>
            <div v-if="subjectList.length === 0" class="empty-state">
              暂无科目，请添加
            </div>
          </div>
        </div>
      </section>
    </main>

    <!-- 科目编辑弹窗 -->
    <div v-if="showSubjectModal" class="modal-overlay" @click="closeSubjectModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>{{ isEditingSubject ? '编辑科目' : '添加科目' }}</h3>
          <button class="modal-close" @click="closeSubjectModal">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>科目代码</label>
            <input
              v-model="subjectForm.code"
              type="text"
              class="form-input"
              placeholder="例如: c_language"
              :disabled="isEditingSubject"
            >
            <small class="form-hint">科目代码用于系统内部识别，建议使用英文和下划线</small>
          </div>
          <div class="form-group">
            <label>科目名称</label>
            <input
              v-model="subjectForm.name"
              type="text"
              class="form-input"
              placeholder="例如: C语言"
            >
          </div>
          <div class="form-group">
            <label>描述</label>
            <textarea
              v-model="subjectForm.description"
              rows="3"
              class="form-textarea"
              placeholder="请输入科目描述..."
            ></textarea>
          </div>
          <div class="form-group" v-if="isEditingSubject">
            <label>
              <input v-model="subjectForm.is_active" type="checkbox">
              启用此科目
            </label>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="closeSubjectModal" class="cancel-btn">取消</button>
          <button @click="saveSubject" class="save-btn">保存</button>
        </div>
      </div>
    </div>

    <!-- 批量修改科目弹窗 -->
    <div v-if="showBatchSubjectModal" class="modal-overlay" @click="showBatchSubjectModal = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>批量修改科目</h3>
          <button class="modal-close" @click="showBatchSubjectModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <p class="batch-info">已选择 {{ selectedQuestions.length }} 道题目</p>
          <div class="form-group">
            <label>新科目</label>
            <select v-model="batchSubjectForm.subject" class="form-select">
              <option v-for="subject in subjects" :key="subject.value" :value="subject.value">
                {{ subject.label }}
              </option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showBatchSubjectModal = false" class="cancel-btn">取消</button>
          <button @click="batchUpdateSubject" class="save-btn">确认修改</button>
        </div>
      </div>
    </div>

    <!-- 添加/编辑题目弹窗 -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>{{ isEditing ? '编辑题目' : '添加题目' }}</h3>
          <button class="modal-close" @click="closeModal">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group" v-if="currentType === 'professional'">
            <label>科目</label>
            <select v-model="formData.subject" class="form-select">
              <option v-for="subject in subjects" :key="subject.value" :value="subject.value">
                {{ subject.label }}
              </option>
            </select>
          </div>

          <div class="form-group" v-if="currentType === 'professional'">
            <label>难度</label>
            <select v-model="formData.difficulty" class="form-select">
              <option value="easy">简单</option>
              <option value="medium">中等</option>
              <option value="hard">困难</option>
            </select>
          </div>

          <!-- 题目列表（全部按套题处理） -->
          <div class="sub-questions-container">
            <div class="sub-question-item" v-for="(sub, index) in subQuestions" :key="sub.id">
              <div class="sub-question-header">
                <span class="sub-question-number">题目 {{ index + 1 }}</span>
                <button type="button" @click="removeSubQuestion(index)" class="btn-remove-sub" v-if="subQuestions.length > 1">删除</button>
              </div>
              <textarea
                v-model="sub.text"
                rows="4"
                class="form-textarea"
                placeholder="请输入题目内容..."
              ></textarea>
              <!-- 子题图片列表 -->
              <div class="sub-question-images">
                <div v-for="(img, imgIndex) in getSubQuestionImages(sub.contentItems)" :key="imgIndex" class="image-preview">
                  <img :src="img.thumb" alt="题目图片" @click="openImagePreview(img.src)">
                  <button type="button" @click.stop="removeSubQuestionImage(index, img.contentIndex)" class="btn-remove-image">×</button>
                </div>
              </div>
              <button type="button" @click="triggerImageUpload(index)" class="btn-upload">
                添加图片
              </button>
            </div>
            <!-- 明显的添加题目按钮 -->
            <button type="button" @click="addSubQuestion" class="btn-add-sub-large">
              + 添加题目
            </button>
          </div>

          <!-- 隐藏的文件输入 -->
          <input type="file" ref="imageInput" @change="handleImageSelect" accept="image/*" style="display: none">
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="closeModal">取消</button>
          <button class="btn-save" @click="saveQuestion">{{ isEditing ? '保存' : '添加' }}</button>
        </div>
      </div>
    </div>

    <!-- 批量导入弹窗 -->
    <div v-if="showBatchImportModal" class="modal-overlay" @click="closeBatchImportModal">
      <div class="modal modal-large" @click.stop>
        <div class="modal-header">
          <h3>批量导入题目</h3>
          <button class="modal-close" @click="closeBatchImportModal">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>题目类型</label>
            <select v-model="batchImportData.type" class="form-select">
              <option value="translation">翻译题</option>
              <option value="professional">专业题</option>
            </select>
          </div>

          <div class="form-group" v-if="batchImportData.type === 'professional'">
            <label>科目</label>
            <select v-model="batchImportData.subject" class="form-select">
              <option v-for="subject in subjects" :key="subject.value" :value="subject.value">
                {{ subject.label }}
              </option>
            </select>
          </div>

          <div class="form-group" v-if="batchImportData.type === 'professional'">
            <label>难度</label>
            <select v-model="batchImportData.difficulty" class="form-select">
              <option value="easy">简单</option>
              <option value="medium">中等</option>
              <option value="hard">困难</option>
            </select>
          </div>

          <div class="form-group">
            <label>题目内容（用空行分隔不同题目）</label>
            <textarea
              v-model="batchImportData.content"
              rows="12"
              class="form-textarea"
              placeholder="请输入题目内容...

题目1内容
题目1第二行

题目2内容
题目2第二行

题目3内容"
            ></textarea>
          </div>

          <div class="preview-section" v-if="batchImportData.content">
            <h4>预览（共 {{ getParsedQuestions().length }} 道题目）</h4>
            <div class="preview-list">
              <div
                v-for="(questionSet, idx) in getParsedQuestions()"
                :key="idx"
                class="preview-item"
              >
                <span class="preview-index">{{ idx + 1 }}</span>
                <div class="preview-content">
                  <!-- 套题：点击展开/折叠 -->
                  <div v-if="questionSet.length > 1" class="question-set-preview">
                    <div class="question-set-header" @click="togglePreviewSet(idx)">
                      <span class="expand-icon">{{ expandedPreviewSets.includes(idx) ? '▼' : '▶' }}</span>
                      <span class="question-set-label">套题({{ questionSet.length }}题)</span>
                    </div>
                    <div v-if="expandedPreviewSets.includes(idx)" class="question-set-items">
                      <div v-for="(sub, subIdx) in questionSet" :key="subIdx" class="sub-question-preview">
                        <span class="sub-index">{{ subIdx + 1 }}.</span>
                        <span class="sub-text">{{ sub.substring(0, 50) }}{{ sub.length > 50 ? '...' : '' }}</span>
                      </div>
                    </div>
                  </div>
                  <!-- 单题：直接显示 -->
                  <span v-else class="preview-text">
                    {{ questionSet[0].substring(0, 50) }}{{ questionSet[0].length > 50 ? '...' : '' }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="closeBatchImportModal">取消</button>
          <button class="btn-save btn-import" @click="handleBatchImport">导入</button>
        </div>
      </div>
    </div>

    <!-- 批量导出弹窗 -->
    <div v-if="showBatchExportModal" class="modal-overlay" @click="closeBatchExportModal">
      <div class="modal modal-large" @click.stop>
        <div class="modal-header">
          <h3>批量导出题目</h3>
          <button class="modal-close" @click="closeBatchExportModal">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>题目类型</label>
            <select v-model="batchExportData.type" class="form-select" @change="loadExportContent">
              <option value="translation">翻译题</option>
              <option value="professional">专业题</option>
            </select>
          </div>

          <div class="form-group" v-if="batchExportData.type === 'professional'">
            <label>科目筛选（可选）</label>
            <select v-model="batchExportData.subject" class="form-select" @change="loadExportContent">
              <option value="">全部科目</option>
              <option v-for="subject in subjects" :key="subject.value" :value="subject.value">
                {{ subject.label }}
              </option>
            </select>
          </div>

          <div class="export-info" v-if="batchExportData.count > 0">
            <span>共 {{ batchExportData.count }} 道题目</span>
          </div>

          <div class="form-group">
            <label>导出的题目内容</label>
            <textarea
              v-model="batchExportData.content"
              rows="15"
              class="form-textarea"
              readonly
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="closeBatchExportModal">关闭</button>
          <button class="btn-save btn-copy" @click="copyExportContent">复制内容</button>
        </div>
      </div>
    </div>

    <div v-if="showImagePreview" class="image-preview-overlay" @click="closeImagePreview">
      <div class="image-preview-modal" @click.stop>
        <button class="image-preview-close" @click="closeImagePreview">&times;</button>
        <img :src="previewImageSrc" alt="题目原图" class="image-preview-large">
      </div>
    </div>

    <!-- 底部版权 -->
    <footer class="footer">
      <p>{{ footerCopyright || '版权所有 © 2026 北京石油化工学院 | 联系方式：wangwentong@bipt.edu.cn' }}</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
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

// 状态
const currentTab = ref('translation')  // 当前Tab: translation, professional, subjects
const selectedSubject = ref('')
const searchKeyword = ref('')
const questions = ref([])
const subjects = ref([])
const selectedQuestions = ref([])  // 选中的题目ID列表
const showBatchSubjectModal = ref(false)  // 批量修改科目弹窗
const batchSubjectForm = ref({ subject: '' })  // 批量修改科目表单
const showModal = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const isQuestionSet = ref(false)  // 是否为套题模式
const subQuestions = ref([])  // 子题列表
const showImagePreview = ref(false)
const previewImageSrc = ref('')

// 计算属性：兼容现有代码
const currentType = computed(() => currentTab.value === 'subjects' ? 'professional' : currentTab.value)

// 科目管理相关
const subjectList = ref([])
const showSubjectModal = ref(false)
const isEditingSubject = ref(false)
const subjectForm = reactive({
  id: null,
  code: '',
  name: '',
  description: '',
  is_active: true
})

// 切换Tab
const switchTab = (tab) => {
  currentTab.value = tab
  currentPage.value = 1  // 重置页码
  selectedQuestions.value = []  // 清除选中状态
  if (tab === 'translation' || tab === 'professional') {
    selectedSubject.value = ''
    loadQuestions()
  } else if (tab === 'subjects') {
    loadSubjectList()
  }
}

// 加载科目列表
const loadSubjectList = async () => {
  try {
    // 使用分页参数获取完整的科目信息
    const response = await api.get('/api/subjects', {
      params: { page: 1, limit: 100 }
    })
    if (response.success) {
      subjectList.value = response.data?.subjects || []
    }
  } catch (error) {
    console.error('加载科目失败:', error)
    toast.error('加载科目失败')
  }
}

// 打开科目弹窗
const openSubjectModal = (subject = null) => {
  if (subject) {
    isEditingSubject.value = true
    subjectForm.id = subject.id
    subjectForm.code = subject.code
    subjectForm.name = subject.name
    subjectForm.description = subject.description || ''
    subjectForm.is_active = subject.is_active
  } else {
    isEditingSubject.value = false
    subjectForm.id = null
    subjectForm.code = ''
    subjectForm.name = ''
    subjectForm.description = ''
    subjectForm.is_active = true
  }
  showSubjectModal.value = true
}

// 关闭科目弹窗
const closeSubjectModal = () => {
  showSubjectModal.value = false
}

// 编辑科目
const editSubject = (subject) => {
  openSubjectModal(subject)
}

// 保存科目
const saveSubject = async () => {
  if (!subjectForm.code || !subjectForm.name) {
    toast.error('请填写科目代码和名称')
    return
  }

  try {
    let response
    if (isEditingSubject.value) {
      response = await api.put(`/api/editor/subjects/${subjectForm.id}`, {
        name: subjectForm.name,
        description: subjectForm.description,
        is_active: subjectForm.is_active
      })
    } else {
      response = await api.post('/api/editor/subjects', {
        code: subjectForm.code,
        name: subjectForm.name,
        description: subjectForm.description,
        is_active: subjectForm.is_active
      })
    }

    if (response.success) {
      toast.success(isEditingSubject.value ? '更新成功' : '添加成功')
      closeSubjectModal()
      loadSubjectList()
      loadSubjects()  // 刷新科目下拉框
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
      loadSubjectList()
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
      loadSubjectList()
      loadSubjects()
    } else {
      toast.error(response.error || '删除失败')
    }
  } catch (error) {
    toast.error('删除失败: ' + error.message)
  }
}

// 批量导入弹窗状态
const showBatchImportModal = ref(false)
const batchImportData = ref({
  type: 'translation',
  subject: 'computer_science',
  difficulty: 'medium',
  content: ''
})

// 预览展开/折叠状态
const expandedPreviewSets = ref([])

const togglePreviewSet = (idx) => {
  const index = expandedPreviewSets.value.indexOf(idx)
  if (index > -1) {
    expandedPreviewSets.value.splice(index, 1)
  } else {
    expandedPreviewSets.value.push(idx)
  }
}

// 批量导出弹窗状态
const showBatchExportModal = ref(false)
const batchExportData = ref({
  type: 'translation',
  subject: '',
  content: '',
  count: 0
})

const formData = ref({
  question_index: '',
  subject: '',
  difficulty: 'medium',
  content: ''
})

// 计算属性
const filteredQuestions = computed(() => {
  let result = questions.value

  if (selectedSubject.value) {
    result = result.filter(q => q.subject === selectedSubject.value)
  }

  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(q => {
      const content = getPreview(q).toLowerCase()
      return content.includes(keyword)
    })
  }

  return result
})

// 获取题目预览（兼容两种格式）
const getPreview = (question) => {
  if (!question) return ''
  try {
    // API返回的是 content 字段，不是 question_data
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
        return data[0][1].substring(0, 100) + (data[0][1].length > 100 ? '...' : '')
      }
    }
    return ''
  } catch {
    return String(question.content || question.question_data || '').substring(0, 100)
  }
}

// 获取子题内容预览（包含图片）
const getSubPreview = (subContent) => {
  if (!subContent || !Array.isArray(subContent)) return ''
  let result = { text: '', images: [] }
  // 提取文本内容
  const texts = subContent
    .filter(item => Array.isArray(item) && item[0] === 'txt' && item[1])
    .map(item => item[1])
  result.text = texts.join(' ').substring(0, 80) + (texts.join(' ').length > 80 ? '...' : '')
  // 提取图片内容
  result.images = subContent
    .filter(item => Array.isArray(item) && item[0] === 'img' && item[1] && typeof item[1] === 'object' && item[1].thumb)
    .map(item => item[1].thumb)
  return result
}

// 获取题目内容预览（最多50字符）
const getContentPreview = (content) => {
  if (!content) return ''
  try {
    const data = typeof content === 'string' ? JSON.parse(content) : content
    if (!Array.isArray(data)) return String(content).substring(0, 50)
    let text = ''
    for (const item of data) {
      if (item[0] === 'txt' && item[1]) {
        text += item[1]
      }
    }
    return text.length > 50 ? text.substring(0, 50) + '...' : text
  } catch {
    return String(content).substring(0, 50)
  }
}

// 获取题目中的图片列表
const getQuestionImages = (content) => {
  if (!content) return []
  try {
    const data = typeof content === 'string' ? JSON.parse(content) : content
    if (!Array.isArray(data)) return []
    return data
      .filter(item => Array.isArray(item) && item[0] === 'img' && item[1] && typeof item[1] === 'object' && item[1].thumb)
      .map(item => item[1].thumb)
  } catch {
    return []
  }
}

// 总题目数
const totalQuestions = ref(0)
// 当前页码
const currentPage = ref(1)
// 每页显示数量
const pageSize = 10

// 加载题目
const loadQuestions = async () => {
  try {
    const params = { page: currentPage.value, limit: pageSize }
    // 科目筛选 - 仅对专业题有效
    if (currentType.value === 'professional' && selectedSubject.value) {
      params.subject = selectedSubject.value
    }
    const response = await api.get(`/api/questions/${currentType.value}`, {
      params
    })
    if (response.success) {
      questions.value = response.data?.questions || response.data || []
      totalQuestions.value = response.data?.pagination?.total || questions.value.length
    }
  } catch (error) {
    toast.error('加载题目失败: ' + error.message)
  }
}

// 切换页码
const changePage = (page) => {
  currentPage.value = page
  loadQuestions()
}

// 监听科目筛选变化
watch(selectedSubject, () => {
  if (currentTab.value === 'professional') {
    currentPage.value = 1  // 重置页码
    loadQuestions()
  }
})

// 全选/取消全选
const toggleSelectAll = () => {
  if (selectedQuestions.value.length === filteredQuestions.value.length) {
    selectedQuestions.value = []
  } else {
    selectedQuestions.value = filteredQuestions.value.map(q => q.id)
  }
}

// 选择/取消单个题目
const toggleSelectQuestion = (id) => {
  const index = selectedQuestions.value.indexOf(id)
  if (index > -1) {
    selectedQuestions.value.splice(index, 1)
  } else {
    selectedQuestions.value.push(id)
  }
}

// 批量删除
const batchDelete = async () => {
  if (selectedQuestions.value.length === 0) return
  if (!confirm(`确定要删除选中的 ${selectedQuestions.value.length} 道题目吗？`)) {
    return
  }
  try {
    const response = await api.post('/api/questions/batch-delete', {
      question_ids: selectedQuestions.value,
      question_type: currentType.value
    })
    if (response.success) {
      toast.success(`成功删除 ${selectedQuestions.value.length} 道题目`)
      selectedQuestions.value = []
      loadQuestions()
    } else {
      toast.error(response.error || '批量删除失败')
    }
  } catch (error) {
    toast.error('批量删除失败: ' + error.message)
  }
}

// 打开批量修改科目弹窗
const openBatchSubjectModal = () => {
  batchSubjectForm.value.subject = subjects.value[0]?.value || ''
  showBatchSubjectModal.value = true
}

// 批量修改科目
const batchUpdateSubject = async () => {
  if (!batchSubjectForm.value.subject) {
    toast.error('请选择科目')
    return
  }
  try {
    const response = await api.post('/api/questions/batch-update-subject', {
      question_ids: selectedQuestions.value,
      subject: batchSubjectForm.value.subject
    })
    if (response.success) {
      toast.success(`成功修改 ${selectedQuestions.value.length} 道题目的科目`)
      selectedQuestions.value = []
      showBatchSubjectModal.value = false
      loadQuestions()
    } else {
      toast.error(response.error || '批量修改失败')
    }
  } catch (error) {
    toast.error('批量修改失败: ' + error.message)
  }
}

// 加载科目
const loadSubjects = async () => {
  try {
    const response = await api.get('/api/subjects')
    if (response.success) {
      subjects.value = response.data || []
    }
  } catch (error) {
    toast.error('加载科目失败: ' + error.message)
  }
}

// 选择题目
const selectQuestion = (q) => {
  editQuestion(q)
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
    if (!Array.isArray(data)) return String(content).substring(0, 100)
    // 提取所有文本
    const texts = data
      .filter(item => Array.isArray(item) && item[0] === 'txt' && item[1])
      .map(item => item[1])
    const text = texts.join(' ')
    return text.substring(0, 100) + (text.length > 100 ? '...' : '')
  } catch {}
  return String(content).substring(0, 100)
}

// 提取题目内容中的纯文本（用于编辑显示）
const extractTextContent = (contentArray) => {
  if (!contentArray || !Array.isArray(contentArray)) return ''
  const texts = contentArray
    .filter(item => Array.isArray(item) && item[0] === 'txt' && item[1])
    .map(item => item[1])
  return texts.join('\n')
}

const extractImageContent = (contentArray) => {
  if (!contentArray || !Array.isArray(contentArray)) return []
  return contentArray.filter(item => {
    return Array.isArray(item) &&
      item[0] === 'img' &&
      typeof item[1] === 'object' &&
      item[1] &&
      typeof item[1].src === 'string' &&
      typeof item[1].thumb === 'string'
  })
}

// 编辑题目
const editQuestion = (q) => {
  isEditing.value = true
  editingId.value = q.id

  // 判断是否为套题格式
  const content = q.content || q.question_data
  const isSet = isQuestionSetFormat(content)

  if (isSet) {
    isQuestionSet.value = true
    subQuestions.value = content.map((sub, index) => ({
      id: index,
      text: extractTextContent(sub.content),
      contentItems: extractImageContent(sub.content)
    }))
  } else {
    isQuestionSet.value = true
    const normalizedContent = Array.isArray(content) ? content : []
    const plainText = extractTextContent(normalizedContent) || getPreviewText(content)
    subQuestions.value = [{
      id: 1,
      text: plainText,
      contentItems: extractImageContent(normalizedContent)
    }]
  }

  formData.value = {
    question_index: q.question_index,
    subject: q.subject || subjects.value[0]?.value || '',
    difficulty: q.difficulty || 'medium',
    content: ''
  }
  showModal.value = true
}

// 删除题目
const deleteQuestion = async (q) => {
  if (!confirm(`确定要删除题目 #${q.question_index} 吗？`)) {
    return
  }

  try {
    const response = await api.delete(`/api/questions/question/${q.id}`)
    if (response.success) {
      toast.success('删除成功')
      loadQuestions()
    } else {
      toast.error(response.error || '删除失败')
    }
  } catch (error) {
    toast.error('删除失败: ' + error.message)
  }
}

// 打开添加弹窗
const openAddModal = () => {
  if (currentType.value === 'professional' && subjects.value.length === 0) {
    toast.warning('请先添加科目，再添加专业题目')
    return
  }

  isEditing.value = false
  editingId.value = null
  isQuestionSet.value = true  // 套题模式
  subQuestions.value = [{ id: 1, text: '', contentItems: [] }]  // 默认一个空题目
  formData.value = {
    question_index: '',
    subject: currentType.value === 'professional' ? (subjects.value[0]?.value || '') : '',
    difficulty: 'medium',
    content: ''
  }
  showModal.value = true
}

// 关闭弹窗
const closeModal = () => {
  showModal.value = false
}

// 添加子题
const addSubQuestion = () => {
  subQuestions.value.push({
    id: Date.now(),
    text: '',
    contentItems: []
  })
}

// 将单题转换为套题模式
const convertToQuestionSet = () => {
  const currentContent = formData.value.content

  isQuestionSet.value = true
  subQuestions.value = [
    { id: 1, text: currentContent, contentItems: [] },
    { id: 2, text: '', contentItems: [] }
  ]
  formData.value.content = ''
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
const getSubQuestionImages = (contentItems) => {
  if (!contentItems || !Array.isArray(contentItems)) return []
  return contentItems
    .map((item, index) => {
      if (!Array.isArray(item) || item[0] !== 'img' || typeof item[1] !== 'object' || !item[1]) {
        return null
      }
      if (!item[1].src || !item[1].thumb) {
        return null
      }
      return {
        src: item[1].src,
        thumb: item[1].thumb,
        contentIndex: index
      }
    })
    .filter(Boolean)
}

// 删除子题中的图片
const removeSubQuestionImage = (subIndex, imgIndex) => {
  const contentItems = subQuestions.value[subIndex].contentItems
  if (Array.isArray(contentItems)) {
    contentItems.splice(imgIndex, 1)
  }
}

const openImagePreview = (src) => {
  previewImageSrc.value = src
  showImagePreview.value = true
}

const closeImagePreview = () => {
  showImagePreview.value = false
  previewImageSrc.value = ''
}

const handleKeydown = (event) => {
  if (event.key === 'Escape' && showImagePreview.value) {
    closeImagePreview()
  }
}

const isVirtualSubject = (subject) => {
  return typeof subject?.id === 'string' && subject.id.startsWith('virtual:')
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
    const formDataObj = new FormData()
    formDataObj.append('file', file)

    const response = await fetch('/api/upload/image', {
      method: 'POST',
      body: formDataObj
    })
    const result = await response.json()

    if (result.success) {
      const imagePath = result.data.path
      const thumbnailPath = result.data.thumbnail

      if (typeof currentImageUploadTarget.value === 'number') {
        const subIndex = currentImageUploadTarget.value
        if (!Array.isArray(subQuestions.value[subIndex].contentItems)) {
          subQuestions.value[subIndex].contentItems = []
        }
        subQuestions.value[subIndex].contentItems.push(['img', { src: imagePath, thumb: thumbnailPath }])
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

// 保存题目
const saveQuestion = async () => {
  if (currentType.value === 'professional' && !formData.value.subject) {
    toast.warning('当前没有可用科目，请先到科目管理添加科目')
    return
  }

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
      if (sub.text && sub.text.trim()) {
        subContent.push(['txt', sub.text])
      }
      if (Array.isArray(sub.contentItems) && sub.contentItems.length > 0) {
        subContent = subContent.concat(sub.contentItems)
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
        type: currentType.value,
        content: content,
        subject: formData.value.subject,
        difficulty: formData.value.difficulty
      })
    } else {
      // 添加 - 不传递index，由后端自动生成序号
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

// 监听Tab变化
import { watch } from 'vue'
watch(currentTab, (newTab) => {
  if (newTab === 'translation' || newTab === 'professional') {
    selectedSubject.value = ''
    loadQuestions()
  }
})

watch(() => batchImportData.value.type, (newType) => {
  if (newType === 'professional') {
    if (subjects.value.length === 0) {
      batchImportData.value.subject = ''
      toast.warning('当前没有可用科目，请先到科目管理添加科目')
      return
    }
    batchImportData.value.subject = subjects.value[0].value
  } else {
    batchImportData.value.subject = ''
  }
})

// 解析导入内容为题目列表
// 解析批量导入内容（用于预览）
// 格式：每一行是一个子题目，空行分隔不同题目组（套题）
// - 每一行 = 一个子题目
// - 空行 = 分隔不同题目组
const getParsedQuestions = () => {
  const content = batchImportData.value.content
  if (!content) return []

  const lines = content.split('\n')
  const questionSets = []
  let currentSubQuestions = []

  for (const line of lines) {
    if (line.trim() === '') {
      // 空行：表示题目组之间分隔
      if (currentSubQuestions.length > 0) {
        questionSets.push([...currentSubQuestions])
        currentSubQuestions = []
      }
    } else {
      // 非空行：添加到当前子题目
      currentSubQuestions.push(line)
    }
  }

  // 处理最后一部分
  if (currentSubQuestions.length > 0) {
    questionSets.push(currentSubQuestions)
  }

  return questionSets
}

// 打开批量导入弹窗
const openBatchImportModal = () => {
  const qType = currentTab.value === 'subjects' ? 'professional' : currentTab.value
  if (qType === 'professional' && subjects.value.length === 0) {
    toast.warning('请先添加科目，再批量导入专业题目')
    return
  }
  batchImportData.value = {
    type: qType,
    subject: qType === 'professional' ? (subjects.value[0]?.value || '') : '',
    difficulty: 'medium',
    content: ''
  }
  expandedPreviewSets.value = []  // 重置展开状态
  showBatchImportModal.value = true
}

// 关闭批量导入弹窗
const closeBatchImportModal = () => {
  showBatchImportModal.value = false
  expandedPreviewSets.value = []  // 重置展开状态
}

// 处理批量导入
const handleBatchImport = async () => {
  if (batchImportData.value.type === 'professional' && !batchImportData.value.subject) {
    toast.warning('当前没有可用科目，请先到科目管理添加科目')
    return
  }

  const content = batchImportData.value.content
  if (!content || !content.trim()) {
    toast.warning('请输入题目内容')
    return
  }

  const questions = getParsedQuestions()
  if (questions.length === 0) {
    toast.warning('未能解析出有效题目')
    return
  }

  try {
    const response = await api.post('/api/questions/batch-import', {
      type: batchImportData.value.type,
      content: content,
      subject: batchImportData.value.subject,
      difficulty: batchImportData.value.difficulty
    })

    if (response.success) {
      const data = response.data
      toast.success(`成功导入 ${data.imported} 道题目，共 ${data.total} 道`)
      closeBatchImportModal()
      loadQuestions()
    } else {
      toast.error(response.error || '导入失败')
    }
  } catch (error) {
    toast.error('导入失败: ' + error.message)
  }
}

// 打开批量导出弹窗
const openBatchExportModal = () => {
  const qType = currentTab.value === 'subjects' ? 'professional' : currentTab.value
  batchExportData.value = {
    type: qType,
    subject: '',
    content: '',
    count: 0
  }
  showBatchExportModal.value = true
  loadExportContent()
}

// 关闭批量导出弹窗
const closeBatchExportModal = () => {
  showBatchExportModal.value = false
}

// 加载导出内容
const loadExportContent = async () => {
  try {
    const params = {
      type: batchExportData.value.type
    }
    if (batchExportData.value.type === 'professional' && batchExportData.value.subject) {
      params.subject = batchExportData.value.subject
    }

    const response = await api.get('/api/questions/batch-export', { params })

    if (response.success) {
      batchExportData.value.content = response.data.content || ''
      batchExportData.value.count = response.data.count || 0
    } else {
      toast.error(response.error || '获取导出内容失败')
    }
  } catch (error) {
    toast.error('获取导出内容失败: ' + error.message)
  }
}

// 复制导出内容
const copyExportContent = async () => {
  try {
    await navigator.clipboard.writeText(batchExportData.value.content)
    toast.success('已复制到剪贴板')
  } catch (error) {
    toast.error('复制失败，请手动复制')
  }
}

// 初始化
onMounted(() => {
  loadQuestions()
  loadSubjects()
  loadFooterCopyright()
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.editor-page {
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
}

.nav-btn:hover {
  background: rgba(255,255,255,0.3);
}

.batch-btn {
  background: rgba(255,255,255,0.2);
  border: none;
  cursor: pointer;
}

.batch-btn:hover {
  background: rgba(255,255,255,0.3);
}

.main-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.sidebar {
  width: 250px;
  background: white;
  border-right: 1px solid #dee2e6;
  padding: 20px;
  overflow-y: auto;
}

.sidebar-section {
  margin-bottom: 20px;
}

.sidebar-section h3 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #666;
}

.type-buttons {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tab-buttons {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tab-btn {
  padding: 10px 15px;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  text-align: left;
  transition: all 0.2s;
}

.tab-btn:hover {
  background: #e9ecef;
  border-color: #adb5bd;
}

.tab-btn.active {
  background: #007bff;
  color: white;
  border-color: #007bff;
}

.type-btn {
  padding: 10px;
  border: 1px solid #dee2e6;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s;
}

.type-btn.active {
  background: #007bff;
  color: white;
  border-color: #007bff;
}

.subject-select {
  width: 100%;
  padding: 8px;
  border: 1px solid #dee2e6;
  border-radius: 4px;
}

.add-btn {
  width: 100%;
  padding: 12px;
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

.subjects-link {
  display: block;
  margin-top: 10px;
  padding: 8px;
  background: #6c757d;
  color: white;
  text-align: center;
  text-decoration: none;
  border-radius: 4px;
  font-size: 14px;
}

.subjects-link:hover {
  background: #5a6268;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #eee;
}

.stat-label {
  color: #666;
}

.stat-value {
  font-weight: bold;
  color: #007bff;
}

.content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.toolbar {
  margin-bottom: 20px;
}

.search-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  font-size: 14px;
}

.question-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.question-item {
  display: flex;
  align-items: center;
  padding: 15px;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.question-item:hover {
  border-color: #007bff;
  box-shadow: 0 2px 8px rgba(0,123,255,0.1);
}

.question-index {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #007bff;
  color: white;
  border-radius: 50%;
  font-weight: bold;
  margin-right: 15px;
  flex-shrink: 0;
}

.question-content {
  flex: 1;
}

.question-preview {
  color: #333;
  margin-bottom: 5px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px;
}

/* 套题列表样式 */
.question-set-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.question-set-item {
  display: flex;
  align-items: flex-start;
  padding: 6px 10px;
  background: #f8f9fa;
  border-radius: 4px;
  border-left: 3px solid #007bff;
}

.sub-label {
  color: #007bff;
  font-weight: bold;
  margin-right: 8px;
  flex-shrink: 0;
}

.sub-content {
  color: #333;
  font-size: 13px;
  line-height: 1.4;
}

.sub-images {
  display: inline-flex;
  gap: 4px;
  margin-left: 8px;
  vertical-align: middle;
}

.preview-thumb {
  width: 40px;
  height: 30px;
  object-fit: cover;
  border-radius: 3px;
  border: 1px solid #ddd;
}

.question-meta {
  display: flex;
  gap: 8px;
}

.meta-tag {
  padding: 2px 8px;
  background: #e9ecef;
  border-radius: 12px;
  font-size: 12px;
  color: #666;
}

.meta-tag.difficulty {
  background: #fff3cd;
  color: #856404;
}

.question-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 5px 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.action-btn.edit {
  background: #ffc107;
  color: #333;
}

.action-btn.delete {
  background: #dc3545;
  color: white;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #999;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
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
  max-height: 80vh;
  overflow-y: auto;
}

.modal-large {
  max-width: 700px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #dee2e6;
}

.modal-header h3 {
  margin: 0;
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
  margin-bottom: 5px;
  font-weight: bold;
  color: #333;
}

.form-input, .form-select, .form-textarea {
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

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 15px 20px;
  border-top: 1px solid #dee2e6;
}

.btn-cancel {
  padding: 10px 20px;
  border: 1px solid #dee2e6;
  background: white;
  border-radius: 4px;
  cursor: pointer;
}

.btn-save {
  padding: 10px 20px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-save:hover {
  background: #0056b3;
}

.btn-import {
  background: #28a745;
}

.btn-import:hover {
  background: #218838;
}

.btn-copy {
  background: #17a2b8;
}

.btn-copy:hover {
  background: #138496;
}

.preview-section {
  margin-top: 15px;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 4px;
  max-height: 200px;
  overflow-y: auto;
}

.preview-section h4 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #666;
}

.preview-list {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.preview-item {
  display: flex;
  align-items: flex-start;
  padding: 5px;
  background: white;
  border-radius: 3px;
}

.preview-index {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: #007bff;
  color: white;
  border-radius: 50%;
  font-size: 12px;
  margin-right: 8px;
  flex-shrink: 0;
}

.preview-text {
  font-size: 13px;
  color: #666;
  word-break: break-all;
}

.preview-content {
  flex: 1;
}

.question-set-preview {
  width: 100%;
}

.question-set-header {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #007bff;
  font-size: 13px;
}

.question-set-header:hover {
  color: #0056b3;
}

.expand-icon {
  margin-right: 5px;
  font-size: 10px;
}

.question-set-label {
  font-weight: 500;
}

.question-set-items {
  margin-top: 8px;
  padding-left: 20px;
  border-left: 2px solid #e9ecef;
}

.sub-question-preview {
  display: flex;
  align-items: flex-start;
  padding: 4px 0;
  font-size: 12px;
  color: #666;
}

.sub-index {
  margin-right: 6px;
  color: #999;
}

.sub-text {
  word-break: break-all;
}

.export-info {
  padding: 8px 12px;
  background: #d1ecf1;
  border-radius: 4px;
  margin-bottom: 15px;
  color: #0c5460;
  font-size: 14px;
}

/* 科目管理样式 */
.subjects-manager {
  padding: 0;
}

.subjects-toolbar {
  margin-bottom: 20px;
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

.subject-tip {
  color: #6c757d;
  font-size: 13px;
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

/* 分页样式 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  margin-top: 20px;
  padding: 15px 0;
}

.page-btn {
  padding: 8px 16px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.page-btn:hover:not(:disabled) {
  background: #0056b3;
}

.page-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #666;
}

/* 批量操作样式 */
.batch-toolbar {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 10px 15px;
  background: #f8f9fa;
  border-radius: 4px;
  margin-bottom: 10px;
}

.select-all {
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
  font-size: 14px;
  color: #333;
}

.select-all input {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.selected-count {
  font-size: 14px;
  color: #666;
}

.batch-actions {
  display: flex;
  gap: 10px;
  margin-left: auto;
}

.batch-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  background: #007bff;
  color: white;
}

.batch-btn:hover {
  background: #0056b3;
}

.batch-btn.delete {
  background: #dc3545;
}

.batch-btn.delete:hover {
  background: #c82333;
}

.question-item {
  display: flex;
  align-items: center;
  padding: 15px;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.question-item:hover {
  border-color: #007bff;
  box-shadow: 0 2px 8px rgba(0,123,255,0.1);
}

.question-item.selected {
  border-color: #007bff;
  background: #f0f7ff;
}

.question-checkbox {
  width: 18px;
  height: 18px;
  margin-right: 15px;
  cursor: pointer;
  flex-shrink: 0;
}

.question-index {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #007bff;
  color: white;
  border-radius: 50%;
  font-weight: bold;
  margin-right: 15px;
  flex-shrink: 0;
}

.question-content {
  flex: 1;
  cursor: pointer;
}

.batch-info {
  padding: 10px 15px;
  background: #e7f3ff;
  border-radius: 4px;
  margin-bottom: 15px;
  color: #007bff;
  font-size: 14px;
}

/* 套题相关样式 */
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

.btn-remove-sub {
  padding: 4px 10px;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
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
  cursor: zoom-in;
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

.image-preview-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 30px;
}

.image-preview-modal {
  position: relative;
  max-width: 100%;
  max-height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-preview-large {
  max-width: 100%;
  max-height: calc(100vh - 60px);
  object-fit: contain;
  border-radius: 8px;
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.45);
}

.image-preview-close {
  position: absolute;
  top: -40px;
  right: 0;
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.25);
  color: #fff;
  font-size: 28px;
  line-height: 1;
  cursor: pointer;
}

.btn-upload {
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
  padding: 12px;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

/* 明显的添加题目按钮 */
.btn-add-sub-large {
  width: 100%;
  padding: 16px 24px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
  margin-top: 15px;
  box-shadow: 0 2px 8px rgba(0, 123, 255, 0.3);
}

.btn-add-sub-large:hover {
  background: #0056b3;
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.4);
}

.btn-add-sub:hover {
  background: #218838;
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

.question-set-badge {
  display: inline-block;
  padding: 2px 8px;
  background: #ffc107;
  color: #333;
  border-radius: 10px;
  font-size: 12px;
  margin-left: 8px;
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
