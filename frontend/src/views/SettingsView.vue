<template>
  <div class="settings-page">
    <!-- 顶部导航 -->
    <header class="settings-header">
      <div class="header-left">
        <svg class="header-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="3"/>
          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9c.26.604.852.997 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
        </svg>
        <h1>考试设置</h1>
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

    <!-- 主内容区 -->
    <main class="main-content">
      <div class="settings-container">
        <!-- 左侧侧边栏 -->
        <div class="sidebar">
          <!-- 步骤列表 -->
          <div class="steps-section">
            <h3>考试步骤</h3>
            <div class="steps-list">
              <div
                v-for="(step, index) in steps"
                :key="step.step_number"
                :class="['step-item', { active: selectedStep === index }]"
                @click="selectStep(index)"
              >
                <span class="step-number">{{ index + 1 }}</span>
                <span class="step-name">{{ step.title }}</span>
              </div>
            </div>
          </div>

          <!-- 系统外观 -->
          <div class="system-section">
            <h3>系统外观</h3>
            <div
              :class="['system-card', { active: activeSection === 'header' }]"
              @click="selectedStep = -1; activeSection = 'header'; loadHeaderSettings()"
            >
              <svg class="system-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                <circle cx="8.5" cy="8.5" r="1.5"/>
                <polyline points="21 15 16 10 5 21"/>
              </svg>
              <span class="system-label">Logo设置</span>
            </div>
            <div class="system-card" @click="$router.push('/settings/ai')">
              <svg class="system-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2a4 4 0 0 1 4 4v2a4 4 0 0 1-8 0V6a4 4 0 0 1 4-4z"/>
                <path d="M16 14H8a4 4 0 0 0-4 4v2h20v-2a4 4 0 0 0-4-4z"/>
                <circle cx="12" cy="6" r="1"/>
              </svg>
              <span class="system-label">AI 配置</span>
            </div>
          </div>
        </div>

        <!-- 右侧内容区：步骤设置 或 Logo设置 -->
        <div class="content-section">
          <!-- 步骤设置 -->
          <template v-if="activeSection === 'steps'">
            <h3>步骤设置 - {{ steps[selectedStep]?.title }}</h3>

            <div class="settings-editor">
              <!-- 步骤标题 -->
              <div class="form-group">
                <label>步骤标题</label>
                <input
                  v-model="currentStepSettings.title"
                  type="text"
                  class="form-input"
                  placeholder="例如：中文自我介绍"
                >
              </div>

              <!-- 步骤描述 -->
              <div class="form-group">
                <label>步骤描述</label>
                <textarea
                  v-model="currentStepSettings.description"
                  rows="2"
                  class="form-textarea"
                  placeholder="请输入步骤描述..."
                ></textarea>
              </div>

              <!-- 时间限制 -->
              <div class="form-group">
                <label>时间限制（秒）</label>
                <div class="time-input-group">
                  <input
                    v-model.number="currentStepSettings.duration"
                    type="number"
                    min="0"
                    max="3600"
                    class="form-input"
                  >
                  <span class="time-display">({{ formatTime(currentStepSettings.duration) }})</span>
                </div>
                <small class="form-hint">设置为0表示无时间限制</small>
              </div>

              <!-- 步骤类型 -->
              <div class="form-group">
                <label>步骤类型</label>
                <select v-model="currentStepSettings.step_type" class="form-select">
                  <option value="introduction">自我介绍</option>
                  <option value="translation">英文翻译</option>
                  <option value="professional">专业问题</option>
                  <option value="comprehensive">综合问答</option>
                  <option value="completion">考试结束</option>
                </select>
              </div>

              <button @click="saveStepSettings" class="save-btn">保存设置</button>
            </div>
          </template>

          <!-- Logo设置 -->
          <template v-if="activeSection === 'header'">
            <h3>Logo设置</h3>

            <div class="settings-editor">
              <!-- 系统标题 -->
              <div class="form-group">
                <label>系统标题</label>
                <input
                  v-model="headerSettings.title"
                  type="text"
                  placeholder="例如：研究生复试流程控制系统"
                  class="form-input"
                >
              </div>

              <!-- 学校Logo（第一个） -->
              <div class="form-group">
                <label>学校Logo</label>
                <div class="logo-upload">
                  <input
                    type="file"
                    accept="image/*"
                    @change="(e) => handleLogoUpload(e, 'instituteLogo')"
                    class="file-input"
                    id="instituteLogoInput"
                  >
                  <label for="instituteLogoInput" class="file-label">选择图片</label>
                </div>
                <div v-if="headerSettings.instituteLogo" class="logo-preview">
                  <img :src="headerSettings.instituteLogo" alt="学校Logo预览">
                  <button @click="removeLogo('instituteLogo')" class="remove-btn">×</button>
                </div>
              </div>

              <!-- 学院Logo（第二个） -->
              <div class="form-group">
                <label>学院Logo</label>
                <div class="logo-upload">
                  <input
                    type="file"
                    accept="image/*"
                    @change="(e) => handleLogoUpload(e, 'collegeLogo')"
                    class="file-input"
                    id="collegeLogoInput"
                  >
                  <label for="collegeLogoInput" class="file-label">选择图片</label>
                </div>
                <div v-if="headerSettings.collegeLogo" class="logo-preview">
                  <img :src="headerSettings.collegeLogo" alt="学院Logo预览">
                  <button @click="removeLogo('collegeLogo')" class="remove-btn">×</button>
                </div>
              </div>

              <!-- 预览区域 -->
              <div class="preview-section">
                <h4>预览效果</h4>
                <div class="header-preview">
                  <div class="preview-logos">
                    <img v-if="headerSettings.instituteLogo" :src="headerSettings.instituteLogo" class="preview-logo" alt="学校Logo">
                    <img v-if="headerSettings.collegeLogo" :src="headerSettings.collegeLogo" class="preview-logo" alt="学院Logo">
                  </div>
                  <h2 class="preview-title">{{ headerSettings.title || '研究生复试流程控制系统' }}</h2>
                </div>
              </div>

              <button @click="saveHeaderSettings" class="save-btn">保存设置</button>
            </div>
          </template>
        </div>
      </div>
    </main>

    <!-- 底部版权 -->
    <footer class="footer">
      <p>{{ footerSettings.footerCopyright || '版权所有 © 2026 北京石油化工学院 | 联系方式：wangwentong@bipt.edu.cn' }}</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useToastStore } from '@/stores/toast'
