#!/usr/bin/env python3
"""
Resume Scorer - Score resume on multiple criteria
"""
import sys
import json
import re
from collections import Counter
from resume_parser import parse_pdf, parse_docx
from nlp_analyzer import analyze_text
from keyword_extractor import extract_keywords
from recommendation_engine import generate_comprehensive_recommendations
from enhanced_analyzer import EnhancedResumeAnalyzer

# Industry-specific keywords for better scoring
INDUSTRY_KEYWORDS = {
    'technology': ['python', 'javascript', 'react', 'node.js', 'aws', 'docker', 'kubernetes', 'api', 'database', 'sql', 'git', 'agile', 'scrum'],
    'data_science': ['machine learning', 'data analysis', 'python', 'r', 'sql', 'tableau', 'statistics', 'modeling', 'pandas', 'numpy'],
    'business': ['strategy', 'analysis', 'management', 'leadership', 'project management', 'stakeholder', 'roi', 'kpi'],
    'marketing': ['digital marketing', 'seo', 'social media', 'analytics', 'campaign', 'brand', 'conversion', 'engagement'],
    'finance': ['financial analysis', 'budgeting', 'forecasting', 'excel', 'financial modeling', 'accounting', 'audit']
}

# Achievement impact words for better scoring
IMPACT_WORDS = {
    'high_impact': ['increased', 'decreased', 'improved', 'optimized', 'reduced', 'generated', 'saved', 'exceeded', 'achieved', 'delivered'],
    'medium_impact': ['developed', 'created', 'implemented', 'designed', 'built', 'established', 'launched', 'managed'],
    'quantifiers': ['%', 'percent', '$', 'million', 'thousand', 'users', 'customers', 'team', 'projects', 'revenue']
}

