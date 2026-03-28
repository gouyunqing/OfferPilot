import { post } from '@/utils/request'

export const wechatLogin = (code, device_id) => post('/v1/auth/wechat', { code, device_id })

export const smsSend = (phone) => post('/v1/auth/sms/send', { phone })
export const smsVerify = (phone, code, device_id) => post('/v1/auth/sms/verify', { phone, code, device_id })

export const emailRegister = (email, password, verification_code) =>
  post('/v1/auth/email/register', { email, password, verification_code })
export const emailLogin = (email, password) => post('/v1/auth/email/login', { email, password })
export const emailSendCode = (email) => post('/v1/auth/email/send-code', { email })

export const refreshToken = (refresh_token) => post('/v1/auth/token/refresh', { refresh_token })
export const logout = () => post('/v1/auth/logout')
