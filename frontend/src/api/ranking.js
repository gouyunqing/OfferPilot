import { get } from '@/utils/request'

export const getQuestionRankings = (params) => get('/v1/rankings/questions', params)
export const getUserRankings = (params) => get('/v1/rankings/users', params)
