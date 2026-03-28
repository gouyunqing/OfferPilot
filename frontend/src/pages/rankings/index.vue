<template>
  <view class="container">
    <!-- 顶部 Tabs -->
    <view class="tab-bar">
      <view
        class="tab-item"
        :class="{ active: activeTab === 'questions' }"
        @click="switchTab('questions')"
      >
        <text>热门题目</text>
        <view class="tab-indicator" v-if="activeTab === 'questions'" />
      </view>
      <view
        class="tab-item"
        :class="{ active: activeTab === 'users' }"
        @click="switchTab('users')"
      >
        <text>用户排行</text>
        <view class="tab-indicator" v-if="activeTab === 'users'" />
      </view>
    </view>

    <!-- 题目排行 -->
    <view class="ranking-list" v-if="activeTab === 'questions'">
      <view
        class="ranking-item"
        v-for="(item, index) in questionList"
        :key="item.id"
        @click="goDetail(item.id)"
      >
        <view class="rank-number" :class="'rank-' + (index < 3 ? index + 1 : 'normal')">
          <text>{{ index + 1 }}</text>
        </view>
        <view class="rank-content">
          <text class="rank-title">{{ item.content_preview }}</text>
          <view class="rank-meta">
            <text class="rank-stat">{{ item.confirm_count || 0 }} 确认</text>
            <text class="rank-stat" v-if="item.companies && item.companies.length">
              {{ item.companies[0].name }}
            </text>
          </view>
        </view>
        <view class="rank-badge">
          <u-icon name="checkmark-circle" size="28" color="#4C84FF" />
          <text class="badge-count">{{ item.confirm_count || 0 }}</text>
        </view>
      </view>

      <view class="empty" v-if="!questionList.length && !loadingQ">
        <text>暂无排行数据</text>
      </view>

      <view class="loading-more" v-if="loadingQ">
        <u-loading-icon size="28" />
        <text class="loading-text">加载中...</text>
      </view>

      <view class="no-more" v-if="!loadingQ && finishedQ && questionList.length">
        <text>没有更多了</text>
      </view>
    </view>

    <!-- 用户排行 -->
    <view class="ranking-list" v-if="activeTab === 'users'">
      <!-- 排序切换 -->
      <view class="sort-bar">
        <view
          class="sort-item"
          :class="{ active: sortBy === 'exp' }"
          @click="changeSortBy('exp')"
        >
          <text>经验值</text>
        </view>
        <view
          class="sort-item"
          :class="{ active: sortBy === 'questions' }"
          @click="changeSortBy('questions')"
        >
          <text>题目数</text>
        </view>
        <view
          class="sort-item"
          :class="{ active: sortBy === 'confirms' }"
          @click="changeSortBy('confirms')"
        >
          <text>确认数</text>
        </view>
      </view>

      <view
        class="ranking-item user-ranking-item"
        v-for="(item, index) in userList"
        :key="item.id"
      >
        <view class="rank-number" :class="'rank-' + (index < 3 ? index + 1 : 'normal')">
          <text>{{ index + 1 }}</text>
        </view>
        <image
          class="user-avatar"
          :src="item.avatar || '/static/default-avatar.png'"
          mode="aspectFill"
        />
        <view class="rank-content">
          <view class="user-name-row">
            <text class="rank-title">{{ item.nickname }}</text>
            <view class="level-badge" v-if="item.level">
              <text>Lv.{{ item.level }}</text>
            </view>
          </view>
          <text class="rank-stat">
            {{ sortByLabel }}: {{ item.value || 0 }}
          </text>
        </view>
        <text class="rank-value">{{ item.value || 0 }}</text>
      </view>

      <view class="empty" v-if="!userList.length && !loadingU">
        <text>暂无排行数据</text>
      </view>

      <view class="loading-more" v-if="loadingU">
        <u-loading-icon size="28" />
        <text class="loading-text">加载中...</text>
      </view>

      <view class="no-more" v-if="!loadingU && finishedU && userList.length">
        <text>没有更多了</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { onReachBottom } from '@dcloudio/uni-app'
import { getQuestionRankings, getUserRankings } from '@/api/ranking'

const activeTab = ref('questions')
const sortBy = ref('exp')

// Questions
const questionList = ref([])
const loadingQ = ref(false)
const finishedQ = ref(false)
const pageQ = ref(1)

// Users
const userList = ref([])
const loadingU = ref(false)
const finishedU = ref(false)
const pageU = ref(1)

const pageSize = 20

const sortByLabel = computed(() => {
  const map = { exp: '经验值', questions: '题目数', confirms: '确认数' }
  return map[sortBy.value] || sortBy.value
})

