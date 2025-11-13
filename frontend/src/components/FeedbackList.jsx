import React, { useState } from 'react'
import { ChevronDown, ChevronUp, AlertTriangle, Info } from 'lucide-react'
import './FeedbackList.css'

function FeedbackList({ feedback, recommendations }) {
  const [expandedItems, setExpandedItems] = useState(new Set())

  const toggleItem = (index) => {
    const newExpanded = new Set(expandedItems)
    if (newExpanded.has(index)) {
      newExpanded.delete(index)
    } else {
      newExpanded.add(index)
    }
    setExpandedItems(newExpanded)
  }

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high':
      case 'critical':
        return '#ef4444'
      case 'medium':
        return '#f59e0b'
      case 'low':
        return '#3b82f6'
      default:
        return '#6b7280'
    }
  }

  return (
    <div className="feedback-list">
      {recommendations && recommendations.length > 0 && (
        <div className="recommendations-section">
          <h3>Top Recommendations</h3>
          <div className="recommendation-cards">
            {recommendations.map((rec, index) => (
              <div key={index} className="recommendation-card" style={{ borderLeftColor: getSeverityColor(rec.priority) }}>
                <div className="recommendation-header">
                  <AlertTriangle size={20} color={getSeverityColor(rec.priority)} />
                  <span className="recommendation-category">{rec.category}</span>
                  <span className="priority-badge" style={{ backgroundColor: getSeverityColor(rec.priority) }}>
                    {rec.priority}
                  </span>
                </div>
                <p className="recommendation-message">{rec.message}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {feedback && feedback.length > 0 && (
        <div className="feedback-section">
          <h3>Line-by-Line Feedback</h3>
          <div className="feedback-items">
            {feedback.map((item, index) => (
              <div key={index} className="feedback-item">
                <div className="feedback-header" onClick={() => toggleItem(index)}>
                  <div className="feedback-text-preview">
                    <Info size={18} color="#667eea" />
                    <span>{item.text}</span>
                  </div>
                  {expandedItems.has(index) ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                </div>
                
                {expandedItems.has(index) && (
                  <div className="feedback-details">
                    {item.issues && item.issues.map((issue, issueIndex) => (
                      <div key={issueIndex} className="issue-item" style={{ borderLeftColor: getSeverityColor(issue.severity) }}>
                        <span className="issue-type">{issue.type.replace(/_/g, ' ')}</span>
                        <p className="issue-message">{issue.message}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default FeedbackList
