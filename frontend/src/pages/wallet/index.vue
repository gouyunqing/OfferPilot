<template>
  <view class="container">
    <!-- 余额卡片 -->
    <view class="balance-card">
      <view class="balance-header">
        <text class="balance-label">账户余额（元）</text>
      </view>
      <text class="balance-amount">{{ wallet.balance || '0.00' }}</text>
      <view class="balance-stats">
        <view class="stat-item">
          <text class="stat-value">{{ wallet.total_earned || '0.00' }}</text>
          <text class="stat-label">累计收入</text>
        </view>
        <view class="stat-divider" />
        <view class="stat-item">
          <text class="stat-value">{{ wallet.total_withdrawn || '0.00' }}</text>
          <text class="stat-label">累计提现</text>
        </view>
        <view class="stat-divider" />
        <view class="stat-item">
          <text class="stat-value">{{ wallet.pending_withdrawal || '0.00' }}</text>
          <text class="stat-label">提现中</text>
        </view>
      </view>
      <view class="withdraw-btn" @click="showWithdrawPopup = true">
        <text class="withdraw-btn-text">提现</text>
      </view>
    </view>

    <!-- 交易记录 -->
    <view class="section">
      <text class="section-title">交易记录</text>

      <view
        class="transaction-item"
        v-for="item in transactions"
        :key="item.id"
      >
        <view class="tx-left">
          <view class="tx-icon" :class="'tx-icon-' + item.type">
            <u-icon
              :name="txIcon(item.type)"
              size="36"
              color="#fff"
            />
          </view>
          <view class="tx-info">
            <text class="tx-desc">{{ item.description }}</text>
            <text class="tx-date">{{ item.created_at }}</text>
          </view>
        </view>
        <text
          class="tx-amount"
          :class="item.amount > 0 ? 'tx-income' : 'tx-expense'"
        >
          {{ item.amount > 0 ? '+' : '' }}{{ item.amount }}
        </text>
      </view>

      <view class="empty" v-if="!transactions.length && !loading">
        <text>暂无交易记录</text>
      </view>

      <view class="loading-more" v-if="loading">
        <u-loading-icon size="28" />
        <text class="loading-text">加载中...</text>
      </view>

      <view class="no-more" v-if="!loading && finished && transactions.length">
        <text>没有更多了</text>
      </view>
    </view>

    <!-- 提现弹窗 -->
    <u-popup :show="showWithdrawPopup" mode="bottom" round="24" @close="showWithdrawPopup = false">
      <view class="withdraw-popup">
        <view class="popup-header">
          <text class="popup-title">申请提现</text>
          <u-icon name="close" size="40" @click="showWithdrawPopup = false" />
        </view>

        <view class="form-group">
          <text class="form-label">提现金额</text>
          <u-input
            v-model="withdrawForm.amount"
            type="digit"
            placeholder="请输入提现金额"
            border="surround"
            clearable
          />
        </view>

        <view class="form-group">
          <text class="form-label">提现渠道</text>
          <view class="channel-row">
            <view
              class="channel-item"
              :class="{ active: withdrawForm.channel === 'wechat' }"
              @click="withdrawForm.channel = 'wechat'"
            >
              <u-icon name="weixin-fill" size="40" :color="withdrawForm.channel === 'wechat' ? '#fff' : '#09BB07'" />
              <text>微信</text>
            </view>
            <view
              class="channel-item"
              :class="{ active: withdrawForm.channel === 'alipay' }"
              @click="withdrawForm.channel = 'alipay'"
            >
              <u-icon name="zhifubao" size="40" :color="withdrawForm.channel === 'alipay' ? '#fff' : '#1677FF'" />
              <text>支付宝</text>
            </view>
          </view>
        </view>

        <view class="form-group">
          <text class="form-label">收款账号</text>
          <u-input
            v-model="withdrawForm.account"
            placeholder="请输入收款账号"
            border="surround"
            clearable
          />
        </view>

        <u-button
          type="primary"
          :loading="submitting"
          :disabled="submitting"
          text="确认提现"
          customStyle="margin-top: 40rpx;"
          @click="handleWithdraw"
        />
      </view>
    </u-popup>
  </view>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { onReachBottom } from '@dcloudio/uni-app'
import { getWallet, getTransactions, withdraw } from '@/api/wallet'

const wallet = ref({})
const transactions = ref([])
const loading = ref(false)
const finished = ref(false)
const page = ref(1)
const pageSize = 20

const showWithdrawPopup = ref(false)
const submitting = ref(false)
const withdrawForm = reactive({
  amount: '',
  channel: 'wechat',
  account: '',
})

const txIcon = (type) => {
  const map = {
    earning: 'red-packet',
    withdraw: 'money',
    reward: 'gift',
    refund: 'reload',
  }
  return map[type] || 'rmb-circle'
}

const fetchWallet = async () => {
  try {
    const data = await getWallet()
    wallet.value = data || {}
  } catch (e) {
    console.error('fetchWallet', e)
  }
}

const fetchTransactions = async () => {
  if (loading.value || finished.value) return
  loading.value = true
  try {
    const data = await getTransactions({ page: page.value, page_size: pageSize })
    const items = data?.items || []
    if (items.length < pageSize) {
      finished.value = true
    }
    transactions.value = [...transactions.value, ...items]
    page.value++
  } catch (e) {
    console.error('fetchTransactions', e)
  } finally {
    loading.value = false
  }
}

