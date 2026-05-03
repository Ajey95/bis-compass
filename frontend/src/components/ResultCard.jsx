import React from 'react'

export default function ResultCard({ standard, index }) {
  const normalizeStandardNumber = (value) => {
    return String(value || '')
      .replace(/\s+/g, ' ')
      .replace(/\s*:\s*/g, ': ')
      .replace(/\s*\(\s*Part\s*/i, ' (Part ')
      .trim()
  }

  const getRelevanceColor = (relevance) => {
    switch(relevance) {
      case 'high':
        return 'high'
      case 'medium':
        return 'medium'
      case 'low':
        return 'low'
      default:
        return 'medium'
    }
  }

  const rankFormatted = String(index + 1).padStart(2, '0')
  const canonicalNumber = normalizeStandardNumber(standard.standard_number)
  const relevanceLabel = (standard.relevance || 'medium').toUpperCase()

  return (
    <div
      className="result-card"
      style={{
        animationDelay: `${index * 0.1}s`
      }}
    >
      <div className="result-card-topline">
        <div className="result-rank">{rankFormatted}</div>
        <div className="result-card-header">
          <div className="result-standard-number">
            {canonicalNumber}
          </div>
          <div className={`badge ${getRelevanceColor(standard.relevance)}`}>
            {relevanceLabel}
          </div>
        </div>
      </div>

      <h3 className="result-title">
        {standard.title}
      </h3>

      <div className="result-meta-row">
        <div className="result-category">
          {standard.category}
        </div>
        <div className="result-pill">
          Top #{index + 1}
        </div>
      </div>

      <p className="result-rationale">
        {standard.rationale}
      </p>

      <div className="result-footer">
        <span className="result-footnote">
          Retrieved from the BIS building-material corpus.
        </span>
        {index === 0 && (
          <span className="result-spotlight">Best match</span>
        )}
      </div>
    </div>
  )
}
