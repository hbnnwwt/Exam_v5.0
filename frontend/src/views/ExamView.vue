<template>
  <div class="exam-page">
    <!-- 顶部栏 -->
    <header class="header">
      <div class="header-content">
        <div class="header-logos">
          <img v-if="settings.instituteLogo" :src="settings.instituteLogo" class="logo" alt="学院Logo">
          <img v-if="settings.collegeLogo" :src="settings.collegeLogo" class="logo" alt="学校Logo">
        </div>
        <h1 class="header-title">{{ settings.title }}</h1>
        <div class="header-controls">
          <span v-if="examStore.currentStudent" class="current-student">
            当前考生: {{ examStore.currentStudent }}
          </span>
          <a href="/editor" target="_blank" class="nav-btn">题库管理</a>
          <a href="/export" target="_blank" class="nav-btn">导出</a>
          <a href="/settings" target="_blank" class="nav-btn">设置</a>
          <a href="/help" target="_blank" class="nav-btn">帮助</a>
        </div>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="main-content">
      <!-- 左侧面板 - 考试流程 -->
      <aside class="left-panel" :class="{ collapsed: leftPanelCollapsed }">
        <button class="panel-toggle" @click="leftPanelCollapsed = !leftPanelCollapsed">
          {{ leftPanelCollapsed ? '▶' : '◀' }}
        </button>
        <div v-if="!leftPanelCollapsed" class="panel-content">
          <h3>面试流程</h3>
          <div class="step-list">
            <div
              v-for="step in steps"
              :key="step.id"
              :class="['step-item', { active: examStore.currentStep === step.id, completed: examStore.currentStep > step.id }]"
              @click="goToStep(step.id)"
            >
              <span class="step-number">{{ step.id }}</span>
              <span class="step-name">{{ step.name }}</span>
            </div>
          </div>
        </div>
      </aside>

      <!-- 中间内容区 -->
      <section class="center-panel">
        <!-- 考生输入区 / 开始考试 -->
        <div v-if="!examStore.currentStudent" class="student-input-area">
          <h2>研究生复试面试</h2>
          <p class="subtitle">点击下方按钮开始考试，系统将自动分配考生编号</p>
          <button @click="startExam" :disabled="isProcessing" class="load-btn">开始考试</button>
        </div>

        <!-- 考试内容区 -->
        <div v-else class="exam-content">
          <div class="step-header">
            <h2>{{ examStore.stepName }}</h2>
            <Timer />
          </div>

          <!-- 步骤内容 -->
          <div class="step-content">
            <StepContent :step="examStore.currentStep" />
          </div>

          <!-- 控制按钮 -->
          <div class="step-controls">
            <button
              @click="prevStep"
              :disabled="examStore.currentStep <= 1"
              class="control-btn prev"
            >
              ◀ 上一步
            </button>
            <button @click="completeExam" class="control-btn complete">
              ✓ 完成考试
            </button>
            <button
              @click="nextStep"
              :disabled="examStore.currentStep >= examStore.totalSteps || isProcessing"
              class="control-btn next"
            >
              {{ isProcessing ? '处理中...' : '下一步 ▶' }}
            </button>
          </div>

          <!-- 下一个考生按钮（考试完成后显示） -->
          <div v-if="examStore.examStatus === 'completed'" class="next-student-section">
            <p class="next-tip">考生 {{ examStore.currentStudent }} 考试已完成</p>
            <button @click="nextStudent" class="next-student-btn">
              下一个考生 →
            </button>
          </div>
        </div>
      </section>

      <!-- 右侧面板 - 控制面板 -->
      <aside class="right-panel" :class="{ collapsed: rightPanelCollapsed }">
        <button class="panel-toggle" @click="rightPanelCollapsed = !rightPanelCollapsed">
          {{ rightPanelCollapsed ? '◀' : '▶' }}
        </button>
        <div v-if="!rightPanelCollapsed" class="panel-content">
          <h3>控制面板</h3>
          <div class="control-section">
            <h4>考试状态</h4>
            <p :class="['status-badge', examStore.examStatus]">
              {{ statusText }}
            </p>
          </div>
          <div class="control-section">
            <h4>快速操作</h4>
            <button @click="resetExam" class="quick-btn danger">重置考试</button>
          </div>
        </div>
      </aside>
    </main>

    <!-- 底部版权 -->
    <footer class="footer">
      <p>{{ settings.footerCopyright || '考试流程控制系统' }}</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useExamStore } from '@/stores/exam'
import { useToastStore } from '@/stores/toast'
import api from '@/api'
import Timer from '@/components/Timer.vue'
import StepContent from '@/components/StepContent.vue'

