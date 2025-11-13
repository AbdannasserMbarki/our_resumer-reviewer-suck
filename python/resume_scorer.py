#!/usr/bin/env python3
"""
Resume Scorer - Score resume on multiple criteria
"""
import sys
import json
from resume_parser import parse_pdf, parse_docx
from nlp_analyzer import analyze_text
from keyword_extractor import extract_keywords

def calculate_score(nlp_analysis, keywords):
    """Calculate overall resume score"""
    scores = {
        'ats_compatibility': 0,
        'content_quality': 0,
        'keyword_optimization': 0,
        'structure': 0
    }
    
    # ATS Compatibility (0-25 points)
    # Check for required sections
    sections_found = nlp_analysis['sections']['found']
    sections_missing = nlp_analysis['sections']['missing']
    section_score = (len(sections_found) / (len(sections_found) + len(sections_missing))) * 25 if (len(sections_found) + len(sections_missing)) > 0 else 0
    scores['ats_compatibility'] = round(section_score)
    
    # Content Quality (0-40 points)
    stats = nlp_analysis['statistics']
    
    # Metrics usage (0-20)
    metrics_score = (stats['metrics_percentage'] / 100) * 20
    
    # Action verbs (0-20)
    verbs_score = (stats['strong_verbs_percentage'] / 100) * 20
    
    scores['content_quality'] = round(metrics_score + verbs_score)
    
    # Keyword Optimization (0-20 points)
    keyword_count = keywords['total_keywords']
    keyword_score = min(20, keyword_count * 2)  # 1 point per keyword, max 20
    scores['keyword_optimization'] = round(keyword_score)
    
    # Structure (0-15 points)
    # Based on bullet count and organization
    bullet_count = stats['total_bullets']
    if bullet_count >= 8 and bullet_count <= 20:
        structure_score = 15
    elif bullet_count > 0:
        structure_score = 10
    else:
        structure_score = 0
    scores['structure'] = structure_score
    
    # Total score
    total_score = sum(scores.values())
    
    return {
        'total': total_score,
        'breakdown': scores
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
        
        # Calculate score
        score_result = calculate_score(nlp_analysis, keywords)
        
        # Generate feedback
        feedback = generate_feedback(nlp_analysis)
        
        # Generate recommendations
        recommendations = []
        
        if score_result['breakdown']['ats_compatibility'] < 20:
            recommendations.append({
                'category': 'ATS',
                'priority': 'high',
                'message': 'Add missing resume sections (Experience, Education, Skills)'
            })
        
        if score_result['breakdown']['content_quality'] < 30:
            recommendations.append({
                'category': 'Content',
                'priority': 'high',
                'message': 'Add more quantifiable metrics and use stronger action verbs'
            })
        
        if score_result['breakdown']['keyword_optimization'] < 15:
            recommendations.append({
                'category': 'Keywords',
                'priority': 'medium',
                'message': 'Include more relevant technical skills and keywords'
            })
        
        result = {
            'success': True,
            'score': score_result['total'],
            'breakdown': score_result['breakdown'],
            'feedback': feedback,
            'recommendations': recommendations,
            'statistics': nlp_analysis['statistics']
        }
        
        print(json.dumps(result))
        
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()
