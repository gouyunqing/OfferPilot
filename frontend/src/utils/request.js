const BASE_URL = 'http://127.0.0.1:8001'

function getToken() {
  return uni.getStorageSync('access_token') || ''
}

export function request(options) {
  const { url, method = 'GET', data, header = {}, loading = true } = options

  if (loading) {
    uni.showLoading({ title: '加载中...', mask: true })
  }

  const token = getToken()
  if (token) {
    header['Authorization'] = `Bearer ${token}`
  }
  header['Content-Type'] = header['Content-Type'] || 'application/json'

  return new Promise((resolve, reject) => {
    uni.request({
      url: `${BASE_URL}${url}`,
      method,
      data,
      header,
      success(res) {
        if (loading) uni.hideLoading()
        const body = res.data

        if (res.statusCode === 401 || body.code === 40001) {
          uni.removeStorageSync('access_token')
          uni.removeStorageSync('refresh_token')
          uni.removeStorageSync('user_info')
          uni.navigateTo({ url: '/pages/login/index' })
          reject(body)
          return
        }

        if (body.code !== 0) {
          uni.showToast({ title: body.message || '请求失败', icon: 'none' })
          reject(body)
          return
        }

        resolve(body.data)
      },
      fail(err) {
        if (loading) uni.hideLoading()
        uni.showToast({ title: '网络异常', icon: 'none' })
        reject(err)
      },
    })
  })
}

export const get = (url, data, options = {}) => request({ url, method: 'GET', data, ...options })
export const post = (url, data, options = {}) => request({ url, method: 'POST', data, ...options })
export const put = (url, data, options = {}) => request({ url, method: 'PUT', data, ...options })
export const del = (url, data, options = {}) => request({ url, method: 'DELETE', data, ...options })