def calculate_score(nlp_analysis, keywords, raw_text=""):
    """Calculate overall resume score with enhanced analysis"""
    scores = {
        'ats_compatibility': 0,      # 0-25 points
        'content_quality': 0,        # 0-30 points (reduced from 35)
        'keyword_optimization': 0,   # 0-20 points
        'structure': 0,              # 0-15 points
        'achievement_impact': 0,     # 0-10 points (NEW)
        'language_quality': 0        # 0-5 points
    }
    
    # Store detailed feedback for better recommendations
    detailed_feedback = {
        'strengths': [],
        'improvements': [],
        'specific_suggestions': [],
        'industry_analysis': {}
    }
    
    # CRITICAL CHECK: If missing Experience, Skills, or Contact sections, return 0
    sections = nlp_analysis['sections']
    if not sections.get('has_all_critical', False):
        return {
            'total': 0,
            'breakdown': scores,
            'critical_failure': True,
            'missing_critical_sections': sections.get('critical_missing', [])
        }
    
    # ATS Compatibility (0-25 points) - Unchanged
    sections_found = sections['found']
    sections_missing = sections['missing']
    section_score = (len(sections_found) / (len(sections_found) + len(sections_missing))) * 25 if (len(sections_found) + len(sections_missing)) > 0 else 0
    scores['ats_compatibility'] = round(section_score)
    
    # Content Quality (0-30 points) - Enhanced analysis
    stats = nlp_analysis['statistics']
    
    # Metrics usage (0-15 points)
    metrics_score = (stats['metrics_percentage'] / 100) * 15
    
    # Action verbs (0-15 points)
    verbs_score = (stats['strong_verbs_percentage'] / 100) * 15
    
    scores['content_quality'] = round(metrics_score + verbs_score)
    
    # Add feedback for content quality
    if stats['metrics_percentage'] > 70:
        detailed_feedback['strengths'].append("Excellent use of quantifiable metrics and achievements")
    elif stats['metrics_percentage'] < 30:
        detailed_feedback['improvements'].append("Add specific numbers, percentages, and measurable results")
    
    if stats['strong_verbs_percentage'] > 80:
        detailed_feedback['strengths'].append("Strong action verbs throughout the resume")
    elif stats['strong_verbs_percentage'] < 50:
        detailed_feedback['improvements'].append("Replace weak verbs with powerful action words")
    
    # Keyword Optimization (0-20 points) - Enhanced with industry analysis
    keyword_count = keywords['total_keywords']
    base_keyword_score = min(15, keyword_count * 1.5)
    
    # Industry relevance bonus (0-5 points)
    industry_bonus = calculate_industry_relevance(keywords.get('technical_skills', []), raw_text)
    detailed_feedback['industry_analysis'] = industry_bonus['analysis']
    
    scores['keyword_optimization'] = round(base_keyword_score + industry_bonus['score'])
    
    # Structure (0-15 points) - Unchanged
    bullet_count = stats['total_bullets']
    if bullet_count >= 8 and bullet_count <= 20:
        structure_score = 15
    elif bullet_count > 0:
        structure_score = 10
    else:
        structure_score = 0
    scores['structure'] = structure_score
    
    # Achievement Impact (0-10 points) - NEW
    impact_analysis = calculate_achievement_impact(nlp_analysis.get('bullet_points', []), raw_text)
    scores['achievement_impact'] = impact_analysis['score']
    detailed_feedback['specific_suggestions'].extend(impact_analysis['suggestions'])
    
    # Language Quality (0-5 points) - Low weight for grammar/spelling
    # This gives minimal penalty for grammatical errors
    language_score = 5  # Start with full points
    
    # Count issues with low severity (grammar-related)
    total_language_issues = 0
    for bullet in nlp_analysis['bullet_points']:
        for issue in bullet['issues']:
            if issue['severity'] == 'low':  # Grammar/spelling issues are typically low severity
                total_language_issues += 1
    
    # Reduce score minimally for language issues (max 2 points deduction)
    if total_language_issues > 0:
        language_penalty = min(2, total_language_issues * 0.2)  # Very small penalty
        language_score = max(3, language_score - language_penalty)  # Minimum 3 points
    
    scores['language_quality'] = round(language_score)
    
    # Total score (still out of 100)
    total_score = sum(scores.values())
    
    # Generate performance tier
    performance_tier = get_performance_tier(total_score)
    
    return {
        'total': total_score,
        'breakdown': scores,
        'detailed_feedback': detailed_feedback,
        'performance_tier': performance_tier
    }

def generate_feedback(nlp_analysis):
    """Generate line-by-line feedback"""
    feedback = []
    
    for bullet in nlp_analysis['bullet_points']:
        if bullet['issues']:
            feedback.append({
                'text': bullet['text'][:100] + '...' if len(bullet['text']) > 100 else bullet['text'],
                'issues': bullet['issues']
            })
    
    return feedback

def calculate_industry_relevance(technical_skills, raw_text):
    """Calculate industry relevance bonus and provide analysis"""
    text_lower = raw_text.lower()
    skills_lower = [skill.lower() for skill in technical_skills]
    
    industry_scores = {}
    best_industry = None
    best_score = 0
    
    for industry, keywords in INDUSTRY_KEYWORDS.items():
        matches = 0
        matched_keywords = []
        
        for keyword in keywords:
            # Check in both skills and raw text
            if any(keyword in skill for skill in skills_lower) or keyword in text_lower:
                matches += 1
                matched_keywords.append(keyword)
        
        score = min(5, matches * 0.8)  # Up to 5 points
        industry_scores[industry] = {
            'score': score,
            'matches': matches,
            'keywords': matched_keywords
        }
        
        if score > best_score:
            best_score = score
            best_industry = industry
    
    analysis = {
        'best_industry': best_industry,
        'industry_scores': industry_scores,
        'recommendations': []
    }
    
    if best_score >= 3:
        analysis['recommendations'].append(f"Strong alignment with {best_industry} industry")
    elif best_score >= 1:
        analysis['recommendations'].append(f"Some relevance to {best_industry} - consider adding more industry-specific skills")
    else:
        analysis['recommendations'].append("Add more industry-specific technical skills and keywords")
    
    return {
        'score': round(best_score),
        'analysis': analysis
    }

