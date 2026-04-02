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
        <section class="provider-section">
          <h2 class="section-title">选择 AI Provider</h2>
          <div class="provider-grid">
            <!-- OpenAI -->
            <button type="button" class="provider-card" :class="{ active: activeProvider === 'openai', configured: isConfigured('openai') }" @click="selectProvider('openai')" :aria-pressed="activeProvider === 'openai'">
              <span class="provider-icon">OpenAI</span>
              <span class="provider-name">OpenAI</span>
              <span class="provider-model">{{ getProviderModel('openai') }}</span>
              <span class="provider-badge" :class="isConfigured('openai') ? 'badge-success' : 'badge-muted'">
                {{ isConfigured('openai') ? '已配置' : '未配置' }}
              </span>
            </button>

            <!-- Claude -->
            <button type="button" class="provider-card" :class="{ active: activeProvider === 'claude', configured: isConfigured('claude') }" @click="selectProvider('claude')" :aria-pressed="activeProvider === 'claude'">
              <span class="provider-icon">Claude</span>
              <span class="provider-name">Claude</span>
              <span class="provider-model">{{ getProviderModel('claude') }}</span>
              <span class="provider-badge" :class="isConfigured('claude') ? 'badge-success' : 'badge-muted'">
                {{ isConfigured('claude') ? '已配置' : '未配置' }}
              </span>
            </button>

            <!-- Gemini -->
            <button type="button" class="provider-card" :class="{ active: activeProvider === 'gemini', configured: isConfigured('gemini') }" @click="selectProvider('gemini')" :aria-pressed="activeProvider === 'gemini'">
              <span class="provider-icon">Gemini</span>
              <span class="provider-name">Gemini</span>
              <span class="provider-model">{{ getProviderModel('gemini') }}</span>
              <span class="provider-badge" :class="isConfigured('gemini') ? 'badge-success' : 'badge-muted'">
                {{ isConfigured('gemini') ? '已配置' : '未配置' }}
              </span>
            </button>

            <!-- MiniMax -->
            <button type="button" class="provider-card" :class="{ active: activeProvider === 'minimax', configured: isConfigured('minimax') }" @click="selectProvider('minimax')" :aria-pressed="activeProvider === 'minimax'">
              <span class="provider-icon">MiniMax</span>
              <span class="provider-name">MiniMax</span>
              <span class="provider-model">{{ getProviderModel('minimax') }}</span>
              <span class="provider-badge" :class="isConfigured('minimax') ? 'badge-success' : 'badge-muted'">
                {{ isConfigured('minimax') ? '已配置' : '未配置' }}
              </span>
            </button>

            <!-- ModelScope -->
            <button type="button" class="provider-card" :class="{ active: activeProvider === 'modelscope', configured: isConfigured('modelscope') }" @click="selectProvider('modelscope')" :aria-pressed="activeProvider === 'modelscope'">
              <span class="provider-icon">ModelScope</span>
              <span class="provider-name">ModelScope</span>
              <span class="provider-model">{{ getProviderModel('modelscope') }}</span>
              <span class="provider-badge" :class="isConfigured('modelscope') ? 'badge-success' : 'badge-muted'">
                {{ isConfigured('modelscope') ? '已配置' : '未配置' }}
              </span>
            </button>

            <!-- 自定义 Provider -->
            <button
              v-for="providerId in customProviderIds"
              :key="providerId"
              type="button"
              class="provider-card"
              :class="{ active: activeProvider === providerId, configured: isConfigured(providerId) }"
              @click="selectProvider(providerId)"
              :aria-pressed="activeProvider === providerId"
            >
              <span class="provider-icon">{{ allProviders[providerId]?.name?.substring(0, 2) || 'AI' }}</span>
              <span class="provider-name">{{ allProviders[providerId]?.name || '自定义' }}</span>
              <span class="provider-model">{{ getProviderModel(providerId) }}</span>
              <span class="provider-badge" :class="isConfigured(providerId) ? 'badge-success' : 'badge-muted'">
                {{ isConfigured(providerId) ? '已配置' : '未配置' }}
              </span>
            </button>

            <!-- 自定义添加 -->
            <button type="button" class="provider-card add-card" @click="showAddModal = true">
              <span class="provider-icon">+</span>
              <span class="provider-name">添加自定义</span>
              <span class="provider-model">自定义端点</span>
              <span class="provider-badge badge-add">添加</span>
            </button>
          </div>
        </section>

        <!-- 提供商配置面板 -->
        <section v-if="activeProvider" class="config-section">
          <div class="config-panel">
            <div class="panel-header">
              <h2 class="panel-title">
                <span class="provider-dot" :class="isConfigured(activeProvider) ? 'dot-success' : 'dot-muted'"></span>
                {{ getProviderDisplayName(activeProvider) }} 配置
              </h2>
              <div class="panel-actions">
                <label class="default-toggle" v-if="isConfigured(activeProvider)">
                  <input type="checkbox" :checked="defaultProvider === activeProvider" @change="toggleDefault(activeProvider)" />
                  <span>设为默认</span>
                </label>
                <button v-if="!isBuiltInProvider(activeProvider)" class="delete-btn" @click="deleteCustomProvider">删除</button>
              </div>
            </div>

            <div class="settings-editor">
              <!-- 必需：API Key -->
              <div class="form-group form-group-required">
                <label for="apiKey">API Key <span class="required-mark">*</span></label>
                <div class="input-with-toggle">
                  <input
                    id="apiKey"
                    v-model="providerSettings.apiKey"
                    :type="showApiKey ? 'text' : 'password'"
                    class="form-input"
                    placeholder="请输入 API Key"
                    autocomplete="off"
                  >
                  <button
                    type="button"
                    class="toggle-visibility-btn"
                    @click="showApiKey = !showApiKey"
                    :title="showApiKey ? '隐藏' : '显示'"
                  >
                    <svg v-if="showApiKey" class="toggle-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                      <circle cx="12" cy="12" r="3"/>
                    </svg>
                    <svg v-else class="toggle-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                      <line x1="1" y1="1" x2="23" y2="23"/>
                    </svg>
                  </button>
                </div>
              </div>

              <!-- 可选：Base URL -->
              <details class="form-details">
                <summary class="form-details-summary">
                  <span>高级选项</span>
                  <svg class="details-arrow" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"/></svg>
                </summary>
                <div class="form-details-content">
                  <div class="form-group">
                    <label for="baseUrl">Base URL</label>
                    <input
                      id="baseUrl"
                      v-model="providerSettings.baseUrl"
                      type="text"
                      class="form-input"
                      :placeholder="getDefaultBaseUrl(activeProvider) || '例如：https://api.openai.com/v1'"
                    >
                  </div>
                  <div class="form-group">
                    <label for="model">模型</label>
                    <input
                      id="model"
                      v-model="providerSettings.defaultModel"
                      type="text"
                      class="form-input"
                      :placeholder="getAvailableModels(activeProvider)[0] || '例如：gpt-4o'"
                      list="modelList"
                    >
                    <datalist id="modelList">
                      <option v-for="m in getAvailableModels(activeProvider)" :key="m" :value="m" />
                    </datalist>
                  </div>
                </div>
              </details>

              <!-- 测试连接（仅内置提供商） -->
              <div class="test-section" v-if="isBuiltInProvider(activeProvider)">
                <button @click="testConnection" class="test-btn" :disabled="testing">
                  <span v-if="testing" class="spinner"></span>
                  {{ testing ? '测试中...' : '测试连接' }}
                </button>
                <span v-if="testResult" class="test-result" :class="testResult.success ? 'success' : 'error'">
                  {{ testResult.message }}
                </span>
              </div>

              <button @click="saveProviderSettings" class="save-btn">保存配置</button>
            </div>
          </div>
        </section>
      </div>
    </main>

    <!-- 添加自定义提供商弹窗 -->
    <div v-if="showAddModal" class="modal-overlay" @click.self="showAddModal = false">
      <div class="modal-content">
        <h3>添加自定义 AI 提供商</h3>

        <div class="form-group">
          <label for="modalProviderName">提供商名称</label>
          <input
            id="modalProviderName"
            v-model="newProvider.name"
            type="text"
            class="form-input"
            placeholder="例如：公司内部AI服务"
          >
        </div>

        <div class="form-group">
          <label for="modalApiKey">API Key</label>
          <div class="input-with-toggle">
            <input
              id="modalApiKey"
              v-model="newProvider.apiKey"
              :type="showNewProviderApiKey ? 'text' : 'password'"
              class="form-input"
              placeholder="请输入 API Key"
            >
            <button
              type="button"
              class="toggle-visibility-btn"
              @click="showNewProviderApiKey = !showNewProviderApiKey"
              :title="showNewProviderApiKey ? '隐藏' : '显示'"
            >
              <svg v-if="showNewProviderApiKey" class="toggle-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
              <svg v-else class="toggle-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                <line x1="1" y1="1" x2="23" y2="23"/>
              </svg>
            </button>
          </div>
        </div>

        <div class="form-group">
          <label for="modalBaseUrl">Base URL</label>
          <input
            id="modalBaseUrl"
            v-model="newProvider.baseUrl"
            type="text"
            class="form-input"
            placeholder="例如：https://api.example.com/v1"
          >
        </div>

        <div class="form-group">
          <label for="modalModel">模型</label>
          <input
            id="modalModel"
            v-model="newProvider.defaultModel"
            type="text"
            class="form-input"
            placeholder="例如：gpt-4"
          >
        </div>

        <div class="form-group">
          <label for="modalApiFormat">API 格式</label>
          <select
            id="modalApiFormat"
            v-model="newProvider.apiFormat"
            class="form-select"
          >
            <option value="openai">OpenAI 兼容 (chat/completions)</option>
            <option value="anthropic">Anthropic Messages (/v1/messages)</option>
          </select>
          <small class="form-hint">选择与您 Base URL 匹配的 API 格式</small>
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
import { ref, reactive, onMounted, computed } from 'vue'
import { useToastStore } from '@/stores/toast'
import api from '@/api'
import { getDefaultProvider, setDefaultProvider } from '@/api/ai'

