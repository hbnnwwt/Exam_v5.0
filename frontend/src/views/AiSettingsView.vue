<template>
  <div class="ai-settings-page">
    <!-- 顶部导航 -->
    <header class="header">
      <div class="header-left">
        <button class="back-btn" @click="$router.back()">← 返回</button>
        <h1>AI 配置</h1>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="main-content">
      <div class="settings-container">
        <!-- 提供商卡片网格 -->
        <div class="provider-grid">
          <!-- OpenAI -->
          <div class="provider-card" :class="{ active: activeProvider === 'openai' }" @click="selectProvider('openai')">
            <div class="provider-icon">🔑</div>
            <div class="provider-name">OpenAI</div>
            <div class="provider-status" :class="{ configured: isConfigured('openai') }">
              {{ isConfigured('openai') ? '已配置' : '未配置' }}
            </div>
          </div>

          <!-- Claude -->
          <div class="provider-card" :class="{ active: activeProvider === 'claude' }" @click="selectProvider('claude')">
            <div class="provider-icon">🧠</div>
            <div class="provider-name">Claude</div>
            <div class="provider-status" :class="{ configured: isConfigured('claude') }">
              {{ isConfigured('claude') ? '已配置' : '未配置' }}
            </div>
          </div>

          <!-- Gemini -->
          <div class="provider-card" :class="{ active: activeProvider === 'gemini' }" @click="selectProvider('gemini')">
            <div class="provider-icon">🌟</div>
            <div class="provider-name">Gemini</div>
            <div class="provider-status" :class="{ configured: isConfigured('gemini') }">
              {{ isConfigured('gemini') ? '已配置' : '未配置' }}
            </div>
          </div>

          <!-- 自定义添加 -->
          <div class="provider-card add-card" @click="showAddModal = true">
            <div class="provider-icon">➕</div>
            <div class="provider-name">添加自定义</div>
          </div>
        </div>

        <!-- 当前提供商配置面板 -->
        <div v-if="activeProvider && !isBuiltInProvider(activeProvider)" class="config-panel">
          <div class="panel-header">
            <h3>{{ getProviderDisplayName(activeProvider) }} 配置</h3>
            <button class="delete-btn" @click="deleteCustomProvider">删除</button>
          </div>

          <div class="settings-editor">
            <!-- API Key -->
            <div class="form-group">
              <label>API Key</label>
              <input
                v-model="providerSettings.apiKey"
                type="password"
                class="form-input"
                placeholder="请输入 API Key"
              >
            </div>

            <!-- Base URL -->
            <div class="form-group">
              <label>Base URL</label>
              <input
                v-model="providerSettings.baseUrl"
                type="text"
                class="form-input"
                placeholder="例如：https://api.openai.com/v1"
              >
            </div>

            <!-- 默认模型 -->
            <div class="form-group">
              <label>默认模型</label>
              <input
                v-model="providerSettings.defaultModel"
                type="text"
                class="form-input"
                placeholder="例如：gpt-4o"
              >
            </div>

            <button @click="saveProviderSettings" class="save-btn">保存配置</button>
          </div>
        </div>

        <!-- 预设提供商配置面板 -->
        <div v-else-if="activeProvider" class="config-panel">
          <div class="panel-header">
            <h3>{{ getProviderDisplayName(activeProvider) }} 配置</h3>
          </div>

          <div class="settings-editor">
            <!-- API Key -->
            <div class="form-group">
              <label>API Key</label>
              <input
                v-model="providerSettings.apiKey"
                type="password"
                class="form-input"
                placeholder="请输入 API Key"
              >
            </div>

            <!-- Base URL（可选） -->
            <div class="form-group">
              <label>Base URL（可选）</label>
              <input
                v-model="providerSettings.baseUrl"
                type="text"
                class="form-input"
                :placeholder="getDefaultBaseUrl(activeProvider)"
              >
            </div>

            <!-- 默认模型 -->
            <div class="form-group">
              <label>默认模型</label>
              <select v-model="providerSettings.defaultModel" class="form-select">
                <option v-for="model in getAvailableModels(activeProvider)" :key="model" :value="model">
                  {{ model }}
                </option>
              </select>
            </div>

            <!-- 测试连接 -->
            <div class="test-section">
              <button @click="testConnection" class="test-btn" :disabled="testing">
                {{ testing ? '测试中...' : '测试连接' }}
              </button>
              <span v-if="testResult" class="test-result" :class="testResult.success ? 'success' : 'error'">
                {{ testResult.message }}
              </span>
            </div>

            <button @click="saveProviderSettings" class="save-btn">保存配置</button>
          </div>
        </div>
      </div>
    </main>

    <!-- 添加自定义提供商弹窗 -->
    <div v-if="showAddModal" class="modal-overlay" @click.self="showAddModal = false">
      <div class="modal-content">
        <h3>添加自定义 AI 提供商</h3>

        <div class="form-group">
          <label>提供商名称</label>
          <input
            v-model="newProvider.name"
            type="text"
            class="form-input"
            placeholder="例如：OpenAI 兼容接口"
          >
        </div>

        <div class="form-group">
          <label>API Key</label>
          <input
            v-model="newProvider.apiKey"
            type="password"
            class="form-input"
            placeholder="请输入 API Key"
          >
        </div>

        <div class="form-group">
          <label>Base URL</label>
          <input
            v-model="newProvider.baseUrl"
            type="text"
            class="form-input"
            placeholder="例如：https://api.example.com/v1"
          >
        </div>

        <div class="form-group">
          <label>默认模型</label>
          <input
            v-model="newProvider.defaultModel"
            type="text"
            class="form-input"
            placeholder="例如：gpt-4"
          >
        </div>

        <div class="modal-actions">
          <button @click="showAddModal = false" class="cancel-btn">取消</button>
          <button @click="addCustomProvider" class="confirm-btn">添加</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useToastStore } from '@/stores/toast'