import { useExamStore } from '@/stores/exam'
import api from '@/api'

const toast = useToastStore()

// 步骤列表 - 默认值，会被数据库数据覆盖
const steps = ref([
  { step_number: 1, title: '', description: '', duration: 0, step_type: 'introduction' },
  { step_number: 2, title: '', description: '', duration: 0, step_type: 'introduction' },
  { step_number: 3, title: '', description: '', duration: 0, step_type: 'translation' },
  { step_number: 4, title: '', description: '', duration: 0, step_type: 'professional' },
  { step_number: 5, title: '', description: '', duration: 0, step_type: 'comprehensive' },
  { step_number: 6, title: '', description: '', duration: 0, step_type: 'completion' }
])

const selectedStep = ref(0)
const activeSection = ref('steps') // 当前显示的区块：steps 或 header

// 底部版权信息
const footerSettings = reactive({
  footerCopyright: ''
})

// Logo设置
const headerSettings = reactive({
  title: '',
  instituteLogo: '',
  collegeLogo: ''
})

// 加载Logo设置
const loadHeaderSettings = async () => {
  try {
    const response = await api.get('/api/header-settings')
    if (response.success && response.data) {
      headerSettings.title = response.data.title || ''
      headerSettings.instituteLogo = response.data.instituteLogo || ''
      headerSettings.collegeLogo = response.data.collegeLogo || ''
    }
  } catch (error) {
    console.error('加载Logo设置失败:', error)
  }
}

// 上传Logo图片
const handleLogoUpload = async (event, field) => {
  const file = event.target.files[0]
  if (!file) return

  try {
    const formData = new FormData()
    formData.append('file', file)

    const response = await fetch('/api/image', {
      method: 'POST',
      body: formData
    })
    const result = await response.json()

    if (result.success) {
      // 保存返回的图片路径 (后端返回 result.data.path)
      headerSettings[field] = result.data.path
      toast.success('上传成功')
    } else {
      toast.error(result.error || '上传失败')
    }
  } catch (error) {
    console.error('上传失败:', error)
    toast.error('上传失败: ' + error.message)
  }

  // 清空input，允许重复选择同一文件
  event.target.value = ''
}

