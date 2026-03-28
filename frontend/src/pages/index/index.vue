<template>
  <view class="container">
    <!-- 搜索栏 -->
    <view class="search-bar" @click="goSearch">
      <u-icon name="search" size="32" color="#999"></u-icon>
      <text class="search-placeholder">搜索面试题目...</text>
    </view>

    <!-- 公司列表 -->
    <view class="section">
      <view class="section-title">热门公司</view>
      <scroll-view scroll-x class="company-scroll">
        <view class="company-item" v-for="item in companies" :key="item.id" @click="goCompany(item.id)">
          <image class="company-logo" :src="item.logo || '/static/default-company.png'" mode="aspectFit" />
          <text class="company-name">{{ item.name }}</text>
          <text class="company-count">{{ item.question_count || 0 }}题</text>
        </view>
      </scroll-view>
    </view>

    <!-- 热门题目 -->
    <view class="section">
      <view class="section-header">
        <text class="section-title">热门题目</text>
        <text class="section-more" @click="goRankings">查看更多</text>
      </view>
      <view class="question-card" v-for="item in hotQuestions" :key="item.id" @click="goDetail(item.id)">
        <view class="q-top">
          <view class="q-tag" :class="'tag-' + item.type">{{ typeLabel(item.type) }}</view>
          <text class="q-company" v-if="item.companies.length">{{ item.companies[0].name }}</text>
        </view>
        <text class="q-content">{{ item.content_preview }}</text>
        <view class="q-bottom">
          <text class="q-stat">{{ item.confirm_count }} 确认</text>
          <text class="q-stat">{{ item.comment_count }} 评论</text>
          <text class="q-stat">{{ item.favorite_count }} 收藏</text>
        </view>
      </view>

      <view class="empty" v-if="!hotQuestions.length && !loading">
        <text>暂无热门题目</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getHotQuestions } from '@/api/question'
import { getCompanies, getCompanyStats } from '@/api/meta'

const companies = ref([])
const hotQuestions = ref([])
const loading = ref(true)

const typeLabel = (type) => {
  const map = { bagu: '八股文', algorithm: '算法', system_design: '系统设计', behavior: '行为面', project: '项目' }
  return map[type] || type
}

onMounted(async () => {
  try {
    const [compList, stats, hot] = await Promise.all([
      getCompanies(),
      getCompanyStats().catch(() => []),
      getHotQuestions({ period: 'month', page: 1, page_size: 10 }),
    ])
    const statsMap = {}
    if (Array.isArray(stats)) {
      stats.forEach(s => { statsMap[s.company_id] = s.question_count })
    }
    companies.value = (compList || []).map(c => ({ ...c, question_count: statsMap[c.id] || 0 }))
    hotQuestions.value = hot?.items || []
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})

const goSearch = () => uni.navigateTo({ url: '/pages/search/index' })
const goCompany = (id) => uni.navigateTo({ url: `/pages/questions/index?company_id=${id}` })
const goDetail = (id) => uni.navigateTo({ url: `/pages/question-detail/index?id=${id}` })
const goRankings = () => uni.switchTab({ url: '/pages/rankings/index' })
</script>

<style lang="scss" scoped>
.search-bar {
  display: flex; align-items: center; background: #fff;
  border-radius: 40rpx; padding: 16rpx 24rpx; margin-bottom: 24rpx;
  .search-placeholder { color: #999; margin-left: 12rpx; font-size: 28rpx; }
}
.section { margin-bottom: 24rpx; }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16rpx; }
.section-title { font-size: 32rpx; font-weight: bold; color: #1a1a2e; margin-bottom: 16rpx; }
.section-more { font-size: 24rpx; color: #4C84FF; }
.company-scroll { white-space: nowrap; }
.company-item { display: inline-flex; flex-direction: column; align-items: center; width: 140rpx; margin-right: 16rpx; }
.company-logo { width: 80rpx; height: 80rpx; border-radius: 16rpx; background: #f0f0f0; }
.company-name { font-size: 24rpx; color: #333; margin-top: 8rpx; }
.company-count { font-size: 20rpx; color: #999; }
.question-card { background: #fff; border-radius: 16rpx; padding: 24rpx; margin-bottom: 16rpx; }
.q-top { display: flex; align-items: center; margin-bottom: 12rpx; }
.q-tag { font-size: 22rpx; padding: 4rpx 12rpx; border-radius: 6rpx; margin-right: 12rpx; color: #fff; }
.tag-bagu { background: #4C84FF; }
.tag-algorithm { background: #FF6B6B; }
.tag-system_design { background: #00C48C; }
.tag-behavior { background: #FF9F43; }
.tag-project { background: #845EF7; }
.q-company { font-size: 24rpx; color: #666; }
.q-content { font-size: 28rpx; color: #333; line-height: 1.5; margin-bottom: 12rpx; }
.q-bottom { display: flex; gap: 24rpx; }
.q-stat { font-size: 22rpx; color: #999; }
.empty { text-align: center; padding: 60rpx 0; color: #999; font-size: 28rpx; }
</style>
