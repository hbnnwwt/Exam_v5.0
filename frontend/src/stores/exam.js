import { defineStore } from 'pinia'
import api from '@/api'

export const useExamStore = defineStore('exam', {
  state: () => ({
    // 当前考生
    currentStudent: null,
    currentStudentInfo: null,

    // 面试流程 - totalSteps 从API加载
    currentStep: 1,
    totalSteps: 0,  // 从API动态获取
    examStatus: 'ready', // ready, in_progress, completed

    // 重置标志（防止 beforeUnload 在重置后保存进度）
    isReset: false,

    // 计时器
    timer: {
      isRunning: false,
      remainingTime: 0,
      totalTime: 0
    },

    // 题目
    translationQuestion: null,
    professionalQuestion: null,
    currentTranslationQuestionId: null,
    currentProfessionalQuestionId: null,
    
    // 已使用题目ID列表
    usedQuestionIds: [],
    // 分别存储翻译题和专业题的已使用ID，避免ID冲突
    usedTranslationQuestionIds: [],
    usedProfessionalQuestionIds: [],

    // 步骤时间配置（秒）- 从API加载，备用默认值为0
    stepTimes: {
      1: 0,
      2: 0,
      3: 0,
      4: 0,
      5: 0,
      6: 0
    },

    // 步骤信息
    stepInfos: []
  }),

  getters: {
    stepName: (state) => {
      // 从API加载的步骤信息中获取
      const stepInfo = state.stepInfos.find(s => s.step_number === state.currentStep)
      if (stepInfo && stepInfo.title) {
        return stepInfo.title
      }
      return `步骤 ${state.currentStep}`
    },

    formattedTime: (state) => {
      const minutes = Math.floor(state.timer.remainingTime / 60)
      const seconds = state.timer.remainingTime % 60
      return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
    }
  },

  actions: {
    // 加载步骤配置
    async loadStepSettings() {
      try {
        const response = await api.get('/exam-api/exam-steps')
        if (response.success && response.data) {
          this.stepInfos = response.data
          // 更新总步骤数
          this.totalSteps = response.data.length
          // 更新stepTimes
          response.data.forEach(step => {
            if (step.step_number >= 1 && step.step_number <= this.totalSteps) {
              this.stepTimes[step.step_number] = step.duration || 0
            }
          })
        }
      } catch (error) {
        console.error('加载步骤设置失败:', error)
      }
    },

    // 重新加载步骤设置（供设置页面调用）
    async reloadStepSettings() {
      await this.loadStepSettings()
    },

    async setStudent(studentNumber) {
      this.currentStudent = studentNumber
      try {
        const response = await api.get(`/exam-api/students/${studentNumber}`)
        if (response.success) {
          this.currentStudentInfo = response.data
        }
      } catch (error) {
        console.error('获取学生信息失败:', error)
      }
    },

    nextStep() {
      if (this.currentStep < this.totalSteps) {
        this.currentStep++
        this.startStepTimer()
      }
    },

    prevStep() {
      if (this.currentStep > 1) {
        this.currentStep--
        this.startStepTimer()
      }
    },

    startStepTimer() {
      const duration = this.stepTimes[this.currentStep] || 60
      this.timer.totalTime = duration
      this.timer.remainingTime = duration
      this.timer.isRunning = true
    },

    decrementTimer() {
      if (this.timer.remainingTime > 0) {
        this.timer.remainingTime--
      } else {
        this.timer.isRunning = false
      }
    },

    pauseTimer() {
      this.timer.isRunning = false
    },

    resumeTimer() {
      this.timer.isRunning = true
    },

    // 保存考试进度
    async saveProgress() {
      // 如果系统已重置或状态不对，不保存
      if (this.isReset || !this.currentStudent || this.examStatus === 'ready') {
        return
      }

      try {
        await api.post('/exam-api/progress/save', {
          studentNumber: this.currentStudent,
          currentStep: this.currentStep,
          remainingTime: this.timer.remainingTime,
          translationQuestionId: this.currentTranslationQuestionId,
          professionalQuestionId: this.currentProfessionalQuestionId,
          usedQuestionIds: this.usedQuestionIds,
          examStatus: this.examStatus
        })
      } catch (error) {
        console.error('保存考试进度失败:', error)
      }
    },

    // 加载考试进度
    async loadProgress() {
      try {
        const response = await api.get('/exam-api/progress/load')
        if (response.success && response.data.hasProgress) {
          const data = response.data
          this.currentStudent = data.studentNumber
          this.currentStep = data.currentStep
          this.timer.remainingTime = data.remainingTime || this.stepTimes[data.currentStep]
          this.timer.totalTime = this.stepTimes[data.currentStep]
          this.timer.isRunning = false
          this.currentTranslationQuestionId = data.translationQuestionId
          this.currentProfessionalQuestionId = data.professionalQuestionId
          this.usedQuestionIds = data.usedQuestionIds || []
          this.examStatus = data.examStatus || 'in_progress'
          this.isReset = false  // 恢复进度后清除重置标志

          // 恢复题目详情
          if (data.translationQuestionId) {
            await this.loadQuestionDetail(data.translationQuestionId, 'translation')
          }
          if (data.professionalQuestionId) {
            await this.loadQuestionDetail(data.professionalQuestionId, 'professional')
          }

          return true
        } else if (response.success && response.data && (response.data.allUsedTranslationIds?.length > 0 || response.data.allUsedProfessionalIds?.length > 0)) {
          // 没有进行中的考试，但有已使用题目ID（新考生时使用）
          // 分别处理翻译题和专业题的ID，避免ID冲突
          const translationIds = response.data.allUsedTranslationIds || []
          const professionalIds = response.data.allUsedProfessionalIds || []
          // 合并两个列表，前端会根据题目类型过滤
          this.usedQuestionIds = [...translationIds, ...professionalIds]
          // 保存按类型分类的ID
          this.usedTranslationQuestionIds = translationIds
          this.usedProfessionalQuestionIds = professionalIds

          // 检查最后一个考生是否已完成考试
          // 如果 examStatus 是 'completed'，说明考生已完成考试，需要手动点击"开始考试"
          if (response.data.examStatus === 'completed') {
            // 考生已完成考试，不设置 currentStudent，显示"开始考试"按钮
            this.currentStudent = null
            this.currentStudentInfo = null
          } else {
            // 没有考试记录或已重置，设置 currentStudent
            this.currentStudent = response.data.studentNumber
          }
          this.currentStep = 1
          this.examStatus = 'ready'
          return false
        } else {
          // 数据库没有进度记录时，清空前端状态，防止自动保存创建新记录
          this.currentStudent = null
          this.currentStudentInfo = null
          this.currentStep = 1
          this.examStatus = 'ready'
          this.timer.isRunning = false
          this.timer.remainingTime = 0
          this.translationQuestion = null
          this.professionalQuestion = null
          this.currentTranslationQuestionId = null
          this.currentProfessionalQuestionId = null
          this.usedQuestionIds = []
          return false
        }
      } catch (error) {
        console.error('加载考试进度失败:', error)
        return false
      }
    },
    
    // 加载题目详情
    async loadQuestionDetail(questionId, questionType) {
      try {
        const response = await api.get(`/exam-api/questions/${questionType}/id/${questionId}`)
        if (response.success && response.data) {
          // 只保存 content 内容，不保存整个对象
          const content = response.data.content || response.data.question_data
          if (questionType === 'translation') {
            this.translationQuestion = content
          } else {
            this.professionalQuestion = content
          }
        }
      } catch (error) {
        console.error('加载题目详情失败:', error)
      }
    },

    // 重置考试系统（包含数据库重置）
    async resetExam() {
      try {
        // 先设置状态为 ready，阻止自动保存
        const previousStatus = this.examStatus
        this.examStatus = 'ready'

        // 调用后端 API 清空数据库
        const response = await api.post('/exam-api/reset')
        if (response.success) {
          // 清空前端状态
          this.currentStudent = null
          this.currentStudentInfo = null
          this.currentStep = 1
          this.examStatus = 'ready'
          this.timer.isRunning = false
          this.timer.remainingTime = 0
          this.translationQuestion = null
          this.professionalQuestion = null
          this.currentTranslationQuestionId = null
          this.currentProfessionalQuestionId = null
          this.usedQuestionIds = []
          this.isReset = true  // 设置重置标志，防止 beforeUnload 保存

          console.log('系统已完全重置:', response.message)
          return { success: true, message: response.message }
        } else {
          console.error('重置失败:', response.error)
          return { success: false, error: response.error || '重置失败' }
        }
      } catch (error) {
        console.error('重置考试失败:', error)
        return { success: false, error: error.message || '网络错误' }
      }
    },
  }
})