const toast = useToastStore()

// 默认 Provider
const defaultProvider = ref('')

// 内置提供商列表
const builtInProviders = ['openai', 'claude', 'gemini', 'minimax', 'modelscope']

// 自定义提供商列表
const customProviderIds = computed(() => {
  return Object.keys(allProviders.value).filter(id => !builtInProviders.includes(id))
})

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
  defaultModel: '',
  apiFormat: 'openai'
})

// 测试连接
const testing = ref(false)
const testResult = ref(null)

// API Key 显示/隐藏
const showApiKey = ref(false)
const showNewProviderApiKey = ref(false)

// 判断是否为内置提供商
const isBuiltInProvider = (provider) => {
  return builtInProviders.includes(provider)
}

// 判断提供商是否已配置
const isConfigured = (provider) => {
  const config = allProviders.value[provider]
  return config && config.apiKey
}

// 获取提供商当前配置的模型（用于卡片显示）
const getProviderModel = (provider) => {
  const config = allProviders.value[provider]
  if (config && config.defaultModel) return config.defaultModel
  const models = {
    openai: 'gpt-4o',
    claude: 'claude-sonnet-4',
    gemini: 'gemini-2.0-flash',
    minimax: 'MiniMax-M2.5',
    modelscope: 'qwen3.5-397b'
  }
  return models[provider] || ''
}

