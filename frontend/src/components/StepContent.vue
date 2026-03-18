<template>
  <div class="step-content-wrapper">
    <!-- 步骤 1 -->
    <div v-if="step === 1" class="step-intro">
      <h3>{{ currentStepInfo.title || `步骤 ${step}` }}</h3>
      <p>{{ currentStepInfo.description || '请考生进行自我介绍' }}</p>
    </div>

    <!-- 步骤 2 -->
    <div v-if="step === 2" class="step-intro">
      <h3>{{ currentStepInfo.title || `步骤 ${step}` }}</h3>
      <p>{{ currentStepInfo.description || 'Please introduce yourself' }}</p>
    </div>

    <!-- 步骤 3: 英文翻译 -->
    <div v-if="step === 3" class="step-translation">
      <h3>{{ currentStepInfo.title || `步骤 ${step}` }}</h3>
      <div v-if="examStore.translationQuestion" class="question-display">
        <div class="question-content" v-html="renderQuestion(examStore.translationQuestion)"></div>
        <!-- 添加查看/重新抽取按钮 -->
        <button @click="openQuestionSelection('translation')" class="select-btn" style="margin-top: 10px;">
          查看题目
        </button>
      </div>
      <div v-else class="no-question">
        <button @click="openQuestionSelection('translation')" class="select-btn">
          抽取翻译题目
        </button>
      </div>
    </div>

    <!-- 步骤 4: 专业问题 -->
    <div v-if="step === 4" class="step-professional">
      <h3>{{ currentStepInfo.title || `步骤 ${step}` }}</h3>
      <!-- 已抽取的题目 -->
      <div v-if="examStore.professionalQuestion" class="question-display">
        <div class="question-content" v-html="renderQuestion(examStore.professionalQuestion)"></div>
        <!-- 添加查看/重新抽取按钮 -->
        <button @click="openProfessionalQuestion" class="select-btn" style="margin-top: 10px;">
          查看题目
        </button>
      </div>
      <!-- 没有专业题时显示抽取按钮，点击后弹出科目选择弹窗 -->
      <div v-else class="no-question">
        <button @click="openProfessionalQuestion" class="select-btn">
          抽取专业题目
        </button>
      </div>
    </div>

    <!-- 步骤 5: 综合问答 -->
    <div v-if="step === 5" class="step-qna">
      <h3>{{ currentStepInfo.title || `步骤 ${step}` }}</h3>
      <p>{{ currentStepInfo.description || '考官可进行综合提问' }}</p>
    </div>

    <!-- 步骤 6: 考试结束 -->
    <div v-if="step === 6" class="step-complete">
      <h3>{{ currentStepInfo.title || `步骤 ${step}` }}</h3>
      <p>{{ currentStepInfo.description || '感谢考生的配合！' }}</p>
    </div>

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

    <!-- 图片预览弹窗 -->
    <div v-if="showImagePreview" class="image-preview-overlay" @click="closeImagePreview">
      <div class="image-preview-content" @click.stop>
        <button class="image-preview-close" @click="closeImagePreview">&times;</button>
        <img :src="previewImageUrl" alt="图片预览" class="image-preview-img">
      </div>
    </div>

    <!-- 题目选择弹窗 -->
    <div v-if="showQuestionModal" class="modal-overlay" @click="closeModal">
      <div class="modal question-modal" @click.stop>
        <div class="modal-header">
          <h3>{{ modalTitle }}</h3>
          <button class="modal-close" @click="closeModal">&times;</button>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p>正在加载题目...</p>
        </div>

        <!-- 题目选择区域 -->
        <div class="question-grid-container">
          <div class="question-stats">
            总计: {{ questions.length }} | 已使用: {{ usedCount }} | 可用: {{ availableCount }}
            <span v-if="selectedQuestionId" class="selected-hint">（已抽取）</span>
          </div>

          <!-- 题目网格（始终显示，抽取时禁用交互） -->
          <div class="question-grid" :class="{ drawing: isDrawing }">
            <div
              v-for="(q, index) in questions"
              :key="q.id"
              class="question-item"
              :style="{ backgroundColor: getQuestionColor(q, selectedQuestionId) }"
              :data-question-id="q.id"
              :data-index="index"
            >
              <span class="question-number">{{ index + 1 }}</span>
              <span class="question-status">
                {{ selectedQuestionId === q.id ? '已抽取' : (q.is_used ? '已使用' : '可用') }}
              </span>
            </div>
          </div>

          <!-- 抽取动画（叠加在网格上方） -->
          <div v-if="isDrawing" class="drawing-overlay">
            <div class="drawing-spinner"></div>
            <p class="drawing-text">正在抽取题目...</p>
          </div>
          <div class="modal-footer">
            <!-- 抽取/确定按钮 -->
            <button
              v-if="!selectedQuestionId"
              @click="startDraw"
              :disabled="availableCount === 0 || isDrawing"
              class="draw-btn"
            >
              开始抽取
            </button>
            <button
              v-else
              @click="closeModal"
              class="confirm-btn"
            >
              确定
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useExamStore } from '@/stores/exam'
import { useToastStore } from '@/stores/toast'
import api from '@/api'

