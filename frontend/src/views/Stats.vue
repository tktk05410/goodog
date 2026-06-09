<template>
  <div class="stats-page">
    <header class="header">
      <div class="header-content">
        <h1 class="logo" @click="$router.push('/')">goodog <span class="chinese-name">闲狗</span></h1>
        <div class="user-area">
          <span class="username">{{ userStore.userInfo?.username }}</span>
          <router-link to="/profile">个人中心</router-link>
        </div>
      </div>
    </header>

    <div class="main-content" v-loading="loading">
      <h2>数据统计</h2>

      <div class="overview-cards">
        <div class="overview-card">
          <div class="card-value">{{ overview.total_users }}</div>
          <div class="card-label">总用户数</div>
        </div>
        <div class="overview-card">
          <div class="card-value">{{ overview.total_products }}</div>
          <div class="card-label">商品总数</div>
        </div>
        <div class="overview-card">
          <div class="card-value">{{ overview.active_products }}</div>
          <div class="card-label">在售商品</div>
        </div>
        <div class="overview-card">
          <div class="card-value">{{ overview.completed_transactions }}</div>
          <div class="card-label">完成交易</div>
        </div>
      </div>

      <div class="charts-grid">
        <div class="chart-card">
          <h3>商品分类分布</h3>
          <div ref="categoryChart" class="chart"></div>
        </div>
        <div class="chart-card">
          <h3>商品状态分布</h3>
          <div ref="statusChart" class="chart"></div>
        </div>
        <div class="chart-card">
          <h3>交易状态分布</h3>
          <div ref="transactionChart" class="chart"></div>
        </div>
        <div class="chart-card">
          <h3>每日交易量</h3>
          <div ref="dailyChart" class="chart"></div>
        </div>
        <div class="chart-card full-width">
          <h3>用户活跃时段</h3>
          <div ref="hourlyChart" class="chart"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { useUserStore } from '@/store/user'
import { statsAPI } from '@/api/modules'

const userStore = useUserStore()

const loading = ref(false)
const overview = reactive({
  total_users: 0,
  total_products: 0,
  active_products: 0,
  completed_transactions: 0
})

let categoryChart = null
let statusChart = null
let transactionChart = null
let dailyChart = null
let hourlyChart = null

async function fetchOverview() {
  try {
    const res = await statsAPI.getOverview()
    Object.assign(overview, res.data)
  } catch (e) {
    console.error(e)
  }
}

async function initCharts() {
  categoryChart = echarts.init(document.querySelector('.stats-page .chart:nth-child(1)'))
  statusChart = echarts.init(document.querySelector('.stats-page .chart:nth-child(2)'))
  transactionChart = echarts.init(document.querySelector('.stats-page .chart:nth-child(3)'))
  dailyChart = echarts.init(document.querySelector('.stats-page .chart:nth-child(4)'))
  hourlyChart = echarts.init(document.querySelector('.stats-page .chart:nth-child(5)'))

  try {
    const categoryRes = await statsAPI.getCategoryDistribution()
    categoryChart.setOption({
      tooltip: { trigger: 'item' },
      legend: { bottom: 0 },
      series: [{
        type: 'pie',
        radius: '60%',
        data: categoryRes.data.distribution.map(item => ({
          name: item.name,
          value: item.value
        }))
      }]
    })

    const statusRes = await statsAPI.getProductStatus()
    statusChart.setOption({
      tooltip: { trigger: 'item' },
      legend: { bottom: 0 },
      series: [{
        type: 'pie',
        radius: '60%',
        data: statusRes.data.distribution.map(item => ({
          name: item.name,
          value: item.value
        }))
      }]
    })

    const txRes = await statsAPI.getTransactionStates()
    transactionChart.setOption({
      tooltip: { trigger: 'item' },
      legend: { bottom: 0 },
      series: [{
        type: 'pie',
        radius: '60%',
        data: txRes.data.distribution.map(item => ({
          name: item.name,
          value: item.value
        }))
      }]
    })

    const dailyRes = await statsAPI.getDailyTransactions({ days: 7 })
    dailyChart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: dailyRes.data.data.map(item => item.date)
      },
      yAxis: { type: 'value' },
      series: [{
        type: 'bar',
        data: dailyRes.data.data.map(item => item.count)
      }]
    })

    const hourlyRes = await statsAPI.getHourlyActivity()
    hourlyChart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: hourlyRes.data.data.map(item => `${item.hour}:00`)
      },
      yAxis: { type: 'value' },
      series: [{
        type: 'line',
        smooth: true,
        data: hourlyRes.data.data.map(item => item.count)
      }]
    })
  } catch (e) {
    console.error(e)
  }
}

function handleResize() {
  categoryChart?.resize()
  statusChart?.resize()
  transactionChart?.resize()
  dailyChart?.resize()
  hourlyChart?.resize()
}

onMounted(() => {
  if (!userStore.isLoggedIn) {
    userStore.fetchUserInfo()
  }
  loading.value = true
  fetchOverview().finally(() => {
    loading.value = false
    initCharts()
  })
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.stats-page {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.header {
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  cursor: pointer;
}

.user-area {
  display: flex;
  align-items: center;
  gap: 16px;
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.main-content h2 {
  margin-bottom: 20px;
}

.overview-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.overview-card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.card-value {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.card-label {
  color: #666;
  font-size: 14px;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.chart-card {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chart-card.full-width {
  grid-column: 1 / -1;
}

.chart-card h3 {
  margin-bottom: 16px;
}

.chart {
  height: 300px;
}
</style>