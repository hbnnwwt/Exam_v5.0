import { defineStore } from 'pinia'

export const useToastStore = defineStore('toast', {
  state: () => ({
    messages: []
  }),

  actions: {
    show(message, type = 'info', duration = 3000) {
      const id = Date.now()
      this.messages.push({ id, message, type })

      if (duration > 0) {
        setTimeout(() => {
          this.remove(id)
        }, duration)
      }

      return id
    },

    remove(id) {
      const index = this.messages.findIndex(m => m.id === id)
      if (index > -1) {
        this.messages.splice(index, 1)
      }
    },

    success(message, duration = 3000) {
      return this.show(message, 'success', duration)
    },

    error(message, duration = 4000) {
      return this.show(message, 'error', duration)
    },

    warning(message, duration = 3500) {
      return this.show(message, 'warning', duration)
    },

    info(message, duration = 3000) {
      return this.show(message, 'info', duration)
    }
  }
})
