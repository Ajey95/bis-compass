import React, { useState, useEffect } from 'react'

export default function LoadingState() {
  const [message, setMessage] = useState('Parsing product description...')

  const messages = [
    "Parsing product description...",
    "Scanning BIS standards index...",
    "Running hybrid retrieval...",
    "Reranking and preparing rationale..."
  ]

  useEffect(() => {
    let messageIndex = 0
    const interval = setInterval(() => {
      messageIndex = (messageIndex + 1) % messages.length
      setMessage(messages[messageIndex])
    }, 1500)

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="loading-state">
      <div className="loading-spinner"></div>
      <div className="loading-message">
        {message}
      </div>
      <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
        Avg response time: ~2-3 seconds on a warm cache
      </p>
    </div>
  )
}