import api from '@/api'

const toast = useToastStore()

// 内置提供商列表
const builtInProviders = ['openai', 'claude', 'gemini']

// 当前选中的提供商
const activeProvider = ref(null)

// 提供商配置
const providerSettings = reactive({
  apiKey: '',
  baseUrl: '',
  defaultModel: ''
})

// 所有提供商配置（从后端加载）
const allProviders = ref({})

// 添加自定义弹窗
const showAddModal = ref(false)
const newProvider = reactive({
  name: '',
  apiKey: '',
  baseUrl: '',
  defaultModel: ''
})

// 测试连接
const testing = ref(false)
const testResult = ref(null)

// 判断是否为内置提供商
const isBuiltInProvider = (provider) => {
  return builtInProviders.includes(provider)
}

// 判断提供商是否已配置
const isConfigured = (provider) => {
  const config = allProviders.value[provider]
  return config && config.apiKey
}

// 获取提供商显示名称
const getProviderDisplayName = (provider) => {
  const names = {
    openai: 'OpenAI',
    claude: 'Claude',
    gemini: 'Gemini'
  }
  if (names[provider]) return names[provider]
  return allProviders.value[provider]?.name || provider
}

// 获取默认 Base URL
const getDefaultBaseUrl = (provider) => {
  const urls = {
    openai: 'https://api.openai.com/v1',
    claude: 'https://api.anthropic.com',
    gemini: 'https://generativelanguage.googleapis.com/v1'
  }
  return urls[provider] || ''
}

// 获取可用模型列表
const getAvailableModels = (provider) => {
  const models = {
    openai: ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-4', 'gpt-3.5-turbo'],
    claude: ['claude-sonnet-4-20250514', 'claude-sonnet-3-5-20250501', 'claude-3-opus-20240229', 'claude-3-sonnet-20240229'],
    gemini: ['gemini-2.0-flash', 'gemini-1.5-pro', 'gemini-1.5-flash']
  }
  return models[provider] || []
}

