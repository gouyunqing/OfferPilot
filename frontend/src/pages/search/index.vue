<template>
  <view class="page">
    <!-- 顶部搜索栏 -->
    <view class="search-header">
      <view class="search-wrap">
        <u-icon name="search" size="30" color="#999" />
        <input
          class="search-input"
          ref="searchInputRef"
          v-model="keyword"
          placeholder="搜索面试题目..."
          focus
          confirm-type="search"
          @confirm="doSearch"
          @input="onInput"
        />
        <u-icon
          v-if="keyword"
          name="close-circle-fill"
          size="30"
          color="#ccc"
          @click="clearKeyword"
        />
      </view>
      <text class="cancel-btn" @click="goBack">取消</text>
    </view>

    <scroll-view scroll-y class="content">
      <!-- 搜索结果 -->
      <template v-if="keyword && hasSearched">
        <view class="result-section">
          <view
            class="question-card"
            v-for="item in results"
            :key="item.id"
            @click="goDetail(item.id)"
          >
            <view class="q-top">
              <view class="q-tag" :class="'tag-' + item.type">{{ typeLabel(item.type) }}</view>
              <text class="q-company" v-if="item.companies && item.companies.length">
                {{ item.companies[0].name }}
              </text>
            </view>
            <text class="q-content">{{ item.content_preview || item.content }}</text>
            <view class="q-bottom">
              <text class="q-stat">{{ item.confirm_count || 0 }} 确认</text>
              <text class="q-stat">{{ item.comment_count || 0 }} 评论</text>
              <text class="q-stat">{{ item.favorite_count || 0 }} 收藏</text>
            </view>
          </view>

          <!-- 加载更多 -->
          <view class="load-more" v-if="hasMore" @click="loadMore">
            <text>加载更多</text>
          </view>

          <view class="empty" v-if="!results.length && !searching">
            <text>没有找到相关题目</text>
          </view>

          <view class="loading-wrap" v-if="searching">
            <u-loading-icon mode="circle" />
          </view>
        </view>
      </template>

      <!-- 默认状态：历史 + 热搜 -->
      <template v-if="!keyword || !hasSearched">
        <!-- 搜索历史 -->
        <view class="section" v-if="history.length">
          <view class="section-header">
            <text class="section-title">搜索历史</text>
            <text class="section-clear" @click="clearHistory">清除</text>
          </view>
          <view class="tag-list">
            <view
              class="history-tag"
              v-for="(item, idx) in history"
              :key="idx"
              @click="selectKeyword(item)"
            >
              {{ item }}
            </view>
          </view>
        </view>

        <!-- 热门搜索 -->
        <view class="section" v-if="hotTags.length">
          <view class="section-header">
            <text class="section-title">热门搜索</text>
          </view>
          <view class="tag-list">
            <view
              class="hot-tag"
              v-for="(item, idx) in hotTags"
              :key="idx"
              @click="selectKeyword(item)"
            >
              <text class="hot-index" :class="{ top: idx < 3 }">{{ idx + 1 }}</text>
              <text class="hot-text">{{ item }}</text>
            </view>
          </view>
        </view>
      </template>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { searchQuestions } from '@/api/question'

const HISTORY_KEY = 'search_history'
const MAX_HISTORY = 20

// --- 状态 ---
const keyword = ref('')
const results = ref([])
const searching = ref(false)
const hasSearched = ref(false)
const page = ref(1)
const total = ref(0)
const hasMore = ref(false)

const history = ref([])
const hotTags = ref([
  'JavaScript', 'React', 'Vue', 'CSS', '算法',
  '系统设计', 'HTTP', 'TypeScript', '数据库', '操作系统',
])

let debounceTimer = null

const typeLabel = (type) => {
  const map = { bagu: '八股文', algorithm: '算法', system_design: '系统设计', behavior: '行为面', project: '项目' }
  return map[type] || type
}

// --- 搜索历史 ---
const loadHistory = () => {
  try {
    const raw = uni.getStorageSync(HISTORY_KEY)
    history.value = raw ? JSON.parse(raw) : []
  } catch {
    history.value = []
  }
}

const saveHistory = (kw) => {
  const trimmed = kw.trim()
  if (!trimmed) return
  const list = history.value.filter((h) => h !== trimmed)
  list.unshift(trimmed)
  if (list.length > MAX_HISTORY) list.length = MAX_HISTORY
  history.value = list
  uni.setStorageSync(HISTORY_KEY, JSON.stringify(list))
}

