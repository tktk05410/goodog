<template>
  <div class="publish-page">
    <header class="header">
      <div class="header-content">
        <h1 class="logo" @click="$router.push('/')">goodog <span class="chinese-name">闲狗</span></h1>
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

        <el-form-item label="商品标签">
          <div class="tags-input-area">
            <div class="selected-tags">
              <el-tag
                v-for="tag in form.tags"
                :key="tag.id || tag.name"
                :color="tag.color || '#409eff'"
                style="color: white; margin: 4px;"
                closable
                @close="removeTag(tag)"
              >
                {{ tag.name }}
              </el-tag>
              <el-button size="small" @click="showTagDialog = true">+ 添加标签</el-button>
            </div>
            <p class="tag-hint">AI将自动识别商品并生成标签，您也可以手动添加</p>
          </div>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="loading">发布</el-button>
          <el-button @click="$router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </div>

    <el-dialog v-model="showTagDialog" title="选择或创建标签" width="500px">
      <el-input
        v-model="newTagName"
        placeholder="输入新标签名称，按回车创建"
        @keyup.enter="createNewTag"
      >
        <template #append>
          <el-button @click="createNewTag">创建</el-button>
        </template>
      </el-input>
      <div class="existing-tags" v-if="availableTags.length > 0">
        <p>已有标签（点击选择）：</p>
        <div class="tags-container">
          <el-tag
            v-for="tag in availableTags"
            :key="tag.id"
            :color="tag.color"
            style="color: white; margin: 4px; cursor: pointer;"
            :type="isTagSelected(tag) ? 'primary' : 'info'"
            @click="selectTag(tag)"
          >
            {{ tag.name }}
          </el-tag>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { productAPI, aiAPI, tagAPI } from '@/api/modules'

const router = useRouter()

const formRef = ref(null)
const uploadRef = ref(null)
const loading = ref(false)
const fileList = ref([])
const showTagDialog = ref(false)
const newTagName = ref('')
const availableTags = ref([])

const form = reactive({
  type: 'sell',
  title: '',
  description: '',
  price: null,
  tags: []
})

const rules = {
  type: [{ required: true, message: '请选择商品类型', trigger: 'change' }],
  title: [{ required: true, message: '请输入商品标题', trigger: 'blur' }],
  description: [{ required: true, message: '请输入商品描述', trigger: 'blur' }]
}

async function fetchAvailableTags() {
  try {
    const res = await tagAPI.getList({ per_page: 100 })
    availableTags.value = res.data.tags || []
  } catch (e) {
    console.error(e)
  }
}

function handleFileChange(file) {
  fileList.value = [file]
}

function isTagSelected(tag) {
  return form.tags.some(t => t.id === tag.id || t.name === tag.name)
}

function selectTag(tag) {
  if (isTagSelected(tag)) {
    form.tags = form.tags.filter(t => t.id !== tag.id && t.name !== tag.name)
  } else {
    form.tags.push({ ...tag })
  }
}

function removeTag(tag) {
  form.tags = form.tags.filter(t => t.id !== tag.id && t.name !== tag.name)
}

async function createNewTag() {
  if (!newTagName.value.trim()) {
    ElMessage.warning('请输入标签名称')
    return
  }

  const tagName = newTagName.value.trim()
  if (form.tags.some(t => t.name === tagName)) {
    ElMessage.warning('标签已存在')
    return
  }

  form.tags.push({ name: tagName, color: '#409eff' })
  newTagName.value = ''
  ElMessage.success('标签已添加')
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
    const productId = res.data.product.id

    if (form.tags.length > 0) {
      for (const tag of form.tags) {
        try {
          if (tag.id) {
            await tagAPI.addProductTag(productId, { tag_id: tag.id })
          } else {
            await tagAPI.addProductTag(productId, { tag_name: tag.name })
          }
        } catch (e) {
          console.error('Failed to add tag:', e)
        }
      }
    }

    ElMessage.success('发布成功')
    router.push(`/product/${productId}`)
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchAvailableTags()
})
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

.tags-input-area {
  width: 100%;
}

.selected-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  align-items: center;
}

.tag-hint {
  margin-top: 8px;
  font-size: 12px;
  color: #999;
}

.existing-tags {
  margin-top: 16px;
}

.existing-tags p {
  margin-bottom: 8px;
  color: #666;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
</style>