const fetchQuestionRankings = async () => {
  if (loadingQ.value || finishedQ.value) return
  loadingQ.value = true
  try {
    const data = await getQuestionRankings({ page: pageQ.value, page_size: pageSize })
    const items = data?.items || []
    if (items.length < pageSize) {
      finishedQ.value = true
    }
    questionList.value = [...questionList.value, ...items]
    pageQ.value++
  } catch (e) {
    console.error('fetchQuestionRankings', e)
  } finally {
    loadingQ.value = false
  }
}

const fetchUserRankings = async () => {
  if (loadingU.value || finishedU.value) return
  loadingU.value = true
  try {
    const data = await getUserRankings({ sort_by: sortBy.value, page: pageU.value, page_size: pageSize })
    const items = data?.items || []
    if (items.length < pageSize) {
      finishedU.value = true
    }
    userList.value = [...userList.value, ...items]
    pageU.value++
  } catch (e) {
    console.error('fetchUserRankings', e)
  } finally {
    loadingU.value = false
  }
}

const switchTab = (tab) => {
  if (activeTab.value === tab) return
  activeTab.value = tab
  if (tab === 'questions' && !questionList.value.length) {
    fetchQuestionRankings()
  }
  if (tab === 'users' && !userList.value.length) {
    fetchUserRankings()
  }
}

const changeSortBy = (val) => {
  if (sortBy.value === val) return
  sortBy.value = val
  userList.value = []
  pageU.value = 1
  finishedU.value = false
  fetchUserRankings()
}

const goDetail = (id) => {
  uni.navigateTo({ url: `/pages/question-detail/index?id=${id}` })
}

onMounted(() => {
  fetchQuestionRankings()
})

onReachBottom(() => {
  if (activeTab.value === 'questions') {
    fetchQuestionRankings()
  } else {
    fetchUserRankings()
  }
})
</script>

<style lang="scss" scoped>
$brand: #4C84FF;

.container {
  min-height: 100vh;
  background: #f5f6fa;
}

.tab-bar {
  display: flex;
  background: #fff;
  padding: 0 60rpx;
  position: sticky;
  top: 0;
  z-index: 10;

  .tab-item {
    flex: 1;
    text-align: center;
    padding: 28rpx 0;
    font-size: 30rpx;
    color: #999;
    position: relative;
    transition: color 0.2s;

    &.active {
      color: $brand;
      font-weight: bold;
    }
  }

  .tab-indicator {
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

.sort-bar {
  display: flex;
  background: #fff;
  padding: 16rpx 24rpx;
  margin-bottom: 2rpx;
  gap: 16rpx;

  .sort-item {
    padding: 10rpx 28rpx;
    border-radius: 32rpx;
    font-size: 24rpx;
    color: #666;
    background: #f5f6fa;
    transition: all 0.2s;

    &.active {
      background: $brand;
      color: #fff;
    }
  }
}

.ranking-list {
  padding: 16rpx 24rpx;
}

.ranking-item {
  display: flex;
  align-items: center;
  background: #fff;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 12rpx;

  .rank-number {
    width: 52rpx;
    height: 52rpx;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 26rpx;
    font-weight: bold;
    color: #999;
    background: #f5f6fa;
    margin-right: 20rpx;
    flex-shrink: 0;
  }

  .rank-1 {
    background: linear-gradient(135deg, #FFD700, #FFA500);
    color: #fff;
  }

  .rank-2 {
    background: linear-gradient(135deg, #C0C0C0, #A0A0A0);
    color: #fff;
  }

  .rank-3 {
    background: linear-gradient(135deg, #CD7F32, #B8690E);
    color: #fff;
  }

  .rank-content {
    flex: 1;
    min-width: 0;
  }

  .rank-title {
    font-size: 28rpx;
    color: #333;
    display: block;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .rank-meta {
    display: flex;
    gap: 16rpx;
    margin-top: 8rpx;
  }

  .rank-stat {
    font-size: 22rpx;
    color: #999;
  }

  .rank-badge {
    display: flex;
    align-items: center;
    gap: 6rpx;
    flex-shrink: 0;
    margin-left: 16rpx;

    .badge-count {
      font-size: 24rpx;
      color: $brand;
      font-weight: 600;
    }
  }
}

.user-ranking-item {
  .user-avatar {
    width: 72rpx;
    height: 72rpx;
    border-radius: 50%;
    margin-right: 20rpx;
    flex-shrink: 0;
    background: #f0f0f0;
  }

  .user-name-row {
    display: flex;
    align-items: center;
    gap: 12rpx;
  }

  .level-badge {
    background: $brand;
    color: #fff;
    font-size: 18rpx;
    padding: 2rpx 10rpx;
    border-radius: 6rpx;
  }

  .rank-value {
    font-size: 32rpx;
    font-weight: bold;
    color: $brand;
    flex-shrink: 0;
    margin-left: 16rpx;
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
</style>
