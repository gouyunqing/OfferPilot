<template>
  <view class="page">
    <!-- 导航栏 -->
    <u-navbar title="题目详情" leftIconColor="#333" bgColor="#fff" />

    <scroll-view scroll-y class="content" :style="{ paddingBottom: commentBarHeight + 'px' }">
      <!-- 加载中 -->
      <view class="loading-wrap" v-if="loading">
        <u-loading-icon mode="circle" />
      </view>

      <template v-if="detail && !loading">
        <!-- 题目主体 -->
        <view class="card question-card">
          <!-- 标签行 -->
          <view class="tag-row">
            <view class="q-tag" :class="'tag-' + detail.type">{{ typeLabel(detail.type) }}</view>
            <text class="round-tag" v-if="detail.round">{{ detail.round }}</text>
          </view>

          <!-- 公司标签 -->
          <view class="company-row" v-if="detail.companies && detail.companies.length">
            <view class="company-tag" v-for="c in detail.companies" :key="c.id">
              {{ c.name }}
            </view>
          </view>

          <!-- 职位与面试时间 -->
          <view class="meta-row">
            <text class="meta-item" v-if="detail.position">
              <u-icon name="bag" size="26" color="#999" /> {{ detail.position }}
            </text>
            <text class="meta-item" v-if="detail.interview_time">
              <u-icon name="clock" size="26" color="#999" /> {{ detail.interview_time }}
            </text>
          </view>

          <!-- 题目内容 -->
          <view class="q-content">{{ detail.content }}</view>

          <!-- 参考答案 -->
          <view class="answer-section" v-if="detail.answer">
            <text class="answer-title">参考答案</text>
            <view class="answer-body">{{ detail.answer }}</view>
          </view>

          <!-- 统计 -->
          <view class="stat-row">
            <text class="stat-item">{{ detail.confirm_count || 0 }} 确认</text>
            <text class="stat-item">{{ detail.comment_count || 0 }} 评论</text>
            <text class="stat-item">{{ detail.favorite_count || 0 }} 收藏</text>
          </view>
        </view>

        <!-- 操作按钮 -->
        <view class="action-bar">
          <view class="action-btn" :class="{ active: isFavorited }" @click="toggleFavorite">
            <u-icon :name="isFavorited ? 'heart-fill' : 'heart'" size="40" :color="isFavorited ? '#FF6B6B' : '#999'" />
            <text class="action-text">{{ isFavorited ? '已收藏' : '收藏' }}</text>
          </view>
          <view class="action-btn" :class="{ active: isConfirmed }" @click="handleConfirm">
            <u-icon :name="isConfirmed ? 'checkmark-circle-fill' : 'checkmark-circle'" size="40" :color="isConfirmed ? '#00C48C' : '#999'" />
            <text class="action-text">{{ isConfirmed ? '已确认' : '确认原题' }}</text>
          </view>
          <view class="action-btn" @click="handleAiAnswer">
            <u-icon name="reload" size="40" color="#4C84FF" />
            <text class="action-text ai-text">AI 回答</text>
          </view>
        </view>

        <!-- AI 回答区域 -->
        <view class="card ai-card" v-if="aiAnswer || aiLoading">
          <view class="ai-header">
            <text class="ai-title">AI 参考回答</text>
            <u-loading-icon mode="circle" size="24" v-if="aiLoading" />
          </view>
          <view class="ai-body">{{ aiAnswer }}<text class="cursor" v-if="aiLoading">|</text></view>
        </view>

        <!-- 评论区 -->
        <view class="card comment-section">
          <view class="comment-header">
            <text class="comment-title">评论 ({{ commentTotal }})</text>
          </view>

          <view class="comment-list" v-if="comments.length">
            <view class="comment-item" v-for="item in comments" :key="item.id">
              <image class="avatar" :src="item.user?.avatar || '/static/default-avatar.png'" mode="aspectFill" />
              <view class="comment-body">
                <view class="comment-top">
                  <text class="comment-name">{{ item.user?.nickname || '匿名用户' }}</text>
                  <text class="comment-time">{{ formatTime(item.created_at) }}</text>
                </view>
                <text class="comment-text">{{ item.content }}</text>
              </view>
            </view>
          </view>

          <view class="empty" v-if="!comments.length && !commentLoading">
            <text>暂无评论，快来发表第一条评论吧</text>
          </view>

          <!-- 加载更多 -->
          <view class="load-more" v-if="hasMoreComments" @click="loadMoreComments">
            <text>加载更多</text>
          </view>
        </view>
      </template>
    </scroll-view>

    <!-- 底部评论输入栏 -->
    <view class="comment-input-bar" v-if="detail" ref="commentBarRef">
      <input
        class="comment-input"
        v-model="commentText"
        placeholder="写评论..."
        confirm-type="send"
        @confirm="submitComment"
      />
      <view class="send-btn" :class="{ disabled: !commentText.trim() }" @click="submitComment">
        <text>发送</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { getQuestionDetail, getComments, createComment, confirmQuestion } from '@/api/question'
