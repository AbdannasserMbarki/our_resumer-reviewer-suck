#!/usr/bin/env python3
"""
Recommendation Engine - Map detected issues to specific recommendations
"""
import json

# Recommendation templates
RECOMMENDATIONS = {
    'missing_metrics': {
        'priority': 'high',
        'category': 'quantification',
        'message': 'Add numbers to quantify your achievements',
        'examples': [
            'Instead of "Improved system performance" → "Improved system performance by 45%"',
            'Instead of "Managed a team" → "Managed a team of 8 engineers"',
            'Instead of "Increased sales" → "Increased sales by $2.3M annually"'
        ]
    },
    'missing_action_verb': {
        'priority': 'critical',
        'category': 'action_verbs',
        'message': 'Start bullet points with strong action verbs',
        'examples': [
            'Use verbs like: Implemented, Developed, Led, Designed, Architected',
            'Avoid passive voice and weak phrases like "Responsible for" or "Worked on"'
        ]
    },
    'weak_action_verb': {
        'priority': 'high',
        'category': 'action_verbs',
        'message': 'Replace weak verbs with stronger action verbs',
        'suggestions': {
            'helped': ['Assisted', 'Supported', 'Facilitated', 'Enabled'],
            'worked on': ['Developed', 'Built', 'Implemented', 'Created'],
            'responsible for': ['Led', 'Managed', 'Directed', 'Oversaw'],
            'participated in': ['Contributed to', 'Collaborated on', 'Drove'],
            'involved in': ['Executed', 'Delivered', 'Spearheaded']
        }
    },
    'section_missing': {
        'priority': 'critical',
        'category': 'structure',
        'message': 'Include all required resume sections',
        'details': 'A complete resume should include: Experience, Education, and Skills sections'
    },
    'low_p_strong': {
        'priority': 'high',
        'category': 'impact',
        'message': 'Strengthen this bullet point',
        'tips': [
            'Add specific metrics and numbers',
            'Use strong action verbs',
            'Highlight the impact of your work',
            'Include the result or outcome'
        ]
    },
    'low_p_relevant': {
        'priority': 'medium',
        'category': 'relevance',
        'message': 'Tailor this bullet to match the job description',
        'tips': [
            'Include keywords from the job posting',
            'Emphasize relevant skills and technologies',
            'Connect your experience to job requirements'
        ]
    },
    'too_short': {
        'priority': 'low',
        'category': 'length',
        'message': 'Expand this bullet point with more detail',
        'tips': ['Add context about your role', 'Include the impact or result', 'Mention tools/technologies used']
    },
    'too_long': {
        'priority': 'low',
        'category': 'length',
        'message': 'Shorten this bullet point or split into multiple bullets',
        'tips': ['Focus on one achievement per bullet', 'Remove unnecessary details', 'Be concise']
    }
}

def generate_recommendations(nlp_issues, classifier_results):
    """Generate prioritized recommendations based on detected issues"""
    recommendations = []
    
    # Process NLP issues
    for issue in nlp_issues:
        issue_type = issue.get('type')
        if issue_type in RECOMMENDATIONS:
            rec = RECOMMENDATIONS[issue_type].copy()
            rec['source'] = 'nlp_analysis'
            rec['line'] = issue.get('line', '')
            recommendations.append(rec)
    
    # Process classifier results
    for result in classifier_results:
        if result.get('p_strong', 1.0) < 0.4:
            rec = RECOMMENDATIONS['low_p_strong'].copy()
            rec['source'] = 'ml_classifier'
            rec['line'] = result.get('text', '')
            rec['score'] = result.get('p_strong')
            recommendations.append(rec)
        
        if result.get('p_relevant') is not None and result['p_relevant'] < 0.3:
            rec = RECOMMENDATIONS['low_p_relevant'].copy()
            rec['source'] = 'ml_classifier'
            rec['line'] = result.get('text', '')
            rec['score'] = result.get('p_relevant')
            recommendations.append(rec)
    
    # Sort by priority
    priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    recommendations.sort(key=lambda x: priority_order.get(x.get('priority', 'low'), 3))
    
    return recommendations

def generate_overall_feedback(statistics, sections):
    """Generate overall resume feedback"""
    feedback = []
    
    # Check metrics usage
    metrics_pct = statistics.get('metrics_percentage', 0)
    if metrics_pct < 50:
        feedback.append({
            'type': 'metrics',
            'severity': 'high',
            'message': f'Only {metrics_pct}% of your bullet points include quantifiable metrics. Aim for at least 70%.'
        })
    elif metrics_pct >= 70:
        feedback.append({
            'type': 'metrics',
            'severity': 'positive',
            'message': f'Good job! {metrics_pct}% of your bullet points include metrics.'
        })
    
    # Check action verbs
    verbs_pct = statistics.get('strong_verbs_percentage', 0)
    if verbs_pct < 60:
        feedback.append({
            'type': 'action_verbs',
            'severity': 'high',
            'message': f'Only {verbs_pct}% of your bullet points start with strong action verbs. Aim for at least 80%.'
        })
    elif verbs_pct >= 80:
        feedback.append({
            'type': 'action_verbs',
            'severity': 'positive',
            'message': f'Excellent! {verbs_pct}% of your bullet points start with strong action verbs.'
        })
    
    # Check missing sections
    missing_sections = sections.get('missing', [])
    if missing_sections:
        feedback.append({
            'type': 'sections',
            'severity': 'critical',
            'message': f'Your resume is missing these important sections: {", ".join(missing_sections)}'
        })
    
    return feedback

def main():
    import sys
    
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "No data provided"}))
        sys.exit(1)
    
    try:
        data = json.loads(sys.argv[1])
        nlp_issues = data.get('nlp_issues', [])
        classifier_results = data.get('classifier_results', [])
        statistics = data.get('statistics', {})
        sections = data.get('sections', {})
        
        recommendations = generate_recommendations(nlp_issues, classifier_results)
        overall_feedback = generate_overall_feedback(statistics, sections)
        
        print(json.dumps({
            "success": True,
            "recommendations": recommendations,
            "overall_feedback": overall_feedback
        }))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()
