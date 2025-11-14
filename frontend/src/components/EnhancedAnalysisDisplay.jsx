import React from 'react'
import { CheckCircle, XCircle, AlertTriangle, Info, TrendingUp, FileText, Clock, Target } from 'lucide-react'
import CriteriaCards from './CriteriaCards'
import './EnhancedAnalysisDisplay.css'

const EnhancedAnalysisDisplay = ({ enhancedAnalysis }) => {
  if (!enhancedAnalysis) return null

  const {
    sections,
    readability,
    writing_quality,
    action_verbs,
    quantification,
    skills_analysis,
    chronology,
    tone_analysis,
    formatting,
    final_score,
    summary_analysis,
    buzzwords_analysis,
    impact_analysis,
    date_consistency,
    unnecessary_sections,
    criteria
  } = enhancedAnalysis

  const getScoreColor = (score) => {
    if (score >= 80) return '#10b981'
    if (score >= 60) return '#f59e0b' 
    return '#ef4444'
  }

  const getGradeColor = (grade) => {
    const colors = {
      'A': '#10b981',
      'B': '#22c55e', 
      'C': '#eab308',
      'D': '#f59e0b',
      'F': '#ef4444'
    }
    return colors[grade] || '#6b7280'
  }

  return (
    <div className="enhanced-analysis">
      <div className="analysis-header">
        <h2>
          <Target className="section-icon" />
          Comprehensive Resume Analysis
        </h2>
        <div className="final-score-badge" style={{ backgroundColor: getGradeColor(final_score.grade) }}>
          {final_score.grade}
        </div>
      </div>

      {/* Criteria Cards - Standardized Display */}
      {criteria && <CriteriaCards criteria={criteria} />}

      {/* Overall Score Breakdown */}
      <div className="score-breakdown-section">
        <h3>Score Breakdown ({final_score.final_score}/100)</h3>
        <div className="score-categories">
          {Object.entries(final_score.category_scores).map(([category, score]) => (
            <div key={category} className="score-category">
              <div className="category-header">
                <span className="category-name">{category.replace('_', ' ').toUpperCase()}</span>
                <span className="category-score" style={{ color: getScoreColor(score) }}>
                  {score.toFixed(1)}
                </span>
              </div>
              <div className="score-bar">
                <div 
                  className="score-fill" 
                  style={{ 
                    width: `${score}%`, 
                    backgroundColor: getScoreColor(score) 
                  }}
                />
              </div>
              <span className="weight-info">Weight: {(final_score.weights[category] * 100).toFixed(0)}%</span>
            </div>
          ))}
        </div>
      </div>

      {/* Section Analysis */}
      <div className="analysis-section">
        <h3>
          <FileText className="section-icon" />
          Section Structure Analysis
        </h3>
        <div className="section-grid">
          <div className="analysis-card">
            <h4>Required Sections</h4>
            <div className="section-items">
              {['contact', 'experience', 'education', 'skills'].map(section => (
                <div key={section} className="section-item">
                  {sections.detected_sections.includes(section) ? (
                    <CheckCircle size={16} color="#10b981" />
                  ) : (
                    <XCircle size={16} color="#ef4444" />
                  )}
                  <span className={sections.detected_sections.includes(section) ? 'present' : 'missing'}>
                    {section.charAt(0).toUpperCase() + section.slice(1)}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="analysis-card">
            <h4>Optional Sections Present</h4>
            <div className="section-items">
              {sections.present_optional.length > 0 ? (
                sections.present_optional.map(section => (
                  <div key={section} className="section-item">
                    <CheckCircle size={16} color="#10b981" />
                    <span className="present">{section.charAt(0).toUpperCase() + section.slice(1)}</span>
                  </div>
                ))
              ) : (
                <div className="section-item">
                  <Info size={16} color="#6b7280" />
                  <span>Consider adding Projects, Certifications, or Awards</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {sections.missing_required.length > 0 && (
          <div className="missing-sections-alert">
            <AlertTriangle size={20} color="#ef4444" />
            <div>
              <strong>Missing Required Sections:</strong>
              <ul>
                {sections.missing_required.map(section => (
                  <li key={section}>{section.charAt(0).toUpperCase() + section.slice(1)}</li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>

      {/* Writing Quality Analysis */}
      <div className="analysis-section">
        <h3>
          <TrendingUp className="section-icon" />
          Writing Quality Analysis
        </h3>
        <div className="quality-grid">
          <div className="quality-metric">
            <h4>Professionalism Score</h4>
            <div className="metric-score" style={{ color: getScoreColor(writing_quality.professionalism_score) }}>
              {writing_quality.professionalism_score}/100
            </div>
            {writing_quality.informal_words.length > 0 && (
              <div className="metric-details">
                <span className="detail-label">Informal words found:</span>
                <span className="detail-value">{writing_quality.informal_words.join(', ')}</span>
              </div>
            )}
            {writing_quality.vague_phrases.length > 0 && (
              <div className="metric-details">
                <span className="detail-label">Vague phrases:</span>
                <span className="detail-value">{writing_quality.vague_phrases.join(', ')}</span>
              </div>
            )}
          </div>

          <div className="quality-metric">
            <h4>Readability</h4>
            <div className="metric-score">
              {readability.readability_grade}
            </div>
            <div className="metric-details">
              <span className="detail-label">Flesch Score:</span>
              <span className="detail-value">{readability.flesch_score.toFixed(1)}</span>
            </div>
            <div className="metric-details">
              <span className="detail-label">Avg. Sentence Length:</span>
              <span className="detail-value">{readability.avg_sentence_length.toFixed(1)} words</span>
            </div>
          </div>
        </div>

        {readability.recommendations.length > 0 && (
          <div className="recommendations-list">
            <strong>Readability Recommendations:</strong>
            <ul>
              {readability.recommendations.map((rec, index) => (
                <li key={index}>{rec}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Action Verbs & Quantification */}
      <div className="analysis-section">
        <h3>
          <Target className="section-icon" />
          Content Quality Analysis
        </h3>
        <div className="content-grid">
          <div className="content-metric">
            <h4>Action Verbs Usage</h4>
            <div className="percentage-display">
              <div className="percentage-circle" style={{ '--percentage': action_verbs.strong_percentage }}>
                <span>{action_verbs.strong_percentage.toFixed(1)}%</span>
              </div>
              <div className="metric-breakdown">
                <div>Strong: {action_verbs.strong_verb_count}</div>
                <div>Weak: {action_verbs.weak_verb_count}</div>
                <div>Total: {action_verbs.total_bullets}</div>
              </div>
            </div>
            
            {action_verbs.weak_verb_bullets.length > 0 && (
              <div className="examples-section">
                <strong>Examples to improve:</strong>
                <ul>
                  {action_verbs.weak_verb_bullets.slice(0, 3).map((bullet, index) => (
                    <li key={index} className="weak-example">{bullet}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <div className="content-metric">
            <h4>Quantification</h4>
            <div className="percentage-display">
              <div className="percentage-circle" style={{ '--percentage': quantification.quantification_percentage }}>
                <span>{quantification.quantification_percentage.toFixed(1)}%</span>
              </div>
              <div className="metric-breakdown">
                <div>Quantified: {quantification.quantified_count}</div>
                <div>Total: {quantification.total_bullets}</div>
                <div className={quantification.meets_threshold ? 'threshold-met' : 'threshold-missed'}>
                  {quantification.meets_threshold ? '✓ Target met' : '✗ Below 30%'}
                </div>
              </div>
            </div>

            {quantification.quantified_examples.length > 0 && (
              <div className="examples-section">
                <strong>Good examples found:</strong>
                <ul>
                  {quantification.quantified_examples.map((example, index) => (
                    <li key={index} className="good-example">{example}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Skills Analysis */}
      <div className="analysis-section">
        <h3>
          <CheckCircle className="section-icon" />
          Skills Analysis
        </h3>
        <div className="skills-grid">
          <div className="skills-category">
            <h4>Technical Skills ({skills_analysis?.total_technical_skills || 0})</h4>
            <div className="skills-list">
              {skills_analysis?.skills_by_category ? (
                Object.entries(skills_analysis.skills_by_category)
                  .filter(([category]) => category !== 'soft_skills')
                  .flatMap(([category, skills]) => skills)
                  .map(skill => (
                    <span key={skill} className="skill-tag technical">{skill}</span>
                  ))
              ) : (
                <span className="no-skills">No technical skills detected</span>
              )}
            </div>
          </div>

          <div className="skills-category">
            <h4>Soft Skills ({skills_analysis?.total_soft_skills || 0})</h4>
            <div className="skills-list">
              {skills_analysis?.skills_by_category?.soft_skills?.length > 0 ? (
                skills_analysis.skills_by_category.soft_skills.map(skill => (
                  <span key={skill} className="skill-tag soft">{skill}</span>
                ))
              ) : (
                <span className="no-skills">No soft skills detected</span>
              )}
            </div>
          </div>
        </div>

        <div className="skill-balance">
          <strong>Skill Balance Assessment: </strong>
          <span className={`balance-${skills_analysis?.skill_balance?.balance || 'unknown'}`}>
            {skills_analysis?.skill_balance?.recommendation || 'No skill balance assessment available'}
          </span>
        </div>
      </div>

      {/* Summary Analysis */}
      {summary_analysis && (
        <div className="analysis-section">
          <h3>
            <FileText className="section-icon" />
            Professional Summary Analysis
          </h3>
          <div className="summary-analysis">
            {summary_analysis.has_summary ? (
              <div className="summary-content">
                <div className="summary-quality-score">
                  <span className="quality-label">Quality Score:</span>
                  <span className="quality-score" style={{ color: getScoreColor(summary_analysis.quality_score) }}>
                    {summary_analysis.quality_score}/100
                  </span>
                </div>
                
                <div className="summary-details">
                  <div className="summary-text">
                    <strong>Current Summary:</strong>
                    <p className="summary-preview">"{summary_analysis.summary_text}"</p>
                  </div>
                  
                  <div className="summary-stats">
                    <span>Word Count: {summary_analysis.word_count}</span>
                    <span>Has Specific Skills: {summary_analysis.has_specific_skills ? '✓' : '✗'}</span>
                    <span>Has Metrics: {summary_analysis.has_metrics ? '✓' : '✗'}</span>
                  </div>
                </div>

                {summary_analysis.issues && summary_analysis.issues.length > 0 && (
                  <div className="summary-issues">
                    <strong>Issues Found:</strong>
                    <ul>
                      {summary_analysis.issues.map((issue, index) => (
                        <li key={index} className="summary-issue">{issue}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {summary_analysis.generic_phrases_found && summary_analysis.generic_phrases_found.length > 0 && (
                  <div className="generic-phrases">
                    <strong>Generic Phrases to Replace:</strong>
                    <div className="phrase-tags">
                      {summary_analysis.generic_phrases_found.map(phrase => (
                        <span key={phrase} className="generic-phrase-tag">{phrase}</span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="no-summary">
                <AlertTriangle size={20} color="#f59e0b" />
                <span>No professional summary found</span>
              </div>
            )}

            <div className="summary-recommendations">
              <strong>Recommendations:</strong>
              <ul>
                {summary_analysis.recommendations?.map((rec, index) => (
                  <li key={index}>{rec}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Buzzwords Analysis */}
      {buzzwords_analysis && (
        <div className="analysis-section">
          <h3>
            <AlertTriangle className="section-icon" />
            Buzzwords Analysis
          </h3>
          <div className="buzzwords-content">
            <div className="buzzwords-summary">
              <div className="buzzword-score">
                <span className="score-label">Professional Language Score:</span>
                <span className="score-value" style={{ color: getScoreColor(buzzwords_analysis.buzzword_score) }}>
                  {buzzwords_analysis.buzzword_score}/100
                </span>
              </div>
              
              <div className="buzzword-severity">
                <span className="severity-label">Severity:</span>
                <span className={`severity-${buzzwords_analysis.severity}`}>
                  {buzzwords_analysis.severity}
                </span>
              </div>
            </div>

            {buzzwords_analysis.buzzwords_found && buzzwords_analysis.buzzwords_found.length > 0 ? (
              <div className="buzzwords-found">
                <strong>Buzzwords Detected ({buzzwords_analysis.total_buzzwords}):</strong>
                <div className="buzzword-list">
                  {buzzwords_analysis.buzzwords_found.map(bw => (
                    <div key={bw.word} className="buzzword-item">
                      <span className="buzzword-text">"{bw.word}" ({bw.count}x)</span>
                      <div className="buzzword-alternatives">
                        <strong>Replace with:</strong>
                        <span className="alternatives">{bw.suggestions.join(', ')}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="no-buzzwords">
                <CheckCircle size={20} color="#10b981" />
                <span>Great! No generic buzzwords detected</span>
              </div>
            )}

            <div className="buzzword-recommendations">
              <strong>Recommendations:</strong>
              <ul>
                {buzzwords_analysis.recommendations?.map((rec, index) => (
                  <li key={index}>{rec}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Impact Metrics Analysis */}
      {impact_analysis && (
        <div className="analysis-section">
          <h3>
            <TrendingUp className="section-icon" />
            Impact Metrics Diversity
          </h3>
          <div className="impact-metrics-content">
            <div className="metrics-summary">
              <div className="diversity-score">
                <span className="score-label">Metrics Diversity:</span>
                <span className="score-value" style={{ color: getScoreColor(impact_analysis.diversity_score) }}>
                  {impact_analysis.metrics_diversity}/6 types
                </span>
              </div>
              
              {impact_analysis.strongest_metric_type && (
                <div className="strongest-metric">
                  <span className="metric-label">Most Used:</span>
                  <span className="metric-value">{impact_analysis.strongest_metric_type.replace('_', ' ')}</span>
                </div>
              )}
            </div>

            <div className="metrics-breakdown">
              <strong>Metrics Found:</strong>
              <div className="metrics-grid">
                {Object.entries(impact_analysis.impact_metrics).map(([type, metrics]) => (
                  <div key={type} className={`metric-type ${metrics.length > 0 ? 'present' : 'missing'}`}>
                    <span className="type-name">{type.replace('_', ' ')}</span>
                    <span className="type-count">{metrics.length}</span>
                    {metrics.length > 0 && metrics[0] && (
                      <span className="type-example">e.g., "{metrics[0]}"</span>
                    )}
                  </div>
                ))}
              </div>
            </div>

            <div className="impact-recommendations">
              <strong>Recommendations:</strong>
              <ul>
                {impact_analysis.recommendations?.map((rec, index) => (
                  <li key={index}>{rec}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Date Consistency Analysis */}
      {date_consistency && (
        <div className="analysis-section">
          <h3>
            <Clock className="section-icon" />
            Date Format Consistency
          </h3>
          <div className="date-consistency-content">
            <div className="consistency-summary">
              <div className="consistency-score">
                <span className="score-label">Consistency Score:</span>
                <span className="score-value" style={{ color: getScoreColor(date_consistency.consistency_score) }}>
                  {date_consistency.consistency_score}/100
                </span>
              </div>
              
              <div className="consistency-status">
                {date_consistency.is_consistent ? (
                  <div className="status-good">
                    <CheckCircle size={16} color="#10b981" />
                    <span>Dates are consistently formatted</span>
                  </div>
                ) : (
                  <div className="status-issue">
                    <XCircle size={16} color="#ef4444" />
                    <span>Multiple date formats detected</span>
                  </div>
                )}
              </div>
            </div>

            {date_consistency.date_examples && date_consistency.date_examples.length > 0 && (
              <div className="date-examples">
                <strong>Date Examples Found:</strong>
                <div className="example-list">
                  {date_consistency.date_examples.map((example, index) => (
                    <span key={index} className="date-example">"{example}"</span>
                  ))}
                </div>
              </div>
            )}

            {date_consistency.formats_found && date_consistency.formats_found.length > 1 && (
              <div className="format-issues">
                <strong>Multiple Formats Detected:</strong>
                <div className="format-list">
                  {date_consistency.formats_found.map(format => (
                    <span key={format} className="format-tag">{format.replace('_', ' ')}</span>
                  ))}
                </div>
              </div>
            )}

            <div className="date-recommendations">
              <strong>Recommendations:</strong>
              <ul>
                {date_consistency.recommendations?.map((rec, index) => (
                  <li key={index}>{rec}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Unnecessary Sections Analysis */}
      {unnecessary_sections && (
        <div className="analysis-section">
          <h3>
            <XCircle className="section-icon" />
            Modern Resume Standards
          </h3>
          <div className="unnecessary-sections-content">
            <div className="modernization-summary">
              <div className="modernization-score">
                <span className="score-label">Modernization Score:</span>
                <span className="score-value" style={{ color: getScoreColor(unnecessary_sections.modernization_score) }}>
                  {unnecessary_sections.modernization_score}/100
                </span>
              </div>
              
              <div className="modernization-status">
                {!unnecessary_sections.has_outdated_sections ? (
                  <div className="status-good">
                    <CheckCircle size={16} color="#10b981" />
                    <span>Follows modern resume standards</span>
                  </div>
                ) : (
                  <div className="status-issue">
                    <AlertTriangle size={16} color="#f59e0b" />
                    <span>{unnecessary_sections.total_issues} outdated section(s) found</span>
                  </div>
                )}
              </div>
            </div>

            {/* Summary */}
            <div className="modernization-overview">
              <p className="analysis-summary">{unnecessary_sections.summary}</p>
            </div>

            {/* Passed Checks - Positive Feedback */}
            {unnecessary_sections.passed_checks && unnecessary_sections.passed_checks.length > 0 && (
              <div className="passed-checks">
                <h4 className="passed-checks-title">
                  <CheckCircle size={18} color="#10b981" />
                  Passed Checks
                </h4>
                <div className="passed-checks-list">
                  {unnecessary_sections.passed_checks.map((check, index) => (
                    <div key={index} className="passed-check-item">
                      <CheckCircle size={14} color="#10b981" />
                      <div className="check-content">
                        <span className="check-type">No {check.type} section</span>
                        <span className="check-description">{check.description}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Unnecessary Sections Found */}
            {unnecessary_sections.unnecessary_sections_found && unnecessary_sections.unnecessary_sections_found.length > 0 && (
              <div className="unnecessary-sections-found">
                <h4 className="issues-title">
                  <XCircle size={18} color="#ef4444" />
                  Outdated Sections Detected
                </h4>
                <div className="unnecessary-sections-list">
                  {unnecessary_sections.unnecessary_sections_found.map((section, index) => (
                    <div key={index} className={`unnecessary-section-item severity-${section.severity}`}>
                      <div className="section-header">
                        <div className="section-info">
                          <span className="section-type">{section.type.replace('_', ' ').toUpperCase()}</span>
                          <span className={`severity-badge severity-${section.severity}`}>
                            {section.severity.toUpperCase()}
                          </span>
                        </div>
                        {section.patterns_found && section.patterns_found.length > 0 && (
                          <div className="detected-patterns">
                            <strong>Detected:</strong> "{section.patterns_found.join('", "')}"
                          </div>
                        )}
                      </div>
                      
                      <div className="section-description">
                        {section.description}
                      </div>
                      
                      <div className="section-recommendation">
                        <strong>Action:</strong> {section.recommendation}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Modernization Recommendations */}
            <div className="modernization-recommendations">
              <strong>Modernization Recommendations:</strong>
              <ul>
                {unnecessary_sections.recommendations?.map((rec, index) => (
                  <li key={index} className={rec.startsWith('URGENT:') ? 'urgent-recommendation' : 
                                             rec.startsWith('Important:') ? 'important-recommendation' : 
                                             'standard-recommendation'}>
                    {rec}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Timeline Analysis */}
      {chronology && (
        <div className="analysis-section">
          <h3>
            <Clock className="section-icon" />
            Timeline & Date Analysis
          </h3>
          <div className="timeline-info">
            {chronology.has_dates === false ? (
              <div className="no-dates-warning">
                <div className="critical-issue">
                  <AlertTriangle size={24} color="#ef4444" />
                  <div className="issue-content">
                    <h4>Critical Issue: No Dates Found</h4>
                    <p>We couldn't find any dates on your resume. Dates are essential for work experience and education sections.</p>
                  </div>
                </div>
                
                <div className="date-requirements">
                  <strong>Date Format Requirements:</strong>
                  <ul>
                    <li>Include at least the full year (e.g., "2020-2023")</li>
                    <li>Use consistent format throughout (recommended: "Jan 2020 - Dec 2023")</li>
                    <li>Use "Present" or "Current" for ongoing positions</li>
                    <li>List experience in reverse chronological order (most recent first)</li>
                  </ul>
                </div>

                <div className="date-examples">
                  <strong>Good Examples:</strong>
                  <div className="example-formats">
                    <span className="good-format">Jan 2020 - Dec 2023</span>
                    <span className="good-format">2020 - Present</span>
                    <span className="good-format">Sep 2019 - May 2023</span>
                  </div>
                </div>
              </div>
            ) : (
              <>
                <div className="timeline-stat">
                  <span className="stat-label">Date Ranges Found:</span>
                  <span className="stat-value">{chronology.total_date_ranges}</span>
                </div>
                
                <div className="date-formats-summary">
                  <span className="stat-label">Date Formats Used:</span>
                  <div className="formats-list">
                    {chronology.date_formats_used.map(format => (
                      <span key={format} className="format-badge">{format.replace('_', ' ')}</span>
                    ))}
                  </div>
                </div>
              </>
            )}
            
            {chronology.chronological_order_issues && chronology.chronological_order_issues.length > 0 && (
              <div className="timeline-issues">
                <strong>Timeline Issues:</strong>
                <ul>
                  {chronology.chronological_order_issues.map((issue, index) => (
                    <li key={index} className="timeline-issue">{issue}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {chronology.has_dates && (!chronology.chronological_order_issues || chronology.chronological_order_issues.length === 0) && (
              <div className="timeline-success">
                <CheckCircle size={16} color="#10b981" />
                <span>No chronological issues detected</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Formatting Analysis */}
      <div className="analysis-section">
        <h3>
          <FileText className="section-icon" />
          Formatting Consistency
        </h3>
        <div className="formatting-grid">
          <div className="formatting-item">
            <div className="format-check">
              {formatting.bullet_consistency ? (
                <CheckCircle size={16} color="#10b981" />
              ) : (
                <XCircle size={16} color="#ef4444" />
              )}
              <span>Bullet Point Consistency</span>
            </div>
          </div>

          <div className="formatting-item">
            <div className="format-check">
              {formatting.date_consistency ? (
                <CheckCircle size={16} color="#10b981" />
              ) : (
                <XCircle size={16} color="#ef4444" />
              )}
              <span>Date Format Consistency</span>
            </div>
          </div>

          <div className="formatting-item">
            <div className="formatting-score">
              <span className="score-label">Overall Formatting Score:</span>
              <span className="score-value" style={{ color: getScoreColor(formatting.formatting_score) }}>
                {formatting.formatting_score}/100
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default EnhancedAnalysisDisplay
