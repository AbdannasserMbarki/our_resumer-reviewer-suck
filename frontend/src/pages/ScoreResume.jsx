import React, { useState } from 'react'
import axios from 'axios'
import FileUpload from '../components/FileUpload'
import ScoreCard from '../components/ScoreCard'
import FeedbackList from '../components/FeedbackList'
import './ScoreResume.css'

function ScoreResume() {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  const handleFileSelect = (selectedFile) => {
    setFile(selectedFile)
    setError(null)
    setResult(null)
  }

  const handleAnalyze = async () => {
    if (!file) {
      setError('Please select a file first')
      return
    }

    setLoading(true)
    setError(null)

    const formData = new FormData()
    formData.append('resume', file)

    try {
      const response = await axios.post('/api/resume/score', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      if (response.data.success) {
        setResult(response.data.data)
      } else {
        setError(response.data.error || 'Failed to analyze resume')
      }
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred while analyzing your resume')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <div className="page-header">
        <h1>Resume Scoring & Analysis</h1>
        <p>Upload your resume to get a comprehensive score and detailed feedback</p>
      </div>

      <div className="card">
        <FileUpload onFileSelect={handleFileSelect} />

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <div className="button-group">
          <button
            className="button"
            onClick={handleAnalyze}
            disabled={!file || loading}
          >
            {loading ? 'Analyzing...' : 'Analyze Resume'}
          </button>
        </div>
      </div>

      {loading && (
        <div className="loading">
          <div className="spinner"></div>
          <p>Analyzing your resume... This may take a few moments.</p>
        </div>
      )}

      {result && (
        <>
          <div className="card">
            <h2>Overall Score</h2>
            <ScoreCard score={result.score} breakdown={result.breakdown} />
          </div>

          {result.feedback && result.feedback.length > 0 && (
            <div className="card">
              <h2>Detailed Feedback</h2>
              <FeedbackList 
                feedback={result.feedback} 
                recommendations={result.recommendations}
              />
            </div>
          )}

          {result.statistics && (
            <div className="card">
              <h2>Statistics</h2>
              <div className="statistics-grid">
                <div className="stat-item">
                  <div className="stat-value">{result.statistics.total_bullets}</div>
                  <div className="stat-label">Total Bullet Points</div>
                </div>
                <div className="stat-item">
                  <div className="stat-value">{result.statistics.metrics_percentage}%</div>
                  <div className="stat-label">With Metrics</div>
                </div>
                <div className="stat-item">
                  <div className="stat-value">{result.statistics.strong_verbs_percentage}%</div>
                  <div className="stat-label">Strong Action Verbs</div>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default ScoreResume
