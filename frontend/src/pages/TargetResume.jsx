import React, { useState } from 'react'
import axios from 'axios'
import FileUpload from '../components/FileUpload'
import JobDescriptionInput from '../components/JobDescriptionInput'
import { CheckCircle, XCircle, TrendingUp } from 'lucide-react'
import './TargetResume.css'

function TargetResume() {
  const [file, setFile] = useState(null)
  const [jobDescription, setJobDescription] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  const handleFileSelect = (selectedFile) => {
    setFile(selectedFile)
    setError(null)
    setResult(null)
  }

  const handleMatch = async () => {
    if (!file) {
      setError('Please select a resume file')
      return
    }

    if (!jobDescription.trim()) {
      setError('Please enter a job description')
      return
    }

    setLoading(true)
    setError(null)

    const formData = new FormData()
    formData.append('resume', file)
    formData.append('jobDescription', jobDescription)

    try {
      const response = await axios.post('/api/resume/target', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      if (response.data.success) {
        setResult(response.data.data)
      } else {
        setError(response.data.error || 'Failed to match resume')
      }
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred while matching your resume')
    } finally {
      setLoading(false)
    }
  }

  const getMatchColor = (percentage) => {
    if (percentage >= 70) return '#22c55e'
    if (percentage >= 50) return '#eab308'
    return '#ef4444'
  }

  return (
    <div className="container">
      <div className="page-header">
        <h1>Job Matching Analysis</h1>
        <p>Compare your resume against a job description to see how well they align</p>
      </div>

      <div className="card">
        <FileUpload onFileSelect={handleFileSelect} />
        <JobDescriptionInput 
          value={jobDescription} 
          onChange={setJobDescription}
        />

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <div className="button-group">
          <button
            className="button"
            onClick={handleMatch}
            disabled={!file || !jobDescription.trim() || loading}
          >
            {loading ? 'Matching...' : 'Match Resume'}
          </button>
        </div>
      </div>

      {loading && (
        <div className="loading">
          <div className="spinner"></div>
          <p>Analyzing match... This may take a few moments.</p>
        </div>
      )}

      {result && (
        <>
          <div className="card">
            <h2>Match Score</h2>
            <div className="match-score-container">
              <div 
                className="match-circle" 
                style={{ borderColor: getMatchColor(result.matchPercentage) }}
              >
                <div 
                  className="match-percentage" 
                  style={{ color: getMatchColor(result.matchPercentage) }}
                >
                  {result.matchPercentage}%
                </div>
                <div className="match-label">Match</div>
              </div>
              <div className="match-info">
                <div className="match-stat">
                  <CheckCircle size={24} color="#22c55e" />
                  <div>
                    <div className="match-stat-value">{result.matchedKeywords?.length || 0}</div>
                    <div className="match-stat-label">Matched Keywords</div>
                  </div>
                </div>
                <div className="match-stat">
                  <XCircle size={24} color="#ef4444" />
                  <div>
                    <div className="match-stat-value">{result.missingKeywords?.length || 0}</div>
                    <div className="match-stat-label">Missing Keywords</div>
                  </div>
                </div>
                <div className="match-stat">
                  <TrendingUp size={24} color="#667eea" />
                  <div>
                    <div className="match-stat-value">{result.resumeKeywords?.length || 0}</div>
                    <div className="match-stat-label">Your Keywords</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {result.matchedKeywords && result.matchedKeywords.length > 0 && (
            <div className="card">
              <h2>Matched Keywords</h2>
              <div className="keyword-tags">
                {result.matchedKeywords.map((keyword, index) => (
                  <span key={index} className="keyword-tag matched">
                    {keyword}
                  </span>
                ))}
              </div>
            </div>
          )}

          {result.missingKeywords && result.missingKeywords.length > 0 && (
            <div className="card">
              <h2>Missing Keywords</h2>
              <p className="missing-keywords-hint">
                Consider adding these keywords to your resume to improve your match:
              </p>
              <div className="keyword-tags">
                {result.missingKeywords.map((keyword, index) => (
                  <span key={index} className="keyword-tag missing">
                    {keyword}
                  </span>
                ))}
              </div>
            </div>
          )}

          {result.suggestions && result.suggestions.length > 0 && (
            <div className="card">
              <h2>Recommendations</h2>
              <ul className="suggestions-list">
                {result.suggestions.map((suggestion, index) => (
                  <li key={index}>{suggestion}</li>
                ))}
              </ul>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default TargetResume
