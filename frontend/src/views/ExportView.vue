<template>
  <div class="export-page">
    <header class="export-header">
      <div class="header-left">
        <svg class="header-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
          <polyline points="7 10 12 15 17 10"/>
          <line x1="12" y1="15" x2="12" y2="3"/>
        </svg>
        <h1>数据导出</h1>
      </div>
      <div class="header-right">
        <router-link to="/" class="header-btn header-btn-secondary">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="15 18 9 12 15 6"/>
          </svg>
          返回考试
        </router-link>
        <router-link to="/help" class="header-btn header-btn-ghost">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
            <line x1="12" y1="17" x2="12.01" y2="17"/>
          </svg>
          帮助
        </router-link>
      </div>
    </header>

    <main class="main-content">
      <div class="export-container">
        <!-- 左侧：数据概览 + 导出选项 -->
        <div class="left-panel">
          <div class="stats-section">
            <h3>数据概览</h3>
            <div class="stats-grid">
              <div class="stat-card">
                <div class="stat-value">{{ stats.totalStudents }}</div>
                <div class="stat-label">考生总数</div>
              </div>
              <div class="stat-card">
                <div class="stat-value">{{ stats.completedExams }}</div>
                <div class="stat-label">已完成</div>
              </div>
              <div class="stat-card">
                <div class="stat-value">{{ stats.inProgressExams }}</div>
                <div class="stat-label">进行中</div>
              </div>
              <div class="stat-card">
                <div class="stat-value">{{ stats.translationQuestions }}</div>
                <div class="stat-label">翻译题目</div>
              </div>
              <div class="stat-card">
                <div class="stat-value">{{ stats.professionalQuestions }}</div>
                <div class="stat-label">专业题目</div>
              </div>
            </div>
          </div>

          <div class="export-section">
            <h3>导出选项</h3>
            <div class="export-options">
              <div class="export-card export-card-accent">
                <div class="export-card-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                    <line x1="8" y1="13" x2="16" y2="13"/>
                    <line x1="8" y1="17" x2="16" y2="17"/>
                  </svg>
                </div>
                <div class="export-card-body">
                  <h4>考生列表 Excel</h4>
                  <p>导出所有考生的基本信息与考试状态</p>
                </div>
                <button @click="exportStudents" class="export-btn export-btn-primary">导出Excel</button>
              </div>

              <div class="export-card">
                <div class="export-card-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                    <path d="M9 15v-2h2a1 1 0 0 1 0 2H9z"/>
                  </svg>
                </div>
                <div class="export-card-body">
                  <h4>PDF报告</h4>
                  <p>生成可归档的PDF考试报告（含题目图片）</p>
                </div>
                <button @click="exportPDF" class="export-btn export-btn-secondary">导出PDF</button>
              </div>

              <div class="export-card">
                <div class="export-card-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="16 18 22 12 16 6"/>
                    <polyline points="8 6 2 12 8 18"/>
                  </svg>
                </div>
                <div class="export-card-body">
                  <h4>HTML报告</h4>
                  <p>生成可打印的HTML考试报告（含题目图片）</p>
                </div>
                <button @click="exportHTML" class="export-btn export-btn-secondary">导出HTML</button>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧：考试记录预览 -->
        <div class="right-panel preview-section">
          <div class="preview-header">
            <h3>考试记录预览</h3>
            <div class="preview-actions">
              <span class="record-count">{{ students.length }} 条记录</span>
              <button @click="loadStudents" class="refresh-btn" :disabled="isLoading">
                <svg v-if="isLoading" class="spin-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
                </svg>
                <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="23 4 23 10 17 10"/>
                  <polyline points="1 20 1 14 7 14"/>
                  <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
                </svg>
                {{ isLoading ? '加载中...' : '刷新' }}
              </button>
            </div>
          </div>

          <!-- 空状态 -->
          <div v-if="!isLoading && students.length === 0" class="empty-state">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/>
              <rect x="9" y="3" width="6" height="4" rx="1"/>
              <line x1="9" y1="12" x2="15" y2="12"/>
              <line x1="9" y1="16" x2="13" y2="16"/>
            </svg>
            <p>暂无考试记录</p>
            <span>当前没有找到任何考生的考试数据</span>
          </div>

          <div v-else class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th class="col-number">考生号</th>
                  <th class="col-status">状态</th>
                  <th class="col-subject">专业科目</th>
                  <th class="col-time">开始时间</th>
                  <th class="col-time">结束时间</th>
                  <th class="col-duration">时长</th>
                  <th class="col-action">操作</th>
                </tr>
              </thead>
              <tbody>
                <template v-for="(student, index) in students" :key="student.studentNumber">
                  <tr :class="['data-row', { 'row-even': index % 2 === 1, 'row-expanded': isExpanded(student.studentNumber) }]">
                    <td class="cell-number">{{ student.studentNumber }}</td>
                    <td>
                      <span :class="['status-badge', getStatusClass(student)]">
                        <span class="status-dot"></span>
                        {{ getStatusText(student.examStatus) }}
                      </span>
                    </td>
                    <td class="cell-subject">{{ student.professionalSubject || '-' }}</td>
                    <td class="cell-time">{{ student.startTime || '-' }}</td>
                    <td class="cell-time">{{ student.endTime || '-' }}</td>
                    <td class="cell-duration">{{ student.durationMinutes ? student.durationMinutes + '分钟' : '-' }}</td>
                    <td>
                      <button @click="toggleExpand(student.studentNumber)" :class="['expand-btn', { 'is-expanded': isExpanded(student.studentNumber) }]">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <polyline points="6 9 12 15 18 9"/>
                        </svg>
                        {{ isExpanded(student.studentNumber) ? '收起' : '详情' }}
                      </button>
                    </td>
                  </tr>
                  <tr v-if="isExpanded(student.studentNumber)" class="expand-row">
                    <td colspan="7">
                      <div class="question-details">
                        <div v-if="student.translationInfo" class="question-section">
                          <div class="question-header">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                              <path d="M5 5h14M5 10h14M5 15h10"/>
                            </svg>
                            <span class="question-title">翻译题目</span>
                            <span class="question-number">题号: {{ student.translationInfo.questionNumber }}</span>
                          </div>
                          <div class="question-content" v-html="renderQuestion(student.translationInfo.questionContent)"></div>
                        </div>
                        <div v-if="student.professionalInfo" class="question-section">
                          <div class="question-header">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                              <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
                              <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
                            </svg>
                            <span class="question-title">专业题目</span>
                            <span class="question-number">题号: {{ student.professionalInfo.questionNumber }}</span>
                            <span class="question-tag">{{ student.professionalInfo.subject }}</span>
                          </div>
                          <div class="question-content" v-html="renderQuestion(student.professionalInfo.questionContent)"></div>
                        </div>
                        <div v-if="!student.translationInfo && !student.professionalInfo" class="no-questions">
                          暂无题目信息
                        </div>
                      </div>
                    </td>
                  </tr>
                </template>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </main>

    <!-- 图片预览弹窗 -->
    <div v-if="showImagePreview" class="image-preview-overlay" @click="closeImagePreview">
      <div class="image-preview-content" @click.stop>
        <img :src="previewImageUrl" alt="预览图片" />
        <button class="close-btn" @click="closeImagePreview">&times;</button>
      </div>
    </div>

    <!-- 底部版权 -->
    <footer class="footer">
      <p>{{ footerCopyright || '版权所有 © 2026 北京石油化工学院 | 联系方式：wangwentong@bipt.edu.cn' }}</p>
    </footer>
  </div>
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

