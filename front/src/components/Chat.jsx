import React, { useEffect, useState, useRef } from 'react'
import { sendChatStep } from '../api'

function Message({ m }) {
  const left = m.agent === 1
  return (
    <div className={`message-row ${left ? 'left' : 'right'}`}>
      <div className={`ai-badge ${left ? 'ai-one' : 'ai-two'}`}>
        <img src={left ? '/trump.png' : '/musk.png'} alt={left ? 'Trump' : 'Musk'} />
      </div>
      <div className="bubble">{m.text}</div>
    </div>
  )
}

function formatTopicTitle(topic) {
  const words = topic.split(/\s+/).filter(Boolean)
  if (!words.length) return 'Chủ đề'
  const firstFive = words.slice(0, 5)
  return firstFive.length < words.length ? `${firstFive.join(' ')} ...` : firstFive.join(' ')
}

export default function Chat({ session, onSessionUpdate }) {
  const [messages, setMessages] = useState(session?.messages || [])
  const [running, setRunning] = useState(false)
  const [progress, setProgress] = useState(0)
  const cancelRef = useRef(false)
  const containerRef = useRef(null)

  useEffect(() => {
    setMessages(session?.messages || [])
    setRunning(false)
    setProgress(0)
    cancelRef.current = true
  }, [session?.id])

  useEffect(() => {
    if (!session || !session.topic) {
      setMessages([])
      setRunning(false)
      cancelRef.current = true
      return
    }

    if (session.messages && session.messages.length > 0) {
      return
    }

    cancelRef.current = false
    setMessages([])
    setRunning(true)
    setProgress(0)
    let step = 0

    async function runConversation() {
      while (!cancelRef.current) {
        try {
          const result = await sendChatStep({ topic: session.topic, step, sessionId: session.id })
          if (cancelRef.current) return
          setMessages(prev => {
            const next = [...prev, ...result.messages]
            onSessionUpdate && onSessionUpdate(session.id, next)
            return next
          })
          if (result.done) {
            setRunning(false)
            return
          }
          step = result.step
        } catch (error) {
          console.error('Chat step failed', error)
          setRunning(false)
          return
        }
      }
      setRunning(false)
    }

    runConversation()
    return () => {
      cancelRef.current = true
    }
  }, [session?.id, session?.topic, onSessionUpdate])

  function handleStop() {
    cancelRef.current = true
    setRunning(false)
    setProgress(0)
  }

  useEffect(() => {
    if (!running || !session?.topic) return

    const totalMs = 5 * 60 * 1000
    const start = Date.now()
    const timer = window.setInterval(() => {
      const elapsed = Date.now() - start
      const nextProgress = Math.min(100, (elapsed / totalMs) * 100)
      setProgress(nextProgress)
      if (nextProgress >= 100) {
        cancelRef.current = true
        setRunning(false)
        setProgress(100)
        window.clearInterval(timer)
      }
    }, 200)

    return () => window.clearInterval(timer)
  }, [running, session?.topic])

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight
    }
  }, [messages])

  return (
    <div className="chat-area">
      <div className="chat-header">
        <span className="chat-title">Trò chuyện</span>
        <span className="topic-title">{session ? `Tên chủ đề: ${formatTopicTitle(session.topic)}` : 'Tên chủ đề: ...'}</span>
        <button className="stop-btn" onClick={handleStop} disabled={!running}>
          Dừng thảo luận
        </button>
      </div>
      {running && (
        <div className="progress-wrap" aria-label="Tiến trình thảo luận">
          <div className="progress-label">Đang thảo luận...</div>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${progress}%` }} />
          </div>
        </div>
      )}
      <div className="chat-messages" ref={containerRef}>
        {messages.map((m, i) => (
          <Message key={i} m={m} />
        ))}
      </div>
    </div>
  )
}
