const API_BASE = '/api'

export async function* streamChat({ sessionId, message, enableRag, topK }) {
  const response = await fetch(`${API_BASE}/chat/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId || null,
      message,
      enable_rag: enableRag,
      top_k: topK,
    }),
  })

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n\n')
    buffer = lines.pop()
    for (const line of lines) {
      const trimmed = line.trim()
      if (trimmed.startsWith('data: ')) {
        try {
          yield JSON.parse(trimmed.slice(6))
        } catch {
          // skip malformed JSON
        }
      }
    }
  }
}

export async function* streamAgentChat({ sessionId, message, enableRag, topK }) {
  const response = await fetch(`${API_BASE}/chat/agent`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId || null,
      message,
      enable_rag: enableRag,
      top_k: topK,
    }),
  })

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n\n')
    buffer = lines.pop()
    for (const line of lines) {
      const trimmed = line.trim()
      if (trimmed.startsWith('data: ')) {
        try {
          yield JSON.parse(trimmed.slice(6))
        } catch {
          // skip malformed JSON
        }
      }
    }
  }
}

export async function clearSession(sessionId) {
  const response = await fetch(`${API_BASE}/chat/clear`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId }),
  })
  return response.json()
}

export async function uploadDocument(file) {
  const formData = new FormData()
  formData.append('file', file)
  const response = await fetch(`${API_BASE}/document/upload`, {
    method: 'POST',
    body: formData,
  })
  return response.json()
}