def calculate_achievement_impact(bullet_points, raw_text):
    """Calculate achievement impact score and provide suggestions"""
    impact_score = 0
    suggestions = []
    text_lower = raw_text.lower()
    
    # Count high-impact words
    high_impact_count = sum(1 for word in IMPACT_WORDS['high_impact'] if word in text_lower)
    medium_impact_count = sum(1 for word in IMPACT_WORDS['medium_impact'] if word in text_lower)
    quantifier_count = sum(1 for word in IMPACT_WORDS['quantifiers'] if word in text_lower)
    
    # Score based on impact language
    impact_score += min(4, high_impact_count * 0.8)  # Up to 4 points
    impact_score += min(3, medium_impact_count * 0.5)  # Up to 3 points
    impact_score += min(3, quantifier_count * 0.4)    # Up to 3 points
    
    # Check for specific achievement patterns
    achievement_patterns = [
        r'\d+%\s*(increase|improvement|growth|reduction|decrease)',
        r'\$[\d,]+',  # Dollar amounts
        r'\d+\s*(users|customers|clients|projects|people|team members)',
        r'(saved|generated|increased|reduced)\s*(\$?[\d,]+|[\d.]+%)',
        r'(led|managed)\s*(team of|group of)?\s*\d+'
    ]
    
    pattern_matches = sum(1 for pattern in achievement_patterns if re.search(pattern, text_lower))
    if pattern_matches > 0:
        impact_score += min(2, pattern_matches * 0.5)  # Bonus for specific patterns
    
    # Generate suggestions based on analysis
    if high_impact_count < 3:
        suggestions.append("Use more high-impact verbs like 'optimized', 'increased', 'generated', 'exceeded'")
    
    if quantifier_count < 5:
        suggestions.append("Add specific numbers: team sizes, percentages, dollar amounts, timeframes")
    
    if pattern_matches == 0:
        suggestions.append("Include measurable achievements: '25% increase in sales', 'managed team of 8', 'saved $50K annually'")
    
    if len(suggestions) == 0:
        suggestions.append("Excellent use of quantified achievements and impact language!")
    
    return {
        'score': round(min(10, impact_score)),
        'suggestions': suggestions,
        'analysis': {
            'high_impact_words': high_impact_count,
            'quantifiers': quantifier_count,
            'achievement_patterns': pattern_matches
        }
    }