const stats = reactive({
  totalStudents: 0,
  completedExams: 0,
  inProgressExams: 0,
  translationQuestions: 0,
  professionalQuestions: 0
})

const students = ref([])
const isLoading = ref(false)

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

// 图片预览状态
const showImagePreview = ref(false)
const previewImageUrl = ref('')

const openImagePreview = (url) => {
  previewImageUrl.value = url
  showImagePreview.value = true
}

const closeImagePreview = () => {
  showImagePreview.value = false
  previewImageUrl.value = ''
}

// 转义HTML
const escapeHtml = (text) => {
  if (!text) return ''
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

// 规范化图片数据
const normalizeImageData = (item) => {
  if (!item || !Array.isArray(item) || item.length < 2) return null
  const type = item[0]
  const data = item[1]
  if (type !== 'img') return null
  if (!data) return null

  let src = ''
  let thumb = ''

  if (typeof data === 'string') {
    if (data.startsWith('data:image/')) {
      src = data
      thumb = data
    } else if (data.startsWith('/') || data.startsWith('http')) {
      src = data
      thumb = data
    }
  } else if (typeof data === 'object') {
    src = data.src || data.url || data.path || ''
    thumb = data.thumb || src
  }

  if (!src) return null
  return { src, thumb }
}

// 判断是否是套题格式
const isQuestionSet = (data) => {
  if (!data || !Array.isArray(data)) return false
  return data.length > 0 && typeof data[0] === 'object' && 'content' in data[0]
}

// 渲染单个题目内容（支持图片）
const renderContentItems = (contentArray) => {
  if (!contentArray || !Array.isArray(contentArray)) return ''
  return contentArray.map(item => {
    if (Array.isArray(item) && item[0] === 'txt') {
      const text = (item[1] || '').trim()
      if (!text) return ''
      return `<p>${escapeHtml(text)}</p>`
    }
    const imageData = normalizeImageData(item)
    if (imageData) {
      return `<div class="image-container" onclick="window.openImagePreview('${imageData.src}')" title="点击查看原图"><img src="${imageData.thumb}" alt="题目图片缩略图"></div>`
    }
    return ''
  }).filter(Boolean).join('')
}

// 渲染题目内容（与考试界面一致）
const renderQuestion = (questionData) => {
  if (!questionData) return ''

  try {
    let data = questionData

    // 如果是字符串，尝试解析为 JSON
    if (typeof data === 'string') {
      try {
        data = JSON.parse(data)
      } catch {
        return escapeHtml(data)
      }
    }

    // 如果是数组，先判断是否是套题格式
    if (Array.isArray(data)) {
      // 检查是否是套题格式
      if (isQuestionSet(data)) {
        return data.map((sub, index) => `<div class="sub-question"><div class="sub-question-title">第${index + 1}题</div><div class="sub-question-content">${renderContentItems(sub.content)}</div></div>`).join('')
      }

      // 普通数组
      return data.map(item => {
        if (Array.isArray(item) && item[0] === 'txt') {
          const text = (item[1] || '').trim()
          if (!text) return ''
          return `<p>${escapeHtml(text)}</p>`
        }
        const imageData = normalizeImageData(item)
        if (imageData) {
          return `<div class="image-container" onclick="window.openImagePreview('${imageData.src}')" title="点击查看原图"><img src="${imageData.thumb}" alt="题目图片缩略图"></div>`
        }
        return ''
      }).filter(Boolean).join('')
    }

    // 如果是对象，尝试获取 content 字段
    if (typeof data === 'object' && data !== null && data.content) {
      return renderQuestion(data.content)
    }
  } catch (e) {
    console.error('渲染题目失败:', e)
    return escapeHtml(String(questionData))
  }

  return escapeHtml(String(questionData))
}

// 将openImagePreview暴露到window供v-html调用
if (typeof window !== 'undefined') {
  window.openImagePreview = openImagePreview
}

const loadStats = async () => {
  try {
    console.log('[DEBUG] Loading stats...')
    const response = await api.get('/exam-api/stats/overview')
    console.log('[DEBUG] Stats response:', response)
    if (response.success && response.data) {
      stats.totalStudents = response.data.students?.total || 0
      stats.completedExams = response.data.exams?.completed || 0
      stats.inProgressExams = response.data.exams?.inProgress || 0
      stats.translationQuestions = response.data.questions?.translation?.total || 0
      stats.professionalQuestions = response.data.questions?.professional?.total || 0
      console.log('[DEBUG] Loaded stats:', stats)
    }
  } catch (error) {
    console.error('加载统计失败:', error)
  }
}

const loadQuestionStats = async () => {
  try {
    // 题目统计已在 loadStats 中一起加载，这里保留函数结构但不做重复请求
    // 数据已经在 /exam-api/stats/overview 中一起返回了
  } catch (error) {
    console.error('加载题目统计失败:', error)
  }
}

const loadStudents = async () => {
  isLoading.value = true
  try {
    const response = await api.get('/export-api/preview')
    if (response.success) {
      students.value = response.data || []
    }
  } catch (error) {
    console.error('加载考生列表失败:', error)
  } finally {
    isLoading.value = false
  }
}

const getStatusText = (status) => {
  const map = {
    'ready': '准备中',
    'in_progress': '进行中',
    'completed': '已完成',
    'paused': '暂停'
  }
  return map[status] || status
}

const getStatusClass = (student) => {
  if (student.isCompleted) {
    return 'completed'
  }
  return student.examStatus || 'ready'
}

const getTimestamp = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const hour = String(now.getHours()).padStart(2, '0')
  const minute = String(now.getMinutes()).padStart(2, '0')
  const second = String(now.getSeconds()).padStart(2, '0')
  return `${year}${month}${day}_${hour}${minute}${second}`
}