// 选择提供商
const selectProvider = (provider) => {
  activeProvider.value = provider
  const config = allProviders.value[provider] || {}
  providerSettings.apiKey = config.apiKey || ''
  providerSettings.baseUrl = config.baseUrl || getDefaultBaseUrl(provider)
  providerSettings.defaultModel = config.defaultModel || getAvailableModels(provider)[0]
  testResult.value = null
}

// 保存提供商配置
const saveProviderSettings = async () => {
  try {
    const response = await api.post('/api/ai-providers', {
      provider: activeProvider.value,
      apiKey: providerSettings.apiKey,
      baseUrl: providerSettings.baseUrl,
      defaultModel: providerSettings.defaultModel
    })

    if (response.success) {
      toast.success('保存成功')
      // 更新本地配置
      allProviders.value[activeProvider.value] = {
        ...allProviders.value[activeProvider.value],
        apiKey: providerSettings.apiKey,
        baseUrl: providerSettings.baseUrl,
        defaultModel: providerSettings.defaultModel
      }
    } else {
      toast.error(response.error || '保存失败')
    }
  } catch (error) {
    toast.error('保存失败: ' + error.message)
  }
}

// 测试连接
const testConnection = async () => {
  testing.value = true
  testResult.value = null

  try {
    const response = await api.post('/api/ai-providers/test', {
      provider: activeProvider.value,
      apiKey: providerSettings.apiKey,
      baseUrl: providerSettings.baseUrl,
      defaultModel: providerSettings.defaultModel
    })

    if (response.success) {
      testResult.value = { success: true, message: '连接成功' }
    } else {
      testResult.value = { success: false, message: response.error || '连接失败' }
    }
  } catch (error) {
    testResult.value = { success: false, message: error.message }
  } finally {
    testing.value = false
  }
}

// 添加自定义提供商
const addCustomProvider = async () => {
  if (!newProvider.name || !newProvider.apiKey || !newProvider.baseUrl) {
    toast.error('请填写完整信息')
    return
  }

  try {
    const customId = 'custom_' + Date.now()
    const response = await api.post('/api/ai-providers', {
      provider: customId,
      name: newProvider.name,
      apiKey: newProvider.apiKey,
      baseUrl: newProvider.baseUrl,
      defaultModel: newProvider.defaultModel
    })

    if (response.success) {
      toast.success('添加成功')
      // 更新本地配置
      allProviders.value[customId] = {
        name: newProvider.name,
        apiKey: newProvider.apiKey,
        baseUrl: newProvider.baseUrl,
        defaultModel: newProvider.defaultModel
      }
      // 选中新添加的提供商
      selectProvider(customId)
      // 关闭弹窗
      showAddModal.value = false
      // 重置表单
      newProvider.name = ''
      newProvider.apiKey = ''
      newProvider.baseUrl = ''
      newProvider.defaultModel = ''
    } else {
      toast.error(response.error || '添加失败')
    }
  } catch (error) {
    toast.error('添加失败: ' + error.message)
  }
}

// 删除自定义提供商
const deleteCustomProvider = async () => {
  if (!activeProvider.value || isBuiltInProvider(activeProvider.value)) {
    return
  }

  try {
    const response = await api.delete(`/api/ai-providers/${activeProvider.value}`)

    if (response.success) {
      toast.success('删除成功')
      // 从本地配置中移除
      delete allProviders.value[activeProvider.value]
      // 清除选中状态
      activeProvider.value = null
    } else {
      toast.error(response.error || '删除失败')
    }
  } catch (error) {
    toast.error('删除失败: ' + error.message)
  }
}

// 加载所有提供商配置
const loadProviders = async () => {
  try {
    const response = await api.get('/api/ai-providers')
    if (response.success && response.data) {
      allProviders.value = response.data
      // 默认选中第一个已配置的提供商或第一个内置提供商
      const firstConfigured = Object.keys(allProviders.value).find(p => isConfigured(p))
      if (firstConfigured) {
        selectProvider(firstConfigured)
      } else if (builtInProviders.length > 0) {
        selectProvider(builtInProviders[0])
      }
    }
  } catch (error) {
    console.error('加载AI配置失败:', error)
    // 默认选中 OpenAI
    selectProvider('openai')
  }
}