const handleWithdraw = async () => {
  if (!withdrawForm.amount || Number(withdrawForm.amount) <= 0) {
    uni.showToast({ title: '请输入正确的金额', icon: 'none' })
    return
  }
  if (!withdrawForm.account) {
    uni.showToast({ title: '请输入收款账号', icon: 'none' })
    return
  }
  submitting.value = true
  try {
    await withdraw({
      amount: Number(withdrawForm.amount),
      channel: withdrawForm.channel,
      account: withdrawForm.account,
    })
    uni.showToast({ title: '提现申请已提交', icon: 'success' })
    showWithdrawPopup.value = false
    withdrawForm.amount = ''
    withdrawForm.account = ''
    // Refresh wallet data
    await fetchWallet()
  } catch (e) {
    console.error('withdraw', e)
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchWallet()
  fetchTransactions()
})

onReachBottom(() => {
  fetchTransactions()
})
</script>

<style lang="scss" scoped>
.container {
  min-height: 100vh;
  background: #f5f6fa;
  padding: 24rpx;
}

.balance-card {
  background: linear-gradient(135deg, #4C84FF, #6A9DFF);
  border-radius: 24rpx;
  padding: 40rpx;
  color: #fff;
  margin-bottom: 32rpx;
  position: relative;

  .balance-header {
    margin-bottom: 12rpx;
  }

  .balance-label {
    font-size: 26rpx;
    opacity: 0.85;
  }

  .balance-amount {
    font-size: 64rpx;
    font-weight: bold;
    display: block;
    margin-bottom: 32rpx;
  }

  .balance-stats {
    display: flex;
    align-items: center;
    background: rgba(255, 255, 255, 0.15);
    border-radius: 16rpx;
    padding: 24rpx 0;
  }

  .stat-item {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .stat-value {
    font-size: 30rpx;
    font-weight: 600;
    margin-bottom: 6rpx;
  }

  .stat-label {
    font-size: 22rpx;
    opacity: 0.8;
  }

  .stat-divider {
    width: 1rpx;
    height: 48rpx;
    background: rgba(255, 255, 255, 0.3);
  }

  .withdraw-btn {
    position: absolute;
    top: 40rpx;
    right: 40rpx;
    background: rgba(255, 255, 255, 0.25);
    border-radius: 32rpx;
    padding: 10rpx 32rpx;

    .withdraw-btn-text {
      font-size: 26rpx;
      color: #fff;
    }
  }
}

.section {
  background: #fff;
  border-radius: 20rpx;
  padding: 24rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #1a1a2e;
  margin-bottom: 20rpx;
  display: block;
}

.transaction-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx 0;
  border-bottom: 1rpx solid #f5f5f5;

  &:last-child {
    border-bottom: none;
  }

  .tx-left {
    display: flex;
    align-items: center;
    flex: 1;
    min-width: 0;
  }

  .tx-icon {
    width: 72rpx;
    height: 72rpx;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 20rpx;
    flex-shrink: 0;
  }

  .tx-icon-earning {
    background: #ff6b6b;
  }

  .tx-icon-withdraw {
    background: #4C84FF;
  }

  .tx-icon-reward {
    background: #ff9f43;
  }

  .tx-icon-refund {
    background: #00c48c;
  }

  .tx-info {
    display: flex;
    flex-direction: column;
    flex: 1;
    min-width: 0;
  }

  .tx-desc {
    font-size: 28rpx;
    color: #333;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .tx-date {
    font-size: 22rpx;
    color: #999;
    margin-top: 6rpx;
  }

  .tx-amount {
    font-size: 30rpx;
    font-weight: 600;
    flex-shrink: 0;
    margin-left: 16rpx;
  }

  .tx-income {
    color: #ff6b6b;
  }

  .tx-expense {
    color: #333;
  }
}

.empty {
  text-align: center;
  padding: 80rpx 0;
  color: #999;
  font-size: 28rpx;
}

.loading-more {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 30rpx 0;

  .loading-text {
    font-size: 24rpx;
    color: #999;
    margin-left: 12rpx;
  }
}

.no-more {
  text-align: center;
  padding: 30rpx 0;
  color: #ccc;
  font-size: 24rpx;
}

/* 提现弹窗 */
.withdraw-popup {
  padding: 40rpx;

  .popup-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 40rpx;
  }

  .popup-title {
    font-size: 34rpx;
    font-weight: bold;
    color: #1a1a2e;
  }

  .form-group {
    margin-bottom: 28rpx;
  }

  .form-label {
    font-size: 28rpx;
    color: #333;
    margin-bottom: 12rpx;
    display: block;
  }

  .channel-row {
    display: flex;
    gap: 24rpx;
  }

  .channel-item {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12rpx;
    padding: 20rpx 0;
    border-radius: 12rpx;
    border: 2rpx solid #e0e0e0;
    font-size: 28rpx;
    color: #333;

    &.active {
      border-color: #4C84FF;
      background: #4C84FF;
      color: #fff;
    }
  }
}
</style>