const downloadBlob = (blob, fileName) => {
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = fileName
  link.click()
  window.URL.revokeObjectURL(url)
}

const exportBlobFile = async (endpoint, fileName) => {
  const blob = await api.get(endpoint, { responseType: 'blob' })
  const fileBlob = blob instanceof Blob ? blob : new Blob([blob])
  downloadBlob(fileBlob, fileName)
}

const exportStudents = async () => {
  try {
    await exportBlobFile('/export-api/students/csv', `考生列表_${getTimestamp()}.csv`)
    toast.success('考生列表导出成功')
  } catch (error) {
    toast.error('导出失败: ' + error.message)
  }
}

const exportRecords = async () => {
  try {
    const response = await api.get('/export-api/preview')
    if (response.success) {
      const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' })
      downloadBlob(blob, `考试记录_${getTimestamp()}.json`)
      toast.success('考试记录导出成功')
      return
    }
    toast.error(response.error || '导出失败')
  } catch (error) {
    toast.error('导出失败: ' + error.message)
  }
}

const exportFullData = async () => {
  try {
    const response = await api.get('/export-api/bundle')
    if (response.success) {
      const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' })
      downloadBlob(blob, `完整备份_${getTimestamp()}.json`)
      toast.success('完整备份导出成功')
      return
    }
    toast.error(response.error || '导出失败')
  } catch (error) {
    toast.error('导出失败: ' + error.message)
  }
}

