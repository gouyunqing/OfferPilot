<template>
  <view class="questions-page">
    <!-- 类型筛选 -->
    <scroll-view scroll-x class="filter-tabs">
      <view
        class="filter-tab"
        :class="{ active: currentType === item.value }"
        v-for="item in typeOptions"
        :key="item.value"
        @click="switchType(item.value)"
      >
        <text>{{ item.label }}</text>
      </view>
    </scroll-view>

    <!-- 排序选择 -->
    <view class="sort-bar">
      <view
        class="sort-item"
        :class="{ active: currentSort === item.value }"
        v-for="item in sortOptions"
        :key="item.value"
        @click="switchSort(item.value)"
      >
        <text>{{ item.label }}</text>
      </view>
    </view>

    <!-- 题目列表 -->
    <view class="question-list">
      <view
        class="question-card"
        v-for="item in list"
        :key="item.id"
        @click="goDetail(item.id)"
      >
        <view class="card-top">
          <view class="q-tag" :class="'tag-' + item.type">{{ typeLabel(item.type) }}</view>
          <text class="q-company" v-if="item.companies && item.companies.length">
            {{ item.companies[0].name }}
          </text>
          <text class="q-recruit" v-if="item.recruit_type">
            {{ recruitLabel(item.recruit_type) }}
          </text>
        </view>
        <text class="card-content">{{ item.content_preview }}</text>
        <view class="card-bottom">
          <view class="stat-item">
            <u-icon name="checkmark-circle" size="28" color="#999" />
            <text class="stat-num">{{ item.confirm_count || 0 }}</text>
          </view>
          <view class="stat-item">
            <u-icon name="chat" size="28" color="#999" />
            <text class="stat-num">{{ item.comment_count || 0 }}</text>
          </view>
          <view class="stat-item">
            <u-icon name="star" size="28" color="#999" />
            <text class="stat-num">{{ item.favorite_count || 0 }}</text>
          </view>
        </view>
      </view>

      <!-- 加载状态 -->
      <u-loadmore :status="loadStatus" :loading-text="'加载中...'" :nomore-text="'没有更多了'" />

      <!-- 空状态 -->
      <view class="empty" v-if="!list.length && loadStatus !== 'loading'">
        <text>暂无题目</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { onLoad, onReachBottom, onPullDownRefresh } from '@dcloudio/uni-app'
import { getQuestions } from '@/api/question'

// 类型选项
const typeOptions = [
  { label: '全部', value: '' },
  { label: '八股文', value: 'bagu' },
  { label: '算法', value: 'algorithm' },
  { label: '系统设计', value: 'system_design' },
  { label: '行为面', value: 'behavior' },
  { label: '项目', value: 'project' },
]

const sortOptions = [
  { label: '最新', value: 'latest' },
  { label: '最热', value: 'hot' },
  { label: '最多确认', value: 'most_confirmed' },
]

const typeLabel = (type) => {
  const map = { bagu: '八股文', algorithm: '算法', system_design: '系统设计', behavior: '行为面', project: '项目' }
  return map[type] || type
}

const recruitLabel = (type) => {
  const map = { campus: '校招', social: '社招', intern: '实习' }
  return map[type] || type
}

// 查询参数
const companyId = ref('')
const recruitType = ref('')
const currentType = ref('')
const currentSort = ref('latest')

// 列表数据
const list = ref([])
const page = ref(1)
const pageSize = 20
const total = ref(0)
const loadStatus = ref('loadmore') // loadmore | loading | nomore

onLoad((query) => {
  if (query.company_id) companyId.value = query.company_id
  if (query.type) currentType.value = query.type
  if (query.recruit_type) recruitType.value = query.recruit_type
  fetchList(true)
})

