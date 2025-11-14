import React from 'react'
import { CheckCircle, AlertTriangle, XCircle, Target, Calendar, FileText, Zap, Award, Layout, Bot } from 'lucide-react'
import './CriteriaCards.css'

const CriteriaCards = ({ criteria }) => {
  if (!criteria || criteria.length === 0) return null

  const getScoreColor = (score) => {
    if (score <= 1) return '#ef4444' // Red
    if (score <= 3) return '#f59e0b' // Yellow/Orange
    return '#10b981' // Green
  }

  const getScoreIcon = (score) => {
    if (score <= 1) return <XCircle size={20} />
    if (score <= 3) return <AlertTriangle size={20} />
    return <CheckCircle size={20} />
  }

  const getCriterionIcon = (name) => {
    switch (name.toLowerCase()) {
      case 'quantify impact':
        return <Target size={20} />
      case 'dates':
        return <Calendar size={20} />
      case 'summary':
        return <FileText size={20} />
      case 'buzzwords':
        return <Zap size={20} />
      case 'skills section':
        return <Award size={20} />
      case 'structure':
        return <Layout size={20} />
      case 'ats compatibility':
        return <Bot size={20} />
      default:
        return <CheckCircle size={20} />
    }
  }

  const getScoreLabel = (score) => {
    if (score <= 1) return 'Needs Work'
    if (score <= 3) return 'Good Progress'
    return 'Excellent'
  }

  return (
    <div className="criteria-cards">
      <div className="criteria-header">
        <h2>Resume Analysis Criteria</h2>
        <p className="criteria-subtitle">
          Each criterion is scored from 0-5 based on professional resume standards
        </p>
      </div>
      
      <div className="criteria-grid">
        {criteria.map((criterion, index) => (
          <div 
            key={index}
            className="criterion-card"
            style={{ borderLeftColor: getScoreColor(criterion.score) }}
          >
            <div className="criterion-header">
              <div className="criterion-title">
                <div className="criterion-icon">
                  {getCriterionIcon(criterion.name)}
                </div>
                <h3>{criterion.name}</h3>
              </div>
              
              <div className="criterion-score">
                <div 
                  className="score-circle"
                  style={{ backgroundColor: getScoreColor(criterion.score) }}
                >
                  <span className="score-number">{criterion.score}</span>
                  <span className="score-max">/5</span>
                </div>
              </div>
            </div>

            <div className="criterion-content">
              <div className="score-status">
                <div 
                  className="status-indicator"
                  style={{ color: getScoreColor(criterion.score) }}
                >
                  {getScoreIcon(criterion.score)}
                  <span className="status-label">
                    {getScoreLabel(criterion.score)}
                  </span>
                </div>
              </div>

              <div className="criterion-description">
                <p>{criterion.description}</p>
              </div>

              {/* Progress bar */}
              <div className="score-progress">
                <div className="progress-bar">
                  <div 
                    className="progress-fill"
                    style={{ 
                      width: `${(criterion.score / 5) * 100}%`,
                      backgroundColor: getScoreColor(criterion.score)
                    }}
                  />
                </div>
                <div className="progress-labels">
                  <span>0</span>
                  <span>1</span>
                  <span>2</span>
                  <span>3</span>
                  <span>4</span>
                  <span>5</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Summary Stats */}
      <div className="criteria-summary">
        <div className="summary-stats">
          <div className="stat-item">
            <span className="stat-label">Criteria Evaluated:</span>
            <span className="stat-value">{criteria.length}</span>
          </div>
          
          <div className="stat-item">
            <span className="stat-label">Average Score:</span>
            <span className="stat-value">
              {(criteria.reduce((sum, c) => sum + c.score, 0) / criteria.length).toFixed(1)}/5
            </span>
          </div>
          
          <div className="stat-item">
            <span className="stat-label">Excellent Criteria:</span>
            <span className="stat-value" style={{ color: '#10b981' }}>
              {criteria.filter(c => c.score >= 4).length}
            </span>
          </div>

          <div className="stat-item">
            <span className="stat-label">Need Improvement:</span>
            <span className="stat-value" style={{ color: '#ef4444' }}>
              {criteria.filter(c => c.score <= 1).length}
            </span>
          </div>
        </div>

        <div className="next-steps">
          <h4>Priority Actions</h4>
          <ul>
            {criteria
              .filter(c => c.score <= 1)
              .slice(0, 3)
              .map((criterion, index) => (
                <li key={index} className="priority-action">
                  <strong>{criterion.name}:</strong> {criterion.description}
                </li>
              ))}
            {criteria.filter(c => c.score <= 1).length === 0 && (
              <li className="no-critical-issues">
                <CheckCircle size={16} color="#10b981" />
                Great! No critical issues found. Focus on areas scoring 2-3 to reach excellence.
              </li>
            )}
          </ul>
        </div>
      </div>
    </div>
  )
}

export default CriteriaCards