const exportHTML = async () => {
  try {
    await exportBlobFile('/export-api/html', `考试报告_${getTimestamp()}.html`)
    toast.success('HTML报告导出成功')
  } catch (error) {
    toast.error('导出失败: ' + error.message)
  }
}

const exportPDF = async () => {
  try {
    await exportBlobFile('/export-api/pdf', `考试报告_${getTimestamp()}.pdf`)
    toast.success('PDF报告导出成功')
  } catch (error) {
    toast.error('导出失败: ' + error.message)
  }
}

onMounted(() => {
  loadStats()
  loadQuestionStats()
  loadStudents()
  loadFooterCopyright()
})
</script>

<style scoped>
.export-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: var(--color-background);
}

/* Header */
.export-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 var(--spacing-5);
  height: var(--header-height);
  background: var(--color-primary);
  color: var(--color-text-on-primary);
  gap: var(--spacing-4);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
}

.header-icon {
  width: 24px;
  height: 24px;
  opacity: 0.9;
}

.export-header h1 {
  margin: 0;
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.header-btn {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-2) var(--spacing-4);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  text-decoration: none;
  cursor: pointer;
  transition: background var(--transition-fast), opacity var(--transition-fast);
  border: none;
}

.header-btn svg {
  width: 16px;
  height: 16px;
}

.header-btn-secondary {
  background: var(--color-header-btn-bg);
  color: var(--color-text-on-primary);
}

.header-btn-secondary:hover {
  background: var(--color-header-btn-hover);
  opacity: 0.9;
}

.header-btn-ghost {
  background: transparent;
  color: var(--color-text-on-primary);
}

.header-btn-ghost:hover {
  background: var(--color-header-btn-bg);
}

/* Main */
.main-content {
  flex: 1;
  padding: var(--spacing-5);
  overflow-y: auto;
}

.export-container {
  max-width: var(--content-max-width);
  margin: 0 auto;
  display: flex;
  gap: var(--spacing-5);
}

.left-panel {
  width: 320px;
  flex-shrink: 0;
}

.right-panel {
  flex: 1;
  min-width: 0;
}

/* Stats */
.stats-section,
.export-section,
.preview-section {
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  padding: var(--spacing-5);
  margin-bottom: var(--spacing-5);
  box-shadow: var(--shadow-sm);
}

