export async function sendChatStep({ topic, step = 0, sessionId }) {
  const res = await fetch('/api/chat/step', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ topic, step, session_id: sessionId })
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

