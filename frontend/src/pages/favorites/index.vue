<template>
  <view class="favorites-page">
    <u-navbar title="我的收藏" leftIconColor="#333" bgColor="#fff" />

    <view v-if="list.length === 0 && !loading" class="empty-state">
      <u-empty mode="data" text="暂无收藏内容" />
    </view>

    <scroll-view
      v-else
      scroll-y
      class="scroll-area"
      refresher-enabled
      :refresher-triggered="refreshing"
      @refresherrefresh="onRefresh"
      @scrolltolower="loadMore"
    >
      <view
        v-for="item in list"
        :key="item.id"
        class="favorite-item"
        @click="goDetail(item)"
      >
        <view class="item-header">
          <u-tag
            :text="item.type || '面试题'"
            size="mini"
            type="primary"
            plain
          />
          <text v-if="item.company" class="company-name">{{ item.company }}</text>
        </view>
        <text class="item-content">{{ item.content }}</text>
        <view class="item-footer">
          <text class="time-text">{{ item.created_at }}</text>
        </view>
      </view>

      <u-loadmore :status="loadStatus" />
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getFavorites } from '@/api/favorite'

const list = ref([])
const page = ref(1)
const pageSize = 20
const loading = ref(false)
const refreshing = ref(false)
const loadStatus = ref('loadmore')
const total = ref(0)

const fetchList = async (isRefresh = false) => {
  if (loading.value) return
  loading.value = true

  if (isRefresh) {
    page.value = 1
    loadStatus.value = 'loadmore'
  }

  try {
    const res = await getFavorites({ page: page.value, page_size: pageSize })
    const data = res.data || {}
    const items = data.items || data.list || []
    total.value = data.total || 0

    if (isRefresh) {
      list.value = items
    } else {
      list.value = [...list.value, ...items]
    }

    if (list.value.length >= total.value) {
      loadStatus.value = 'nomore'
    } else {
      loadStatus.value = 'loadmore'
    }
  } catch (e) {
    console.error('获取收藏列表失败', e)
    loadStatus.value = 'loadmore'
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

const onRefresh = () => {
  refreshing.value = true
  fetchList(true)
}

const loadMore = () => {
  if (loadStatus.value === 'nomore' || loading.value) return
  page.value++
  loadStatus.value = 'loading'
  fetchList()
}

const goDetail = (item) => {
  uni.navigateTo({
    url: `/pages/question/detail?id=${item.question_id || item.id}`
  })
}

onMounted(() => {
  fetchList(true)
})
</script>

<style lang="scss" scoped>
.favorites-page {
  min-height: 100vh;
  background-color: #f5f6fa;
}

.empty-state {
  padding-top: 300rpx;
}

.scroll-area {
  height: calc(100vh - 88rpx);
}

.favorite-item {
  background-color: #fff;
  margin: 20rpx 24rpx 0;
  padding: 28rpx;
  border-radius: 16rpx;

  .item-header {
    display: flex;
    align-items: center;
    gap: 16rpx;
    margin-bottom: 16rpx;

    .company-name {
      font-size: 24rpx;
      color: #666;
    }
  }

  .item-content {
    font-size: 28rpx;
    color: #333;
    line-height: 1.6;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .item-footer {
    margin-top: 16rpx;
    display: flex;
    justify-content: flex-end;

    .time-text {
      font-size: 22rpx;
      color: #999;
    }
  }
}
</style>
