import React from 'react'
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom'
import './App.css'
import Home from './pages/Home'
import ScoreResume from './pages/ScoreResume'
import TargetResume from './pages/TargetResume'
import AnalysisResults from './pages/AnalysisResults'

function App() {
  return (
    <Router>
      <div className="App">
        <nav className="navbar">
          <div className="nav-container">
            <Link to="/" className="nav-logo">
              📄 Resume Reviewer
            </Link>
            <div className="nav-links">
              <Link to="/score-resume" className="nav-link">Score Resume</Link>
              <Link to="/target-resume" className="nav-link">Job Match</Link>
            </div>
          </div>
        </nav>

        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/score-resume" element={<ScoreResume />} />
          <Route path="/target-resume" element={<TargetResume />} />
          <Route path="/analysis-results" element={<AnalysisResults />} />
          {/* Redirect old routes */}
          <Route path="/score" element={<Navigate to="/score-resume" replace />} />
          <Route path="/target" element={<Navigate to="/target-resume" replace />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
