<template>
  <view class="notes-page">
    <u-navbar title="我的笔记" leftIconColor="#333" bgColor="#fff" />

    <view v-if="list.length === 0 && !loading" class="empty-state">
      <u-empty mode="data" text="暂无笔记" />
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
        class="note-item"
        @click="goDetail(item)"
      >
        <text class="note-content">{{ item.content }}</text>

        <view v-if="item.question" class="question-info">
          <u-icon name="chat" size="26rpx" color="#999" />
          <text class="question-title">{{ item.question.title || item.question.content }}</text>
        </view>

        <view class="note-footer">
          <text class="update-time">{{ item.updated_at }}</text>
        </view>
      </view>

      <u-loadmore :status="loadStatus" />
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { get } from '@/utils/request'

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
    const res = await get('/v1/notes', { page: page.value, page_size: pageSize })
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
    console.error('获取笔记列表失败', e)
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
.notes-page {
  min-height: 100vh;
  background-color: #f5f6fa;
}

.empty-state {
  padding-top: 300rpx;
}

.scroll-area {
  height: calc(100vh - 88rpx);
}

.note-item {
  background-color: #fff;
  margin: 20rpx 24rpx 0;
  padding: 28rpx;
  border-radius: 16rpx;

  .note-content {
    font-size: 28rpx;
    color: #333;
    line-height: 1.6;
    display: -webkit-box;
    -webkit-line-clamp: 4;
    -webkit-box-orient: vertical;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .question-info {
    display: flex;
    align-items: center;
    gap: 10rpx;
    margin-top: 20rpx;
    padding: 16rpx 20rpx;
    background-color: #f8f8fa;
    border-radius: 10rpx;

    .question-title {
      font-size: 24rpx;
      color: #666;
      flex: 1;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
  }

  .note-footer {
    margin-top: 16rpx;
    display: flex;
    justify-content: flex-end;

    .update-time {
      font-size: 22rpx;
      color: #999;
    }
  }
}
</style>
