import React, { useState } from 'react'

export default function Sidebar({ open = true, onToggle, onSendTopic, onNewChat, topicHistory = [], onSelectHistory, activeSessionId }) {
  const [topic, setTopic] = useState('')
  const [historyOpen, setHistoryOpen] = useState(true)

  function handleSend() {
    const cleanTopic = topic.trim()
    if (!cleanTopic) return
    onSendTopic && onSendTopic(cleanTopic)
    setTopic('')
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
          <h3 className="title">AI Debate </h3>
          <div className="subtitle">Think continously & decide efficently</div>
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
                    className={`history-item ${item.id === activeSessionId ? 'active' : ''}`}
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
        <button className="new-chat" onClick={onNewChat}>Trò chuyện mới</button>
      </div>
    </div>
  )
}