import { addFavorite, removeFavorite } from '@/api/favorite'
import { useUserStore } from '@/store/user'

const userStore = useUserStore()

// --- 页面参数 ---
const questionId = ref('')

// --- 题目详情 ---
const detail = ref(null)
const loading = ref(true)
const isFavorited = ref(false)
const isConfirmed = ref(false)

// --- AI 回答 ---
const aiAnswer = ref('')
const aiLoading = ref(false)

// --- 评论 ---
const comments = ref([])
const commentText = ref('')
const commentPage = ref(1)
const commentTotal = ref(0)
const commentLoading = ref(false)
const commentBarHeight = ref(100)

const hasMoreComments = computed(() => comments.value.length < commentTotal.value)

const typeLabel = (type) => {
  const map = { bagu: '八股文', algorithm: '算法', system_design: '系统设计', behavior: '行为面', project: '项目' }
  return map[type] || type
}

const formatTime = (time) => {
  if (!time) return ''
  const d = new Date(time)
  const now = new Date()
  const diff = (now - d) / 1000
  if (diff < 60) return '刚刚'
  if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`
  if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`
  if (diff < 2592000) return `${Math.floor(diff / 86400)}天前`
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

// --- 获取题目详情 ---
const fetchDetail = async () => {
  loading.value = true
  try {
    const data = await getQuestionDetail(questionId.value)
    detail.value = data
    isFavorited.value = !!data.is_favorited
    isConfirmed.value = !!data.is_confirmed
  } catch (e) {
    uni.showToast({ title: '加载失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

// --- 获取评论 ---
const fetchComments = async (page = 1) => {
  commentLoading.value = true
  try {
    const data = await getComments(questionId.value, { page, page_size: 20 })
    if (page === 1) {
      comments.value = data.items || []
    } else {
      comments.value.push(...(data.items || []))
    }
    commentTotal.value = data.total || 0
    commentPage.value = page
  } catch (e) {
    console.error('获取评论失败', e)
  } finally {
    commentLoading.value = false
  }
}

const loadMoreComments = () => {
  if (commentLoading.value) return
  fetchComments(commentPage.value + 1)
}

// --- 发送评论 ---
const submitComment = async () => {
  const text = commentText.value.trim()
  if (!text) return

  if (!userStore.isLoggedIn) {
    uni.navigateTo({ url: '/pages/login/index' })
    return
  }

  try {
    await createComment(questionId.value, text)
    commentText.value = ''
    uni.showToast({ title: '评论成功', icon: 'success' })
    fetchComments(1)
    // 更新评论数
    if (detail.value) {
      detail.value.comment_count = (detail.value.comment_count || 0) + 1
    }
  } catch (e) {
    uni.showToast({ title: '评论失败', icon: 'none' })
  }
}

// --- 收藏 ---
const toggleFavorite = async () => {
  if (!userStore.isLoggedIn) {
    uni.navigateTo({ url: '/pages/login/index' })
    return
  }

  try {
    if (isFavorited.value) {
      await removeFavorite(questionId.value)
      isFavorited.value = false
      if (detail.value) detail.value.favorite_count = Math.max(0, (detail.value.favorite_count || 0) - 1)
      uni.showToast({ title: '取消收藏', icon: 'none' })
    } else {
      await addFavorite(questionId.value)
      isFavorited.value = true
      if (detail.value) detail.value.favorite_count = (detail.value.favorite_count || 0) + 1
      uni.showToast({ title: '收藏成功', icon: 'success' })
    }
  } catch (e) {
    uni.showToast({ title: '操作失败', icon: 'none' })
  }
}

// --- 确认原题 ---
const handleConfirm = async () => {
  if (!userStore.isLoggedIn) {
    uni.navigateTo({ url: '/pages/login/index' })
    return
  }

  if (isConfirmed.value) {
    uni.showToast({ title: '你已确认过', icon: 'none' })
    return
  }

  try {
    await confirmQuestion(questionId.value)
    isConfirmed.value = true
    if (detail.value) detail.value.confirm_count = (detail.value.confirm_count || 0) + 1
    uni.showToast({ title: '确认成功', icon: 'success' })
  } catch (e) {
    uni.showToast({ title: '确认失败', icon: 'none' })
  }
}

// --- AI 回答 (SSE 流式) ---
const handleAiAnswer = () => {
  if (aiLoading.value) return

  if (!userStore.isLoggedIn) {
    uni.navigateTo({ url: '/pages/login/index' })
    return
  }

  aiAnswer.value = ''
  aiLoading.value = true

  const token = uni.getStorageSync('access_token') || ''

  // 使用 uni.request 进行 SSE 流式请求
  // 在 H5 端使用 fetch + ReadableStream，小程序端使用 enableChunked
  // #ifdef H5
  const baseUrl = 'http://127.0.0.1:8001'
  fetch(`${baseUrl}/v1/ai/answer`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : '',
      'Accept': 'text/event-stream',
    },
    body: JSON.stringify({ question_id: questionId.value }),
  })
    .then(async (response) => {
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })

        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            if (data === '[DONE]') {
              aiLoading.value = false
              return
            }
            try {
              const parsed = JSON.parse(data)
              if (parsed.content) {
                aiAnswer.value += parsed.content
              }
            } catch {
              // 纯文本模式
              aiAnswer.value += data
            }
          }
        }
      }
      aiLoading.value = false
    })
    .catch((err) => {
      console.error('AI 回答失败', err)
      aiLoading.value = false
      uni.showToast({ title: 'AI 回答失败', icon: 'none' })
    })
  // #endif

  // #ifndef H5
  const requestTask = uni.request({
    url: 'http://127.0.0.1:8001/v1/ai/answer',
    method: 'POST',
    header: {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : '',
      'Accept': 'text/event-stream',
    },
    data: { question_id: questionId.value },
    enableChunked: true,
    success: () => {
      aiLoading.value = false
    },
    fail: (err) => {
      console.error('AI 回答失败', err)
      aiLoading.value = false
      uni.showToast({ title: 'AI 回答失败', icon: 'none' })
    },
  })

  let sseBuffer = ''
  requestTask.onChunkReceived?.((res) => {
    const text = typeof res.data === 'string' ? res.data : new TextDecoder().decode(new Uint8Array(res.data))
    sseBuffer += text
    const lines = sseBuffer.split('\n')
    sseBuffer = lines.pop() || ''

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = line.slice(6)
        if (data === '[DONE]') {
          aiLoading.value = false
          return
        }
        try {
          const parsed = JSON.parse(data)
          if (parsed.content) {
            aiAnswer.value += parsed.content
          }
        } catch {
          aiAnswer.value += data
        }
      }
    }
  })
  // #endif
}

