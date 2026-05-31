<template>
  <div class="products-page">
    <header class="header">
      <div class="header-content">
        <h1 class="logo" @click="$router.push('/')">GoodDog</h1>
        <div class="user-area">
          <template v-if="userStore.isLoggedIn">
            <span class="username">{{ userStore.userInfo?.username }}</span>
            <router-link to="/profile">个人中心</router-link>
          </template>
          <template v-else>
            <router-link to="/login">登录</router-link>
            <router-link to="/register">注册</router-link>
          </template>
        </div>
      </div>
    </header>

    <div class="main-content">
      <div class="search-bar">
        <el-input
          v-model="keyword"
          placeholder="搜索商品..."
          @keyup.enter="handleSearch"
          clearable
          style="width: 400px"
        >
          <template #append>
            <el-button @click="handleSearch">搜索</el-button>
          </template>
        </el-input>
      </div>

      <div class="filter-bar">
        <el-radio-group v-model="typeFilter" @change="handleFilterChange">
          <el-radio-button label="">全部</el-radio-button>
          <el-radio-button label="sell">出售</el-radio-button>
          <el-radio-button label="buy">求购</el-radio-button>
        </el-radio-group>
      </div>

      <div class="product-list" v-loading="loading">
        <el-empty v-if="products.length === 0 && !loading" description="暂无商品" />
        <div class="product-grid">
          <div
            v-for="product in products"
            :key="product.id"
            class="product-card"
            @click="$router.push(`/product/${product.id}`)"
          >
            <div class="product-image">
              <img v-if="product.image_path" :src="`/uploads/${product.image_path}`" alt="">
              <div v-else class="no-image">暂无图片</div>
            </div>
            <div class="product-info">
              <h3 class="product-title">{{ product.title }}</h3>
              <p class="product-desc">{{ product.description }}</p>
              <div class="product-meta">
                <span class="product-price" v-if="product.price">¥{{ product.price }}</span>
                <span class="product-type" :class="product.type">
                  {{ product.type === 'sell' ? '出售' : '求购' }}
                </span>
              </div>
            </div>
          </div>
        </div>
        <el-pagination
          v-if="total > 0"
          class="pagination"
          :current-page="page"
          :page-size="perPage"
          :total="total"
          @current-change="handlePageChange"
          layout="prev, pager, next"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { productAPI } from '@/api/modules'

const router = useRouter()
const userStore = useUserStore()

const keyword = ref('')
const typeFilter = ref('')
const products = ref([])
const loading = ref(false)
const page = ref(1)
const perPage = ref(12)
const total = ref(0)

async function fetchProducts() {
  loading.value = true
  try {
    const res = await productAPI.getList({
      page: page.value,
      per_page: perPage.value,
      type: typeFilter.value,
      keyword: keyword.value
    })
    products.value = res.data.products
    total.value = res.data.total
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  page.value = 1
  fetchProducts()
}

function handleFilterChange() {
  page.value = 1
  fetchProducts()
}

function handlePageChange(newPage) {
  page.value = newPage
  fetchProducts()
}

onMounted(() => {
  fetchProducts()
})
</script>

<style scoped>
.products-page {
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

.search-bar {
  margin-bottom: 20px;
}

.filter-bar {
  margin-bottom: 20px;
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 20px;
}

.product-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
}

.product-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.product-image {
  height: 180px;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-image {
  color: #999;
}

.product-info {
  padding: 12px;
}

.product-title {
  font-size: 16px;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-desc {
  font-size: 12px;
  color: #999;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.product-price {
  color: #f56c6c;
  font-weight: bold;
}

.product-type {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 10px;
}

.product-type.sell {
  background: #e6f7ff;
  color: #1890ff;
}

.product-type.buy {
  background: #fff7e6;
  color: #fa8c16;
}

.pagination {
  margin-top: 20px;
  justify-content: center;
}
</style>