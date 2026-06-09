<template>
  <div class="profile-page">
    <header class="header">
      <div class="header-content">
        <h1 class="logo" @click="$router.push('/')">goodog <span class="chinese-name">闲狗</span></h1>
      </div>
    </header>

    <div class="main-content" v-loading="loading">
      <div class="profile-card" v-if="user">
        <div class="profile-header">
          <div class="avatar">{{ user.username?.charAt(0).toUpperCase() }}</div>
          <div class="user-info">
            <h2>{{ user.username }}</h2>
            <p>学号：{{ user.student_id || '未绑定' }}</p>
            <p>注册时间：{{ user.create_time }}</p>
          </div>
        </div>

        <div class="profile-stats">
          <div class="stat-item">
            <span class="stat-value">{{ user.credit_score }}</span>
            <span class="stat-label">信用分</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ stats.total_products }}</span>
            <span class="stat-label">发布商品</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ stats.completed_deals }}</span>
            <span class="stat-label">完成交易</span>
          </div>
        </div>

        <div class="profile-actions">
          <el-button @click="showEditDialog = true">编辑资料</el-button>
          <el-button @click="showPasswordDialog = true">修改密码</el-button>
        </div>
      </div>

      <div class="my-products">
        <h3>我的商品</h3>
        <el-tabs v-model="activeTab">
          <el-tab-pane label="在售" name="on">
            <div class="product-list" v-if="myProducts.length > 0">
              <div
                v-for="product in myProducts"
                :key="product.id"
                class="product-item"
                @click="$router.push(`/product/${product.id}`)"
              >
                <div class="product-image">
                  <img v-if="product.image_path" :src="`/uploads/${product.image_path}`" alt="">
                  <div v-else class="no-image">暂无</div>
                </div>
                <div class="product-info">
                  <h4>{{ product.title }}</h4>
                  <p>{{ product.description }}</p>
                  <span class="product-price" v-if="product.price">¥{{ product.price }}</span>
                </div>
              </div>
            </div>
            <el-empty v-else description="暂无在售商品" />
          </el-tab-pane>
          <el-tab-pane label="已售出" name="sold">
            <el-empty description="暂无已售商品" />
          </el-tab-pane>
        </el-tabs>
      </div>

      <div class="my-transactions">
        <h3>我的交易</h3>
        <el-tabs v-model="transactionTab">
          <el-tab-pane label="买入" name="buyer">
            <div class="transaction-list" v-if="buyerTransactions.length > 0">
              <div v-for="tx in buyerTransactions" :key="tx.id" class="transaction-item">
                <span>{{ tx.product?.title }}</span>
                <el-tag :type="getStateType(tx.state)">{{ getStateLabel(tx.state) }}</el-tag>
              </div>
            </div>
            <el-empty v-else description="暂无买入记录" />
          </el-tab-pane>
          <el-tab-pane label="卖出" name="seller">
            <div class="transaction-list" v-if="sellerTransactions.length > 0">
              <div v-for="tx in sellerTransactions" :key="tx.id" class="transaction-item">
                <span>{{ tx.product?.title }}</span>
                <el-tag :type="getStateType(tx.state)">{{ getStateLabel(tx.state) }}</el-tag>
              </div>
            </div>
            <el-empty v-else description="暂无卖出记录" />
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>

    <el-dialog v-model="showEditDialog" title="编辑资料" width="400px">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="学号">
          <el-input v-model="editForm.student_id" placeholder="请输入学号" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="handleEditProfile">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showPasswordDialog" title="修改密码" width="400px">
      <el-form :model="passwordForm" label-width="80px">
        <el-form-item label="旧密码">
          <el-input v-model="passwordForm.old_password" type="password" />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="passwordForm.new_password" type="password" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPasswordDialog = false">取消</el-button>
        <el-button type="primary" @click="handleChangePassword">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'
import { userAPI, productAPI, transactionAPI, authAPI } from '@/api/modules'

const userStore = useUserStore()