.stats-section h3,
.export-section h3,
.preview-section h3 {
  margin: 0 0 var(--spacing-4) 0;
  color: var(--color-text-primary);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-3);
}

.stat-card {
  background: var(--color-gray-50);
  border-radius: var(--radius-lg);
  padding: var(--spacing-4);
  text-align: center;
}

.stat-value {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-primary);
  margin-bottom: var(--spacing-1);
  font-variant-numeric: tabular-nums;
}

.stat-label {
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
}

/* Export Options */
.export-options {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.export-card {
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
  padding: var(--spacing-4);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.export-card:hover {
  border-color: var(--color-border-light);
  box-shadow: var(--shadow-base);
}

.export-card-accent {
  border-color: var(--color-accent-light);
  background: linear-gradient(135deg, var(--color-surface) 0%, var(--color-accent-light) 100%);
}

.export-card-accent:hover {
  border-color: var(--color-accent);
}

.export-card-icon {
  width: 40px;
  height: 40px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-gray-100);
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
}

.export-card-accent .export-card-icon {
  background: var(--color-accent-light);
  color: var(--color-accent);
}

.export-card-icon svg {
  width: 20px;
  height: 20px;
}

.export-card-body {
  flex: 1;
  min-width: 0;
}

.export-card h4 {
  margin: 0 0 var(--spacing-1) 0;
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
}

.export-card p {
  margin: 0;
  color: var(--color-text-muted);
  font-size: var(--font-size-xs);
}

/* Export Buttons */
.export-btn {
  padding: var(--spacing-2) var(--spacing-4);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  border: none;
  transition: background var(--transition-fast), transform var(--transition-fast);
  flex-shrink: 0;
}

.export-btn:active {
  transform: scale(0.97);
}

.export-btn-primary {
  background: var(--color-accent);
  color: white;
}

.export-btn-primary:hover {
  background: var(--color-accent-hover);
}

.export-btn-secondary {
  background: var(--color-gray-100);
  color: var(--color-text-secondary);
}

.export-btn-secondary:hover {
  background: var(--color-gray-200);
}

/* Preview */
.preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-4);
}

.preview-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
}

.record-count {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  padding: var(--spacing-1) var(--spacing-3);
  background: var(--color-gray-100);
  border-radius: var(--radius-full);
}

.refresh-btn {
  padding: var(--spacing-2) var(--spacing-4);
  background: var(--color-surface);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-2);
  transition: all var(--transition-fast);
}

.refresh-btn svg {
  width: 16px;
  height: 16px;
}

.refresh-btn:hover:not(:disabled) {
  background: var(--color-gray-50);
  border-color: var(--color-border-light);
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spin-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-10);
  color: var(--color-text-muted);
}

.empty-state svg {
  width: 64px;
  height: 64px;
  margin-bottom: var(--spacing-4);
  opacity: 0.4;
}

.empty-state p {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  margin: 0 0 var(--spacing-2) 0;
}

.empty-state span {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
}

/* Table */
.table-container {
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--font-size-sm);
}

.data-table th {
  background: var(--color-gray-50);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  padding: var(--spacing-3) var(--spacing-4);
  text-align: left;
  border-bottom: 1px solid var(--color-border);
  white-space: nowrap;
}

.data-table td {
  padding: var(--spacing-3) var(--spacing-4);
  color: var(--color-text-secondary);
  border-bottom: 1px solid var(--color-border-light);
}

/* Column Widths */
.col-number { width: 100px; }
.col-status { width: 90px; }
.col-subject { min-width: 100px; }
.col-time { width: 150px; }
.col-duration { width: 80px; }
.col-action { width: 70px; }

/* Row Styling */
.data-row {
  transition: background var(--transition-fast);
}

.data-row:hover {
  background: var(--color-gray-50);
}

.row-even {
  background: var(--color-gray-50);
}

.row-even:hover {
  background: var(--color-gray-100);
}

.row-expanded {
  background: var(--color-surface);
  box-shadow: inset 0 2px 0 var(--color-primary);
}

.row-expanded:hover {
  background: var(--color-surface);
}

