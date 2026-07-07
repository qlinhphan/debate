import React, { useCallback, useEffect, useRef, useState } from 'react'
import {
  fetchChatReview,
  fetchMultiDocPrompt,
  queryRagDocument,
  saveMultiDocPrompt,
  sendChatStep,
  uploadRagDocument,
} from '../api'

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
    <div className="review-overlay" role="dialog" aria-modal="true" aria-label="Káº¿t luáº­n tháº£o luáº­n">
      <div className="review-modal">
        <div className="review-header">
          <div>
            <div className="review-eyebrow">Káº¿t luáº­n</div>
            <h2 className="review-title">Sau má»™t há»“i bÃ n báº¡c nhanh chÃ³ng thÃ¬</h2>
          </div>
          <button className="review-close" onClick={onClose} aria-label="ÄÃ³ng káº¿t luáº­n">Ã—</button>
        </div>
        <div className="review-body">{review}</div>
      </div>
    </div>
  )
}

function formatTopicTitle(topic) {
  const words = topic.split(/\s+/).filter(Boolean)
  if (!words.length) return 'Chá»§ Ä‘á»'
  const firstFive = words.slice(0, 5)
  return firstFive.length < words.length ? `${firstFive.join(' ')} ...` : firstFive.join(' ')
}

function ToolWorkspace({ type }) {
  const isRag = type === 'rag'
  const fileInputRef = useRef(null)
  const [multiDocPrompt, setMultiDocPrompt] = useState('')
  const [promptStatus, setPromptStatus] = useState('')
  const [promptSaving, setPromptSaving] = useState(false)
  const [showPromptEditor, setShowPromptEditor] = useState(false)
  const [ragQuestion, setRagQuestion] = useState('')
  const [ragStatus, setRagStatus] = useState('ChÆ°a upload tÃ i liá»‡u')
  const [ragUpload, setRagUpload] = useState(null)
  const [ragResult, setRagResult] = useState(null)
  const [ragBusy, setRagBusy] = useState(false)
  const [ragLearning, setRagLearning] = useState(false)

  useEffect(() => {
    if (isRag) {
      setMultiDocPrompt('')
      setPromptStatus('')
      return
    }

    let cancelled = false
    setPromptStatus('Äang táº£i prompt...')
    fetchMultiDocPrompt()
      .then(data => {
        if (cancelled) return
        setMultiDocPrompt(data.prompt || '')
        setPromptStatus(data.file_name ? `Äang dÃ¹ng ${data.file_name}` : 'ÄÃ£ táº£i prompt')
      })
      .catch(error => {
        if (cancelled) return
        console.error('Fetch prompt failed', error)
        setPromptStatus('ChÆ°a táº£i Ä‘Æ°á»£c prompt')
      })

    return () => {
      cancelled = true
    }
  }, [isRag])

  async function handleSavePrompt() {
    if (isRag || promptSaving) return
    setPromptSaving(true)
    setPromptStatus('Äang lÆ°u prompt...')
    try {
      const data = await saveMultiDocPrompt(multiDocPrompt)
      setMultiDocPrompt(data.prompt || '')
      setPromptStatus(`ÄÃ£ lÆ°u vÃ o ${data.file_name || 'prompt_nhieutailieu.json'}`)
    } catch (error) {
      console.error('Save prompt failed', error)
      setPromptStatus('LÆ°u prompt tháº¥t báº¡i')
    } finally {
      setPromptSaving(false)
    }
  }

  async function handleRagFileChange(event) {
    const file = event.target.files?.[0]
    if (!file || ragBusy) return
    setRagBusy(true)
    setRagLearning(true)
    setRagResult(null)
    setRagStatus('Äang upload vÃ  xá»­ lÃ½ tÃ i liá»‡u...')
    try {
      const data = await uploadRagDocument(file)
      setRagUpload(data)
      setRagStatus(`ÄÃ£ xá»­ lÃ½ ${data.file_name} (${data.chunk_count} chunks)`)
    } catch (error) {
      console.error('RAG upload failed', error)
      setRagUpload(null)
      setRagStatus(error.message || 'Upload tháº¥t báº¡i')
    } finally {
      setRagLearning(false)
      setRagBusy(false)
      event.target.value = ''
    }
  }

  async function handleRagQuery() {
    const question = ragQuestion.trim()
    if (!question || ragBusy) return
    setRagBusy(true)
    setRagStatus('Äang tra cá»©u tÃ i liá»‡u...')
    try {
      const data = await queryRagDocument(question)
      setRagResult(data)
      setRagStatus('ÄÃ£ cÃ³ cÃ¢u tráº£ lá»i')
    } catch (error) {
      console.error('RAG query failed', error)
      setRagResult({ answer: error.message || 'Tra cá»©u tháº¥t báº¡i', sources: [] })
      setRagStatus('Tra cá»©u tháº¥t báº¡i')
    } finally {
      setRagBusy(false)
    }
  }

  return (
    <div className="chat-area">
      {isRag && ragLearning && (
        <div className="rag-learning-toast" role="status" aria-live="polite">
          <span className="rag-learning-spinner" aria-hidden="true" />
          <span>Hệ thống đang học tài liệu...</span>
        </div>
      )}
      <div className="tool-workspace">
        <div className="tool-panel tool-primary">
          <div className="tool-kicker">{isRag ? 'RAG Workspace' : 'Document QA'}</div>
          <h1>{isRag ? 'Há»i Ä‘Ã¡p tÃ i liá»‡u' : 'Kiá»ƒm tra lá»—i tÃ i liá»‡u'}</h1>
          <div className="tool-upload">
            <div className="upload-icon">{isRag ? 'RAG' : 'DOC'}</div>
            <div>
              <div className="upload-title">Tháº£ tÃ i liá»‡u vÃ o Ä‘Ã¢y</div>
              <div className="upload-subtitle">{isRag && ragUpload ? ragUpload.file_name : 'File: PDF, DOCX-WORD, TXT'}</div>
            </div>
            <button
              type="button"
              className="upload-button"
              onClick={() => isRag && fileInputRef.current?.click()}
              disabled={isRag && ragBusy}
            >
              {isRag && ragBusy ? 'Đang xử lý...' : 'Chọn tệp'}
            </button>
            {isRag && (
              <input
                ref={fileInputRef}
                type="file"
                className="hidden-file-input"
                accept=".pdf,.docx,.txt"
                onChange={handleRagFileChange}
              />
            )}
          </div>
          <textarea
            className="tool-textarea"
            value={isRag ? ragQuestion : undefined}
            onChange={isRag ? event => setRagQuestion(event.target.value) : undefined}
            placeholder={isRag ? 'Nháº­p cÃ¢u há»i vá» tÃ i liá»‡u...' : 'Nháº­p tiÃªu chÃ­ hoáº·c loáº¡i lá»—i cáº§n kiá»ƒm tra...'}
          />
          <div className="tool-action-row">
            <button
              type="button"
              className="tool-submit"
              onClick={isRag ? handleRagQuery : undefined}
              disabled={isRag && (ragBusy || !ragQuestion.trim())}
            >
              {isRag ? (ragBusy ? 'Đang chạy...' : 'Hỏi tài liệu') : 'Kiểm tra tài liệu'}
            </button>
            {!isRag && (
              <button
                type="button"
                className={`prompt-toggle ${showPromptEditor ? 'active' : ''}`}
                onClick={() => setShowPromptEditor(prev => !prev)}
              >
                Prompt nhiá»u tÃ i liá»‡u
              </button>
            )}
          </div>
          {!isRag && showPromptEditor && (
            <div className="prompt-editor">
              <div className="prompt-editor-header">
                <div>
                  <div className="prompt-editor-title">Prompt nhiá»u tÃ i liá»‡u</div>
                  <div className="prompt-file-name">prompt_nhieutailieu.json</div>
                </div>
                <span className="prompt-status">{promptStatus}</span>
              </div>
              <textarea
                className="prompt-textarea"
                value={multiDocPrompt}
                onChange={event => setMultiDocPrompt(event.target.value)}
                placeholder="Nháº­p prompt kiá»ƒm tra nhiá»u tÃ i liá»‡u..."
              />
              <div className="prompt-actions">
                <button type="button" className="prompt-save" onClick={handleSavePrompt} disabled={promptSaving}>
                  {promptSaving ? 'Äang lÆ°u...' : 'LÆ°u prompt'}
                </button>
              </div>
            </div>
          )}
        </div>
        <div className="tool-panel tool-result">
          <div className="tool-kicker">Káº¿t quáº£</div>
          {isRag && ragResult ? (
            <div className="rag-result">
              <div className="rag-answer">{ragResult.answer}</div>
              <div className="rag-sources">
                {(ragResult.sources || []).map((source, index) => (
                  <div className="rag-source" key={`${source.chunk_index}-${index}`}>
                    <div className="rag-source-meta">
                      <span>{source.source || 'Tài liệu'}</span>
                      <strong>{Math.round((source.score || 0) * 100)}%</strong>
                    </div>
                    <p>{source.text}</p>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="result-placeholder">
              {isRag
                ? 'Câu trả lời dựa trên tài liệu sẽ hiển thị tại đây.'
                : 'Danh sách lỗi, cảnh báo và đề xuất chỉnh sửa sẽ hiển thị tại đây.'}
            </div>
          )}
          <div className="result-grid">
            <div><span>Nguồn</span><strong>{isRag ? (ragResult?.sources?.length || 0) : 0}</strong></div>
            <div><span>Chunks</span><strong>{isRag ? (ragUpload?.chunk_count || '--') : '--'}</strong></div>
            <div><span>Trạng thái</span><strong>{isRag ? ragStatus : 'Chưa chạy'}</strong></div>
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
      const nextReview = result.review || 'ChÆ°a cÃ³ káº¿t luáº­n.'
      setReview(nextReview)
      setShowReview(true)
      onSessionReview && onSessionReview(sessionId, nextReview)
    } catch (error) {
      console.error('Chat review failed', error)
      const fallbackReview = 'ChÆ°a láº¥y Ä‘Æ°á»£c káº¿t luáº­n. Vui lÃ²ng thá»­ láº¡i.'
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
          <span className="chat-title">TrÃ² chuyá»‡n</span>
          <span className="topic-title">{session ? `TÃªn chá»§ Ä‘á»: ${formatTopicTitle(topic)}` : ''}</span>
          <button className="stop-btn" onClick={handleStop} disabled={!running}>
            Dá»«ng tháº£o luáº­n
          </button>
        </div>
        {reviewing && (
          <div className="final-report-loader" aria-label="Äang xuáº¥t bÃ¡o cÃ¡o cuá»‘i">
            <div className="final-report-copy">Äang xuáº¥t bÃ¡o cÃ¡o cuá»‘i...</div>
            <div className="final-report-track">
              <div className="final-report-bar" />
            </div>
          </div>
        )}
        {running && (
          <div className="progress-wrap" aria-label="Tiáº¿n trÃ¬nh tháº£o luáº­n">
            <div className="progress-label">Äang tháº£o luáº­n...</div>
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
            Xem káº¿t luáº­n
          </button>
        )}
      </div>
      <ReviewModal review={showReview ? review : ''} onClose={() => setShowReview(false)} />
    </div>
  )
}

