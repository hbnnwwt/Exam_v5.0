import axios from './index'

export const getAiProviders = () => axios.get('/api/ai/config')

export const addAiProvider = (data) => axios.post('/api/ai/config', data)

export const updateAiProvider = (id, data) => axios.put(`/api/ai/config/${id}`, data)

export const deleteAiProvider = (id) => axios.delete(`/api/ai/config/${id}`)

export const testAiConnection = (id) => axios.post(`/api/ai/test/${id}`)

export const generateQuestion = (data) => axios.post('/api/ai/generate', data)

export const batchGenerateQuestions = (data) => axios.post('/api/ai/batch-generate', data)