<template>
  <view class="mine-page">
    <!-- Not logged in -->
    <view v-if="!isLoggedIn" class="login-prompt">
      <u-image
        src="/static/default-avatar.png"
        width="160rpx"
        height="160rpx"
        shape="circle"
      />
      <text class="login-hint">登录后体验更多功能</text>
      <u-button type="primary" text="立即登录" @click="goLogin" />
    </view>

    <!-- Logged in -->
    <view v-else class="user-section">
      <!-- Profile header -->
      <view class="profile-header">
        <u-avatar :src="userInfo.avatar" size="130rpx" />
        <view class="profile-info">
          <text class="nickname">{{ userInfo.nickname }}</text>
          <view class="level-badge">
            <u-icon name="level" size="28rpx" color="#ff9900" />
            <text class="level-title">Lv.{{ userInfo.level }}</text>
            <text class="level-name">{{ userInfo.level_title }}</text>
          </view>
          <view class="exp-bar-wrapper">
            <u-line-progress
              :percentage="expPercent"
              activeColor="#ff9900"
              height="16rpx"
            />
            <text class="exp-text">{{ userInfo.exp }} / {{ userInfo.next_level_exp }}</text>
          </view>
        </view>
      </view>

      <!-- Stats row -->
      <view class="stats-row">
        <view class="stat-item">
          <text class="stat-value">{{ userInfo.question_count || 0 }}</text>
          <text class="stat-label">提问</text>
        </view>
        <view class="stat-item">
          <text class="stat-value">{{ userInfo.comment_count || 0 }}</text>
          <text class="stat-label">评论</text>
        </view>
        <view class="stat-item">
          <text class="stat-value">{{ userInfo.confirm_received_count || 0 }}</text>
          <text class="stat-label">被采纳</text>
        </view>
        <view class="stat-item">
          <text class="stat-value">{{ userInfo.favorite_count || 0 }}</text>
          <text class="stat-label">收藏</text>
        </view>
      </view>

      <!-- Member section -->
      <view class="member-section">
        <view class="member-info">
          <u-icon name="crown" size="40rpx" :color="userInfo.is_member ? '#ff9900' : '#999'" />
          <view class="member-detail">
            <text class="member-status">
              {{ userInfo.is_member ? '尊享会员' : '普通用户' }}
            </text>
            <text v-if="userInfo.is_member" class="member-plan">
              {{ userInfo.plan }} | 到期时间: {{ userInfo.expires_at }}
            </text>
          </view>
        </view>
        <u-button
          :text="userInfo.is_member ? '续费会员' : '开通会员'"
          type="warning"
          size="small"
          @click="goMember"
        />
      </view>

      <!-- Menu cells -->
      <u-cell-group :border="false" class="menu-group">
        <u-cell
          title="我的收藏"
          isLink
          icon="star"
          @click="navigateTo('/pages/favorites/index')"
        />
        <u-cell
          title="我的笔记"
          isLink
          icon="edit-pen"
          @click="navigateTo('/pages/notes/index')"
        />
        <u-cell
          title="我的钱包"
          isLink
          icon="red-packet"
          @click="navigateTo('/pages/wallet/index')"
        />
        <u-cell
          title="设置"
          isLink
          icon="setting"
          @click="navigateTo('/pages/setting/index')"
        />
        <u-cell
          title="退出登录"
          icon="close"
          @click="handleLogout"
        />
      </u-cell-group>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/store/user'
import { getMe } from '@/api/user'

const userStore = useUserStore()

const isLoggedIn = computed(() => !!userStore.token)
const userInfo = computed(() => userStore.userInfo || {})

const expPercent = computed(() => {
  const { exp = 0, next_level_exp = 1 } = userInfo.value
  if (!next_level_exp) return 0
  return Math.min(Math.round((exp / next_level_exp) * 100), 100)
})

const fetchUserInfo = async () => {
  if (!isLoggedIn.value) return
  try {
    const res = await getMe()
    userStore.setUserInfo(res.data)
  } catch (e) {
    console.error('获取用户信息失败', e)
  }
}

const goLogin = () => {
  uni.navigateTo({ url: '/pages/login/index' })
}

const goMember = () => {
  uni.navigateTo({ url: '/pages/member/index' })
}

const navigateTo = (url) => {
  uni.navigateTo({ url })
}

const handleLogout = () => {
  uni.showModal({
    title: '提示',
    content: '确认退出登录？',
    success: (res) => {
      if (res.confirm) {
        userStore.logout()
        uni.reLaunch({ url: '/pages/mine/index' })
      }
    }
  })
}

onMounted(() => {
  fetchUserInfo()
})
</script>

<style lang="scss" scoped>
.mine-page {
  min-height: 100vh;
  background-color: #f5f6fa;
}

.login-prompt {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 200rpx;
  gap: 30rpx;

  .login-hint {
    font-size: 28rpx;
    color: #999;
  }
}

.user-section {
  .profile-header {
    display: flex;
    align-items: center;
    padding: 40rpx 30rpx;
    background: linear-gradient(135deg, #4a90d9, #667eea);
    color: #fff;

    .profile-info {
      margin-left: 30rpx;
      flex: 1;

      .nickname {
        font-size: 36rpx;
        font-weight: bold;
        color: #fff;
      }

      .level-badge {
        display: flex;
        align-items: center;
        margin-top: 10rpx;
        gap: 8rpx;

        .level-title {
          font-size: 24rpx;
          color: #ffe8b0;
          font-weight: bold;
        }

        .level-name {
          font-size: 22rpx;
          color: #ffe8b0;
        }
      }

      .exp-bar-wrapper {
        margin-top: 16rpx;

        .exp-text {
          font-size: 20rpx;
          color: rgba(255, 255, 255, 0.8);
          margin-top: 4rpx;
        }
      }
    }
  }

  .stats-row {
    display: flex;
    justify-content: space-around;
    background-color: #fff;
    padding: 30rpx 0;
    margin-bottom: 20rpx;

    .stat-item {
      display: flex;
      flex-direction: column;
      align-items: center;

      .stat-value {
        font-size: 36rpx;
        font-weight: bold;
        color: #333;
      }

      .stat-label {
        font-size: 24rpx;
        color: #999;
        margin-top: 8rpx;
      }
    }
  }

  .member-section {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background-color: #fff;
    padding: 30rpx;
    margin-bottom: 20rpx;

    .member-info {
      display: flex;
      align-items: center;
      gap: 16rpx;

      .member-detail {
        display: flex;
        flex-direction: column;

        .member-status {
          font-size: 30rpx;
          font-weight: bold;
          color: #333;
        }

        .member-plan {
          font-size: 22rpx;
          color: #999;
          margin-top: 6rpx;
        }
      }
    }
  }

  .menu-group {
    margin-top: 20rpx;
  }
}
</style>
