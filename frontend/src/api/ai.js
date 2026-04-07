import axios from './index'

export const getAiProviders = () => axios.get('/api/ai/providers')

export const addAiProvider = (data) => axios.post('/api/ai/providers', data)

export const updateAiProvider = (id, data) => axios.put(`/api/ai/providers/${id}`, data)

export const deleteAiProvider = (id) => axios.delete(`/api/ai/providers/${id}`)

export const testAiConnection = (id) => axios.post(`/api/ai/test/${id}`)

export const generateQuestion = (data) => axios.post('/api/ai/generate', data, { timeout: 60000 })

export const batchGenerateQuestions = (data) => axios.post('/api/ai/batch-generate', data, { timeout: 120000 })

export const getDefaultProvider = () => axios.get('/api/ai/default-provider')

export const setDefaultProvider = (providerId) => axios.post('/api/ai/default-provider', { provider: providerId })