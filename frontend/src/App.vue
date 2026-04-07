<template>
  <div id="app">
    <router-view />
    <Toast />
  </div>
</template>

<script setup>
import { onMounted, watch } from 'vue'
import Toast from '@/components/Toast.vue'
import api from '@/api'
import { useRouter } from 'vue-router'

const router = useRouter()

const loadTitle = async () => {
  try {
    const res = await api.get('/api/header-settings')
    const data = res.data || res
    if (data.title) {
      document.title = data.title
    }
  } catch (e) {
    // ignore
  }
}

onMounted(() => {
  loadTitle()
})

// 路由切换时重新加载标题（用户保存新标题后返回即可生效）
router.afterEach(() => {
  loadTitle()
})
</script>

<style>
#app {
  width: 100%;
  min-height: 100vh;
}
</style>
