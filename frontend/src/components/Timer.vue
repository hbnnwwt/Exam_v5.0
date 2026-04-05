<template>
  <div class="timer" :class="{ 'timer-warning': isWarning, 'timer-danger': isDanger }">
    <div class="timer-display">
      <span class="timer-icon">⏱</span>
      <span class="timer-time">{{ examStore.formattedTime }}</span>
    </div>
    <div class="timer-controls">
      <button
        v-if="!examStore.timer.isRunning"
        class="timer-btn start"
        @click="start"
        :disabled="examStore.timer.remainingTime === 0"
      >
        ▶ 开始
      </button>
      <button
        v-else
        class="timer-btn pause"
        @click="pause"
      >
        ⏸ 暂停
      </button>
      <button class="timer-btn reset" @click="reset">
        ↺ 重置
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

defineExpose({ start, pause, reset })
</script>

<style scoped>
.timer {
  background: #fff;
  border-radius: 12px;
  padding: 15px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  min-width: 280px;
}

.timer-warning {
  background: #fff3cd;
  border: 2px solid #ffc107;
}

.timer-danger {
  background: #f8d7da;
  border: 2px solid #dc3545;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.timer-display {
  display: flex;
  align-items: center;
  gap: 10px;
}

.timer-icon {
  font-size: 24px;
}

.timer-time {
  font-size: 28px;
  font-weight: bold;
  font-family: monospace;
}

.timer-controls {
  display: flex;
  gap: 8px;
}

.timer-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.timer-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.timer-btn.start {
  background: #28a745;
  color: white;
}

.timer-btn.pause {
  background: #ffc107;
  color: #333;
}

.timer-btn.reset {
  background: #6c757d;
  color: white;
}

.timer-btn:hover:not(:disabled) {
  opacity: 0.9;
  transform: scale(1.02);
}
</style>
