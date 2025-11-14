import React from 'react'
import './ScoreCard.css'

function ScoreCard({ score, breakdown, performanceTier }) {
  const getScoreColor = (score) => {
    if (performanceTier?.color) return performanceTier.color
    if (score >= 80) return '#22c55e'
    if (score >= 60) return '#eab308'
    return '#ef4444'
  }

  const getScoreLabel = (score) => {
    if (performanceTier?.tier) return performanceTier.tier
    if (score === 0) return 'Incomplete Resume'
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
        
        {performanceTier && (
          <div className="performance-tier" style={{ color: performanceTier.color }}>
            <div className="tier-description">{performanceTier.description}</div>
            {performanceTier.advice && (
              <div className="tier-advice">{performanceTier.advice}</div>
            )}
          </div>
        )}
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
                  width: `${(breakdown.content_quality / 30) * 100}%`,
                  backgroundColor: scoreColor
                }}
              />
            </div>
            <span className="breakdown-score">{breakdown.content_quality}/30</span>
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

          {breakdown.achievement_impact !== undefined && (
            <div className="breakdown-item">
              <span className="breakdown-name">Achievement Impact</span>
              <div className="breakdown-bar">
                <div
                  className="breakdown-fill"
                  style={{
                    width: `${(breakdown.achievement_impact / 10) * 100}%`,
                    backgroundColor: scoreColor
                  }}
                />
              </div>
              <span className="breakdown-score">{breakdown.achievement_impact}/10</span>
            </div>
          )}

          {breakdown.language_quality !== undefined && (
            <div className="breakdown-item">
              <span className="breakdown-name">Language Quality</span>
              <div className="breakdown-bar">
                <div
                  className="breakdown-fill"
                  style={{
                    width: `${(breakdown.language_quality / 5) * 100}%`,
                    backgroundColor: scoreColor
                  }}
                />
              </div>
              <span className="breakdown-score">{breakdown.language_quality}/5</span>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default ScoreCard