const props = defineProps({
  step: {
    type: Number,
    required: true
  }
})

const examStore = useExamStore()
const toast = useToastStore()

// 当前步骤信息 - 从 store 动态获取
const currentStepInfo = computed(() => {
  return examStore.stepInfos.find(s => s.step_number === props.step) || {}
})

// 科目列表 - 从数据库加载
const subjects = ref([])

// 加载科目列表
const loadSubjects = async () => {
  try {
    const response = await api.get('/api/subjects')
    if (response.success && response.data) {
      // 转换为 { code, name } 格式
      subjects.value = response.data.map(s => ({
        code: s.value,
        name: s.label
      }))
    }
  } catch (error) {
    console.error('加载科目列表失败:', error)
  }
}

// 组件挂载时加载科目
onMounted(() => {
  loadSubjects()
  // 注册全局图片预览函数（供v-html中的onclick调用）
  window.showImagePreview = (url) => {
    previewImageUrl.value = url
    showImagePreview.value = true
  }
})

// 组件卸载时清理定时器
onUnmounted(() => {
  if (animationTimer.value) {
    clearInterval(animationTimer.value)
  }
})

// 状态
const showQuestionModal = ref(false)
const showSubjectModal = ref(false)  // 科目选择弹窗显示
const showImagePreview = ref(false)  // 图片放大预览
const previewImageUrl = ref('')      // 预览图片URL
const currentQuestionType = ref('')
const questions = ref([])
const selectedSubject = ref('')
const loading = ref(false)
const selectedQuestionId = ref(null)  // 被抽中的题目ID
const isDrawing = ref(false)  // 抽取中状态
const tempHighlightId = ref(null)   // 动画中临时高亮的题目ID
const animationTimer = ref(null)     // 动画定时器引用

// 计算属性
const usedCount = computed(() => questions.value.filter(q => q.is_used).length)
const availableCount = computed(() => questions.value.filter(q => !q.is_used).length)

const modalTitle = computed(() => {
  if (currentQuestionType.value === 'translation') {
    return '翻译题目抽取'
  }
  const subject = subjects.value.find(s => s.code === selectedSubject.value)
  return `专业题目抽取 - ${subject?.name || ''}`
})

// 科目选择
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

// 科目选择（保留原逻辑用于兼容）
const selectSubject = (code) => {
  selectedSubject.value = code
  openQuestionSelection('professional')
}

