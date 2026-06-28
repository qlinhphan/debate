import React, { useCallback, useEffect, useState } from 'react'
import Sidebar from './components/Sidebar'
import Chat from './components/Chat'
import { fetchConversation, fetchConversations } from './api'

function summarizeTopic(topic) {
  return topic
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 5)
    .join(' ')
}

export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [sessions, setSessions] = useState([])
  const [activeSessionId, setActiveSessionId] = useState(null)

  useEffect(() => {
    let cancelled = false

    async function loadHistory() {
      try {
        const data = await fetchConversations()
        if (cancelled) return
        setSessions((data.conversations || []).map(normalizeSession))
      } catch (error) {
        console.error('Load conversations failed', error)
      }
    }

    loadHistory()
    return () => {
      cancelled = true
    }
  }, [])

  function createSession(topic) {
    const cleanTopic = String(topic || '').trim()
    if (!cleanTopic) return null

    const newSession = {
      id: Date.now().toString(),
      topic: cleanTopic,
      summary: summarizeTopic(cleanTopic),
      messages: [],
      startedAt: new Date().toISOString(),
    }

    setSessions(prev => [newSession, ...prev])
    setActiveSessionId(newSession.id)
    return newSession.id
  }

  function handleSendTopic(selectedTopic) {
    const sessionId = createSession(selectedTopic)
    if (sessionId) {
      setSessions(prev => prev.map(s => ({ ...s, isCurrent: s.id === sessionId })))
    }
  }

  function handleNewChat() {
    setActiveSessionId(null)
  }

  const handleSessionUpdate = useCallback((sessionId, messages) => {
    setSessions(prev => prev.map(session => {
      if (session.id !== sessionId) return session
      return { ...session, messages }
    }))
  }, [])

  const handleSessionReview = useCallback((sessionId, review) => {
    setSessions(prev => prev.map(session => {
      if (session.id !== sessionId) return session
      return { ...session, review }
    }))
  }, [])

  async function handleSelectHistory(sessionId) {
    setActiveSessionId(sessionId)
    setSessions(prev => prev.map(s => ({ ...s, isCurrent: s.id === sessionId })))

    const selected = sessions.find(session => session.id === sessionId)
    if (selected && selected.messages.length > 0) return

    try {
      const data = await fetchConversation(sessionId)
      if (!data.conversation) return
      const restoredSession = normalizeSession(data.conversation)
      setSessions(prev => prev.map(session => (
        session.id === sessionId ? { ...restoredSession, isCurrent: true } : session
      )))
    } catch (error) {
      console.error('Load conversation failed', error)
    }
  }

  const activeSession = sessions.find(s => s.id === activeSessionId) || null

  return (
    <div className="app-root">
      <Sidebar
        open={sidebarOpen}
        onToggle={() => setSidebarOpen(v => !v)}
        onSendTopic={handleSendTopic}
        onNewChat={handleNewChat}
        topicHistory={sessions}
        onSelectHistory={handleSelectHistory}
        activeSessionId={activeSessionId}
      />
      <Chat
        key={activeSessionId || 'new'}
        session={activeSession}
        onSessionUpdate={handleSessionUpdate}
        onSessionReview={handleSessionReview}
      />
    </div>
  )
}

function normalizeSession(raw) {
  const topic = raw.topic || ''
  return {
    id: raw.id,
    topic,
    summary: raw.summary || summarizeTopic(topic),
    messages: raw.messages || [],
    review: raw.review || raw.state?.review || '',
    startedAt: raw.created_at || raw.startedAt || new Date().toISOString(),
  }
}
