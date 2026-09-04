import { defineStore } from 'pinia'
import { ref } from 'vue'
import { streamChat, streamAgentChat, clearSession, uploadDocument } from '@/api/chat'

let msgId = 0
function nextId() {
  return `msg_${++msgId}`
}

export const useChatStore = defineStore('chat', () => {
  const messages = ref([])
  const sessionId = ref(null)
  const isStreaming = ref(false)
  const enableRag = ref(true)
  const topK = ref(3)
  const error = ref(null)
  const mode = ref('standard') // 'standard' | 'agent'

  async function sendMessage(text) {
    if (!text.trim() || isStreaming.value) return

    error.value = null
    messages.value.push({
      id: nextId(),
      role: 'user',
      content: text,
      sources: [],
      isStreaming: false,
      timestamp: Date.now(),
    })

    const assistantIdx = messages.value.length
    messages.value.push({
      id: nextId(),
      role: 'assistant',
      content: '',
      sources: [],
      isStreaming: true,
      timestamp: Date.now(),
    })
    isStreaming.value = true

    try {
      const generator = mode.value === 'agent'
        ? streamAgentChat({ sessionId: sessionId.value, message: text, enableRag: enableRag.value, topK: topK.value })
        : streamChat({ sessionId: sessionId.value, message: text, enableRag: enableRag.value, topK: topK.value })

      for await (const event of generator) {
        switch (event.type) {
          case 'token':
            messages.value[assistantIdx].content += event.content
            break
          case 'sources':
            messages.value[assistantIdx].sources = event.sources
            break
          case 'done':
            sessionId.value = event.session_id
            messages.value[assistantIdx].isStreaming = false
            break
          case 'error':
            error.value = event.message
            messages.value[assistantIdx].isStreaming = false
            break
          case 'tool_call':
            messages.value.push({
              id: nextId(),
              role: 'tool',
              content: `调用工具: ${event.name}`,
              args: event.args,
              result: null,
              isStreaming: false,
              timestamp: Date.now(),
            })
            break
          case 'tool_result':
            const lastTool = [...messages.value].reverse().find(m => m.role === 'tool' && !m.result)
            if (lastTool) {
              lastTool.result = event.result
              lastTool.content = `工具 ${event.name}: ${event.result}`
            }
            break
        }
      }
    } catch (err) {
      error.value = err.message
      messages.value[assistantIdx].isStreaming = false
    } finally {
      isStreaming.value = false
    }
  }

  async function clearChat() {
    if (sessionId.value) {
      await clearSession(sessionId.value).catch(() => {})
    }
    messages.value = []
    sessionId.value = null
    error.value = null
  }

  function toggleRag() {
    enableRag.value = !enableRag.value
  }

  function setTopK(k) {
    topK.value = k
  }

  function setMode(m) {
    mode.value = m
  }

  async function uploadFile(file) {
    try {
      await uploadDocument(file)
      messages.value.push({
        id: nextId(),
        role: 'system',
        content: `文件 "${file.name}" 上传成功，请调用 /embedding/embedding_files 接口完成向量化后方可检索。`,
        sources: [],
        isStreaming: false,
        timestamp: Date.now(),
      })
    } catch (err) {
      error.value = `上传失败: ${err.message}`
    }
  }

  return {
    messages,
    sessionId,
    isStreaming,
    enableRag,
    topK,
    error,
    mode,
    sendMessage,
    clearChat,
    toggleRag,
    setTopK,
    setMode,
    uploadFile,
  }
})