// 打开题目选择弹窗
const openQuestionSelection = async (type) => {
  currentQuestionType.value = type
  showQuestionModal.value = true
  loading.value = true
  isDrawing.value = false  // 重置抽取状态

  try {
    let url = `/exam-api/questions/${type}`
    if (type === 'professional' && selectedSubject.value) {
      url += `?subject=${selectedSubject.value}`
    }

    const response = await api.get(url)
    if (response.success && response.data) {
      questions.value = response.data

      // 根据 usedQuestionIds 标记已使用的题目
      const usedIds = examStore.usedQuestionIds || []
      console.log('[DEBUG] Marking used questions, usedIds:', usedIds)
      questions.value.forEach(q => {
        if (usedIds.includes(q.id)) {
          q.is_used = true
        }
      })

      console.log('获取题目数据:', questions.value.slice(0, 3))

      // 检查当前考生是否已经抽取过题目
      if (type === 'professional' && examStore.currentProfessionalQuestionId) {
        // 找到对应的题目ID并设置选中状态
        const alreadySelected = questions.value.find(q => q.id === examStore.currentProfessionalQuestionId)
        if (alreadySelected) {
          selectedQuestionId.value = alreadySelected.id
        }
      } else if (type === 'translation' && examStore.currentTranslationQuestionId) {
        const alreadySelected = questions.value.find(q => q.id === examStore.currentTranslationQuestionId)
        if (alreadySelected) {
          selectedQuestionId.value = alreadySelected.id
        }
      }
    } else {
      toast.error('获取题目失败')
    }
  } catch (error) {
    toast.error('获取题目失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 关闭弹窗
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

// 图片预览
const openImagePreview = (url) => {
  previewImageUrl.value = url
  showImagePreview.value = true
}

const closeImagePreview = () => {
  showImagePreview.value = false
  previewImageUrl.value = ''
}

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

    // 3. API返回后，动画继续运行，但停在被抽取的题目上
    if (!response.success || !response.data) {
      throw new Error('没有可用的题目')
    }

    const selectedQuestion = response.data

    // 停止扫描动画，停在被抽取的题目上（显示为待抽取状态）
    if (animationTimer.value) {
      clearInterval(animationTimer.value)
      animationTimer.value = null
    }
    // 停在被抽取的题目上，保持浅绿色高亮
    tempHighlightId.value = selectedQuestion.id

    // 等待500ms，让用户看到最终停在哪个题目上
    await new Promise(resolve => setTimeout(resolve, 500))

    // 4. 然后变成"已抽取"状态（高亮绿色+放大）
    tempHighlightId.value = null
    selectedQuestionId.value = selectedQuestion.id

    // 更新题目状态
    const qIndex = questionList.findIndex(q => q.id === selectedQuestion.id)
    if (qIndex !== -1) {
      questionList[qIndex].is_used = true
    }

    // 更新 usedQuestionIds 到 store
    if (!examStore.usedQuestionIds.includes(selectedQuestion.id)) {
      examStore.usedQuestionIds = [...examStore.usedQuestionIds, selectedQuestion.id]
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

    // 保存题目ID到后端（同时更新 students 和 exam_records 表）
    if (examStore.currentStudent) {
      try {
        const updateData = {}
        if (currentQuestionType.value === 'translation') {
          updateData.translationQuestionId = selectedQuestion.id
          updateData.translationQuestion = typeof selectedQuestion.content === 'string'
            ? selectedQuestion.content
            : JSON.stringify(selectedQuestion.content || selectedQuestion.question_data)
        } else {
          updateData.professionalQuestionId = selectedQuestion.id
          updateData.professionalQuestion = typeof selectedQuestion.content === 'string'
            ? selectedQuestion.content
            : JSON.stringify(selectedQuestion.content || selectedQuestion.question_data)
          updateData.professionalSubject = selectedSubject.value
        }
        // 更新 students 表
        await api.put(`/exam-api/students/${examStore.currentStudent}`, updateData)
        // 更新 exam_records 表（用于加载进度时正确显示已抽取题目）
        await examStore.saveProgress()
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

// 获取题目颜色 - 优先显示选中题目，其次显示已使用题目，最后显示可用题目
// 获取题目颜色 - 优先显示: 选中 > 扫描中 > 已使用 > 可用
const getQuestionColor = (question, selectedId) => {
  // 1. 选中的题目 - 高亮橙红色（最明显）
  if (selectedId === question.id) {
    return '#fd7e14 !important'
  }
  // 2. 扫描中高亮 - 浅橙色
  if (tempHighlightId.value === question.id) {
    return '#fed7aa !important'
  }
  // 3. 已使用题目 - 灰色
  if (question.is_used) {
    return '#6c757d !important'
  }
  // 4. 可用题目 - 绿色
  return '#28a745 !important'
}

// 渲染题目内容
const escapeHtml = (text) => {
  if (!text) return ''
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

const normalizeImageData = (item) => {
  if (!Array.isArray(item) || item[0] !== 'img' || typeof item[1] !== 'object' || !item[1]) {
    return null
  }
  const src = item[1].src
  const thumb = item[1].thumb
  if (!src || !thumb) return null
  return { src, thumb }
}

// 判断是否为套题格式
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
      return `<div class="image-container" onclick="showImagePreview('${imageData.src}')" title="点击查看原图"><img src="${imageData.thumb}" alt="题目图片缩略图"></div>`
    }
    return ''
  }).join('')
}

const renderQuestion = (questionData) => {
  if (!questionData) return ''

  try {
    // 处理各种可能的数据格式
    let data = questionData

    // 如果是字符串，尝试解析为 JSON
    if (typeof data === 'string') {
      try {
        data = JSON.parse(data)
      } catch {
        // 如果解析失败，直接返回字符串
        return escapeHtml(data)
      }
    }

    // 如果是数组，先判断是否是套题格式
    if (Array.isArray(data)) {
      // 检查是否是套题格式（每个元素是包含content字段的对象）
      if (isQuestionSet(data)) {
        // 套题：渲染所有子题
        return data.map((sub, index) => {
          return `<div class="sub-question">
            <div class="sub-question-label">第 ${index + 1} 题</div>
            <div class="sub-question-content">${renderContentItems(sub.content)}</div>
          </div>`
        }).join('')
      }

      // 普通数组：原有逻辑
      return data.map(item => {
        if (Array.isArray(item) && item[0] === 'txt') {
          return `<p>${escapeHtml(item[1])}</p>`
        }
        const imageData = normalizeImageData(item)
        if (imageData) {
          return `<div class="image-container" onclick="showImagePreview('${imageData.src}')" title="点击查看原图"><img src="${imageData.thumb}" alt="题目图片缩略图"></div>`
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
</script>

<style scoped>
.step-content-wrapper {
  padding: 20px;
  background: #fff;
  border-radius: 12px;
  min-height: 300px;
}

.step-intro,
.step-qna,
.step-complete {
  text-align: center;
  padding: 40px;
}

.step-intro h3,
.step-qna h3,
.step-complete h3 {
  font-size: 1.5rem;
  margin-bottom: 15px;
}

.question-display {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.question-content {
  line-height: 1.8;
}

.no-question {
  text-align: center;
  padding: 40px;
}

.select-btn {
  padding: 12px 30px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.select-btn:hover {
  background: #0056b3;
  transform: scale(1.02);
}

/* 科目选择 */
.subject-selection {
  text-align: center;
}

.subject-selection p {
  margin-bottom: 20px;
  color: #666;
}

.subject-buttons {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
}

.subject-btn {
  padding: 10px 20px;
  background: #fff;
  border: 2px solid #007bff;
  border-radius: 8px;
  color: #007bff;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.subject-btn:hover {
  background: #007bff;
  color: white;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.question-modal {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 800px;
  max-height: 80vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
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
  font-size: 28px;
  cursor: pointer;
  color: #999;
  line-height: 1;
}

.loading-state {
  text-align: center;
  padding: 60px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.question-grid-container {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  position: relative;
}

.question-stats {
  text-align: center;
  padding: 10px;
  color: #666;
  font-size: 14px;
  margin-bottom: 15px;
}

.question-stats .selected-hint {
  color: #28a745;
  font-weight: bold;
  margin-left: 10px;
}

/* 抽取动画 - 叠加在网格上方 */
.drawing-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px 50px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 10;
}

.drawing-spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #e9ecef;
  border-top: 5px solid #007bff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.drawing-text {
  margin-top: 15px;
  color: #007bff;
  font-size: 16px;
  font-weight: 500;
}

.question-grid {
  transition: opacity 0.2s;
}

.question-grid.drawing {
  opacity: 0.5;
  pointer-events: none;
}

.question-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  gap: 10px;
}

.question-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 15px 10px;
  border-radius: 8px;
  transition: all 0.2s;
  color: white;
}

/* 未抽题目 - 绿色 */
.question-item.available {
  background: #28a745 !important;
  color: white !important;
  cursor: pointer;
}

/* 已抽过题目 - 灰色 */
.question-item.used {
  background: #6c757d !important;
  color: white !important;
  opacity: 0.5;
}

/* 当前选中题目 - 高亮橙红色 */
.question-item.selected {
  background: #fd7e14 !important;
  color: white !important;
  opacity: 1 !important;
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(253, 126, 20, 0.6);
  border: 2px solid #fff;
}

.question-item.selected .question-status {
  color: white !important;
}

.question-item .question-status {
  color: inherit;
  opacity: 0.9;
}

.question-number {
  font-size: 18px;
  font-weight: bold;
  color: inherit;
}

.question-status {
  font-size: 12px;
  margin-top: 5px;
}

.modal-footer {
  padding: 15px 20px;
  border-top: 1px solid #dee2e6;
  text-align: center;
}

.draw-btn {
  padding: 12px 40px;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.draw-btn:hover:not(:disabled) {
  background: #218838;
}

.draw-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* 抽取完成后的操作区域 */
.completed-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
}

.completed-text {
  color: #28a745;
  font-size: 16px;
  font-weight: bold;
}

.confirm-btn {
  padding: 12px 40px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.confirm-btn:hover {
  background: #0056b3;
}

.drawing-state {
  flex: 1;
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.drawing-text {
  text-align: center;
  font-size: 18px;
  color: #007bff;
  margin-bottom: 20px;
}

.question-item {
  min-height: 60px;
}

/* 图片容器 - 点击放大 */
.image-container {
  display: inline-block;
  width: 180px;
  height: 120px;
  margin: 4px;
  cursor: pointer;
  overflow: hidden;
  border-radius: 4px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
  transition: transform 0.2s, box-shadow 0.2s;
}

.image-container:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.25);
}

.image-container img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: #fff;
}

/* 图片预览弹窗 */
.image-preview-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  padding: 40px;
  box-sizing: border-box;
}

.image-preview-content {
  position: relative;
  max-width: 100%;
  max-height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-preview-img {
  max-width: 100%;
  max-height: calc(100vh - 80px);
  object-fit: contain;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
}

.image-preview-close {
  position: absolute;
  top: -40px;
  right: 0;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  font-size: 28px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.image-preview-close:hover {
  background: rgba(255, 255, 255, 0.4);
}

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
/* 子题目样式 */
.sub-question {
  margin-bottom: 20px;
  padding: 15px;
  background: #fff;
  border-radius: 8px;
  border-left: 4px solid #007bff;
}

.sub-question:last-child {
  margin-bottom: 0;
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

/* 题目内容中的图片 */
.question-content > img {
  max-width: 30%;
  max-height: 15vh;
  height: auto;
  border-radius: 8px;
  margin: 8px 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  object-fit: contain;
}

/* 内容项中的图片 */
.content-item {
  margin: 8px 0;
}

.content-item img {
  max-width: 30%;
  max-height: 15vh;
  height: auto;
  border-radius: 6px;
  object-fit: contain;
  display: block;
}
</style>