// 设为默认 Provider
const toggleDefault = async (providerId) => {
  const newDefault = defaultProvider.value === providerId ? '' : providerId
  try {
    const response = await setDefaultProvider(newDefault)
    if (response.success) {
      defaultProvider.value = newDefault
      toast.success(newDefault ? '已设为默认' : '已取消默认')
    }
  } catch (error) {
    toast.error('设置失败')
  }
}

// 获取提供商显示名称
const getProviderDisplayName = (provider) => {
  const names = {
    openai: 'OpenAI',
    claude: 'Claude',
    gemini: 'Gemini',
    minimax: 'MiniMax',
    modelscope: 'ModelScope'
  }
  if (names[provider]) return names[provider]
  return allProviders.value[provider]?.name || provider
}

// 获取默认 Base URL
const getDefaultBaseUrl = (provider) => {
  const urls = {
    openai: 'https://api.openai.com/v1',
    claude: 'https://api.anthropic.com',
    gemini: 'https://generativelanguage.googleapis.com/v1',
    minimax: 'https://api.minimaxi.com/anthropic',
    modelscope: 'https://api-inference.modelscope.cn'
  }
  return urls[provider] || ''
}

// 获取可用模型列表
const getAvailableModels = (provider) => {
  const models = {
    openai: ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-4', 'gpt-3.5-turbo'],
    claude: ['claude-sonnet-4-20250514', 'claude-sonnet-3-5-20250501', 'claude-3-opus-20240229', 'claude-3-sonnet-20240229'],
    gemini: ['gemini-2.0-flash', 'gemini-1.5-pro', 'gemini-1.5-flash'],
    minimax: ['MiniMax-M2.5', 'abab6.5s-chat', 'abab6.5g-chat'],
    modelscope: ['qwen3.5-397b', 'qwen-turbo', 'qwen-plus', 'qwen-max']
  }
  return models[provider] || []
}

// 已配置的 Provider 列表（用于默认选择，只要有 apiKey 即可）
const enabledProvidersList = computed(() => {
  return Object.values(allProviders.value).filter(p => p.apiKey)
})

