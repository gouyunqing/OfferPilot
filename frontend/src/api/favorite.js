import { get, post, del } from '@/utils/request'

export const getFavorites = (params) => get('/v1/favorites', params)
export const addFavorite = (question_id) => post('/v1/favorites', { question_id })
export const removeFavorite = (question_id) => del('/v1/favorites', { question_id })
