<template>
  <div class="toast-container">
    <TransitionGroup name="toast">
      <div
        v-for="msg in toastStore.messages"
        :key="msg.id"
        :class="['toast', `toast-${msg.type}`]"
        @click="toastStore.remove(msg.id)"
      >
        <span class="toast-icon">{{ iconMap[msg.type] }}</span>
        <span class="toast-message">{{ msg.message }}</span>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup>
import { useToastStore } from '@/stores/toast'

const toastStore = useToastStore()

const iconMap = {
  success: '✓',
  error: '✗',
  warning: '⚠',
  info: 'ℹ'
}
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.toast {
  padding: 12px 20px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
  min-width: 200px;
}

.toast:hover {
  transform: translateX(-5px);
}

.toast-success {
  background: #28a745;
  color: white;
}

.toast-error {
  background: #dc3545;
  color: white;
}

.toast-warning {
  background: #ffc107;
  color: #333;
}

.toast-info {
  background: #17a2b8;
  color: white;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}
</style>