// 保存默认 Provider
const saveDefaultProvider = async () => {
  try {
    const response = await setDefaultProvider(defaultProvider.value)
    if (response.success) {
      toast.success('默认 Provider 已更新')
    } else {
      toast.error(response.error || '更新失败')
    }
  } catch (error) {
    toast.error('更新失败: ' + error.message)
  }
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
    const response = await api.post('/api/ai/providers', {
      provider: activeProvider.value,
      apiKey: providerSettings.apiKey,
      baseUrl: providerSettings.baseUrl,
      defaultModel: providerSettings.defaultModel,
      enabled: true
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
    const response = await api.post('/api/ai/test', {
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
    const response = await api.post('/api/ai/providers', {
      provider: customId,
      name: newProvider.name,
      apiKey: newProvider.apiKey,
      baseUrl: newProvider.baseUrl,
      defaultModel: newProvider.defaultModel,
      apiFormat: newProvider.apiFormat
    })

    if (response.success) {
      toast.success('添加成功')
      // 关闭弹窗
      showAddModal.value = false
      // 重置表单
      newProvider.name = ''
      newProvider.apiKey = ''
      newProvider.baseUrl = ''
      newProvider.defaultModel = ''
      newProvider.apiFormat = 'openai'
      // 重新加载列表
      await loadProviders()
      // 选中新添加的提供商
      selectProvider(customId)
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
    const response = await api.delete(`/api/ai/providers/${activeProvider.value}`)

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
    // 加载所有 providers
    const response = await api.get('/api/ai/providers')
    // GET /api/ai/providers 返回数组，POST 返回 {success: true}
    if (Array.isArray(response)) {
      // 转换为对象形式存储，key 为 provider id
      const providersObj = {}
      response.forEach(p => {
        providersObj[p.id] = p
      })
      allProviders.value = providersObj
      // 默认选中第一个已配置的提供商或第一个内置提供商
      const firstConfigured = Object.keys(allProviders.value).find(p => isConfigured(p))
      if (firstConfigured) {
        selectProvider(firstConfigured)
      } else if (builtInProviders.length > 0) {
        selectProvider(builtInProviders[0])
      }
    }

    // 加载默认 provider
    const defaultResponse = await getDefaultProvider()
    if (defaultResponse && defaultResponse.id) {
      defaultProvider.value = defaultResponse.id
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
  background: var(--color-header-btn-bg);
  color: white;
  border: none;
  border-radius: var(--radius-base);
  cursor: pointer;
  font-size: 14px;
  transition: background var(--transition-fast);
}

.back-btn:hover {
  background: var(--color-header-btn-hover);
}

.back-btn:focus-visible,
.save-btn:focus-visible,
.test-btn:focus-visible,
.delete-btn:focus-visible,
.confirm-btn:focus-visible,
.cancel-btn:focus-visible,
.provider-card:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

.header h1 {
  margin: 0;
  font-size: 20px;
}

.main-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

.settings-container {
  max-width: 900px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Section titles */
.section-title {
  font-size: 13px;
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0 0 12px 0;
}

/* Provider grid */
.provider-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 12px;
}

.provider-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 16px;
  background: var(--color-surface);
  border: 2px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-base);
  font-family: inherit;
  text-align: left;
  position: relative;
}

.provider-card:hover {
  border-color: var(--color-primary);
  box-shadow: var(--shadow-sm);
}

.provider-card.active {
  border-color: var(--color-primary);
  background: var(--color-primary-light);
}

.provider-card.configured .provider-icon {
  color: var(--color-success);
}

.provider-card.add-card {
  border-style: dashed;
  align-items: center;
  justify-content: center;
  min-height: 88px;
}

.provider-card.add-card .provider-icon {
  font-size: 20px;
  color: var(--color-text-muted);
  margin-bottom: 4px;
}

.provider-icon {
  font-size: 11px;
  font-weight: var(--font-weight-bold);
  color: var(--color-text-muted);
  letter-spacing: 0.5px;
  text-transform: uppercase;
  margin-bottom: 4px;
}

.provider-name {
  font-size: 15px;
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin-bottom: 2px;
}

.provider-model {
  font-size: 11px;
  color: var(--color-text-muted);
  margin-bottom: 8px;
  font-family: var(--font-family-mono);
}

.provider-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: var(--radius-full);
  font-weight: var(--font-weight-medium);
}

.badge-success {
  background: var(--color-success-light);
  color: var(--color-success);
}

.badge-muted {
  background: var(--color-gray-100);
  color: var(--color-text-muted);
}

.badge-add {
  background: var(--color-primary-light);
  color: var(--color-primary);
}

/* Config section */
.config-section {
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.config-panel {
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  padding: 28px;
  box-shadow: var(--shadow-base);
  border: 1px solid var(--color-border-light);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--color-border-light);
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0;
  font-size: 17px;
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.provider-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.dot-success {
  background: var(--color-success);
}

.dot-muted {
  background: var(--color-gray-300);
}

.panel-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.default-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--color-text-secondary);
  cursor: pointer;
  user-select: none;
}

.default-toggle input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: var(--color-primary);
}

.delete-btn {
  padding: 6px 16px;
  background: var(--color-danger-light);
  color: var(--color-danger);
  border: none;
  border-radius: var(--radius-base);
  cursor: pointer;
  font-size: 13px;
  transition: all var(--transition-fast);
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
  gap: 6px;
}

.form-group label {
  font-size: 13px;
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
}

.form-group-required label {
  color: var(--color-text-primary);
}

.required-mark {
  color: var(--color-danger);
  margin-left: 2px;
}

.form-input {
  padding: 10px 14px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-base);
  font-size: 14px;
  background: var(--color-surface);
  color: var(--color-text-primary);
  transition: border-color var(--transition-fast);
  width: 100%;
}