onMounted(() => {
  loadProviders()
})
</script>

<style scoped>
.ai-settings-page {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: var(--color-background);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: var(--color-primary);
  color: var(--color-text-on-primary);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.back-btn {
  padding: 8px 16px;
  background: rgba(255,255,255,0.2);
  color: white;
  border: none;
  border-radius: var(--radius-base);
  cursor: pointer;
  font-size: 14px;
}

.back-btn:hover {
  background: rgba(255,255,255,0.3);
}

.header h1 {
  margin: 0;
  font-size: 20px;
}

.main-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.settings-container {
  max-width: 800px;
  margin: 0 auto;
}

/* 提供商卡片网格 */
.provider-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
  margin-bottom: 30px;
}

.provider-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 16px;
  background: var(--color-surface);
  border: 2px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-base);
}

.provider-card:hover {
  border-color: var(--color-primary);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.provider-card.active {
  border-color: var(--color-primary);
  background: var(--color-primary-light);
}

.provider-card.add-card {
  border-style: dashed;
}

.provider-card.add-card:hover {
  border-color: var(--color-accent);
}

.provider-icon {
  font-size: 32px;
  margin-bottom: 12px;
}

.provider-name {
  font-size: 16px;
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin-bottom: 8px;
}

.provider-status {
  font-size: 12px;
  color: var(--color-text-muted);
  padding: 4px 12px;
  background: var(--color-gray-100);
  border-radius: var(--radius-full);
}

.provider-status.configured {
  background: var(--color-success-light);
  color: var(--color-success);
}

/* 配置面板 */
.config-panel {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: var(--shadow-base);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--color-border-light);
}

.panel-header h3 {
  margin: 0;
  font-size: 18px;
  color: var(--color-text-primary);
}

.delete-btn {
  padding: 6px 16px;
  background: var(--color-danger-light);
  color: var(--color-danger);
  border: none;
  border-radius: var(--radius-base);
  cursor: pointer;
  font-size: 14px;
}

.delete-btn:hover {
  background: var(--color-danger);
  color: white;
}

.settings-editor {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
}

.form-input,
.form-select {
  padding: 12px 16px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-base);
  font-size: 14px;
  background: var(--color-surface);
  color: var(--color-text-primary);
  transition: border-color var(--transition-fast);
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: var(--color-primary);
}

.test-section {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 0;
}

.test-btn {
  padding: 10px 20px;
  background: var(--color-gray-100);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-base);
  cursor: pointer;
  font-size: 14px;
}

.test-btn:hover:not(:disabled) {
  background: var(--color-gray-200);
}

.test-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.test-result {
  font-size: 14px;
}

.test-result.success {
  color: var(--color-success);
}

.test-result.error {
  color: var(--color-danger);
}

.save-btn {
  padding: 12px 24px;
  background: var(--color-success);
  color: white;
  border: none;
  border-radius: var(--radius-base);
  cursor: pointer;
  font-size: 14px;
  font-weight: var(--font-weight-medium);
}

.save-btn:hover {
  background: var(--color-success-hover);
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal);
}

.modal-content {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: 24px;
  width: 90%;
  max-width: 480px;
  box-shadow: var(--shadow-xl);
}

.modal-content h3 {
  margin: 0 0 20px 0;
  font-size: 18px;
  color: var(--color-text-primary);
}

.modal-content .form-group {
  margin-bottom: 16px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.cancel-btn {
  padding: 10px 20px;
  background: var(--color-gray-100);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-base);
  cursor: pointer;
  font-size: 14px;
}

.cancel-btn:hover {
  background: var(--color-gray-200);
}

.confirm-btn {
  padding: 10px 20px;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-base);
  cursor: pointer;
  font-size: 14px;
}

.confirm-btn:hover {
  background: var(--color-primary-hover);
}
</style>