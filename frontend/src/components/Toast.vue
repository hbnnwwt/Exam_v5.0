<template>
  <div class="toast-container" role="status" aria-live="polite">
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
  box-shadow: var(--shadow-lg);
  transition: transform 0.3s ease, opacity 0.3s ease;
  min-width: 200px;
}

.toast:hover {
  transform: translateX(-5px);
}

.toast-success {
  background: var(--color-success);
  color: var(--color-text-on-success);
}

.toast-error {
  background: var(--color-danger);
  color: var(--color-text-on-danger);
}

.toast-warning {
  background: var(--color-warning);
  color: var(--color-text-on-warning);
}

.toast-info {
  background: var(--color-info);
  color: white;
}

.toast-enter-active,
.toast-leave-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
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
