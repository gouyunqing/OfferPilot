import { get, post } from '@/utils/request'

export const getWallet = () => get('/v1/wallet')
export const getTransactions = (params) => get('/v1/wallet/transactions', params)
export const withdraw = (data) => post('/v1/wallet/withdraw', data)
