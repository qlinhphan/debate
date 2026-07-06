import React, { useCallback, useEffect, useRef, useState } from 'react'
import { fetchChatReview, fetchMultiDocPrompt, saveMultiDocPrompt, sendChatStep } from '../api'

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

function ReviewModal({ review, onClose }) {
  if (!review) return null
  return (
    <div className="review-overlay" role="dialog" aria-modal="true" aria-label="Kết luận thảo luận">
      <div className="review-modal">
        <div className="review-header">
          <div>
            <div className="review-eyebrow">Kết luận</div>
            <h2 className="review-title">Sau một hồi bàn bạc nhanh chóng thì</h2>
          </div>
          <button className="review-close" onClick={onClose} aria-label="Đóng kết luận">×</button>
        </div>
        <div className="review-body">{review}</div>
      </div>
    </div>
  )
}

function formatTopicTitle(topic) {
  const words = topic.split(/\s+/).filter(Boolean)
  if (!words.length) return 'Chủ đề'
  const firstFive = words.slice(0, 5)
  return firstFive.length < words.length ? `${firstFive.join(' ')} ...` : firstFive.join(' ')
}

function ToolWorkspace({ type }) {
  const isRag = type === 'rag'
  const [multiDocPrompt, setMultiDocPrompt] = useState('')
  const [promptStatus, setPromptStatus] = useState('')
  const [promptSaving, setPromptSaving] = useState(false)
  const [showPromptEditor, setShowPromptEditor] = useState(false)

  useEffect(() => {
    if (isRag) {
      setMultiDocPrompt('')
      setPromptStatus('')
      return
    }

    let cancelled = false
    setPromptStatus('Đang tải prompt...')
    fetchMultiDocPrompt()
      .then(data => {
        if (cancelled) return
        setMultiDocPrompt(data.prompt || '')
        setPromptStatus(data.file_name ? `Đang dùng ${data.file_name}` : 'Đã tải prompt')
      })
      .catch(error => {
        if (cancelled) return
        console.error('Fetch prompt failed', error)
        setPromptStatus('Chưa tải được prompt')
      })

    return () => {
      cancelled = true
    }
  }, [isRag])

  async function handleSavePrompt() {
    if (isRag || promptSaving) return
    setPromptSaving(true)
    setPromptStatus('Đang lưu prompt...')
    try {
      const data = await saveMultiDocPrompt(multiDocPrompt)
      setMultiDocPrompt(data.prompt || '')
      setPromptStatus(`Đã lưu vào ${data.file_name || 'prompt_nhieutailieu.json'}`)
    } catch (error) {
      console.error('Save prompt failed', error)
      setPromptStatus('Lưu prompt thất bại')
    } finally {
      setPromptSaving(false)
    }
  }

  return (
    <div className="chat-area">
      <div className="tool-workspace">
        <div className="tool-panel tool-primary">
          <div className="tool-kicker">{isRag ? 'RAG Workspace' : 'Document QA'}</div>
          <h1>{isRag ? 'Hỏi đáp tài liệu' : 'Kiểm tra lỗi tài liệu'}</h1>
          <div className="tool-upload">
            <div className="upload-icon">{isRag ? 'RAG' : 'DOC'}</div>
            <div>
              <div className="upload-title">Thả tài liệu vào đây</div>
              <div className="upload-subtitle">File: PDF, DOCX-WORD, TXT</div>
            </div>
            <button type="button" className="upload-button">Chọn tệp</button>
          </div>
          <textarea
            className="tool-textarea"
            placeholder={isRag ? 'Nhập câu hỏi về tài liệu...' : 'Nhập tiêu chí hoặc loại lỗi cần kiểm tra...'}
          />
          <div className="tool-action-row">
            <button type="button" className="tool-submit">
              {isRag ? 'Hỏi tài liệu' : 'Kiểm tra tài liệu'}
            </button>
            {!isRag && (
              <button
                type="button"
                className={`prompt-toggle ${showPromptEditor ? 'active' : ''}`}
                onClick={() => setShowPromptEditor(prev => !prev)}
              >
                Prompt nhiều tài liệu
              </button>
            )}
          </div>
          {!isRag && showPromptEditor && (
            <div className="prompt-editor">
              <div className="prompt-editor-header">
                <div>
                  <div className="prompt-editor-title">Prompt nhiều tài liệu</div>
                  <div className="prompt-file-name">prompt_nhieutailieu.json</div>
                </div>
                <span className="prompt-status">{promptStatus}</span>
              </div>
              <textarea
                className="prompt-textarea"
                value={multiDocPrompt}
                onChange={event => setMultiDocPrompt(event.target.value)}
                placeholder="Nhập prompt kiểm tra nhiều tài liệu..."
              />
              <div className="prompt-actions">
                <button type="button" className="prompt-save" onClick={handleSavePrompt} disabled={promptSaving}>
                  {promptSaving ? 'Đang lưu...' : 'Lưu prompt'}
                </button>
              </div>
            </div>
          )}
        </div>
        <div className="tool-panel tool-result">
          <div className="tool-kicker">Kết quả</div>
          <div className="result-placeholder">
            {isRag
              ? 'Câu trả lời dựa trên tài liệu sẽ hiển thị tại đây.'
              : 'Danh sách lỗi, cảnh báo và đề xuất chỉnh sửa sẽ hiển thị tại đây.'}
          </div>
          <div className="result-grid">
            <div><span>Nguồn</span><strong>0</strong></div>
            <div><span>Độ tin cậy</span><strong>--</strong></div>
            <div><span>Trạng thái</span><strong>Chưa chạy</strong></div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function Chat({ session, activeTool = 'chat', onSessionUpdate, onSessionReview }) {
  if (activeTool === 'rag' || activeTool === 'doc-check') {
    return <ToolWorkspace type={activeTool} />
  }

  return (
    <DebateChat
      session={session}
      onSessionUpdate={onSessionUpdate}
      onSessionReview={onSessionReview}
    />
  )
}

function DebateChat({ session, onSessionUpdate, onSessionReview }) {
  const sessionId = session?.id || ''
  const topic = session?.topic || ''
  const savedReview = session?.review || ''
  const isRunningSession = session?.status === 'running'
  const discussionStartedAt = session?.discussionStartedAt || null
  const [messages, setMessages] = useState(session?.messages || [])
  const [running, setRunning] = useState(false)
  const [reviewing, setReviewing] = useState(false)
  const [progress, setProgress] = useState(0)
  const [review, setReview] = useState(savedReview)
  const [showReview, setShowReview] = useState(false)
  const cancelRef = useRef(false)
  const finalizedRef = useRef(false)
  const containerRef = useRef(null)

  useEffect(() => {
    setMessages(session?.messages || [])
    setReview(savedReview)
    setShowReview(false)
    setReviewing(false)
    setRunning(false)
    setProgress(0)
    cancelRef.current = true
    finalizedRef.current = Boolean(savedReview)
  }, [sessionId])

  const finalizeDiscussion = useCallback(async () => {
    if (!sessionId || !topic || finalizedRef.current) return
    finalizedRef.current = true
    cancelRef.current = true
    setRunning(false)
    setReviewing(true)
    setProgress(100)

    try {
      const result = await fetchChatReview({ topic, sessionId })
      const nextReview = result.review || 'Chưa có kết luận.'
      setReview(nextReview)
      setShowReview(true)
      onSessionReview && onSessionReview(sessionId, nextReview)
    } catch (error) {
      console.error('Chat review failed', error)
      const fallbackReview = 'Chưa lấy được kết luận. Vui lòng thử lại.'
      setReview(fallbackReview)
      setShowReview(true)
    } finally {
      setReviewing(false)
    }
  }, [sessionId, topic, onSessionReview])

  useEffect(() => {
    if (!sessionId || !topic) {
      setMessages([])
      setReview('')
      setShowReview(false)
      setReviewing(false)
      setRunning(false)
      cancelRef.current = true
      finalizedRef.current = false
      return
    }

    if (savedReview || !isRunningSession) {
      setRunning(false)
      return
    }

    const initialMessages = session?.messages || []
    cancelRef.current = false
    finalizedRef.current = false
    setMessages(initialMessages)
    setReview('')
    setShowReview(false)
    setReviewing(false)
    setRunning(true)

    const totalMs = 3 * 60 * 1000
    const startedAt = discussionStartedAt || Date.now()
    const elapsed = Date.now() - startedAt
    if (elapsed >= totalMs) {
      finalizeDiscussion()
      return
    }
    setProgress(Math.min(100, (elapsed / totalMs) * 100))
    let step = Math.floor(initialMessages.length / 2)

    async function runConversation() {
      while (!cancelRef.current) {
        try {
          const result = await sendChatStep({ topic, step, sessionId })
          if (cancelRef.current) return
          const nextMessages = result.messages || []
          setMessages(prev => {
            const next = [...prev, ...nextMessages]
            onSessionUpdate && onSessionUpdate(sessionId, next)
            return next
          })
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
  }, [sessionId, topic, isRunningSession, discussionStartedAt, savedReview, finalizeDiscussion, onSessionUpdate])

  function handleStop() {
    cancelRef.current = true
    setRunning(false)
    setProgress(0)
  }

  useEffect(() => {
    if (!running || !topic || savedReview || !isRunningSession) return

    const totalMs = 3 * 60 * 1000
    const startedAt = discussionStartedAt || Date.now()
    const remainingMs = Math.max(0, totalMs - (Date.now() - startedAt))
    const finishTimer = window.setTimeout(() => {
      finalizeDiscussion()
    }, remainingMs)
    const progressTimer = window.setInterval(() => {
      const elapsed = Date.now() - startedAt
      const nextProgress = Math.min(100, (elapsed / totalMs) * 100)
      setProgress(nextProgress)
    }, 200)

    return () => {
      window.clearTimeout(finishTimer)
      window.clearInterval(progressTimer)
    }
  }, [running, topic, savedReview, isRunningSession, discussionStartedAt, finalizeDiscussion])

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight
    }
  }, [messages])

  return (
    <div className="chat-area">
      <div className="chat-surface">
        <div className="chat-header">
          <span className="chat-title">Trò chuyện</span>
          <span className="topic-title">{session ? `Tên chủ đề: ${formatTopicTitle(topic)}` : ''}</span>
          <button className="stop-btn" onClick={handleStop} disabled={!running}>
            Dừng thảo luận
          </button>
        </div>
        {reviewing && (
          <div className="final-report-loader" aria-label="Đang xuất báo cáo cuối">
            <div className="final-report-copy">Đang xuất báo cáo cuối...</div>
            <div className="final-report-track">
              <div className="final-report-bar" />
            </div>
          </div>
        )}
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
        {review && !showReview && (
          <button className="review-reopen" onClick={() => setShowReview(true)}>
            Xem kết luận
          </button>
        )}
      </div>
      <ReviewModal review={showReview ? review : ''} onClose={() => setShowReview(false)} />
    </div>
  )
}
