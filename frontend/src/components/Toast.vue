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
  top: var(--spacing-5);
  right: var(--spacing-5);
  z-index: var(--z-toast);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.toast {
  padding: var(--spacing-3) var(--spacing-5);
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  cursor: pointer;
  box-shadow: var(--shadow-lg);
  transition: var(--transition-all);
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
  color: var(--color-white);
}

.toast-enter-active,
.toast-leave-active {
  transition: var(--transition-all);
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
