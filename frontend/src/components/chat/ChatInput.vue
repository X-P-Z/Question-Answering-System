<script setup>
import { ref, nextTick } from 'vue'

const props = defineProps({
  isStreaming: Boolean,
  enableRag: Boolean,
  topK: Number,
})

const emit = defineEmits(['send-message', 'upload-file', 'toggle-rag', 'update-top-k'])

const inputText = ref('')
const textareaRef = ref(null)
const fileInputRef = ref(null)

function handleSend() {
  const text = inputText.value.trim()
  if (!text || props.isStreaming) return
  emit('send-message', text)
  inputText.value = ''
  nextTick(() => {
    if (textareaRef.value) {
      textareaRef.value.style.height = 'auto'
    }
  })
}

function handleKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}

function autoResize() {
  const el = textareaRef.value
  if (el) {
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 120) + 'px'
  }
}

function handleFileUpload(e) {
  const file = e.target.files[0]
  if (file) {
    emit('upload-file', file)
    fileInputRef.value.value = ''
  }
}
</script>

<template>
  <div class="chat-input-area">
    <div class="input-controls">
      <label class="rag-toggle-label">
        <input
          type="checkbox"
          :checked="enableRag"
          @change="emit('toggle-rag')"
        />
        RAG Search
      </label>
      <select
        class="topk-select"
        :value="topK"
        @change="emit('update-top-k', Number($event.target.value))"
      >
        <option :value="1">Top-1</option>
        <option :value="3">Top-3</option>
        <option :value="5">Top-5</option>
        <option :value="10">Top-10</option>
      </select>
      <button class="file-upload-btn" @click="fileInputRef.click()">
        Upload File
      </button>
      <input
        ref="fileInputRef"
        type="file"
        accept=".txt,.md,.pdf,.docx"
        style="display: none"
        @change="handleFileUpload"
      />
    </div>
    <div class="input-row">
      <textarea
        ref="textareaRef"
        v-model="inputText"
        placeholder="Type a message... (Enter to send, Shift+Enter for newline)"
        :disabled="isStreaming"
        @keydown="handleKeydown"
        @input="autoResize"
        rows="1"
      ></textarea>
      <button
        class="btn-send"
        :disabled="isStreaming || !inputText.trim()"
        @click="handleSend"
      >
        Send
      </button>
    </div>
  </div>
</template>

<style scoped>
</style>