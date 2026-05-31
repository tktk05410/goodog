<template>
  <div class="publish-page">
    <header class="header">
      <div class="header-content">
        <h1 class="logo" @click="$router.push('/')">GoodDog</h1>
      </div>
    </header>

    <div class="main-content">
      <h2>发布商品</h2>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="商品类型" prop="type">
          <el-radio-group v-model="form.type">
            <el-radio label="sell">出售</el-radio>
            <el-radio label="buy">求购</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="商品标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入商品标题" maxlength="100" show-word-limit />
        </el-form-item>

        <el-form-item label="商品描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            placeholder="请详细描述商品信息"
            :rows="6"
            maxlength="1000"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="商品价格" prop="price" v-if="form.type === 'sell'">
          <el-input-number v-model="form.price" :min="0" :precision="2" placeholder="请输入价格" />
        </el-form-item>

        <el-form-item label="商品图片">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :file-list="fileList"
            list-type="picture-card"
            accept="image/*"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="loading">发布</el-button>
          <el-button @click="$router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { productAPI, aiAPI } from '@/api/modules'

const router = useRouter()

const formRef = ref(null)
const uploadRef = ref(null)
const loading = ref(false)
const fileList = ref([])

const form = reactive({
  type: 'sell',
  title: '',
  description: '',
  price: null
})

const rules = {
  type: [{ required: true, message: '请选择商品类型', trigger: 'change' }],
  title: [{ required: true, message: '请输入商品标题', trigger: 'blur' }],
  description: [{ required: true, message: '请输入商品描述', trigger: 'blur' }]
}

function handleFileChange(file) {
  fileList.value = [file]
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const formData = new FormData()
    formData.append('title', form.title)
    formData.append('description', form.description)
    formData.append('type', form.type)
    if (form.price) {
      formData.append('price', form.price)
    }
    if (fileList.value.length > 0) {
      formData.append('image', fileList.value[0].raw)
    }

    const res = await productAPI.create(formData)
    ElMessage.success('发布成功')
    router.push(`/product/${res.data.product.id}`)
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.publish-page {
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
  max-width: 800px;
  margin: 20px auto;
  padding: 30px;
  background: white;
  border-radius: 12px;
}

.main-content h2 {
  margin-bottom: 30px;
}
</style>