const clearHistory = () => {
  history.value = []
  uni.removeStorageSync(HISTORY_KEY)
}

// --- 搜索 ---
const doSearch = async (isLoadMore = false) => {
  const kw = keyword.value.trim()
  if (!kw) return

  if (!isLoadMore) {
    page.value = 1
    results.value = []
  }

  searching.value = true
  hasSearched.value = true

  try {
    const data = await searchQuestions({ keyword: kw, page: page.value, page_size: 20 })
    const items = data.items || []

    if (isLoadMore) {
      results.value.push(...items)
    } else {
      results.value = items
      saveHistory(kw)
    }

    total.value = data.total || 0
    hasMore.value = results.value.length < total.value
  } catch (e) {
    console.error('搜索失败', e)
    if (!isLoadMore) {
      results.value = []
    }
  } finally {
    searching.value = false
  }
}

const loadMore = () => {
  if (searching.value) return
  page.value += 1
  doSearch(true)
}

// --- 防抖输入 ---
const onInput = () => {
  clearTimeout(debounceTimer)
  if (!keyword.value.trim()) {
    hasSearched.value = false
    results.value = []
    return
  }
  debounceTimer = setTimeout(() => {
    doSearch()
  }, 300)
}

const clearKeyword = () => {
  keyword.value = ''
  hasSearched.value = false
  results.value = []
}

const selectKeyword = (kw) => {
  keyword.value = kw
  doSearch()
}

// --- 导航 ---
const goBack = () => {
  uni.navigateBack()
}

const goDetail = (id) => {
  uni.navigateTo({ url: `/pages/question-detail/index?id=${id}` })
}

// --- 生命周期 ---
onMounted(() => {
  loadHistory()
})

onUnmounted(() => {
  clearTimeout(debounceTimer)
})
</script>

<style lang="scss" scoped>
$brand: #4C84FF;

.page {
  min-height: 100vh;
  background: #f5f6fa;
}

// --- 搜索头部 ---
.search-header {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 16rpx 24rpx;
  padding-top: calc(16rpx + var(--status-bar-height));
  background: #fff;

  .search-wrap {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 12rpx;
    background: #f5f6fa;
    border-radius: 36rpx;
    padding: 14rpx 24rpx;
  }

  .search-input {
    flex: 1;
    font-size: 28rpx;
    color: #333;
  }

  .cancel-btn {
    flex-shrink: 0;
    font-size: 28rpx;
    color: #666;
    padding: 8rpx;
  }
}

.content {
  height: calc(100vh - var(--status-bar-height) - 100rpx);
  padding: 24rpx;
  box-sizing: border-box;
}

// --- 区块 ---
.section {
  margin-bottom: 36rpx;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.section-title {
  font-size: 30rpx;
  font-weight: bold;
  color: #1a1a2e;
}

.section-clear {
  font-size: 24rpx;
  color: #999;
}

// --- 标签 ---
.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.history-tag {
  font-size: 24rpx;
  color: #555;
  background: #fff;
  padding: 12rpx 24rpx;
  border-radius: 24rpx;
}

.hot-tag {
  display: flex;
  align-items: center;
  gap: 8rpx;
  width: calc(50% - 8rpx);
  padding: 16rpx 0;

  .hot-index {
    width: 36rpx;
    font-size: 24rpx;
    font-weight: bold;
    color: #999;
    text-align: center;

    &.top {
      color: $brand;
    }
  }

  .hot-text {
    font-size: 26rpx;
    color: #333;
  }
}

// --- 题目卡片 (与首页一致) ---
.question-card {
  background: #fff;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 16rpx;
}

.q-top {
  display: flex;
  align-items: center;
  margin-bottom: 12rpx;
}

.q-tag {
  font-size: 22rpx;
  padding: 4rpx 12rpx;
  border-radius: 6rpx;
  margin-right: 12rpx;
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
}

.q-content {
  font-size: 28rpx;
  color: #333;
  line-height: 1.5;
  margin-bottom: 12rpx;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.q-bottom {
  display: flex;
  gap: 24rpx;
}

.q-stat {
  font-size: 22rpx;
  color: #999;
}

// --- 加载/空状态 ---
.loading-wrap {
  display: flex;
  justify-content: center;
  padding: 48rpx 0;
}

.load-more {
  text-align: center;
  padding: 24rpx 0;
  color: $brand;
  font-size: 24rpx;
}

.empty {
  text-align: center;
  padding: 80rpx 0;
  color: #ccc;
  font-size: 28rpx;
}
</style>