.form-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(15, 23, 42, 0.08);
}

.form-select {
  padding: 10px 14px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-base);
  font-size: 14px;
  background: var(--color-surface);
  color: var(--color-text-primary);
  transition: border-color var(--transition-fast);
  width: 100%;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23666' d='M6 8L1 3h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  padding-right: 36px;
}

.form-select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(15, 23, 42, 0.08);
}

/* Input with toggle button */
.input-with-toggle {
  position: relative;
  display: flex;
  align-items: center;
}

.input-with-toggle .form-input {
  flex: 1;
  padding-right: 44px;
}

.toggle-visibility-btn {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  color: var(--color-text-muted);
  transition: all 0.2s ease;
}

.toggle-visibility-btn:hover {
  background: var(--color-gray-100);
  color: var(--color-text-primary);
}

.toggle-icon {
  width: 18px;
  height: 18px;
}

/* Advanced options details */
.form-details {
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-base);
  overflow: hidden;
}

.form-details-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  font-size: 13px;
  color: var(--color-text-secondary);
  cursor: pointer;
  background: var(--color-gray-50);
  user-select: none;
  list-style: none;
}

.form-details-summary::-webkit-details-marker {
  display: none;
}

.form-details-summary:hover {
  background: var(--color-gray-100);
}

.details-arrow {
  width: 16px;
  height: 16px;
  transition: transform var(--transition-fast);
}

details[open] .details-arrow {
  transform: rotate(180deg);
}

.form-details-content {
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  border-top: 1px solid var(--color-border-light);
}

/* Test section */
.test-section {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 8px 0;
}

.test-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--color-surface);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-base);
  cursor: pointer;
  font-size: 13px;
  transition: all var(--transition-fast);
}

.test-btn:hover:not(:disabled) {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.test-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.test-result {
  font-size: 13px;
}

.test-result.success { color: var(--color-success); }
.test-result.error { color: var(--color-danger); }

/* Save button */
.save-btn {
  padding: 10px 24px;
  background: var(--color-success);
  color: white;
  border: none;
  border-radius: var(--radius-base);
  cursor: pointer;
  font-size: 14px;
  font-weight: var(--font-weight-medium);
  transition: background var(--transition-fast);
  align-self: flex-start;
}

.save-btn:hover:not(:disabled) {
  background: var(--color-success-hover);
}

.save-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--color-modal-overlay);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal);
  animation: fadeOverlay 0.15s ease;
}

@keyframes fadeOverlay {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  padding: 28px;
  width: 90%;
  max-width: 440px;
  box-shadow: var(--shadow-xl);
  animation: slideUp 0.2s ease;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}

.modal-content h3 {
  margin: 0 0 20px 0;
  font-size: 17px;
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.modal-content .form-group {
  margin-bottom: 14px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.cancel-btn,
.confirm-btn {
  padding: 8px 18px;
  border-radius: var(--radius-base);
  cursor: pointer;
  font-size: 13px;
  font-weight: var(--font-weight-medium);
  transition: all var(--transition-fast);
  border: none;
}

.cancel-btn {
  background: var(--color-gray-100);
  color: var(--color-text-primary);
}

.cancel-btn:hover:not(:disabled) {
  background: var(--color-gray-200);
}

.confirm-btn {
  background: var(--color-primary);
  color: white;
}

.confirm-btn:hover:not(:disabled) {
  background: var(--color-primary-hover);
}

.cancel-btn:focus-visible,
.confirm-btn:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}
</style>