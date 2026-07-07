export async function sendChatStep({ topic, step = 0, sessionId }) {
  const res = await fetch('/api/chat/step', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ topic, step, session_id: sessionId })
  })
  if (!res.ok) throw new Error('API error')
  return res.json()
}

export async function fetchChatReview({ topic, sessionId }) {
  const res = await fetch('/api/chat/review', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ topic, session_id: sessionId })
  })
  if (!res.ok) throw new Error('API error')
  return res.json()
}

export async function fetchConversations() {
  const res = await fetch('/api/conversations')
  if (!res.ok) throw new Error('API error')
  return res.json()
}

export async function fetchConversation(sessionId) {
  const res = await fetch(`/api/conversations/${sessionId}`)
  if (!res.ok) throw new Error('API error')
  return res.json()
}

export async function fetchMultiDocPrompt() {
  const res = await fetch('/api/prompts/nhieutailieu')
  if (!res.ok) throw new Error('API error')
  return res.json()
}

export async function saveMultiDocPrompt(prompt) {
  const res = await fetch('/api/prompts/nhieutailieu', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt })
  })
  if (!res.ok) throw new Error('API error')
  return res.json()
}

export async function uploadRagDocument(file) {
  const formData = new FormData()
  formData.append('file', file)
  const res = await fetch('/api/rag/upload', {
    method: 'POST',
    body: formData
  })
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error(data.detail || 'Upload failed')
  }
  return res.json()
}

export async function queryRagDocument(question) {
  const res = await fetch('/api/rag/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question })
  })
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error(data.detail || 'Query failed')
  }
  return res.json()
}