async function fetchList(reset = false) {
  if (loadStatus.value === 'loading') return

  if (reset) {
    page.value = 1
    list.value = []
  }

  loadStatus.value = 'loading'

  try {
    const params = {
      page: page.value,
      page_size: pageSize,
      sort: currentSort.value,
    }
    if (currentType.value) params.type = currentType.value
    if (companyId.value) params.company_id = companyId.value
    if (recruitType.value) params.recruit_type = recruitType.value

    const data = await getQuestions(params)
    const items = data?.items || []
    total.value = data?.total || 0

    if (reset) {
      list.value = items
    } else {
      list.value = [...list.value, ...items]
    }

    if (list.value.length >= total.value || items.length < pageSize) {
      loadStatus.value = 'nomore'
    } else {
      loadStatus.value = 'loadmore'
      page.value++
    }
  } catch (e) {
    console.error('获取题目列表失败', e)
    loadStatus.value = 'loadmore'
    uni.showToast({ title: '加载失败', icon: 'none' })
  }
}

function switchType(type) {
  if (currentType.value === type) return
  currentType.value = type
  fetchList(true)
}

function switchSort(sort) {
  if (currentSort.value === sort) return
  currentSort.value = sort
  fetchList(true)
}

function goDetail(id) {
  uni.navigateTo({ url: `/pages/question-detail/index?id=${id}` })
}

// 下拉刷新
onPullDownRefresh(async () => {
  await fetchList(true)
  uni.stopPullDownRefresh()
})

// 触底加载更多
onReachBottom(() => {
  if (loadStatus.value === 'loadmore') {
    fetchList()
  }
})
</script>

<style lang="scss" scoped>
$brand: #4C84FF;

.questions-page {
  min-height: 100vh;
  background: #f5f6fa;
  padding-bottom: 24rpx;
}

/* 类型筛选 */
.filter-tabs {
  white-space: nowrap;
  background: #fff;
  padding: 20rpx 24rpx;

  .filter-tab {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 12rpx 28rpx;
    margin-right: 16rpx;
    border-radius: 32rpx;
    font-size: 26rpx;
    color: #666;
    background: #f5f6fa;
    transition: all 0.2s;

    &.active {
      color: #fff;
      background: $brand;
    }
  }
}

/* 排序栏 */
.sort-bar {
  display: flex;
  align-items: center;
  background: #fff;
  padding: 16rpx 24rpx;
  border-top: 1rpx solid #f0f0f0;
  gap: 32rpx;

  .sort-item {
    font-size: 26rpx;
    color: #999;
    position: relative;
    padding-bottom: 8rpx;

    &.active {
      color: $brand;
      font-weight: bold;

      &::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 32rpx;
        height: 4rpx;
        border-radius: 2rpx;
        background: $brand;
      }
    }
  }
}

/* 题目列表 */
.question-list {
  padding: 24rpx;
}

.question-card {
  background: #fff;
  border-radius: 16rpx;
  padding: 28rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);

  .card-top {
    display: flex;
    align-items: center;
    margin-bottom: 16rpx;
    flex-wrap: wrap;
    gap: 12rpx;
  }

  .q-tag {
    font-size: 22rpx;
    padding: 4rpx 14rpx;
    border-radius: 6rpx;
    color: #fff;
  }

  .tag-bagu { background: $brand; }
  .tag-algorithm { background: #FF6B6B; }
  .tag-system_design { background: #00C48C; }
  .tag-behavior { background: #FF9F43; }
  .tag-project { background: #845EF7; }

  .q-company {
    font-size: 24rpx;
    color: #666;
    background: #f5f6fa;
    padding: 4rpx 12rpx;
    border-radius: 6rpx;
  }

  .q-recruit {
    font-size: 22rpx;
    color: #999;
    background: #f5f6fa;
    padding: 4rpx 10rpx;
    border-radius: 6rpx;
  }

  .card-content {
    font-size: 28rpx;
    color: #333;
    line-height: 1.6;
    margin-bottom: 16rpx;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    text-overflow: ellipsis;
    word-break: break-all;
  }

  .card-bottom {
    display: flex;
    gap: 32rpx;

    .stat-item {
      display: flex;
      align-items: center;
      gap: 6rpx;

      .stat-num {
        font-size: 22rpx;
        color: #999;
      }
    }
  }
}

.empty {
  text-align: center;
  padding: 100rpx 0;
  color: #ccc;
  font-size: 28rpx;
}
</style>