const examStore = useExamStore()
const toast = useToastStore()

// 状态
const leftPanelCollapsed = ref(false)
const rightPanelCollapsed = ref(false)
const isProcessing = ref(false)  // 处理中状态，防止重复点击
const settings = ref({
  title: '',
  instituteLogo: null,
  collegeLogo: null,
  footerCopyright: ''
})

// 步骤列表 - 从 store 的 stepInfos 加载
const steps = computed(() => {
  return examStore.stepInfos.map((step, index) => ({
    id: step.step_number || index + 1,
    name: step.title || `步骤 ${index + 1}`
  }))
})

// 状态文本
const statusText = computed(() => {
  const statusMap = {
    ready: '准备中',
    in_progress: '进行中',
    completed: '已完成'
  }
  return statusMap[examStore.examStatus] || '未知'
})

// 开始考试（自动创建下一个考生）
const startExam = async () => {
  try {
    const response = await api.post('/exam-api/students/next')
    if (response.success) {
      const studentNumber = response.data.studentNumber
      // 重置 isReset 标志，确保进度可以保存
      examStore.isReset = false
      await examStore.setStudent(studentNumber)
      examStore.examStatus = 'in_progress'
      examStore.startStepTimer()
      // 保存进度
      await examStore.saveProgress()
      toast.success(`考生 ${studentNumber} - 开始考试`)
    } else {
      toast.error(response.error || '开始考试失败')
    }
  } catch (error) {
    toast.error('开始考试失败: ' + error.message)
  }
}

// 下一个考生
const nextStudent = async () => {
  if (isProcessing.value) return  // 防止重复点击
  if (!confirm('确定要进入下一个考生的考试吗？')) {
    return
  }

  isProcessing.value = true
  try {
    // 重置当前考生的前端状态（不调用后端reset）
    examStore.currentStep = 1
    examStore.examStatus = 'ready'
    examStore.translationQuestion = null
    examStore.professionalQuestion = null
    examStore.currentTranslationQuestionId = null
    examStore.currentProfessionalQuestionId = null
    examStore.usedQuestionIds = []
    examStore.isReset = false

    // 开始新的考试（会自动创建下一个考生）
    await startExam()
  } finally {
    isProcessing.value = false
  }
}

// 步骤导航
const goToStep = (stepId) => {
  if (stepId <= examStore.currentStep) {
    examStore.currentStep = stepId
    examStore.startStepTimer()
    examStore.saveProgress()
  }
}

const prevStep = () => {
  examStore.prevStep()
  examStore.saveProgress()
}

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

const completeExam = async () => {
  // 调用后端API完成考试
  try {
    await api.post('/exam-api/complete', {
      studentNumber: examStore.currentStudent
    })
  } catch (error) {
    console.error('完成考试API调用失败:', error)
  }

  examStore.examStatus = 'completed'
  examStore.currentStep = examStore.totalSteps
  await examStore.saveProgress()
  toast.success('考试已完成！')
}

const resetExam = async () => {
  if (isProcessing.value) return  // 防止重复点击
  if (!confirm('确定要重置考试吗？这将清除所有考试数据！')) {
    return
  }

  isProcessing.value = true
  try {
    const result = await examStore.resetExam()
    if (result.success) {
      toast.success('系统已完全重置')
    } else {
      toast.error('重置失败: ' + (result.error || '未知错误'))
    }
  } finally {
    isProcessing.value = false
  }
}

// 加载设置
const loadSettings = async () => {
  try {
    const response = await api.get('/api/header-settings')
    if (response.success) {
      settings.value = response.data
    }
  } catch (error) {
    console.error('加载设置失败:', error)
  }
}

// 页面加载时恢复考试进度
const restoreExamProgress = async () => {
  const hasProgress = await examStore.loadProgress()
  if (hasProgress) {
    toast.success(`已恢复考生 ${examStore.currentStudent} 的考试进度`)
  }
}

// 自动保存进度（每30秒）
let autoSaveInterval = null
const startAutoSave = () => {
  if (autoSaveInterval) clearInterval(autoSaveInterval)
  autoSaveInterval = setInterval(() => {
    if (examStore.examStatus === 'in_progress') {
      examStore.saveProgress()
    }
  }, 30000) // 30秒保存一次
}

// 页面关闭时不保存进度
// 进度保存依赖：用户操作时主动保存

onMounted(() => {
  loadSettings()
  examStore.loadStepSettings()
  restoreExamProgress()
})
</script>

<style scoped>
.exam-page {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: #f8f9fa;
}

