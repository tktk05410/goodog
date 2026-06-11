<template>
  <div class="product-detail-page">
    <header class="header">
      <div class="header-content">
        <h1 class="logo" @click="$router.push('/')">goodog <span class="chinese-name">闲狗</span></h1>
        <div class="user-area">
          <template v-if="userStore.isLoggedIn">
            <span class="username">{{ userStore.userInfo?.username }}</span>
            <router-link to="/messages">消息</router-link>
          </template>
          <template v-else>
            <router-link to="/login">登录</router-link>
            <router-link to="/register">注册</router-link>
          </template>
        </div>
      </div>
    </header>

    <div class="main-content" v-loading="loading">
      <el-empty v-if="!product && !loading" description="商品不存在" />

      <div class="product-detail" v-if="product">
        <div class="product-images">
          <div class="main-image">
            <img v-if="product.image_path" :src="`/uploads/${product.image_path}`" alt="">
            <div v-else class="no-image">暂无图片</div>
          </div>
        </div>

        <div class="product-info-card">
          <h1 class="product-title">{{ product.title }}</h1>
          <div class="product-meta">
            <el-tag v-if="product.type === 'sell'" type="success">出售</el-tag>
            <el-tag v-else type="warning">求购</el-tag>
            <el-tag v-if="product.status === 'on'" type="info">上架中</el-tag>
            <el-tag v-else-if="product.status === 'sold'" type="danger">已售出</el-tag>
            <el-tag v-else type="info">已下架</el-tag>
          </div>
          <div class="product-price" v-if="product.price">
            <span class="price-symbol">¥</span>
            <span class="price-value">{{ product.price }}</span>
          </div>
          <div class="product-price" v-else>
            <span class="price-value">价格待议</span>
          </div>

          <div class="product-tags" v-if="product.tags && product.tags.length > 0">
            <h3>商品标签</h3>
            <div class="tags-container">
              <el-tag
                v-for="tag in product.tags"
                :key="tag.id"
                :color="tag.color"
                style="color: white; margin: 4px;"
              >
                {{ tag.name }}
                <el-tag v-if="tag.is_ai_generated" size="small" type="info" style="margin-left: 4px; font-size: 10px;">AI</el-tag>
              </el-tag>
            </div>
          </div>

          <div class="product-description">
            <h3>商品描述</h3>
            <p>{{ product.description }}</p>
          </div>

          <div class="product-seller">
            <span>发布者：{{ product.publisher }}</span>
            <span>发布时间：{{ product.create_time }}</span>
          </div>

          <div class="product-actions">
            <template v-if="userStore.isLoggedIn && userStore.userInfo?.id !== product.user_id && product.status === 'on'">
              <el-button type="primary" @click="handleBuy">立即购买</el-button>
              <el-button @click="handleContact">联系卖家</el-button>
            </template>
            <template v-if="userStore.userInfo?.id === product.user_id">
              <el-button @click="handleEdit">编辑</el-button>
              <el-button type="danger" @click="handleDelete">删除</el-button>
            </template>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/store/user'
import { productAPI, transactionAPI, messageAPI } from '@/api/modules'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const product = ref(null)
const loading = ref(false)

async function fetchProduct() {
  loading.value = true
  try {
    const res = await productAPI.getById(route.params.id)
    product.value = res.data.product
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function handleBuy() {
  try {
    await ElMessageBox.confirm('确定要购买此商品吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await transactionAPI.create({ product_id: product.value.id })
    ElMessage.success('购买成功，请等待卖家确认')
    fetchProduct()
  } catch (e) {
    if (e !== 'cancel') {
      console.error(e)
    }
  }
}

function handleContact() {
  router.push({ name: 'Messages', query: { to_user: product.value.user_id } })
}

function handleEdit() {
  router.push({ name: 'EditProduct', params: { id: product.value.id } })
}

async function handleDelete() {
  try {
    await ElMessageBox.confirm('确定要删除此商品吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await productAPI.delete(product.value.id)
    ElMessage.success('删除成功')
    router.push('/')
  } catch (e) {
    if (e !== 'cancel') {
      console.error(e)
    }
  }
}

onMounted(() => {
  fetchProduct()
})
</script>

<style scoped>
.product-detail-page {
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

.product-detail {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  background: white;
  border-radius: 12px;
  padding: 30px;
}

.product-images .main-image {
  width: 100%;
  height: 400px;
  background: #f0f0f0;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.product-images img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.no-image {
  color: #999;
  font-size: 16px;
}

.product-info-card {
  display: flex;
  flex-direction: column;
}

.product-title {
  font-size: 24px;
  margin-bottom: 16px;
}

.product-meta {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}

.product-price {
  margin-bottom: 24px;
}

.price-symbol {
  font-size: 20px;
  color: #f56c6c;
}

.price-value {
  font-size: 32px;
  font-weight: bold;
  color: #f56c6c;
}

.product-tags {
  margin-bottom: 24px;
}

.product-tags h3 {
  margin-bottom: 12px;
  font-size: 16px;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.product-description {
  margin-bottom: 24px;
}

.product-description h3 {
  margin-bottom: 12px;
}

.product-description p {
  color: #666;
  line-height: 1.6;
}

.product-seller {
  display: flex;
  flex-direction: column;
  gap: 8px;
  color: #999;
  margin-bottom: 24px;
}

.product-actions {
  display: flex;
  gap: 12px;
  margin-top: auto;
}
</style>
