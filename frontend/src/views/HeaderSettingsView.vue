<template>
  <div class="header-settings-page">
    <!-- 顶部导航 -->
    <header class="header">
      <div class="header-left">
        <h1>头部设置</h1>
      </div>
      <div class="header-right">
        <router-link to="/" class="nav-btn">返回考试</router-link>
        <router-link to="/help" class="nav-btn">帮助</router-link>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="main-content">
      <div class="settings-container">
        <div class="settings-form">
          <h3>考试系统头部设置</h3>

          <!-- 标题设置 -->
          <div class="form-group">
            <label>系统标题</label>
            <input
              v-model="settings.title"
              type="text"
              placeholder="例如：研究生复试流程控制系统"
              class="form-input"
            >
          </div>

          <!-- 学院Logo -->
          <div class="form-group">
            <label>学院Logo URL</label>
            <input
              v-model="settings.instituteLogo"
              type="text"
              placeholder="输入Logo图片URL"
              class="form-input"
            >
            <div v-if="settings.instituteLogo" class="logo-preview">
              <img :src="settings.instituteLogo" alt="学院Logo预览">
            </div>
          </div>

          <!-- 学校Logo -->
          <div class="form-group">
            <label>学校Logo URL</label>
            <input
              v-model="settings.collegeLogo"
              type="text"
              placeholder="输入学校Logo图片URL"
              class="form-input"
            >
            <div v-if="settings.collegeLogo" class="logo-preview">
              <img :src="settings.collegeLogo" alt="学校Logo预览">
            </div>
          </div>

          <!-- 预览区域 -->
          <div class="preview-section">
            <h4>预览效果</h4>
            <div class="header-preview">
              <div class="preview-logos">
                <img v-if="settings.instituteLogo" :src="settings.instituteLogo" class="preview-logo" alt="学院Logo">
                <img v-if="settings.collegeLogo" :src="settings.collegeLogo" class="preview-logo" alt="学校Logo">
              </div>
              <h2 class="preview-title">{{ settings.title || '研究生复试流程控制系统' }}</h2>
            </div>
          </div>

          <button @click="saveSettings" class="save-btn">保存设置</button>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useToastStore } from '@/stores/toast'
import api from '@/api'

const toast = useToastStore()

const settings = reactive({
  title: '',
  instituteLogo: '',
  collegeLogo: ''
})

// 加载设置
const loadSettings = async () => {
  try {
    const response = await api.get('/api/header-settings')
    if (response.success && response.data) {
      settings.title = response.data.title || ''
      settings.instituteLogo = response.data.instituteLogo || ''
      settings.collegeLogo = response.data.collegeLogo || ''
    }
  } catch (error) {
    console.error('加载设置失败:', error)
  }
}

// 保存设置
const saveSettings = async () => {
  try {
    const response = await api.put('/api/header-settings', {
      title: settings.title,
      instituteLogo: settings.instituteLogo,
      collegeLogo: settings.collegeLogo
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

onMounted(() => {
  loadSettings()
})
</script>

<style scoped>
.header-settings-page {
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

.settings-container {
  max-width: 600px;
  margin: 0 auto;
}

.settings-form {
  background: white;
  border-radius: 8px;
  padding: 30px;
}

.settings-form h3 {
  margin: 0 0 20px 0;
  color: #333;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
  color: #333;
}

.form-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.logo-preview {
  margin-top: 10px;
}

.logo-preview img {
  max-height: 60px;
  object-fit: contain;
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
</style>
