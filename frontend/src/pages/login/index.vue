<template>
  <view class="login-page">
    <!-- Logo -->
    <view class="logo-area">
      <image class="logo" src="/static/logo.png" mode="aspectFit" />
      <text class="app-name">OfferPilot</text>
      <text class="app-slogan">面试刷题，轻松拿 Offer</text>
    </view>

    <!-- Tab 切换 -->
    <view class="tab-bar">
      <view
        class="tab-item"
        :class="{ active: currentTab === 'login' }"
        @click="currentTab = 'login'"
      >
        <text>登录</text>
      </view>
      <view
        class="tab-item"
        :class="{ active: currentTab === 'register' }"
        @click="currentTab = 'register'"
      >
        <text>注册</text>
      </view>
    </view>

    <!-- 邮箱登录 -->
    <view class="form-area" v-if="currentTab === 'login'">
      <view class="input-group">
        <u-input
          v-model="loginForm.email"
          placeholder="请输入邮箱"
          prefixIcon="email"
          clearable
          :customStyle="inputStyle"
        />
      </view>
      <view class="input-group">
        <u-input
          v-model="loginForm.password"
          placeholder="请输入密码"
          type="password"
          prefixIcon="lock"
          :customStyle="inputStyle"
        />
      </view>
      <u-button
        type="primary"
        :text="loading ? '登录中...' : '登录'"
        :loading="loading"
        :disabled="loading"
        :customStyle="btnStyle"
        @click="handleEmailLogin"
      />
    </view>

    <!-- 邮箱注册 -->
    <view class="form-area" v-if="currentTab === 'register'">
      <view class="input-group">
        <u-input
          v-model="registerForm.email"
          placeholder="请输入邮箱"
          prefixIcon="email"
          clearable
          :customStyle="inputStyle"
        />
      </view>
      <view class="input-group">
        <u-input
          v-model="registerForm.password"
          placeholder="请输入密码"
          type="password"
          prefixIcon="lock"
          :customStyle="inputStyle"
        />
      </view>
      <view class="input-group code-group">
        <u-input
          v-model="registerForm.code"
          placeholder="请输入验证码"
          prefixIcon="checkbox-mark"
          :customStyle="inputStyle"
        />
        <u-button
          :text="codeBtnText"
          :disabled="codeCounting"
          size="small"
          :customStyle="codeBtnStyle"
          @click="handleSendCode"
        />
      </view>
      <u-button
        type="primary"
        :text="loading ? '注册中...' : '注册'"
        :loading="loading"
        :disabled="loading"
        :customStyle="btnStyle"
        @click="handleEmailRegister"
      />
    </view>

    <!-- 分割线 -->
    <view class="divider">
      <view class="divider-line" />
      <text class="divider-text">其他登录方式</text>
      <view class="divider-line" />
    </view>

    <!-- 微信快捷登录 -->
    <!-- #ifdef MP-WEIXIN -->
    <u-button
      :customStyle="wxBtnStyle"
      :loading="wxLoading"
      :disabled="wxLoading"
      @click="handleWechatLogin"
    >
      <view class="wx-btn-inner">
        <u-icon name="weixin-fill" color="#fff" size="40" />
        <text class="wx-btn-text">{{ wxLoading ? '登录中...' : '微信快捷登录' }}</text>
      </view>
    </u-button>
    <!-- #endif -->
    <!-- #ifndef MP-WEIXIN -->
    <view class="wx-unavailable">
      <text class="wx-tip">微信登录仅在小程序端可用</text>
    </view>
    <!-- #endif -->
  </view>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useUserStore } from '@/store/user'
import { wechatLogin, emailLogin, emailRegister, emailSendCode } from '@/api/auth'

const userStore = useUserStore()

const currentTab = ref('login')
const loading = ref(false)
const wxLoading = ref(false)

// 表单数据
const loginForm = reactive({
  email: '',
  password: '',
})

const registerForm = reactive({
  email: '',
  password: '',
  code: '',
})

// 验证码倒计时
const codeCounting = ref(false)
const codeCountdown = ref(0)
let codeTimer = null

const codeBtnText = computed(() => {
  return codeCounting.value ? `${codeCountdown.value}s` : '获取验证码'
})

// 样式
const inputStyle = {
  backgroundColor: '#F5F7FA',
  borderRadius: '16rpx',
  padding: '20rpx 24rpx',
}

const btnStyle = {
  backgroundColor: '#4C84FF',
  borderColor: '#4C84FF',
  borderRadius: '44rpx',
  height: '88rpx',
  fontSize: '32rpx',
  marginTop: '24rpx',
}

const codeBtnStyle = {
  backgroundColor: '#4C84FF',
  borderColor: '#4C84FF',
  color: '#fff',
  borderRadius: '12rpx',
  height: '64rpx',
  fontSize: '24rpx',
  flexShrink: 0,
  marginLeft: '16rpx',
  width: '200rpx',
}

const wxBtnStyle = {
  backgroundColor: '#07C160',
  borderColor: '#07C160',
  borderRadius: '44rpx',
  height: '88rpx',
}