def get_performance_tier(total_score):
    """Categorize resume performance into tiers"""
    if total_score >= 85:
        return {
            'tier': 'Exceptional',
            'description': 'Industry-leading resume quality',
            'color': '#10b981',
            'advice': 'Your resume is outstanding! Minor tweaks could make it perfect.'
        }
    elif total_score >= 70:
        return {
            'tier': 'Strong',
            'description': 'Competitive and well-structured',
            'color': '#22c55e',
            'advice': 'Great resume! Focus on the specific improvements suggested.'
        }
    elif total_score >= 55:
        return {
            'tier': 'Good',
            'description': 'Solid foundation with room for improvement',
            'color': '#eab308',
            'advice': 'Good start! Address the key areas for significant improvement.'
        }
    elif total_score >= 40:
        return {
            'tier': 'Developing',
            'description': 'Needs significant improvements',
            'color': '#f59e0b',
            'advice': 'Focus on adding quantifiable achievements and stronger content.'
        }
    else:
        return {
            'tier': 'Needs Work',
            'description': 'Major revisions required',
            'color': '#ef4444',
            'advice': 'Start with the critical requirements, then build up content quality.'
        }

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "No file path provided"}))
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    try:
        # Parse resume
        if file_path.endswith('.pdf'):
            parsed = parse_pdf(file_path)
        elif file_path.endswith('.docx'):
            parsed = parse_docx(file_path)
        else:
            print(json.dumps({"success": False, "error": "Unsupported file type"}))
            sys.exit(1)
        
        if not parsed['success']:
            print(json.dumps(parsed))
            sys.exit(1)
        
        text = parsed['text']
        
        # Analyze with NLP
        nlp_analysis = analyze_text(text)
        
        # Extract keywords
        keywords = extract_keywords(text)
        
        # Enhanced comprehensive analysis using the new analyzer
        enhanced_analyzer = EnhancedResumeAnalyzer()  # Create enhanced analyzer instance
        enhanced_analysis = enhanced_analyzer.analyze_resume(text)  # Run full enhanced analysis on the resume text

        # CRITICAL CHECK: ensure resume has either Experience or Projects HEADERS before scoring
        # Use strict header detection (not content-based inference) to ensure proper section structure
        explicit_headers = enhanced_analyzer.detect_explicit_headers_only(text)  # Get only explicit section headers
        has_experience_header = 'experience' in explicit_headers  # True if explicit Experience header found
        has_projects_header = 'projects' in explicit_headers      # True if explicit Projects header found

        if not has_experience_header and not has_projects_header:
            # If neither Experience nor Projects exists, we cannot meaningfully score the resume
            error_result = {
                "success": False,
                "error": "We could not find an Experience or Projects section, which is required to score your resume.",
                "code": "missing_experience_projects"
            }
            print(json.dumps(error_result))  # Send structured error back to Node for redirect/error page handling
            sys.exit(0)  # Exit cleanly so Node can consume the JSON instead of treating it as a crash

        # Use the enhanced analyzer's final score as the single source of truth
        # final_score_data contains: category_scores (per-criterion), weights, final_score (0-100), grade
        final_score_data = enhanced_analysis.get('final_score', {})
        enhanced_total_score = final_score_data.get('final_score', 0)  # Overall 0-100 score from enhanced analysis
        enhanced_breakdown = final_score_data.get('category_scores', {})  # Per-criterion scores used for breakdown
        
        # Derive performance tier from the enhanced total score so tiers stay consistent with the visible score
        performance_tier = get_performance_tier(enhanced_total_score)
        
        # Generate line-by-line feedback from the NLP analysis (still useful for user guidance)
        feedback = generate_feedback(nlp_analysis)
        
        # Generate comprehensive recommendations using the new system
        sections_found = nlp_analysis.get('sections_found', {})
        sections_data = {
            'experience': {'found': sections_found.get('experience', False)},
            'education': {'found': sections_found.get('education', False)},
            'skills': {'found': sections_found.get('skills', False)},
            'contact': {'found': sections_found.get('contact', False)}
        }
        
        recommendations = generate_comprehensive_recommendations(
            resume_data={'text': parsed['text']},  # Raw resume text for recommendation engine
            statistics=nlp_analysis['statistics'],  # High-level statistics from NLP analyzer
            sections=sections_data  # Section presence data for completeness checks
        )
        
        # Build the final result object returned to Node
        # "score" and "breakdown" now come exclusively from the enhanced analyzer's 12-criteria scoring
        result = {
            'success': True,
            'score': enhanced_total_score,  # Unified 0-100 score based on individual criteria weights
            'breakdown': enhanced_breakdown,  # Per-criterion scores for frontend breakdown display
            'performance_tier': performance_tier,  # Tier derived from the enhanced total score
            'detailed_feedback': {},  # Legacy detailed feedback from calculate_score is no longer used
            'feedback': feedback,  # Line-level feedback from NLP analysis
            'recommendations': recommendations,  # Comprehensive recommendation set
            'statistics': nlp_analysis['statistics'],  # NLP statistics for debugging/extra UI
            'resume_content': parsed['text'],  # Include raw text for frontend display
            'enhanced_analysis': enhanced_analysis  # Full enhanced analysis object (criteria + final_score)
        }
        
        print(json.dumps(result))
        
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
        sys.exit(0)  # Exit cleanly so Node can read the JSON error instead of treating it as a crash

if __name__ == "__main__":
    main()