// 移除Logo
const removeLogo = (field) => {
  headerSettings[field] = ''
}

// 保存Logo设置
const saveHeaderSettings = async () => {
  try {
    const response = await api.put('/api/header-settings', {
      title: headerSettings.title,
      instituteLogo: headerSettings.instituteLogo,
      collegeLogo: headerSettings.collegeLogo
    })

    if (response.success) {
      toast.success('保存成功')
    } else {
      toast.error(response.error || '保存失败')
    }
  } catch (error) {
    toast.error('保存失败: ' + error.message)
  }
}

const currentStepSettings = reactive({
  title: '',
  description: '',
  duration: 0,
  step_type: 'introduction'
})

// 加载所有步骤设置
const loadStepSettings = async () => {
  try {
    const response = await api.get('/exam-api/exam-steps')
    if (response.success && response.data && response.data.length > 0) {
      // 更新本地步骤数据
      response.data.forEach((step, index) => {
        if (index < steps.value.length) {
          steps.value[index] = {
            step_number: step.step_number,
            title: step.title,
            description: step.description || '',
            duration: step.duration,
            step_type: step.step_type
          }
        }
      })
    }
  } catch (error) {
    console.error('加载步骤设置失败:', error)
  }
}

// 选择步骤
const selectStep = (index) => {
  selectedStep.value = index
  activeSection.value = 'steps' // 切换到步骤设置区域
  // 加载该步骤的设置到编辑表单
  const step = steps.value[index]
  currentStepSettings.title = step.title || ''
  currentStepSettings.description = step.description || ''
  currentStepSettings.duration = step.duration || 0
  currentStepSettings.step_type = step.step_type || 'introduction'
}

// 保存步骤设置
const saveStepSettings = async () => {
  try {
    const stepNumber = selectedStep.value + 1
    const response = await api.put(`/exam-api/exam-steps/${stepNumber}`, {
      title: currentStepSettings.title,
      description: currentStepSettings.description,
      duration: currentStepSettings.duration,
      step_type: currentStepSettings.step_type
    })

    if (response.success) {
      toast.success('保存成功')
      // 重新加载考试页面的步骤设置
      const examStore = useExamStore()
      await examStore.reloadStepSettings()
      // 更新本地数据
      steps.value[selectedStep.value] = {
        step_number: stepNumber,
        title: currentStepSettings.title,
        description: currentStepSettings.description,
        duration: currentStepSettings.duration,
        step_type: currentStepSettings.step_type
      }
    } else {
      toast.error(response.error || '保存失败')
    }
  } catch (error) {
    toast.error('保存失败: ' + error.message)
  }
}

// 格式化时间显示
const formatTime = (seconds) => {
  if (!seconds || seconds === 0) return '无限制'
  const minutes = Math.floor(seconds / 60)
  const secs = seconds % 60
  if (minutes > 0) {
    return `${minutes}分${secs > 0 ? secs + '秒' : ''}`
  }
  return `${secs}秒`
}

onMounted(async () => {
  await loadStepSettings()
  // 加载完成后再初始化当前步骤的编辑数据
  selectStep(0)
  // 加载底部版权信息
  await loadFooterSettings()
})

// 加载底部版权信息
const loadFooterSettings = async () => {
  try {
    const response = await api.get('/api/header-settings')
    if (response.success && response.data) {
      footerSettings.footerCopyright = response.data.footerCopyright || ''
    }
  } catch (error) {
    console.error('加载版权信息失败:', error)
  }
}
</script>

<style scoped>
.settings-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: var(--color-background);
}

/* Header */
.settings-header {
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

.settings-header h1 {
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

.settings-container {
  display: flex;
  gap: var(--spacing-5);
  max-width: 1000px;
  margin: 0 auto;
}

.sidebar {
  width: 220px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-5);
}

.steps-section,
.system-section {
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  padding: var(--spacing-5);
  box-shadow: var(--shadow-sm);
}

.steps-section h3,
.system-section h3 {
  margin: 0 0 var(--spacing-4) 0;
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-muted);
}

/* System Card */
.system-card {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-3) var(--spacing-4);
  background: var(--color-gray-50);
  border-radius: var(--radius-lg);
  cursor: pointer;
  color: var(--color-text-secondary);
  transition: background var(--transition-fast), color var(--transition-fast);
  border: 1px solid transparent;
  margin-bottom: var(--spacing-2);
}