/* Cell Styles */
.cell-number {
  font-family: var(--font-family-mono);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.cell-subject {
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cell-time {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  white-space: nowrap;
}

.cell-duration {
  font-variant-numeric: tabular-nums;
}

/* Status Badge */
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-1);
  padding: var(--spacing-1) var(--spacing-2);
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

.status-badge.ready {
  background: var(--color-gray-100);
  color: var(--color-gray-600);
}

.status-badge.in_progress {
  background: var(--color-warning-light);
  color: #b45309;
}

.status-badge.completed {
  background: var(--color-success-light);
  color: var(--color-success);
}

.status-badge.paused {
  background: #fef3c7;
  color: #d97706;
}

/* Expand Button */
.expand-btn {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-1);
  padding: var(--spacing-1) var(--spacing-2);
  background: transparent;
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  transition: all var(--transition-fast);
}

.expand-btn svg {
  width: 14px;
  height: 14px;
  transition: transform var(--transition-fast);
}

.expand-btn:hover {
  background: var(--color-surface);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.expand-btn.is-expanded svg {
  transform: rotate(180deg);
}

.expand-btn.is-expanded {
  background: var(--color-primary-light);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

/* Expand Row */
.expand-row {
  background: var(--color-gray-50);
}

.expand-row td {
  padding: 0;
  border-bottom: 1px solid var(--color-border-light);
}

.question-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--spacing-3);
  padding: var(--spacing-3);
}

.question-section {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border-light);
  overflow: hidden;
}

.question-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-2) var(--spacing-3);
  background: var(--color-gray-50);
  border-bottom: 1px solid var(--color-border-light);
}

.question-header svg {
  width: 16px;
  height: 16px;
  color: var(--color-text-muted);
}

.question-title {
  font-weight: var(--font-weight-semibold);
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
}

.question-number {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  margin-left: auto;
}

.question-tag {
  font-size: var(--font-size-xs);
  padding: var(--spacing-1) var(--spacing-2);
  background: var(--color-primary-light);
  color: var(--color-primary);
  border-radius: var(--radius-sm);
}

.question-content {
  padding: var(--spacing-3);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.question-content p {
  margin: 0;
  line-height: 1.6;
}

.question-content p:empty {
  display: none;
}

.question-content .image-container {
  margin: var(--spacing-2) 0;
  cursor: pointer;
  display: block;
}

.question-content .image-container img {
  max-width: 200px;
  max-height: 150px;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border-light);
  transition: all var(--transition-fast);
  vertical-align: middle;
}

.question-content .image-container:hover img {
  border-color: var(--color-primary);
  transform: scale(1.02);
  box-shadow: var(--shadow-base);
}

.question-content .image-container:first-child {
  margin-top: 0;
}

.question-content .image-container:last-child {
  margin-bottom: 0;
}

.question-content .image-container img {
  max-width: 200px;
  max-height: 150px;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border-light);
  transition: all var(--transition-fast);
}

.question-content .image-container:hover img {
  border-color: var(--color-primary);
  transform: scale(1.02);
  box-shadow: var(--shadow-base);
}

.question-content .sub-question {
  margin-bottom: var(--spacing-2);
  padding: var(--spacing-3);
  background: var(--color-gray-50);
  border-radius: var(--radius-md);
  border-left: 3px solid var(--color-primary);
}

.question-content .sub-question-title {
  font-weight: var(--font-weight-semibold);
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-2);
}

.question-content .sub-question p {
  margin: 0;
}

.no-questions {
  grid-column: 1 / -1;
  text-align: center;
  padding: var(--spacing-4);
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
}

/* Image Preview Modal */
.image-preview-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: var(--spacing-5);
  animation: fadeIn 150ms ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.image-preview-content {
  position: relative;
  max-width: 90%;
  max-height: 90%;
  animation: scaleIn 200ms ease-out;
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.image-preview-content img {
  max-width: 100%;
  max-height: 85vh;
  border-radius: var(--radius-lg);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  object-fit: contain;
}

.image-preview-content .close-btn {
  position: absolute;
  top: -12px;
  right: -12px;
  width: 36px;
  height: 36px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 50%;
  color: var(--color-text-secondary);
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
  box-shadow: var(--shadow-base);
}

.image-preview-content .close-btn:hover {
  background: var(--color-gray-100);
  color: var(--color-text-primary);
  transform: scale(1.05);
}

/* Footer */
.footer {
  text-align: center;
  padding: var(--spacing-4);
  background: var(--color-surface);
  border-top: 1px solid var(--color-border-light);
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
}

.footer p {
  margin: 0;
}
</style>
