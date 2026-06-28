import React, { useState } from 'react'

export default function Sidebar({
  open = true,
  onToggle,
  onSendTopic,
  onNewChat,
  topicHistory = [],
  onSelectHistory,
  activeSessionId,
  activeTool = 'chat',
  onSelectTool,
}) {
  const [topic, setTopic] = useState('')
  const [historyOpen, setHistoryOpen] = useState(true)

  function handleSend() {
    const cleanTopic = topic.trim()
    if (!cleanTopic) return
    onSendTopic && onSendTopic(cleanTopic)
    setTopic('')
  }

  function handleToolSelect(tool) {
    onSelectTool && onSelectTool(tool)
  }

  return (
    <div className={`sidebar ${open ? 'open' : 'closed'}`}>
      <div className="sidebar-header">
        <button className="toggle-btn" onClick={onToggle} aria-label="Ẩn hiện thanh bên">
          {open ? '<' : ''}
        </button>
        <div className="logo" onClick={() => !open && onToggle && onToggle()} title="Mở thanh bên">
          <img src="/over.png" alt="think continuosly" />
        </div>
        <div className="title-wrap">
          <h3 className="title">AI Debate</h3>
          <div className="subtitle">Think continuously & decide efficiently</div>
        </div>
      </div>
      <div className="sidebar-body">
        <div className="topic-block">
          <label className="topic-label">Chủ đề</label>
          <input
            className="topic-input"
            placeholder="Nhập chủ đề cuộc thảo luận..."
            value={topic}
            onChange={e => setTopic(e.target.value)}
            onKeyDown={e => {
              if (e.key === 'Enter') {
                e.preventDefault()
                handleSend()
              }
            }}
          />
          <button className="send-topic" onClick={handleSend}>Gửi chủ đề</button>
        </div>
        <div className={`topic-history ${historyOpen ? 'open' : 'collapsed'}`}>
          <button
            type="button"
            className="history-toggle"
            onClick={() => setHistoryOpen(value => !value)}
            aria-expanded={historyOpen}
            aria-label={historyOpen ? 'Ẩn lịch sử chủ đề' : 'Hiện lịch sử chủ đề'}
          >
            <span className="history-title">Lịch sử chủ đề</span>
            <span className={`history-caret ${historyOpen ? 'open' : ''}`} aria-hidden="true" />
          </button>
          {historyOpen && (
            <div className="history-list">
              {topicHistory.length === 0 ? (
                <div className="history-empty">Chưa có chủ đề nào</div>
              ) : (
                topicHistory.map((item) => (
                  <button
                    type="button"
                    className={`history-item ${item.id === activeSessionId && activeTool === 'chat' ? 'active' : ''}`}
                    key={item.id}
                    onClick={() => onSelectHistory && onSelectHistory(item.id)}
                  >
                    {item.summary}
                  </button>
                ))
              )}
            </div>
          )}
        </div>
      </div>
      <div className="sidebar-footer">
        <button className="footer-action new-chat" onClick={onNewChat}>Trò chuyện mới</button>
        <div className="more-actions">
          <button className={`footer-action more-action ${activeTool !== 'chat' ? 'active' : ''}`}>Chức năng khác</button>
          <div className="tool-menu">
            <button
              type="button"
              className={activeTool === 'rag' ? 'active' : ''}
              onClick={() => handleToolSelect('rag')}
            >
              Hỏi đáp tài liệu (RAG)
            </button>
            <button
              type="button"
              className={activeTool === 'doc-check' ? 'active' : ''}
              onClick={() => handleToolSelect('doc-check')}
            >
              Kiểm tra lỗi tài liệu
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