/* 顶部栏 */
.header {
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
  padding: 15px 20px;
  flex-shrink: 0;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1400px;
  margin: 0 auto;
}

.header-logos {
  display: flex;
  gap: 15px;
}

.logo {
  height: 45px;
  object-fit: contain;
}

.header-title {
  font-size: 1.8rem;
  color: #1f2937;
  margin: 0;
}

.header-controls {
  display: flex;
  gap: 10px;
  align-items: center;
}

.current-student {
  color: #6b7280;
  font-size: 14px;
}

.nav-btn {
  padding: 8px 16px;
  background: var(--primary-color, #007bff);
  color: white;
  text-decoration: none;
  border-radius: 6px;
  font-size: 14px;
  transition: opacity 0.2s;
}

.nav-btn:hover {
  opacity: 0.9;
}

/* 主内容区 */
.main-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* 侧边栏 */
.left-panel,
.right-panel {
  width: 200px;
  background: #fff;
  border-right: 1px solid #e5e7eb;
  position: relative;
  transition: width 0.3s ease;
}

.left-panel.collapsed,
.right-panel.collapsed {
  width: 40px;
}

.right-panel {
  border-right: none;
  border-left: 1px solid #e5e7eb;
}

.panel-toggle {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 60px;
  background: #f0f0f0;
  border: 1px solid #ccc;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}

.left-panel .panel-toggle {
  right: -10px;
  border-radius: 0 4px 4px 0;
}

.right-panel .panel-toggle {
  left: -10px;
  border-radius: 4px 0 0 4px;
}

.panel-content {
  padding: 15px;
}

.panel-content h3 {
  margin: 0 0 15px;
  font-size: 16px;
  color: #333;
}

/* 步骤列表 */
.step-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.step-item:hover {
  background: #f3f4f6;
}

.step-item.active {
  background: var(--primary-color, #007bff);
  color: white;
}

.step-item.completed {
  background: #d1fae5;
}

.step-number {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}

.step-item.active .step-number {
  background: white;
  color: var(--primary-color, #007bff);
}

.step-item.completed .step-number {
  background: #10b981;
  color: white;
}

.step-name {
  font-size: 14px;
}

/* 中间内容区 */
.center-panel {
  flex: 1;
  padding: 20px;
  display: flex;
  flex-direction: column;
  overflow: auto;
}

.student-input-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
}

.student-input-area h2 {
  color: #1f2937;
  margin-bottom: 10px;
}

.input-group {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.student-input {
  padding: 12px 20px;
  font-size: 18px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  width: 300px;
  outline: none;
  transition: border-color 0.2s;
}

.student-input:focus {
  border-color: var(--primary-color, #007bff);
}

.load-btn {
  padding: 12px 30px;
  background: var(--primary-color, #007bff);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.load-btn:hover {
  background: #0056b3;
}

.subtitle {
  color: #666;
  margin-bottom: 20px;
}

/* 下一个考生按钮 */
.next-student-section {
  margin-top: 20px;
  padding: 20px;
  background: #e8f5e9;
  border-radius: 8px;
  text-align: center;
}

.next-tip {
  color: #2e7d32;
  margin-bottom: 15px;
  font-size: 16px;
}

.next-student-btn {
  padding: 12px 30px;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.next-student-btn:hover {
  background: #388e3c;
}

/* 考试内容区 */
.exam-content {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.step-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.step-header h2 {
  margin: 0;
  color: #1f2937;
}

.step-content {
  flex: 1;
  overflow-y: auto;
}

.step-controls {
  display: flex;
  justify-content: center;
  gap: 20px;
  padding-top: 20px;
  margin-top: auto;
}

.control-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.control-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.control-btn.prev {
  background: #6c757d;
  color: white;
}

.control-btn.next {
  background: var(--primary-color, #007bff);
  color: white;
}

.control-btn.complete {
  background: var(--success-color, #28a745);
  color: white;
}

.control-btn:hover:not(:disabled) {
  opacity: 0.9;
  transform: translateY(-2px);
}

/* 控制面板 */
.control-section {
  margin-bottom: 20px;
}

.control-section h4 {
  margin: 0 0 10px;
  font-size: 14px;
  color: #6b7280;
}

.status-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.ready {
  background: #fef3c7;
  color: #92400e;
}

.status-badge.in_progress {
  background: #dbeafe;
  color: #1e40af;
}

.status-badge.completed {
  background: #d1fae5;
  color: #065f46;
}

.quick-btn {
  width: 100%;
  padding: 10px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.quick-btn.danger {
  background: #fee2e2;
  color: #dc2626;
}

.quick-btn.danger:hover {
  background: #fecaca;
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