.system-card:last-child {
  margin-bottom: 0;
}

.system-card:hover {
  background: var(--color-gray-100);
  color: var(--color-primary);
}

.system-card.active {
  background: var(--color-primary);
  color: var(--color-text-on-primary);
  border-color: var(--color-primary);
}

.system-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.system-label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
}

/* Steps List */
.steps-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.step-item {
  display: flex;
  align-items: center;
  padding: var(--spacing-3);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: border-color var(--transition-fast), background var(--transition-fast), color var(--transition-fast);
  gap: var(--spacing-3);
}

.step-item:hover {
  border-color: var(--color-primary);
  background: var(--color-primary-light);
}

.step-item.active {
  background: var(--color-primary);
  color: var(--color-text-on-primary);
  border-color: var(--color-primary);
}

.step-number {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-gray-100);
  border-radius: 50%;
  font-weight: var(--font-weight-bold);
  font-size: var(--font-size-sm);
  flex-shrink: 0;
  color: var(--color-text-secondary);
  transition: background var(--transition-fast), color var(--transition-fast);
}

.step-item.active .step-number {
  background: rgba(255,255,255,0.25);
  color: var(--color-text-on-primary);
}

.step-name {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  transition: color var(--transition-fast);
}

.step-item.active .step-name {
  color: var(--color-text-on-primary);
}

/* Content Section */
.content-section {
  flex: 1;
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  padding: var(--spacing-6);
  box-shadow: var(--shadow-sm);
}

.content-section h3 {
  margin: 0 0 var(--spacing-5) 0;
  color: var(--color-text-primary);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  padding-bottom: var(--spacing-4);
  border-bottom: 1px solid var(--color-border-light);
}

.form-group {
  margin-bottom: var(--spacing-5);
}

.form-group label {
  display: block;
  margin-bottom: var(--spacing-2);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: var(--spacing-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  box-sizing: border-box;
  background: var(--color-surface);
  color: var(--color-text-primary);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(15, 23, 42, 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.time-input-group {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
}

.time-input-group .form-input {
  width: 120px;
}

.time-display {
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
}

.form-hint {
  display: block;
  margin-top: var(--spacing-2);
  color: var(--color-text-muted);
  font-size: var(--font-size-xs);
}

/* Logo Upload */
.logo-upload {
  display: flex;
  gap: var(--spacing-3);
}

.file-input {
  display: none;
}

.file-label {
  display: inline-block;
  padding: var(--spacing-2) var(--spacing-4);
  background: var(--color-primary);
  color: var(--color-text-on-primary);
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  transition: background var(--transition-fast);
}

.file-label:hover {
  background: var(--color-primary-hover);
}

.logo-preview {
  margin-top: var(--spacing-3);
  position: relative;
  display: inline-block;
}

.logo-preview img {
  max-height: 80px;
  max-width: 200px;
  object-fit: contain;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
}

.remove-btn {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 22px;
  height: 22px;
  background: var(--color-danger);
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  font-size: 16px;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background var(--transition-fast);
}

.remove-btn:hover {
  background: var(--color-danger-hover);
}

/* Preview Section */
.preview-section {
  margin: var(--spacing-6) 0;
  padding: var(--spacing-5);
  background: var(--color-gray-50);
  border-radius: var(--radius-xl);
  border: 1px solid var(--color-border-light);
}

.preview-section h4 {
  margin: 0 0 var(--spacing-4) 0;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
}

.header-preview {
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
  padding: var(--spacing-4);
  background: var(--color-primary);
  border-radius: var(--radius-lg);
  color: var(--color-text-on-primary);
}

.preview-logos {
  display: flex;
  gap: var(--spacing-3);
}

.preview-logo {
  height: 40px;
  object-fit: contain;
  background: var(--color-surface);
  padding: var(--spacing-2);
  border-radius: var(--radius-md);
}

.preview-title {
  margin: 0;
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
}

/* Save Button */
.save-btn {
  padding: var(--spacing-3) var(--spacing-6);
  background: var(--color-success);
  color: var(--color-text-on-success);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  transition: background var(--transition-fast), transform var(--transition-fast);
}

.save-btn:hover {
  background: var(--color-success-hover);
}

.save-btn:active {
  transform: scale(0.97);
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
