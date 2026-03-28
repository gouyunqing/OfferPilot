import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getMe } from '@/api/user'

export const useUserStore = defineStore('user', () => {
  const token = ref(uni.getStorageSync('access_token') || '')
  const refreshTokenVal = ref(uni.getStorageSync('refresh_token') || '')
  const userInfo = ref(JSON.parse(uni.getStorageSync('user_info') || 'null'))

  const isLoggedIn = computed(() => !!token.value)
  const isMember = computed(() => userInfo.value?.is_member || false)

  function setAuth(data) {
    token.value = data.access_token
    refreshTokenVal.value = data.refresh_token
    userInfo.value = data.user
    uni.setStorageSync('access_token', data.access_token)
    uni.setStorageSync('refresh_token', data.refresh_token)
    uni.setStorageSync('user_info', JSON.stringify(data.user))
  }

  function clearAuth() {
    token.value = ''
    refreshTokenVal.value = ''
    userInfo.value = null
    uni.removeStorageSync('access_token')
    uni.removeStorageSync('refresh_token')
    uni.removeStorageSync('user_info')
  }

  async function fetchUserInfo() {
    try {
      const data = await getMe()
      userInfo.value = data
      uni.setStorageSync('user_info', JSON.stringify(data))
      return data
    } catch (e) {
      return null
    }
  }

  return { token, refreshTokenVal, userInfo, isLoggedIn, isMember, setAuth, clearAuth, fetchUserInfo }
})
