import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import { Lightbulb, AlertTriangle, XCircle, Info, CheckCircle } from 'lucide-react'
import FileUpload from '../components/FileUpload'
import './ScoreResume.css'

function ScoreResume() {
  const navigate = useNavigate()
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleFileSelect = (selectedFile) => {
    setFile(selectedFile)
    setError(null)
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
      const response = await axios.post('http://localhost:5000/api/resume/score', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      if (response.data.success) {
        // Create PDF URL for viewing
        const pdfUrl = URL.createObjectURL(file)
        
        // Navigate to analysis results page with data
        navigate('/analysis-results', {
          state: {
            analysisData: response.data,
            pdfUrl: pdfUrl,
            fileName: file.name
          }
        })
      } else {
        setError(response.data.error || 'Analysis failed')
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

      {/* Professional Recommendations Section */}
      <div className="recommendations-section">
        <div className="recommendations-header">
          <h2>
            <Lightbulb className="section-icon" />
            Professional Resume Guidelines
          </h2>
          <p>Follow these expert recommendations to create a standout resume</p>
        </div>

        <div className="recommendations-grid">
          {/* Critical Recommendations */}
          <div className="recommendation-category critical">
            <h3>
              <AlertTriangle size={20} />
              Critical Requirements
            </h3>
            <div className="recommendation-list">
              <div className="recommendation-item">
                <h4>Quantify Your Achievements</h4>
                <p>Use specific numbers, percentages, and metrics to demonstrate your impact.</p>
                <div className="examples">
                  <strong>Examples:</strong>
                  <ul>
                    <li>"Increased sales by 25%" instead of "Improved sales"</li>
                    <li>"Managed team of 8" instead of "Led a team"</li>
                    <li>"Reduced processing time by 50%" instead of "Improved efficiency"</li>
                  </ul>
                </div>
              </div>

              <div className="recommendation-item">
                <h4>Use Strong Action Verbs</h4>
                <p>Start bullet points with powerful action verbs in past tense.</p>
                <div className="examples">
                  <strong>Strong verbs:</strong> Achieved, Developed, Implemented, Optimized, Generated, Led, Created, Streamlined
                  <br />
                  <strong>Avoid:</strong> Responsible for, Worked on, Helped with, Assisted
                </div>
              </div>

              <div className="recommendation-item">
                <h4>Include All Essential Sections</h4>
                <p>Ensure your resume has all required sections for ATS compatibility.</p>
                <div className="examples">
                  <strong>Required:</strong> Contact Information, Work Experience, Education, Skills
                  <br />
                  <strong>Optional:</strong> Projects, Certifications, Awards
                </div>
              </div>
            </div>
          </div>

          {/* High Priority Recommendations */}
          <div className="recommendation-category high">
            <h3>
              <XCircle size={20} />
              High Priority
            </h3>
            <div className="recommendation-list">
              <div className="recommendation-item">
                <h4>ATS Optimization</h4>
                <p>Format your resume to pass Applicant Tracking Systems.</p>
                <div className="examples">
                  <strong>Tips:</strong>
                  <ul>
                    <li>Use standard section headings</li>
                    <li>Include relevant keywords from job descriptions</li>
                    <li>Save as PDF format</li>
                    <li>Use simple, clean formatting</li>
                  </ul>
                </div>
              </div>

              <div className="recommendation-item">
                <h4>Consistent Formatting</h4>
                <p>Maintain uniform formatting throughout your resume.</p>
                <div className="examples">
                  <strong>Consistency in:</strong> Date formats, bullet points, font sizes, spacing, alignment
                </div>
              </div>
            </div>
          </div>

          {/* Medium Priority Recommendations */}
          <div className="recommendation-category medium">
            <h3>
              <Info size={20} />
              Medium Priority
            </h3>
            <div className="recommendation-list">
              <div className="recommendation-item">
                <h4>Professional Language</h4>
                <p>Use professional, concise language without buzzwords.</p>
                <div className="examples">
                  <strong>Avoid:</strong> "Dynamic professional," "Think outside the box," "Synergy"
                  <br />
                  <strong>Use:</strong> Specific achievements and concrete examples
                </div>
              </div>

              <div className="recommendation-item">
                <h4>Proper Length</h4>
                <p>Keep your resume to 1-2 pages maximum.</p>
                <div className="examples">
                  <strong>Guidelines:</strong> 1 page for entry-level, 2 pages for experienced professionals
                </div>
              </div>
            </div>
          </div>

          {/* Best Practices */}
          <div className="recommendation-category good">
            <h3>
              <CheckCircle size={20} />
              Best Practices
            </h3>
            <div className="recommendation-list">
              <div className="recommendation-item">
                <h4>Tailor for Each Application</h4>
                <p>Customize your resume for each job application.</p>
                <div className="examples">
                  <strong>Strategies:</strong>
                  <ul>
                    <li>Match keywords from job description</li>
                    <li>Highlight relevant experience</li>
                    <li>Adjust skills section</li>
                  </ul>
                </div>
              </div>

              <div className="recommendation-item">
                <h4>Proofread Thoroughly</h4>
                <p>Ensure your resume is error-free before submitting.</p>
                <div className="examples">
                  <strong>Check for:</strong> Spelling errors, grammar mistakes, formatting inconsistencies, contact information accuracy
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>
  )
}

export default ScoreResume
