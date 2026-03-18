<template>
  <div class="export-page">
    <header class="header">
      <div class="header-left">
        <h1>数据导出</h1>
      </div>
      <div class="header-right">
        <router-link to="/" class="nav-btn">返回考试</router-link>
        <router-link to="/help" class="nav-btn">帮助</router-link>
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
              <div class="export-card">
                <h4>考生列表 Excel</h4>
                <p>导出所有考生的基本信息与考试状态</p>
                <button @click="exportStudents" class="export-btn">导出Excel</button>
              </div>

              <div class="export-card">
                <h4>PDF报告</h4>
                <p>生成可归档的PDF考试报告（含题目图片）</p>
                <button @click="exportPDF" class="export-btn">导出PDF</button>
              </div>

              <div class="export-card">
                <h4>HTML报告</h4>
                <p>生成可打印的HTML考试报告（含题目图片）</p>
                <button @click="exportHTML" class="export-btn">导出HTML</button>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧：考试记录预览 -->
        <div class="right-panel preview-section">
          <div class="preview-header">
            <h3>考试记录预览</h3>
            <button @click="loadStudents" class="refresh-btn">刷新预览</button>
          </div>
          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th>考生号</th>
                  <th>考试状态</th>
                  <th>专业科目</th>
                  <th>开始时间</th>
                  <th>结束时间</th>
                  <th>时长(分钟)</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <template v-for="student in students" :key="student.studentNumber">
                  <tr>
                    <td>{{ student.studentNumber }}</td>
                    <td>
                      <span :class="['status-badge', getStatusClass(student)]">
                        {{ getStatusText(student.examStatus) }}
                      </span>
                    </td>
                    <td>{{ student.professionalSubject || '-' }}</td>
                    <td>{{ student.startTime || '-' }}</td>
                    <td>{{ student.endTime || '-' }}</td>
                    <td>{{ student.durationMinutes || '-' }}</td>
                    <td>
                      <button @click="toggleExpand(student.studentNumber)" class="expand-btn">
                        {{ isExpanded(student.studentNumber) ? '收起' : '展开' }}
                      </button>
                    </td>
                  </tr>
                  <tr v-if="isExpanded(student.studentNumber)" class="expand-row">
                    <td colspan="7">
                      <div class="question-details">
                        <div v-if="student.translationInfo" class="question-section">
                          <div class="question-title">翻译题目 (题号: {{ student.translationInfo.questionNumber }})</div>
                          <div class="question-content" v-html="renderQuestion(student.translationInfo.questionContent)"></div>
                        </div>
                        <div v-if="student.professionalInfo" class="question-section">
                          <div class="question-title">专业题目 (题号: {{ student.professionalInfo.questionNumber }}) - {{ student.professionalInfo.subject }}</div>
                          <div class="question-content" v-html="renderQuestion(student.professionalInfo.questionContent)"></div>
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
      return `<p>${escapeHtml(item[1] || '')}</p>`
    }
    const imageData = normalizeImageData(item)
    if (imageData) {
      return `<div class="image-container" onclick="window.openImagePreview('${imageData.src}')" title="点击查看原图"><img src="${imageData.thumb}" alt="题目图片缩略图"></div>`
    }
    return ''
  }).join('')
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
        return data.map((sub, index) => `
          <div class="sub-question">
            <div class="sub-question-title">第${index + 1}题</div>
            <div class="sub-question-content">${renderContentItems(sub.content)}</div>
          </div>`
        ).join('')
      }

      // 普通数组
      return data.map(item => {
        if (Array.isArray(item) && item[0] === 'txt') {
          return `<p>${escapeHtml(item[1])}</p>`
        }
        const imageData = normalizeImageData(item)
        if (imageData) {
          return `<div class="image-container" onclick="window.openImagePreview('${imageData.src}')" title="点击查看原图"><img src="${imageData.thumb}" alt="题目图片缩略图"></div>`
        }
        return ''
      }).join('')
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
  try {
    const response = await api.get('/export-api/preview')
    if (response.success) {
      students.value = response.data || []
    }
  } catch (error) {
    console.error('加载考生列表失败:', error)
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

.main-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.export-container {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  gap: 20px;
}

.left-panel {
  width: 320px;
  flex-shrink: 0;
}

.right-panel {
  flex: 1;
  min-width: 0;
}

.stats-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.stats-section h3 {
  margin: 0 0 15px 0;
  color: #333;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.left-panel .stats-grid {
  grid-template-columns: repeat(2, 1fr);
}

.stat-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #007bff;
  margin-bottom: 5px;
}

.stat-label {
  color: #666;
  font-size: 14px;
}

.export-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.export-section h3 {
  margin: 0 0 15px 0;
  color: #333;
}

.export-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.export-card {
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 20px;
}

.export-card h4 {
  margin: 0 0 10px 0;
  color: #333;
}

.export-card p {
  margin: 0 0 15px 0;
  color: #666;
  font-size: 14px;
}

.export-btn {
  padding: 10px 20px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.export-btn:hover {
  background: #0056b3;
}

.preview-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
}

.preview-section h3 {
  margin: 0 0 15px 0;
  color: #333;
}

.preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 15px;
}

.refresh-btn {
  padding: 8px 14px;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.refresh-btn:hover {
  background: #5a6268;
}

.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #dee2e6;
}

.data-table th {
  background: #f8f9fa;
  font-weight: bold;
  color: #333;
}

.data-table td {
  color: #666;
}

.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.status-badge.ready {
  background: #e9ecef;
  color: #666;
}

.status-badge.in_progress {
  background: #fff3cd;
  color: #856404;
}

.status-badge.completed {
  background: #d4edda;
  color: #155724;
}

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

.question-content p {
  margin: 8px 0;
}

.question-content .image-container {
  margin: 10px 0;
  cursor: pointer;
}

.question-content .image-container img {
  max-width: 150px;
  max-height: 120px;
  border-radius: 4px;
  border: 1px solid #dee2e6;
}

.question-content .image-container:hover img {
  border-color: #007bff;
}

.question-content .sub-question {
  margin-bottom: 15px;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 4px;
}

.question-content .sub-question-title {
  font-weight: bold;
  font-size: 13px;
  color: #333;
  margin-bottom: 8px;
}

/* 图片预览弹窗 */
.image-preview-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.image-preview-content {
  position: relative;
  max-width: 90%;
  max-height: 90%;
}

.image-preview-content img {
  max-width: 100%;
  max-height: 90vh;
  border-radius: 4px;
}

.image-preview-content .close-btn {
  position: absolute;
  top: -40px;
  right: 0;
  background: none;
  border: none;
  color: white;
  font-size: 32px;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.image-preview-content .close-btn:hover {
  color: #ccc;
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
