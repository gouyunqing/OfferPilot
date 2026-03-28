import { get, put } from '@/utils/request'

export const getMe = () => get('/v1/users/me')
export const updateMe = (data) => put('/v1/users/me', data)
export const getMyQuestions = (params) => get('/v1/users/me/questions', params)
export const getUserProfile = (userId) => get(`/v1/users/${userId}/profile`)
