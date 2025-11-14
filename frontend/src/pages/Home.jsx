import React from 'react'
import { Link } from 'react-router-dom'
import { FileText, Target, Sparkles } from 'lucide-react'
import './Home.css'

function Home() {
  return (
    <div className="home">
      <div className="hero">
        <h1 className="hero-title">Improve Your Resume with AI</h1>
        <p className="hero-subtitle">
          Get instant feedback on your resume with our AI-powered analysis.
          Optimize for ATS systems and land your dream job.
        </p>
      </div>

      <div className="features">
        <div className="feature-card">
          <div className="feature-icon" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
            <FileText size={32} color="white" />
          </div>
          <h3>Resume Scoring</h3>
          <p>
            Get a comprehensive score based on ATS compatibility, content quality,
            keyword optimization, and structure.
          </p>
          <Link to="/score-resume" className="feature-link">
            Score Resume →
          </Link>
        </div>

        <div className="feature-card">
          <div className="feature-icon" style={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' }}>
            <Target size={32} color="white" />
          </div>
          <h3>Job Matching</h3>
          <p>
            Upload your resume and a job description to see how well they match.
            Get suggestions for missing keywords and skills.
          </p>
          <Link to="/target" className="feature-link">
            Match Job →
          </Link>
        </div>

        <div className="feature-card">
          <div className="feature-icon" style={{ background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' }}>
            <Sparkles size={32} color="white" />
          </div>
          <h3>AI Improvements</h3>
          <p>
            Get line-by-line suggestions to improve your bullet points with
            stronger action verbs and quantifiable metrics.
          </p>
          <Link to="/score-resume" className="feature-link">
            Get Started →
          </Link>
        </div>
      </div>

      <div className="cta-section">
        <h2>Ready to improve your resume?</h2>
        <p>Start with a free resume analysis and get actionable feedback in seconds.</p>
        <Link to="/score-resume" className="cta-button">
          Analyze My Resume
        </Link>
      </div>
    </div>
  )
}

export default Home
