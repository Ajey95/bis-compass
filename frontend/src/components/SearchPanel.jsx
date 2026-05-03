import React, { useState } from 'react'

export default function SearchPanel({ onSearch, isLoading }) {
  const [query, setQuery] = useState('')

  const exampleQueries = [
    "OPC Cement 53 Grade",
    "TMT Steel Bars Fe500",
    "Coarse Aggregate 20mm",
    "Fly Ash Bricks",
    "Hollow Concrete Blocks"
  ]

  const handleSubmit = (e) => {
    e.preventDefault()
    if (query.trim()) {
      onSearch(query)
    }
  }

  const handleChipSubmit = (chipText) => {
    setQuery(chipText)
    // Submit with the chip query
    setTimeout(() => onSearch(chipText), 0)
  }

  return (
    <div className="search-panel">
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="query" className="form-label">Product Description</label>
          <p className="field-help">
            Describe the product in plain language. The demo shows the top 3 recommendations, while the backend returns the full ranked list.
          </p>
          <div className="textarea-wrapper">
            <textarea
              id="query"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Describe your product... e.g. 'Portland cement for structural concrete in high-humidity coastal construction'"
              disabled={isLoading}
            />
          </div>
        </div>

        <div>
          <p className="form-label" style={{ marginBottom: '0.75rem' }}>Try these examples:</p>
          <div className="chip-container">
            {exampleQueries.map((example, idx) => (
              <button
                type="button"
                key={idx}
                className="chip"
                onClick={() => handleChipSubmit(example)}
              >
                {example}
              </button>
            ))}
          </div>
        </div>

        <button
          type="submit"
          className="submit-btn"
          disabled={isLoading || !query.trim()}
        >
          {isLoading ? (
            <>
              <span className="pulse">SCANNING DATABASE</span>
              <span className="loading-dots">...</span>
            </>
          ) : (
            'SCAN STANDARDS →'
          )}
        </button>
      </form>
    </div>
  )
}