// 登录成功后跳转
function navigateAfterAuth() {
  const pages = getCurrentPages()
  if (pages.length > 1) {
    uni.navigateBack()
  } else {
    uni.switchTab({ url: '/pages/index/index' })
  }
}

// 微信登录
async function handleWechatLogin() {
  // #ifdef MP-WEIXIN
  wxLoading.value = true
  try {
    const [loginRes, sysInfo] = await Promise.all([
      new Promise((resolve, reject) => {
        wx.login({
          success: resolve,
          fail: reject,
        })
      }),
      new Promise((resolve) => {
        uni.getSystemInfo({ success: resolve, fail: () => resolve({}) })
      }),
    ])

    const deviceId = sysInfo.deviceId || ''
    const data = await wechatLogin(loginRes.code, deviceId)
    userStore.setAuth(data)

    uni.showToast({ title: '登录成功', icon: 'success' })
    setTimeout(() => navigateAfterAuth(), 500)
  } catch (e) {
    console.error('微信登录失败', e)
    uni.showToast({ title: e?.message || '微信登录失败', icon: 'none' })
  } finally {
    wxLoading.value = false
  }
  // #endif
}

// 邮箱登录
async function handleEmailLogin() {
  if (!loginForm.email) {
    return uni.showToast({ title: '请输入邮箱', icon: 'none' })
  }
  if (!loginForm.password) {
    return uni.showToast({ title: '请输入密码', icon: 'none' })
  }

  loading.value = true
  try {
    const data = await emailLogin(loginForm.email, loginForm.password)
    userStore.setAuth(data)

    uni.showToast({ title: '登录成功', icon: 'success' })
    setTimeout(() => navigateAfterAuth(), 500)
  } catch (e) {
    console.error('邮箱登录失败', e)
    uni.showToast({ title: e?.message || '登录失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

// 发送验证码
async function handleSendCode() {
  if (!registerForm.email) {
    return uni.showToast({ title: '请输入邮箱', icon: 'none' })
  }
  if (codeCounting.value) return

  try {
    await emailSendCode(registerForm.email)
    uni.showToast({ title: '验证码已发送', icon: 'success' })

    // 开始倒计时
    codeCountdown.value = 60
    codeCounting.value = true
    codeTimer = setInterval(() => {
      codeCountdown.value--
      if (codeCountdown.value <= 0) {
        clearInterval(codeTimer)
        codeTimer = null
        codeCounting.value = false
      }
    }, 1000)
  } catch (e) {
    uni.showToast({ title: e?.message || '发送失败', icon: 'none' })
  }
}

// 邮箱注册
async function handleEmailRegister() {
  if (!registerForm.email) {
    return uni.showToast({ title: '请输入邮箱', icon: 'none' })
  }
  if (!registerForm.password) {
    return uni.showToast({ title: '请输入密码', icon: 'none' })
  }
  if (!registerForm.code) {
    return uni.showToast({ title: '请输入验证码', icon: 'none' })
  }

  loading.value = true
  try {
    const data = await emailRegister(registerForm.email, registerForm.password, registerForm.code)
    userStore.setAuth(data)

    uni.showToast({ title: '注册成功', icon: 'success' })
    setTimeout(() => navigateAfterAuth(), 500)
  } catch (e) {
    console.error('邮箱注册失败', e)
    uni.showToast({ title: e?.message || '注册失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
$brand: #4C84FF;

.login-page {
  min-height: 100vh;
  background: #fff;
  padding: 0 48rpx;
  padding-top: 120rpx;
  box-sizing: border-box;
}

.logo-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 60rpx;

  .logo {
    width: 120rpx;
    height: 120rpx;
    margin-bottom: 16rpx;
  }

  .app-name {
    font-size: 40rpx;
    font-weight: bold;
    color: #1a1a2e;
    margin-bottom: 8rpx;
  }

  .app-slogan {
    font-size: 26rpx;
    color: #999;
  }
}

.tab-bar {
  display: flex;
  justify-content: center;
  margin-bottom: 40rpx;
  gap: 60rpx;

  .tab-item {
    padding-bottom: 12rpx;
    font-size: 32rpx;
    color: #999;
    position: relative;
    transition: color 0.2s;

    &.active {
      color: $brand;
      font-weight: bold;

      &::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 48rpx;
        height: 6rpx;
        border-radius: 3rpx;
        background: $brand;
      }
    }
  }
}

.form-area {
  margin-bottom: 40rpx;

  .input-group {
    margin-bottom: 24rpx;
  }

  .code-group {
    display: flex;
    align-items: center;
  }
}

.divider {
  display: flex;
  align-items: center;
  margin: 48rpx 0 40rpx;

  .divider-line {
    flex: 1;
    height: 1rpx;
    background: #e8e8e8;
  }

  .divider-text {
    font-size: 24rpx;
    color: #bbb;
    padding: 0 24rpx;
  }
}

.wx-btn-inner {
  display: flex;
  align-items: center;
  justify-content: center;

  .wx-btn-text {
    color: #fff;
    font-size: 30rpx;
    margin-left: 12rpx;
  }
}

.wx-unavailable {
  text-align: center;

  .wx-tip {
    font-size: 24rpx;
    color: #ccc;
  }
}
</style>