const loading = ref(false)
const showEditDialog = ref(false)
const showPasswordDialog = ref(false)
const activeTab = ref('on')
const transactionTab = ref('buyer')

const user = ref(null)
const myProducts = ref([])
const buyerTransactions = ref([])
const sellerTransactions = ref([])
const stats = reactive({
  total_products: 0,
  completed_deals: 0
})

const editForm = reactive({
  student_id: ''
})

const passwordForm = reactive({
  old_password: '',
  new_password: ''
})

async function fetchProfile() {
  try {
    const res = await userAPI.getProfile()
    user.value = res.data.user
    editForm.student_id = user.value.student_id || ''
  } catch (e) {
    console.error(e)
  }
}

async function fetchMyProducts() {
  try {
    const res = await productAPI.getMyProducts({ per_page: 100 })
    myProducts.value = res.data.products.filter(p => p.status === 'on')
    stats.total_products = res.data.total
  } catch (e) {
    console.error(e)
  }
}

async function fetchTransactions() {
  try {
    const res = await transactionAPI.getList({ role: 'buyer', per_page: 100 })
    buyerTransactions.value = res.data.transactions
  } catch (e) {
    console.error(e)
  }

  try {
    const res = await transactionAPI.getList({ role: 'seller', per_page: 100 })
    sellerTransactions.value = res.data.transactions
    stats.completed_deals = res.data.transactions.filter(t => t.state === 'done').length
  } catch (e) {
    console.error(e)
  }
}

async function handleEditProfile() {
  try {
    await userAPI.updateProfile({ student_id: editForm.student_id })
    ElMessage.success('修改成功')
    showEditDialog.value = false
    fetchProfile()
  } catch (e) {
    console.error(e)
  }
}

async function handleChangePassword() {
  try {
    await authAPI.changePassword(passwordForm)
    ElMessage.success('密码修改成功')
    showPasswordDialog.value = false
    passwordForm.old_password = ''
    passwordForm.new_password = ''
  } catch (e) {
    console.error(e)
  }
}

function getStateType(state) {
  const map = {
    pending: 'warning',
    paid: 'primary',
    done: 'success',
    canceled: 'info'
  }
  return map[state] || 'info'
}

function getStateLabel(state) {
  const map = {
    pending: '待付款',
    paid: '已付款',
    done: '已完成',
    canceled: '已取消'
  }
  return map[state] || state
}

onMounted(() => {
  if (!userStore.isLoggedIn) {
    userStore.fetchUserInfo()
  }
  fetchProfile()
  fetchMyProducts()
  fetchTransactions()
})
</script>

<style scoped>
.profile-page {
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
}

.logo {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  cursor: pointer;
}

.main-content {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.profile-card {
  background: white;
  border-radius: 12px;
  padding: 30px;
  margin-bottom: 20px;
}

.profile-header {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
}

.avatar {
  width: 80px;
  height: 80px;
  background: #409eff;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  font-weight: bold;
}

.user-info h2 {
  margin-bottom: 8px;
}

.user-info p {
  color: #666;
  margin-bottom: 4px;
}

.profile-stats {
  display: flex;
  justify-content: space-around;
  margin-bottom: 30px;
  padding: 20px 0;
  border-top: 1px solid #eee;
  border-bottom: 1px solid #eee;
}

.stat-item {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
}

.stat-label {
  color: #999;
  font-size: 12px;
}

.profile-actions {
  display: flex;
  gap: 12px;
}

.my-products,
.my-transactions {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
}

.my-products h3,
.my-transactions h3 {
  margin-bottom: 20px;
}

.product-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.product-item {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  transition: box-shadow 0.3s;
}

.product-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.product-image {
  height: 120px;
  background: #f0f0f0;
  border-radius: 4px;
  margin-bottom: 8px;
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
  font-size: 12px;
}

.product-info h4 {
  font-size: 14px;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-info p {
  font-size: 12px;
  color: #999;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 4px;
}

.product-price {
  color: #f56c6c;
  font-weight: bold;
}

.transaction-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.transaction-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border: 1px solid #eee;
  border-radius: 8px;
}
</style>