import React, { useState } from 'react'
import SearchPanel from './components/SearchPanel'
import LoadingState from './components/LoadingState'
import ResultCard from './components/ResultCard'

export default function App() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [latency, setLatency] = useState(null)
  const [showMoreResults, setShowMoreResults] = useState(false)
  const visibleResults = results ? results.slice(0, 3) : []
  const hiddenResults = results ? results.slice(3) : []

  const handleSearch = async (searchQuery) => {
    setQuery(searchQuery)
    setIsLoading(true)
    setError(null)
    setResults(null)
    setShowMoreResults(false)

    try {
      const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: searchQuery,
          top_k: 5
        })
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }

      const data = await response.json()
      setResults(data.retrieved_standards)
      setLatency(data.latency_seconds)
    } catch (err) {
      setError(`Failed to retrieve standards: ${err.message}`)
      console.error('Search error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const getLatencyClass = (latency) => {
    if (latency < 3) return 'latency-fast'
    if (latency < 5) return 'latency-medium'
    return 'latency-slow'
  }

  const strongMatchCount = (() => {
    if (!visibleResults.length) return 0

    const scores = visibleResults
      .map((result) => Number(result.score))
      .filter((score) => Number.isFinite(score))

    if (!scores.length) return visibleResults.length

    const topScore = Math.max(...scores)
    const lowestScore = Math.min(...scores)
    const threshold = topScore - ((topScore - lowestScore) * 0.35)

    return visibleResults.filter((result) => Number(result.score) >= threshold).length
  })()

  return (
    <div className="container app-shell">
      <section className="hero-panel">
        <div className="hero-copy">
          <h1 className="header-title">BIS-COMPASS</h1>
          <p className="header-subtitle">Section-aware hybrid retrieval for BIS building-material standards</p>
        </div>
      </section>

      <SearchPanel onSearch={handleSearch} isLoading={isLoading} />

      {isLoading && <LoadingState />}

      {error && (
        <div className="error-message">
          ⚠️ {error}
        </div>
      )}

      {results && !isLoading && (
        <div className="results-section">
          <div className="results-header">
            <div className="results-count-wrap">
              <div className="results-count">
                <strong>{visibleResults.length}</strong> standards shown
                <span className="results-count-subtext">from {results.length} retrieved</span>
              </div>
              <div className="results-query">Query: {query}</div>
            </div>
            {latency !== null && (
              <div className={`latency-badge ${getLatencyClass(latency)}`}>
                ⚡ {latency.toFixed(2)}s
              </div>
            )}
          </div>

          <div className="metrics-row">
            <div className="metric-card">
              <div className="metric-label">Candidates Retrieved</div>
              <div className="metric-value">{results.length}</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Query Time</div>
              <div className="metric-value">{latency?.toFixed(2)}s</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Strong Matches</div>
              <div className="metric-value">{strongMatchCount}</div>
            </div>
          </div>

          <div className="results-note">
            Showing the top 3 results first. Click to reveal the remaining results.
          </div>

          <div className="results-list">
            {visibleResults.map((standard, index) => (
              <ResultCard key={standard.standard_number} standard={standard} index={index} />
            ))}
          </div>

          {hiddenResults.length > 0 && (
            <div className="results-dropdown">
              <button
                type="button"
                className="results-dropdown-toggle"
                onClick={() => setShowMoreResults((current) => !current)}
              >
                {showMoreResults ? 'Hide extra results' : `Show ${hiddenResults.length} more results`}
              </button>

              {showMoreResults && (
                <div className="results-dropdown-panel">
                  {hiddenResults.map((standard, index) => (
                    <ResultCard key={standard.standard_number} standard={standard} index={index + 3} />
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      <footer className="footer">
        <p>Built for BIS × SS Hackathon | Powered by RAG + Groq LLM</p>
      </footer>
    </div>
  )
}
