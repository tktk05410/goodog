<template>
  <div class="messages-page">
    <header class="header">
      <div class="header-content">
        <h1 class="logo" @click="$router.push('/')">goodog <span class="chinese-name">闲狗</span></h1>
        <div class="user-area">
          <span class="username">{{ userStore.userInfo?.username }}</span>
          <router-link to="/profile">个人中心</router-link>
        </div>
      </div>
    </header>

    <div class="main-content">
      <div class="messages-container">
        <div class="conversations-list">
          <h3>会话列表</h3>
          <div
            v-for="conv in conversations"
            :key="conv.user_id"
            class="conversation-item"
            :class="{ active: currentChatUser === conv.user_id }"
            @click="selectConversation(conv)"
          >
            <div class="conversation-user">
              <span>{{ conv.username }}</span>
              <el-badge :value="conv.unread_count" :hidden="conv.unread_count === 0" />
            </div>
            <div class="last-message" v-if="conv.last_message">
              {{ conv.last_message.content }}
            </div>
          </div>
          <el-empty v-if="conversations.length === 0" description="暂无会话" />
        </div>

        <div class="chat-area">
          <template v-if="currentChatUser">
            <div class="chat-header">
              <span>与 {{ currentUsername }} 的对话</span>
            </div>
            <div class="chat-messages" ref="messagesContainer">
              <template v-for="(msg, index) in messages" :key="msg.id">
                <div v-if="shouldShowTime(msg, index, messages)" class="message-timestamp">
                  {{ formatMessageTime(msg.create_time) }}
                </div>
                <div
                  class="message-item"
                  :class="{ own: userStore.userInfo && Number(msg.from_user) === Number(userStore.userInfo.id) }"
                >
                  <div class="message-content">{{ msg.content }}</div>
                </div>
              </template>
            </div>
            <div class="chat-input">
              <el-input
                v-model="newMessage"
                placeholder="输入消息..."
                @keyup.enter="sendMessage"
              />
              <el-button type="primary" @click="sendMessage">发送</el-button>
            </div>
          </template>
          <el-empty v-else description="选择一个会话开始聊天" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'
import { messageAPI } from '@/api/modules'

const route = useRoute()
const userStore = useUserStore()

const conversations = ref([])
const messages = ref([])
const currentChatUser = ref(null)
const currentUsername = ref('')
const newMessage = ref('')
const messagesContainer = ref(null)

function formatMessageTime(timeStr) {
  if (!timeStr) return ''
  
  const match = timeStr.match(/(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):\d{2}/)
  if (!match) return timeStr
  
  const msgDate = new Date(match[1], match[2] - 1, match[3])
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const yesterday = new Date(today.getTime() - 24 * 60 * 60 * 1000)
  
  const msgTime = `${match[4]}:${match[5]}`
  
  if (msgDate.getTime() === today.getTime()) {
    return msgTime
  } else if (msgDate.getTime() === yesterday.getTime()) {
    return `昨天 ${msgTime}`
  } else {
    return `${match[2]}-${match[3]} ${msgTime}`
  }
}

function shouldShowTime(msg, index, messages) {
  if (index === 0) return true
  
  const currentTime = new Date(msg.create_time.replace(/-/g, '/'))
  const prevTime = new Date(messages[index - 1].create_time.replace(/-/g, '/'))
  
  const diffMinutes = Math.abs((currentTime - prevTime) / (1000 * 60))
  return diffMinutes >= 15
}

async function fetchConversations() {
  try {
    const res = await messageAPI.getConversations()
    conversations.value = res.data.conversations
  } catch (e) {
    console.error(e)
  }
}

async function selectConversation(conv) {
  currentChatUser.value = conv.user_id
  currentUsername.value = conv.username

  try {
    await messageAPI.markAllAsRead(conv.user_id)
    conv.unread_count = 0
  } catch (e) {
    console.error(e)
  }

  await fetchMessages()
}

async function fetchMessages() {
  if (!currentChatUser.value) return
  try {
    const res = await messageAPI.getList({ with_user: currentChatUser.value })
    messages.value = res.data.messages.reverse()
    scrollToBottom()
  } catch (e) {
    console.error(e)
  }
}

async function sendMessage() {
  if (!newMessage.value.trim() || !currentChatUser.value) return

  try {
    const res = await messageAPI.send({
      to_user: currentChatUser.value,
      content: newMessage.value
    })
    messages.value.push(res.data.data)
    newMessage.value = ''
    scrollToBottom()
  } catch (e) {
    console.error(e)
  }
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

onMounted(async () => {
  await userStore.fetchUserInfo()
  await fetchConversations()

  if (route.query.to_user) {
    const toUserId = parseInt(route.query.to_user)
    currentChatUser.value = toUserId
    
    const conv = conversations.value.find(c => c.user_id === toUserId)
    if (conv) {
      currentUsername.value = conv.username
    } else {
      currentUsername.value = `用户${toUserId}`
    }
    
    await fetchMessages()
  }
})
</script>

<style scoped>
.messages-page {
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

.messages-container {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 20px;
  height: 600px;
}

.conversations-list {
  background: white;
  border-radius: 12px;
  padding: 20px;
  overflow-y: auto;
}

.conversations-list h3 {
  margin-bottom: 20px;
}

.conversation-item {
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  margin-bottom: 8px;
  transition: background 0.3s;
}

.conversation-item:hover,
.conversation-item.active {
  background: #f5f5f5;
}

.conversation-user {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.last-message {
  font-size: 12px;
  color: #999;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chat-area {
  background: white;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
}

.chat-header {
  padding: 16px;
  border-bottom: 1px solid #eee;
  font-weight: 500;
}

.chat-messages {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.message-item {
  margin-bottom: 16px;
  max-width: 70%;
  align-self: flex-start;
}

.message-item.own {
  align-self: flex-end;
  margin-right: 0;
}

.message-item.own .message-content {
  background: #409eff;
  color: white;
  border-radius: 8px;
}

.message-content {
  background: #f0f0f0;
  padding: 10px 14px;
  border-radius: 8px;
  word-break: break-word;
  display: inline-block;
}

.message-timestamp {
  text-align: center;
  font-size: 12px;
  color: #999;
  margin: 12px 0;
}

.message-time {
  font-size: 10px;
  color: #999;
  margin-top: 4px;
}

.message-item.own .message-time {
  text-align: right;
}

.chat-input {
  padding: 16px;
  border-top: 1px solid #eee;
  display: flex;
  gap: 12px;
}
</style>