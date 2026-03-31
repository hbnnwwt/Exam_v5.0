<template>
  <div class="timer" :class="{ 'timer-warning': isWarning, 'timer-danger': isDanger }" role="timer" aria-live="polite">
    <div class="timer-display">
      <span class="timer-icon" aria-hidden="true">⏱</span>
      <span class="timer-time" aria-label="剩余时间">{{ examStore.formattedTime }}</span>
    </div>
    <div class="timer-controls">
      <button
        v-if="!examStore.timer.isRunning"
        class="timer-btn start"
        @click="start"
        :disabled="examStore.timer.remainingTime === 0"
        aria-label="开始计时"
        type="button"
      >
        <span aria-hidden="true">▶</span> 开始
      </button>
      <button
        v-else
        class="timer-btn pause"
        @click="pause"
        aria-label="暂停计时"
        type="button"
      >
        <span aria-hidden="true">⏸</span> 暂停
      </button>
      <button
        class="timer-btn reset"
        @click="reset"
        aria-label="重置计时器"
        type="button"
      >
        <span aria-hidden="true">↺</span> 重置
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted, watch } from 'vue'
import { useExamStore } from '@/stores/exam'

const examStore = useExamStore()
const intervalId = ref(null)

const isWarning = computed(() => {
  return examStore.timer.remainingTime <= 60 && examStore.timer.remainingTime > 30
})

const isDanger = computed(() => {
  return examStore.timer.remainingTime <= 30 && examStore.timer.remainingTime > 0
})

const start = () => {
  if (examStore.timer.remainingTime === 0) {
    examStore.startStepTimer()
  }
  examStore.resumeTimer()
  startInterval()
}

const pause = () => {
  examStore.pauseTimer()
  stopInterval()
}

const reset = () => {
  stopInterval()
  examStore.startStepTimer()
}

const startInterval = () => {
  stopInterval()
  intervalId.value = setInterval(() => {
    if (examStore.timer.isRunning) {
      examStore.decrementTimer()
    }
  }, 1000)
}

const stopInterval = () => {
  if (intervalId.value) {
    clearInterval(intervalId.value)
    intervalId.value = null
  }
}

// 监听计时器状态变化
watch(() => examStore.timer.isRunning, (newVal) => {
  if (newVal && !intervalId.value) {
    startInterval()
  }
})

onUnmounted(() => {
  stopInterval()
})
</script>

<style scoped>
.timer {
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  padding: var(--spacing-3) var(--spacing-5);
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: var(--shadow-md);
  min-width: 280px;
}

.timer-warning {
  background: var(--color-warning-light);
  border: 2px solid var(--color-warning);
}

.timer-danger {
  background: var(--color-danger-light);
  border: 2px solid var(--color-danger);
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.timer-display {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.timer-icon {
  font-size: var(--font-size-2xl);
}

.timer-time {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  font-family: var(--font-family-mono);
}

.timer-controls {
  display: flex;
  gap: var(--spacing-2);
}

.timer-btn {
  padding: var(--spacing-2) var(--spacing-4);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: var(--font-size-sm);
  transition: var(--transition-all);
  min-height: var(--touch-target-min);
}

.timer-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.timer-btn.start {
  background: var(--color-success);
  color: var(--color-text-on-success);
}

.timer-btn.start:hover:not(:disabled) {
  background: var(--color-success-hover);
}

.timer-btn.pause {
  background: var(--color-warning);
  color: var(--color-text-on-warning);
}

.timer-btn.pause:hover:not(:disabled) {
  background: var(--color-warning-hover);
}

.timer-btn.reset {
  background: var(--color-gray-600);
  color: var(--color-white);
}

.timer-btn.reset:hover:not(:disabled) {
  background: var(--color-gray-700);
}

.timer-btn:hover:not(:disabled) {
  transform: scale(1.02);
}
</style>
