import React from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import './App.css'
import Home from './pages/Home'
import ScoreResume from './pages/ScoreResume'
import TargetResume from './pages/TargetResume'

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
              <Link to="/score" className="nav-link">Score Resume</Link>
              <Link to="/target" className="nav-link">Job Match</Link>
            </div>
          </div>
        </nav>

        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/score" element={<ScoreResume />} />
          <Route path="/target" element={<TargetResume />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
