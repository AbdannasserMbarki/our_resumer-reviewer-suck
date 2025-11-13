import React from 'react'
import './ScoreCard.css'

function ScoreCard({ score, breakdown }) {
  const getScoreColor = (score) => {
    if (score >= 80) return '#22c55e'
    if (score >= 60) return '#eab308'
    return '#ef4444'
  }

  const getScoreLabel = (score) => {
    if (score >= 80) return 'Excellent'
    if (score >= 60) return 'Good'
    if (score >= 40) return 'Fair'
    return 'Needs Improvement'
  }

  const scoreColor = getScoreColor(score)
  const scoreLabel = getScoreLabel(score)

  return (
    <div className="score-card">
      <div className="score-main">
        <div className="score-circle" style={{ borderColor: scoreColor }}>
          <div className="score-number" style={{ color: scoreColor }}>
            {score}
          </div>
          <div className="score-label">{scoreLabel}</div>
        </div>
      </div>

      <div className="score-breakdown">
        <h3>Score Breakdown</h3>
        <div className="breakdown-items">
          <div className="breakdown-item">
            <span className="breakdown-name">ATS Compatibility</span>
            <div className="breakdown-bar">
              <div
                className="breakdown-fill"
                style={{
                  width: `${(breakdown.ats_compatibility / 25) * 100}%`,
                  backgroundColor: scoreColor
                }}
              />
            </div>
            <span className="breakdown-score">{breakdown.ats_compatibility}/25</span>
          </div>

          <div className="breakdown-item">
            <span className="breakdown-name">Content Quality</span>
            <div className="breakdown-bar">
              <div
                className="breakdown-fill"
                style={{
                  width: `${(breakdown.content_quality / 40) * 100}%`,
                  backgroundColor: scoreColor
                }}
              />
            </div>
            <span className="breakdown-score">{breakdown.content_quality}/40</span>
          </div>

          <div className="breakdown-item">
            <span className="breakdown-name">Keyword Optimization</span>
            <div className="breakdown-bar">
              <div
                className="breakdown-fill"
                style={{
                  width: `${(breakdown.keyword_optimization / 20) * 100}%`,
                  backgroundColor: scoreColor
                }}
              />
            </div>
            <span className="breakdown-score">{breakdown.keyword_optimization}/20</span>
          </div>

          <div className="breakdown-item">
            <span className="breakdown-name">Structure</span>
            <div className="breakdown-bar">
              <div
                className="breakdown-fill"
                style={{
                  width: `${(breakdown.structure / 15) * 100}%`,
                  backgroundColor: scoreColor
                }}
              />
            </div>
            <span className="breakdown-score">{breakdown.structure}/15</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ScoreCard
