import React, { useState, useEffect, useMemo } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { ArrowLeft, Download, RefreshCw, FileText, CheckCircle, XCircle, Target, TrendingUp, AlertTriangle, Info, Lightbulb, BookOpen, ChevronDown, ChevronUp, Filter, Eye, EyeOff } from 'lucide-react'
import { Document, Page, pdfjs } from 'react-pdf'
import CriteriaCards from '../components/CriteriaCards'
import 'react-pdf/dist/Page/AnnotationLayer.css'
import 'react-pdf/dist/Page/TextLayer.css'
import './AnalysisResults.css'

// Use the exact version that matches the installed pdfjs-dist API
pdfjs.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@5.4.296/build/pdf.worker.min.mjs`

function AnalysisResults() {
  const location = useLocation()
  const navigate = useNavigate()
  const [analysisData, setAnalysisData] = useState(null)
  const [isReanalyzing, setIsReanalyzing] = useState(false)
  const [pdfUrl, setPdfUrl] = useState(null)
  const [numPages, setNumPages] = useState(null)
  const [pageNumber, setPageNumber] = useState(1)
  const [pdfError, setPdfError] = useState(null)
  const [highlightTerms, setHighlightTerms] = useState([])
  const [scale, setScale] = useState(1.0)
  const [fitMode, setFitMode] = useState('width') // 'width', 'height', 'page', 'custom'
  const [showCriteria, setShowCriteria] = useState(true)
  const [criteriaFilter, setCriteriaFilter] = useState('all') // 'all', 'critical', 'good', 'excellent'
  const [collapsedSections, setCollapsedSections] = useState({})
  const [selectedCriterion, setSelectedCriterion] = useState(null) // For showing recommendations

  // ===== PDF highlight helpers (top-level, not inside another hook) =====
  const escapeRegExp = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')

  const setHighlightFromText = (text) => {
    if (!text) {
      setHighlightTerms([])
      return
    }
    const terms = String(text)
      .split(/[^A-Za-z0-9]+/)
      .filter(w => w && w.length >= 4)
      .slice(0, 6)
    setHighlightTerms(terms)
  }

  const clearHighlight = () => setHighlightTerms([])

  const customTextRenderer = (item) => {
    const content = item.str || ''
    if (!highlightTerms || highlightTerms.length === 0) return content
    const pattern = highlightTerms.map(escapeRegExp).join('|')
    if (!pattern) return content
    const regex = new RegExp(`(${pattern})`, 'ig')
    const parts = content.split(regex)
    return parts.map((part) => (regex.test(part) ? `<mark class=\"pdf-highlight\">${part}</mark>` : part)).join('')
  }

  // Apply highlight class to PDF text spans when terms change
  useEffect(() => {
    const container = document.querySelector('.pdf-viewer-container')
    if (!container) return
    const spans = container.querySelectorAll('.react-pdf__Page__textContent span')
    spans.forEach(span => {
      const txt = (span.textContent || '').trim()
      const isMatch = highlightTerms && highlightTerms.length > 0
        ? highlightTerms.some(t => new RegExp(escapeRegExp(String(t)), 'i').test(txt))
        : false
      if (isMatch) span.classList.add('pdf-highlight')
      else span.classList.remove('pdf-highlight')
    })
  }, [highlightTerms, pageNumber, numPages])

  // Keyboard shortcuts for PDF controls
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return
      
      switch (e.key) {
        case '+':
        case '=':
          e.preventDefault()
          zoomIn()
          break
        case '-':
          e.preventDefault()
          zoomOut()
          break
        case '0':
          e.preventDefault()
          resetZoom()
          break
        case 'ArrowLeft':
          if (e.ctrlKey) {
            e.preventDefault()
            goToPrevPage()
          }
          break
        case 'ArrowRight':
          if (e.ctrlKey) {
            e.preventDefault()
            goToNextPage()
          }
          break
        case 'f':
          if (e.ctrlKey) {
            e.preventDefault()
            fitToWidth()
          }
          break
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [numPages, pageNumber])

  useEffect(() => {
    // Get analysis data from navigation state
    if (location.state?.analysisData) {
      console.log('Analysis data received (raw):', location.state.analysisData)
      const incoming = location.state.analysisData
      // Support both shapes: { success, data: {...} } or already the {...}
      const base = incoming && incoming.data ? incoming.data : incoming
      console.log('Base data after extraction:', base)
      console.log('detailed_feedback from backend:', base.detailed_feedback)
      // Normalize fields expected by UI
      const normalized = { ...base }
      // helper to coerce arrays to string arrays
      const toStringList = (arr) => (arr || []).map((it) => (
        typeof it === 'string' ? it : (it && (it.message ?? it.text ?? it.title ?? it.name)) || JSON.stringify(it)
      ))
      if (!normalized.resume_content && normalized.text) {
        normalized.resume_content = normalized.text
      }
      if (!normalized.detailed_feedback) {
        const fb = normalized.feedback || {}
        normalized.detailed_feedback = {
          strengths: toStringList(fb.strengths),
          improvements: toStringList(fb.improvements),
          specific_suggestions: toStringList(normalized.recommendations),
          industry_analysis: normalized.detailed_feedback?.industry_analysis || {
            best_industry: 'technology',
            recommendations: ['Strong alignment with technology industry']
          }
        }
      } else {
        // Ensure inner lists are string arrays
        const df = normalized.detailed_feedback
        df.strengths = toStringList(df.strengths)
        df.improvements = toStringList(df.improvements)
        df.specific_suggestions = toStringList(df.specific_suggestions)
        if (df.industry_analysis && Array.isArray(df.industry_analysis.recommendations)) {
          df.industry_analysis.recommendations = toStringList(df.industry_analysis.recommendations)
        }
      }
      
      // Ensure recommendations array is available
      if (!normalized.recommendations) {
        normalized.recommendations = []
      }

      // Ensure enhanced analysis is available
      if (!normalized.enhanced_analysis) {
        normalized.enhanced_analysis = null
      }
      
      console.log('Analysis data (normalized):', normalized)
      console.log('Resume content (normalized):', normalized.resume_content)
      console.log('PDF URL from state:', location.state.pdfUrl)
      setAnalysisData(normalized)
      setPdfUrl(location.state.pdfUrl)
    } else {
      // No analysis data available - redirect to upload page
      console.warn('No analysis data found, redirecting to upload page')
      navigate('/score-resume')
      return
    }
  }, [location.state, navigate])

  const handleReanalyze = async () => {
    setIsReanalyzing(true)
    // Simulate reanalysis - in real implementation, you'd call the API again
    setTimeout(() => {
      setIsReanalyzing(false)
    }, 2000)
  }

  const handleDownloadFeedback = () => {
    // Generate and download feedback PDF
    const feedbackText = generateFeedbackText(analysisData)
    const blob = new Blob([feedbackText], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'resume-feedback.txt'
    a.click()
    URL.revokeObjectURL(url)
  }

  const generateFeedbackText = (data) => {
    if (!data) return ''
    
    let feedback = `RESUME ANALYSIS REPORT\n`
    feedback += `========================\n\n`
    feedback += `Overall Score: ${data.score}/100\n`
    feedback += `Performance Tier: ${data.performance_tier?.tier || 'N/A'}\n\n`
    
    if (data.detailed_feedback?.strengths?.length > 0) {
      feedback += `STRENGTHS:\n`
      data.detailed_feedback.strengths.forEach(strength => {
        feedback += `✓ ${strength}\n`
      })
      feedback += `\n`
    }
    
    if (data.detailed_feedback?.improvements?.length > 0) {
      feedback += `AREAS FOR IMPROVEMENT:\n`
      data.detailed_feedback.improvements.forEach(improvement => {
        feedback += `• ${improvement}\n`
      })
      feedback += `\n`
    }
    
    if (data.detailed_feedback?.specific_suggestions?.length > 0) {
      feedback += `SPECIFIC SUGGESTIONS:\n`
      data.detailed_feedback.specific_suggestions.forEach(suggestion => {
        feedback += `→ ${suggestion}\n`
      })
    }
    
    return feedback
  }

  const getScoreColor = (score) => {
    if (score >= 85) return '#10b981'
    if (score >= 70) return '#22c55e'
    if (score >= 55) return '#eab308'
    if (score >= 40) return '#f59e0b'
    return '#ef4444'
  }

  const getScoreGrade = (score) => {
    if (score >= 85) return 'A'
    if (score >= 70) return 'B'
    if (score >= 55) return 'C'
    if (score >= 40) return 'D'
    return 'F'
  }

  const renderResumeContent = (content) => {
    console.log('Rendering resume content:', content)
    console.log('Content type:', typeof content)
    
    // If content is a string (raw text), parse it into sections
    if (typeof content === 'string') {
      console.log('Parsing as string')
      return parseAndRenderText(content)
    }
    
    // If content is already structured, render it directly
    if (content.sections) {
      console.log('Rendering structured content')
      return renderStructuredContent(content.sections)
    }
    
    // Fallback: display as plain text
    console.log('Using fallback rendering')
    return <div className="resume-text">{content}</div>
  }

  const parseAndRenderText = (text) => {
    const lines = text.split('\n').filter(line => line.trim())
    const sections = []
    let currentSection = null
    
    lines.forEach(line => {
      const trimmedLine = line.trim()
      
      // Check if line is a section header (all caps or common section names)
      if (isSectionHeader(trimmedLine)) {
        if (currentSection) {
          sections.push(currentSection)
        }
        currentSection = {
          title: trimmedLine,
          content: []
        }
      } else if (currentSection) {
        currentSection.content.push(trimmedLine)
      } else {
        // Content before first section (like name/contact)
        if (!currentSection) {
          currentSection = {
            title: 'Header',
            content: []
          }
        }
        currentSection.content.push(trimmedLine)
      }
    })
    
    if (currentSection) {
      sections.push(currentSection)
    }
    
    return renderStructuredContent(sections)
  }

  const isSectionHeader = (line) => {
    const sectionKeywords = [
      'PROFILE', 'SUMMARY', 'OBJECTIVE', 'EXPERIENCE', 'EDUCATION', 
      'SKILLS', 'PROJECTS', 'CERTIFICATIONS', 'CONTACT', 'AWARDS',
      'WORK EXPERIENCE', 'PROFESSIONAL EXPERIENCE', 'TECHNICAL SKILLS',
      'CORE COMPETENCIES', 'ACHIEVEMENTS', 'LANGUAGES'
    ]
    
    const upperLine = line.toUpperCase()
    return sectionKeywords.some(keyword => upperLine.includes(keyword)) ||
           (line === line.toUpperCase() && line.length > 2 && line.length < 30)
  }

  const renderStructuredContent = (sections) => {
    return (
      <div className="resume-sections">
        {sections.map((section, index) => (
          <div key={index} className="resume-section">
            {section.title !== 'Header' && (
              <h3 className="section-title">{section.title}</h3>
            )}
            <div className="section-content">
              {section.content.map((item, itemIndex) => {
                // Check if item looks like a bullet point
                if (item.startsWith('•') || item.startsWith('-') || item.startsWith('*')) {
                  return (
                    <div key={itemIndex} className="bullet-point">
                      {item.substring(1).trim()}
                    </div>
                  )
                }
                // Check if item looks like a job title/company
                if (isJobTitle(item)) {
                  return (
                    <div key={itemIndex} className="job-title">
                      {item}
                    </div>
                  )
                }
                // Regular content
                return (
                  <div key={itemIndex} className="content-line">
                    {item}
                  </div>
                )
              })}
            </div>
          </div>
        ))}
      </div>
    )
  }

  const isJobTitle = (line) => {
    // Simple heuristic: contains common job title indicators
    const jobIndicators = ['engineer', 'developer', 'manager', 'analyst', 'specialist', 'coordinator', 'director', 'lead']
    const lowerLine = line.toLowerCase()
    return jobIndicators.some(indicator => lowerLine.includes(indicator)) ||
           line.includes('|') || // Often job title | company format
           line.includes('@') || // job @ company format
           /\d{4}/.test(line) // Contains year (likely job dates)
  }

  // React-PDF event handlers
  const onDocumentLoadSuccess = ({ numPages }) => {
    setNumPages(numPages)
    setPdfError(null)
  }

  const onDocumentLoadError = (error) => {
    console.error('PDF load error:', error)
    console.error('PDF URL:', pdfUrl)
    setPdfError(`Failed to load PDF: ${error.message}`)
  }

  const goToPrevPage = () => {
    setPageNumber(prevPageNumber => Math.max(prevPageNumber - 1, 1))
  }

  const goToNextPage = () => {
    setPageNumber(prevPageNumber => Math.min(prevPageNumber + 1, numPages || 1))
  }

  // ===== PDF zoom and fit controls =====
  const zoomIn = () => {
    setScale(prevScale => Math.min(prevScale + 0.25, 3.0))
    setFitMode('custom')
  }

  const zoomOut = () => {
    setScale(prevScale => Math.max(prevScale - 0.25, 0.5))
    setFitMode('custom')
  }

  const resetZoom = () => {
    setScale(1.0)
    setFitMode('width')
  }

  const fitToWidth = () => {
    setFitMode('width')
    setScale(1.2)
  }

  const fitToPage = () => {
    setFitMode('page')
    setScale(0.9)
  }

  // Criteria filtering and display functions
  const toggleCriteriaVisibility = () => {
    setShowCriteria(!showCriteria)
  }

  const filterCriteria = (criteria) => {
    if (!criteria) return []
    switch (criteriaFilter) {
      case 'critical':
        return criteria.filter(c => c.score <= 1)
      case 'good':
        return criteria.filter(c => c.score >= 2 && c.score <= 3)
      case 'excellent':
        return criteria.filter(c => c.score >= 4)
      default:
        return criteria
    }
  }

  const toggleSection = (sectionId) => {
    setCollapsedSections(prev => ({
      ...prev,
      [sectionId]: !prev[sectionId]
    }))
  }

  // Function to get recommendations for a specific criterion
  const getCriterionRecommendations = (criterionName) => {
    const recommendations = {
      'Quantify Impact': [
        'Add specific numbers and percentages to your achievements',
        'Include metrics like "increased sales by 25%" or "managed team of 8"',
        'Use dollar amounts, timeframes, and scale indicators',
        'Replace vague terms with measurable results'
      ],
      'Dates': [
        'Add start and end dates to all work experience entries',
        'Use consistent date format throughout (e.g., "Jan 2020 - Dec 2023")',
        'Include graduation dates for education',
        'Use "Present" for current positions'
      ],
      'Summary': [
        'Add a 2-3 line professional summary at the top',
        'Highlight your key skills and experience',
        'Tailor the summary to your target role',
        'Avoid generic phrases and buzzwords'
      ],
      'Action Verbs': [
        'Start bullet points with strong action verbs like "Led", "Developed", "Implemented"',
        'Replace "responsible for" with "managed", "directed", or "oversaw"',
        'Use diverse verb categories: leadership, development, analysis, achievement',
        'Avoid weak phrases like "worked on", "helped with", "participated in"',
        'Combine strong verbs with quantified results for maximum impact'
      ],
      'Buzzwords': [
        'Replace "results-driven" with "increased sales by 30%"',
        'Change "team player" to "collaborated with 8-person cross-functional team"',
        'Replace "detail-oriented" with "achieved 99.9% accuracy in data processing"',
        'Avoid critical buzzwords like "guru", "ninja", "rockstar"',
        'Focus on specific achievements rather than generic personality traits'
      ],
      'Skills Section': [
        'Organize skills into categories (Technical, Soft Skills)',
        'Include 8-12 relevant skills for your field',
        'Balance technical and soft skills',
        'Remove outdated or irrelevant skills'
      ],
      'Structure': [
        'Include all essential sections: Contact, Experience, Education, Skills',
        'Order sections logically (Contact → Summary → Experience → Education → Skills)',
        'Use consistent formatting throughout',
        'Ensure proper section headings'
      ],
      'ATS Compatibility': [
        'Use standard section headings (Experience, Education, Skills)',
        'Save resume as PDF format',
        'Include keywords from job descriptions',
        'Use simple, clean formatting without graphics'
      ],
      'Writing Quality': [
        'Use professional, formal tone throughout',
        'Avoid personal pronouns (I, me, my) in bullet points',
        'Replace passive voice with active voice statements',
        'Remove informal words and casual language',
        'Maintain consistent professional writing style'
      ],
      'Readability': [
        'Keep sentences concise and clear (15-20 words max)',
        'Use simple, direct language that\'s easy to understand',
        'Break up long paragraphs into shorter bullet points',
        'Avoid complex jargon unless industry-specific',
        'Aim for 6th-8th grade reading level for broader accessibility'
      ],
      'Formatting': [
        'Use consistent bullet point styles throughout',
        'Maintain uniform spacing and margins',
        'Apply consistent font sizes and styles',
        'Align text consistently across all sections',
        'Ensure clean, professional visual presentation'
      ],
      'Chronology': [
        'List work experience in reverse chronological order',
        'Include start and end dates for all positions',
        'Use consistent date format (e.g., "Jan 2020 - Dec 2023")',
        'Ensure no overlapping employment periods',
        'Add "Present" for current positions instead of end dates'
      ],
      'Unnecessary Sections': [
        'Remove "References" section (provide references upon request)',
        'Delete "Objective" statements (replace with professional summary)',
        'Remove personal photos unless required for the role',
        'Delete irrelevant personal information (age, marital status)',
        'Remove outdated sections like "Hobbies" unless job-relevant'
      ]
    }
    return recommendations[criterionName] || ['No specific recommendations available for this criterion.']
  }

  // Handle criterion click
  const handleCriterionClick = (criterion) => {
    setSelectedCriterion(selectedCriterion?.name === criterion.name ? null : criterion)
  }

  if (!analysisData) {
    return (
      <div className="analysis-loading">
        <div className="spinner"></div>
        <p>Loading resume analysis results...</p>
        <p className="loading-hint">If this takes too long, please try uploading your resume again.</p>
      </div>
    )
  }

  return (
    <div className="analysis-results">
      {/* Header */}
      <div className="analysis-header">
        <button className="back-button" onClick={() => navigate('/score-resume')}>
          <ArrowLeft size={20} />
          Back to Upload
        </button>
        <h1>Resume Analysis Results</h1>
      </div>

      {/* Score Section - Top */}
      <div className="score-top-section">
        <div className="score-display">
          <div 
            className="score-circle-large" 
            style={{ borderColor: getScoreColor(analysisData.score) }}
          >
            <div className="score-grade" style={{ color: getScoreColor(analysisData.score) }}>
              {getScoreGrade(analysisData.score)}
            </div>
            <div className="score-number" style={{ color: getScoreColor(analysisData.score) }}>
              {analysisData.score}
            </div>
            <div className="score-total">/100</div>
          </div>
          <div className="score-info">
            <h2>{analysisData.performance_tier?.tier || 'Resume Score'}</h2>
            <p className="score-description">
              {analysisData.performance_tier?.description || 'Analysis complete'}
            </p>
            {analysisData.performance_tier?.advice && (
              <p className="score-advice">{analysisData.performance_tier.advice}</p>
            )}
          </div>
        </div>


      </div>

      {/* Modern Main Content Layout */}
      <div className="modern-analysis-layout">
        {/* Left Panel - Criteria Cards */}
        <div className="criteria-panel">
          <div className="criteria-panel-header">
            <h3>
              <Target className="section-icon" />
              Resume Criteria
            </h3>
            <div className="criteria-controls">
              <button 
                className={`filter-btn ${criteriaFilter === 'all' ? 'active' : ''}`}
                onClick={() => setCriteriaFilter('all')}
              >
                All
              </button>
              <button 
                className={`filter-btn critical ${criteriaFilter === 'critical' ? 'active' : ''}`}
                onClick={() => setCriteriaFilter('critical')}
              >
                Critical
              </button>
              <button 
                className={`filter-btn good ${criteriaFilter === 'good' ? 'active' : ''}`}
                onClick={() => setCriteriaFilter('good')}
              >
                Good
              </button>
              <button 
                className={`filter-btn excellent ${criteriaFilter === 'excellent' ? 'active' : ''}`}
                onClick={() => setCriteriaFilter('excellent')}
              >
                Excellent
              </button>
              <button 
                className="visibility-btn"
                onClick={toggleCriteriaVisibility}
                title={showCriteria ? 'Hide Criteria' : 'Show Criteria'}
              >
                {showCriteria ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>
          
          {showCriteria && analysisData.enhanced_analysis?.criteria && (
            <div className="modern-criteria-display">
              {filterCriteria(analysisData.enhanced_analysis.criteria).map((criterion, index) => (
                <div 
                  key={index} 
                  className={`modern-criterion-card ${selectedCriterion?.name === criterion.name ? 'selected' : ''}`}
                  onClick={() => handleCriterionClick(criterion)}
                  style={{ cursor: 'pointer' }}
                >
                  <div className="criterion-header">
                    <div className="criterion-info">
                      <h4>{criterion.name}</h4>
                      <div className="score-display">
                        <span 
                          className="score-badge"
                          style={{ 
                            backgroundColor: criterion.score <= 1 ? '#ef4444' : 
                                           criterion.score <= 3 ? '#f59e0b' : '#10b981'
                          }}
                        >
                          {criterion.score}/5
                        </span>
                      </div>
                    </div>
                    <div className="score-bar">
                      <div 
                        className="score-fill"
                        style={{
                          width: `${(criterion.score / 5) * 100}%`,
                          backgroundColor: criterion.score <= 1 ? '#ef4444' : 
                                         criterion.score <= 3 ? '#f59e0b' : '#10b981'
                        }}
                      />
                    </div>
                  </div>
                  <p className="criterion-description">{criterion.description}</p>
                  
                  {/* Recommendations Panel */}
                  {selectedCriterion?.name === criterion.name && (
                    <div className="criterion-recommendations">
                      <h5>💡 Recommendations for {criterion.name}:</h5>
                      <ul>
                        {getCriterionRecommendations(criterion.name).map((rec, recIndex) => (
                          <li key={recIndex}>{rec}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Quick Stats */}
          {analysisData.enhanced_analysis?.criteria && (
            <div className="criteria-stats">
              <div className="stat-item">
                <span className="stat-label">Average Score:</span>
                <span className="stat-value">
                  {(analysisData.enhanced_analysis.criteria.reduce((sum, c) => sum + c.score, 0) / analysisData.enhanced_analysis.criteria.length).toFixed(1)}/5
                </span>
              </div>
              <div className="stat-item critical">
                <span className="stat-label">Critical Issues:</span>
                <span className="stat-value">
                  {analysisData.enhanced_analysis.criteria.filter(c => c.score <= 1).length}
                </span>
              </div>
              <div className="stat-item excellent">
                <span className="stat-label">Excellent Areas:</span>
                <span className="stat-value">
                  {analysisData.enhanced_analysis.criteria.filter(c => c.score >= 4).length}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Right Panel - PDF Viewer (unchanged logic) */}
        <div className="pdf-panel">
          <div className="resume-header">
            <h3>
              <FileText className="section-icon" />
              Resume Document
              <span className="keyboard-shortcuts-hint" title="Keyboard shortcuts: +/- (zoom), 0 (reset), Ctrl+←/→ (pages), Ctrl+F (fit width)">
                ⌨️
              </span>
            </h3>
            <div className="pdf-toolbar">
              {/* Zoom Controls */}
              <div className="zoom-controls">
                <button className="pdf-control-button" onClick={zoomOut} title="Zoom Out">
                  🔍−
                </button>
                <span className="zoom-display">{Math.round(scale * 100)}%</span>
                <button className="pdf-control-button" onClick={zoomIn} title="Zoom In">
                  🔍+
                </button>
                <button className="pdf-control-button" onClick={resetZoom} title="Reset Zoom">
                  ⟲
                </button>
              </div>
              
              {/* Fit Controls */}
              <div className="fit-controls">
                <button 
                  className={`pdf-control-button ${fitMode === 'width' ? 'active' : ''}`}
                  onClick={fitToWidth}
                  title="Fit to Width"
                >
                  ↔
                </button>
                <button 
                  className={`pdf-control-button ${fitMode === 'page' ? 'active' : ''}`}
                  onClick={fitToPage}
                  title="Fit to Page"
                >
                  ⛶
                </button>
              </div>

              {/* Page Navigation */}
              {numPages && (
                <div className="page-controls">
                  <button 
                    className="pdf-nav-button" 
                    onClick={goToPrevPage}
                    disabled={pageNumber <= 1}
                  >
                    ←
                  </button>
                  <span className="page-info">
                    {pageNumber} / {numPages}
                  </span>
                  <button 
                    className="pdf-nav-button" 
                    onClick={goToNextPage}
                    disabled={pageNumber >= numPages}
                  >
                    →
                  </button>
                </div>
              )}
            </div>
          </div>
          <div className="pdf-viewer-container">
            {pdfUrl ? (
              <MemoizedPdfDocument 
                pdfUrl={pdfUrl}
                onLoadSuccess={onDocumentLoadSuccess}
                onLoadError={onDocumentLoadError}
                customTextRenderer={customTextRenderer}
                pageNumber={pageNumber}
                scale={scale}
                fitMode={fitMode}
                analysisData={analysisData}
                pdfError={pdfError}
                renderResumeContent={renderResumeContent}
              />
            ) : pdfError ? (
              <div className="resume-content-fallback">
                <div className="error-message">
                  <FileText size={24} />
                  <p>PDF viewer unavailable. Showing text content instead.</p>
                </div>
                {analysisData?.resume_content ? (
                  <div className="resume-content">
                    <h4>Resume Content:</h4>
                    {renderResumeContent(analysisData.resume_content)}
                  </div>
                ) : (
                  <p>No resume content available.</p>
                )}
              </div>
            ) : (
              <div className="resume-placeholder">
                <FileText size={48} />
                <p>Resume preview not available</p>
                <p className="resume-placeholder-hint">Upload a resume to see it here</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

// Memoized PDF Document component to prevent unnecessary reloads
const MemoizedPdfDocument = React.memo(({ 
  pdfUrl, 
  onLoadSuccess, 
  onLoadError, 
  customTextRenderer, 
  pageNumber, 
  scale, 
  fitMode, 
  analysisData, 
  pdfError, 
  renderResumeContent 
}) => {
  // Memoize file prop
  const fileConfig = useMemo(() => ({
    url: pdfUrl,
    withCredentials: false
  }), [pdfUrl])

  // Memoize options prop  
  const pdfOptions = useMemo(() => ({
    cMapUrl: `https://unpkg.com/pdfjs-dist@5.4.296/cmaps/`,
    cMapPacked: true,
    standardFontDataUrl: `https://unpkg.com/pdfjs-dist@5.4.296/standard_fonts/`,
  }), [])

  return (
    <Document
      file={fileConfig}
      onLoadSuccess={onLoadSuccess}
      onLoadError={onLoadError}
      className="pdf-document"
      loading={
        <div className="pdf-loading">
          <div className="loading-spinner"></div>
          <p>Loading PDF...</p>
        </div>
      }
      error={
        <div className="resume-content-fallback">
          <div className="error-message">
            <XCircle size={24} color="#ef4444" />
            <p>Failed to load PDF. Showing text content instead.</p>
            {pdfError && <p className="error-details">{pdfError}</p>}
          </div>
          {analysisData?.resume_content ? (
            <div className="resume-content">
              <h4>Resume Content:</h4>
              {renderResumeContent(analysisData.resume_content)}
            </div>
          ) : (
            <p>No resume content available.</p>
          )}
        </div>
      }
      options={pdfOptions}
    >
      <Page 
        pageNumber={pageNumber}
        className="pdf-page"
        width={fitMode === 'custom' ? 600 * scale : 600}
        height={fitMode === 'height' ? 800 : undefined}
        scale={fitMode === 'page' ? scale : undefined}
        customTextRenderer={customTextRenderer}
        renderAnnotationLayer={true}
        renderTextLayer={true}
      />
    </Document>
  )
})

MemoizedPdfDocument.displayName = 'MemoizedPdfDocument'

export default AnalysisResults
