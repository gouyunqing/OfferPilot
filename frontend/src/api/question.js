import { get, post } from '@/utils/request'

export const getQuestions = (params) => get('/v1/questions', params)
export const getHotQuestions = (params) => get('/v1/questions/hot', params)
export const searchQuestions = (params) => get('/v1/questions/search', params)
export const getQuestionDetail = (id) => get(`/v1/questions/${id}`)
export const createQuestion = (data) => post('/v1/questions', data)

export const getComments = (questionId, params) => get(`/v1/questions/${questionId}/comments`, params)
export const createComment = (questionId, content) => post(`/v1/questions/${questionId}/comments`, { content })

export const confirmQuestion = (questionId) => post(`/v1/questions/${questionId}/confirm`)
export const getNote = (questionId) => get(`/v1/questions/${questionId}/note`)
