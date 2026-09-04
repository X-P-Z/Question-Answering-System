<script setup>
import { useChatStore } from '@/stores/chat'
import ChatContainer from '@/components/chat/ChatContainer.vue'
import ChatHeader from '@/components/chat/ChatHeader.vue'
import MessageList from '@/components/chat/MessageList.vue'
import ChatInput from '@/components/chat/ChatInput.vue'
import '@/assets/chat.css'

const chatStore = useChatStore()
</script>

<template>
  <ChatContainer>
    <ChatHeader
      :session-id="chatStore.sessionId"
      :mode="chatStore.mode"
      @clear="chatStore.clearChat()"
      @update:mode="chatStore.setMode($event)"
    />
    <div v-if="chatStore.error" class="error-bar">
      {{ chatStore.error }}
      <button @click="chatStore.error = null">x</button>
    </div>
    <MessageList :messages="chatStore.messages" />
    <ChatInput
      :is-streaming="chatStore.isStreaming"
      :enable-rag="chatStore.enableRag"
      :top-k="chatStore.topK"
      @send-message="chatStore.sendMessage($event)"
      @upload-file="chatStore.uploadFile($event)"
      @toggle-rag="chatStore.toggleRag()"
      @update-top-k="chatStore.setTopK($event)"
    />
  </ChatContainer>
</template>

<style scoped>
.error-bar {
  background: #fef0f0;
  color: #f56c6c;
  padding: 8px 16px;
  font-size: 13px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #fde2e2;
  flex-shrink: 0;
}
.error-bar button {
  background: none;
  border: none;
  color: #f56c6c;
  cursor: pointer;
  font-size: 16px;
  padding: 0 4px;
}
</style>