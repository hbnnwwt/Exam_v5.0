<template>
  <div class="settings-page">
    <!-- 顶部导航 -->
    <header class="header">
      <div class="header-left">
        <h1>考试设置</h1>
      </div>
      <div class="header-right">
        <router-link to="/" class="nav-btn">返回考试</router-link>
        <router-link to="/help" class="nav-btn">帮助</router-link>
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
              <span class="system-icon">🎨</span>
              <span class="system-label">Logo设置</span>
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

.main-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.settings-container {
  display: flex;
  gap: 20px;
  max-width: 1000px;
  margin: 0 auto;
}

.sidebar {
  width: 220px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.system-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
}

.system-section h3 {
  margin: 0 0 15px 0;
  color: #333;
}

.system-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 15px;
  background: #f8f9fa;
  border-radius: 6px;
  cursor: pointer;
  color: #333;
  transition: all 0.2s;
}

.system-card:hover {
  background: #e9ecef;
  color: #007bff;
}

.system-card.active {
  background: #007bff;
  color: white;
}

.system-icon {
  font-size: 18px;
}

.system-label {
  font-size: 14px;
}

.steps-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
}

.steps-section h3 {
  margin: 0 0 15px 0;
  color: #333;
}

.steps-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.step-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.step-item:hover {
  border-color: #007bff;
}

.step-item.active {
  background: #007bff;
  color: white;
  border-color: #007bff;
}

.step-number {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #e9ecef;
  border-radius: 50%;
  font-weight: bold;
  margin-right: 10px;
}

.step-item.active .step-number {
  background: rgba(255,255,255,0.3);
}

.step-name {
  font-size: 14px;
}

.content-section {
  flex: 1;
  background: white;
  border-radius: 8px;
  padding: 20px;
}

.content-section h3 {
  margin: 0 0 20px 0;
  color: #333;
}

.form-group {
  margin-bottom: 20px;
}

/* Logo设置相关样式 */
.logo-upload {
  display: flex;
  gap: 10px;
}

.file-input {
  display: none;
}

.file-label {
  display: inline-block;
  padding: 8px 16px;
  background: #007bff;
  color: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.file-label:hover {
  background: #0056b3;
}

.logo-preview {
  margin-top: 10px;
  position: relative;
  display: inline-block;
}

.logo-preview img {
  max-height: 80px;
  max-width: 200px;
  object-fit: contain;
  border: 1px solid #dee2e6;
  border-radius: 4px;
}

.remove-btn {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 20px;
  height: 20px;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  font-size: 14px;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.remove-btn:hover {
  background: #c82333;
}

.preview-section {
  margin: 30px 0;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.preview-section h4 {
  margin: 0 0 15px 0;
  color: #666;
}

.header-preview {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: #007bff;
  border-radius: 4px;
  color: white;
}

.preview-logos {
  display: flex;
  gap: 10px;
}

.preview-logo {
  height: 40px;
  object-fit: contain;
  background: white;
  padding: 5px;
  border-radius: 4px;
}

.preview-title {
  margin: 0;
  font-size: 18px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
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

.time-input-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.time-input-group .form-input {
  width: 120px;
}

.time-display {
  color: #666;
  font-size: 14px;
}

.form-hint {
  display: block;
  margin-top: 5px;
  color: #999;
  font-size: 12px;
}

.save-btn {
  padding: 12px 30px;
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
