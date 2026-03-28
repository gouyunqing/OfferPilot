<template>
  <view class="container">
    <!-- 当前订阅状态 -->
    <view class="status-card">
      <view class="status-icon">
        <u-icon :name="currentPlan ? 'crown-fill' : 'lock'" size="56" :color="currentPlan ? '#FFD700' : '#999'" />
      </view>
      <view class="status-info" v-if="currentPlan">
        <text class="status-title">{{ currentPlan.name }}</text>
        <text class="status-desc">有效期至 {{ currentPlan.expire_at }}</text>
      </view>
      <view class="status-info" v-else>
        <text class="status-title">未开通会员</text>
        <text class="status-desc">开通会员解锁全部功能</text>
      </view>
    </view>

    <!-- 会员权益 -->
    <view class="benefits-section">
      <text class="section-title">会员权益</text>
      <view class="benefits-grid">
        <view class="benefit-item" v-for="b in benefits" :key="b.icon">
          <u-icon :name="b.icon" size="48" color="#4C84FF" />
          <text class="benefit-text">{{ b.text }}</text>
        </view>
      </view>
    </view>

    <!-- 套餐选择 -->
    <view class="plans-section">
      <text class="section-title">选择套餐</text>
      <view class="plans-grid">
        <view
          class="plan-card"
          v-for="plan in plans"
          :key="plan.id"
          :class="{ selected: selectedPlan?.id === plan.id }"
          @click="selectedPlan = plan"
        >
          <view class="discount-label" v-if="plan.discount_label">
            <text>{{ plan.discount_label }}</text>
          </view>
          <text class="plan-name">{{ plan.name }}</text>
          <view class="plan-price-row">
            <text class="plan-price-symbol">¥</text>
            <text class="plan-price">{{ plan.price }}</text>
          </view>
          <text class="plan-original-price" v-if="plan.original_price">
            ¥{{ plan.original_price }}
          </text>
        </view>
      </view>
    </view>

    <!-- 订阅按钮 -->
    <view class="subscribe-footer">
      <u-button
        type="primary"
        shape="circle"
        :text="selectedPlan ? `立即订阅 ¥${selectedPlan.price}` : '请选择套餐'"
        :disabled="!selectedPlan"
        customStyle="height: 88rpx; font-size: 32rpx;"
        @click="handleSubscribe"
      />
      <text class="agreement-text">
        订阅即表示同意
        <text class="link">《会员服务协议》</text>
      </text>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { get } from '@/utils/request'

const currentPlan = ref(null)
const plans = ref([])
const selectedPlan = ref(null)

const benefits = [
  { icon: 'file-text', text: '无限刷题' },
  { icon: 'star', text: '高级题解' },
  { icon: 'chat', text: 'AI 模拟面试' },
  { icon: 'bookmark', text: '专属题库' },
]

const fetchPlans = async () => {
  try {
    const data = await get('/v1/subscriptions/plans')
    const items = data?.plans || data || []
    plans.value = items
    currentPlan.value = data?.current || null
    // Auto-select the first plan
    if (items.length && !selectedPlan.value) {
      selectedPlan.value = items[0]
    }
  } catch (e) {
    console.error('fetchPlans', e)
    // Fallback default plans
    plans.value = [
      { id: 1, name: '连续包月', price: '25', original_price: '30', discount_label: '推荐' },
      { id: 2, name: '月订阅', price: '30', original_price: null, discount_label: null },
      { id: 3, name: '季订阅', price: '68', original_price: '90', discount_label: '省22元' },
      { id: 4, name: '年订阅', price: '228', original_price: '360', discount_label: '最划算' },
    ]
    selectedPlan.value = plans.value[0]
  }
}

const handleSubscribe = () => {
  if (!selectedPlan.value) return
  uni.showToast({
    title: '即将上线',
    icon: 'none',
    duration: 2000,
  })
}

onMounted(() => {
  fetchPlans()
})
</script>

<style lang="scss" scoped>
$brand: #4C84FF;

.container {
  min-height: 100vh;
  background: #f5f6fa;
  padding: 24rpx;
  padding-bottom: 200rpx;
}

.status-card {
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, #1a1a2e, #2d2d4a);
  border-radius: 24rpx;
  padding: 40rpx;
  margin-bottom: 28rpx;

  .status-icon {
    width: 96rpx;
    height: 96rpx;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.1);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 28rpx;
    flex-shrink: 0;
  }

  .status-info {
    display: flex;
    flex-direction: column;
  }

  .status-title {
    font-size: 34rpx;
    font-weight: bold;
    color: #fff;
    margin-bottom: 8rpx;
  }

  .status-desc {
    font-size: 24rpx;
    color: rgba(255, 255, 255, 0.65);
  }
}

.benefits-section {
  background: #fff;
  border-radius: 20rpx;
  padding: 28rpx;
  margin-bottom: 28rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #1a1a2e;
  margin-bottom: 24rpx;
  display: block;
}

.benefits-grid {
  display: flex;
  flex-wrap: wrap;

  .benefit-item {
    width: 25%;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 16rpx 0;
  }

  .benefit-text {
    font-size: 22rpx;
    color: #666;
    margin-top: 10rpx;
  }
}

.plans-section {
  background: #fff;
  border-radius: 20rpx;
  padding: 28rpx;
  margin-bottom: 28rpx;
}

.plans-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.plan-card {
  width: calc(50% - 8rpx);
  background: #f8f9fc;
  border-radius: 16rpx;
  padding: 28rpx 20rpx;
  text-align: center;
  border: 3rpx solid transparent;
  position: relative;
  overflow: hidden;
  transition: all 0.2s;

  &.selected {
    border-color: $brand;
    background: rgba(76, 132, 255, 0.06);
  }

  .discount-label {
    position: absolute;
    top: 0;
    right: 0;
    background: #ff6b6b;
    color: #fff;
    font-size: 20rpx;
    padding: 4rpx 14rpx;
    border-radius: 0 14rpx 0 14rpx;
  }

  .plan-name {
    font-size: 28rpx;
    color: #333;
    display: block;
    margin-bottom: 12rpx;
  }

  .plan-price-row {
    display: flex;
    align-items: baseline;
    justify-content: center;
    margin-bottom: 6rpx;
  }

  .plan-price-symbol {
    font-size: 26rpx;
    font-weight: bold;
    color: $brand;
  }

  .plan-price {
    font-size: 52rpx;
    font-weight: bold;
    color: $brand;
  }

  .plan-original-price {
    font-size: 22rpx;
    color: #bbb;
    text-decoration: line-through;
    display: block;
  }
}

.subscribe-footer {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  background: #fff;
  padding: 20rpx 40rpx;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  box-shadow: 0 -2rpx 20rpx rgba(0, 0, 0, 0.05);

  .agreement-text {
    display: block;
    text-align: center;
    font-size: 22rpx;
    color: #999;
    margin-top: 14rpx;
  }

  .link {
    color: $brand;
  }
}
</style>