// --- 生命周期 ---
onLoad((options) => {
  questionId.value = options.id
  if (!questionId.value) {
    uni.showToast({ title: '参数错误', icon: 'none' })
    setTimeout(() => uni.navigateBack(), 1500)
    return
  }
  fetchDetail()
  fetchComments(1)
})
</script>

<style lang="scss" scoped>
$brand: #4C84FF;

.page {
  min-height: 100vh;
  background: #f5f6fa;
}

.content {
  height: calc(100vh - var(--status-bar-height) - 88rpx);
  padding: 24rpx;
  box-sizing: border-box;
}

.loading-wrap {
  display: flex;
  justify-content: center;
  padding: 120rpx 0;
}

.card {
  background: #fff;
  border-radius: 16rpx;
  padding: 28rpx;
  margin-bottom: 24rpx;
}

// --- 题目卡片 ---
.question-card {
  .tag-row {
    display: flex;
    align-items: center;
    gap: 12rpx;
    margin-bottom: 16rpx;
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

  .round-tag {
    font-size: 22rpx;
    padding: 4rpx 14rpx;
    border-radius: 6rpx;
    background: #f0f4ff;
    color: $brand;
  }

  .company-row {
    display: flex;
    flex-wrap: wrap;
    gap: 10rpx;
    margin-bottom: 16rpx;
  }

  .company-tag {
    font-size: 22rpx;
    padding: 6rpx 16rpx;
    border-radius: 20rpx;
    background: #f7f7f7;
    color: #555;
  }

  .meta-row {
    display: flex;
    flex-wrap: wrap;
    gap: 24rpx;
    margin-bottom: 20rpx;
  }

  .meta-item {
    display: flex;
    align-items: center;
    gap: 6rpx;
    font-size: 24rpx;
    color: #999;
  }

  .q-content {
    font-size: 30rpx;
    color: #1a1a2e;
    line-height: 1.7;
    margin-bottom: 24rpx;
    word-break: break-all;
  }

  .answer-section {
    background: #f8f9fd;
    border-radius: 12rpx;
    padding: 20rpx;
    margin-bottom: 24rpx;

    .answer-title {
      font-size: 26rpx;
      font-weight: bold;
      color: $brand;
      margin-bottom: 12rpx;
      display: block;
    }

    .answer-body {
      font-size: 28rpx;
      color: #444;
      line-height: 1.7;
      white-space: pre-wrap;
      word-break: break-all;
    }
  }

  .stat-row {
    display: flex;
    gap: 32rpx;
    padding-top: 16rpx;
    border-top: 1rpx solid #f0f0f0;
  }

  .stat-item {
    font-size: 22rpx;
    color: #999;
  }
}

// --- 操作按钮 ---
.action-bar {
  display: flex;
  justify-content: space-around;
  background: #fff;
  border-radius: 16rpx;
  padding: 24rpx 0;
  margin-bottom: 24rpx;

  .action-btn {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8rpx;

    .action-text {
      font-size: 22rpx;
      color: #999;
    }

    .ai-text {
      color: $brand;
    }

    &.active .action-text {
      color: #333;
    }
  }
}

// --- AI 回答 ---
.ai-card {
  .ai-header {
    display: flex;
    align-items: center;
    gap: 12rpx;
    margin-bottom: 16rpx;
  }

  .ai-title {
    font-size: 28rpx;
    font-weight: bold;
    color: $brand;
  }

  .ai-body {
    font-size: 28rpx;
    color: #333;
    line-height: 1.8;
    white-space: pre-wrap;
    word-break: break-all;
  }

  .cursor {
    color: $brand;
    animation: blink 0.8s infinite;
  }
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

// --- 评论区 ---
.comment-section {
  .comment-header {
    margin-bottom: 20rpx;
  }

  .comment-title {
    font-size: 28rpx;
    font-weight: bold;
    color: #1a1a2e;
  }
}

.comment-list {
  .comment-item {
    display: flex;
    gap: 16rpx;
    padding: 20rpx 0;
    border-bottom: 1rpx solid #f5f5f5;

    &:last-child {
      border-bottom: none;
    }
  }

  .avatar {
    width: 64rpx;
    height: 64rpx;
    border-radius: 50%;
    flex-shrink: 0;
    background: #eee;
  }

  .comment-body {
    flex: 1;
    min-width: 0;
  }

  .comment-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8rpx;
  }

  .comment-name {
    font-size: 24rpx;
    font-weight: 500;
    color: #333;
  }

  .comment-time {
    font-size: 22rpx;
    color: #bbb;
  }

  .comment-text {
    font-size: 26rpx;
    color: #555;
    line-height: 1.6;
    word-break: break-all;
  }
}

.load-more {
  text-align: center;
  padding: 20rpx 0;
  color: $brand;
  font-size: 24rpx;
}

.empty {
  text-align: center;
  padding: 48rpx 0;
  color: #ccc;
  font-size: 26rpx;
}

// --- 底部评论输入栏 ---
.comment-input-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 16rpx 24rpx;
  padding-bottom: calc(16rpx + env(safe-area-inset-bottom));
  background: #fff;
  box-shadow: 0 -2rpx 10rpx rgba(0, 0, 0, 0.05);
  z-index: 100;

  .comment-input {
    flex: 1;
    height: 68rpx;
    background: #f5f6fa;
    border-radius: 34rpx;
    padding: 0 28rpx;
    font-size: 28rpx;
    color: #333;
  }

  .send-btn {
    flex-shrink: 0;
    background: $brand;
    color: #fff;
    font-size: 26rpx;
    padding: 14rpx 32rpx;
    border-radius: 34rpx;

    &.disabled {
      opacity: 0.5;
    }
  }
}
</style>
