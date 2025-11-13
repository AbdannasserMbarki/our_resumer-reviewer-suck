#!/usr/bin/env python3
"""
Text Improver - Suggest improvements for resume text
"""
import sys
import json
import re
from resume_parser import parse_pdf, parse_docx
from nlp_analyzer import analyze_text, STRONG_ACTION_VERBS

# Verb replacement suggestions
VERB_IMPROVEMENTS = {
    'managed': ['orchestrated', 'directed', 'led', 'oversaw'],
    'created': ['architected', 'designed', 'built', 'developed'],
    'helped': ['facilitated', 'enabled', 'supported', 'drove'],
    'worked': ['collaborated', 'partnered', 'contributed'],
    'made': ['produced', 'generated', 'delivered', 'executed'],
    'did': ['accomplished', 'achieved', 'completed', 'performed'],
    'responsible': ['led', 'managed', 'directed', 'oversaw']
}

def improve_bullet(bullet_text, issues):
    """Generate improvement suggestions for a bullet point"""
    suggestions = []
    
    for issue in issues:
        if issue['type'] == 'missing_metrics':
            suggestions.append({
                'type': 'add_metrics',
                'suggestion': 'Add specific numbers or percentages',
                'example': f"{bullet_text} [Add: by X%, reducing costs by $Y, impacting Z users]"
            })
        
        elif issue['type'] == 'missing_action_verb':
            strong_verbs = ['Implemented', 'Developed', 'Led', 'Designed', 'Built']
            suggestions.append({
                'type': 'add_action_verb',
                'suggestion': f'Start with a strong action verb',
                'example': f"[Action verb]: {bullet_text}"
            })
        
        elif issue['type'] == 'weak_action_verb':
            first_word = bullet_text.split()[0].lower() if bullet_text.split() else ''
            replacements = VERB_IMPROVEMENTS.get(first_word, list(STRONG_ACTION_VERBS)[:3])
            suggestions.append({
                'type': 'improve_verb',
                'suggestion': f'Replace with: {", ".join(replacements)}',
                'example': f"{replacements[0].capitalize()}{bullet_text[len(first_word):]}"
            })
    
    return suggestions

def generate_improvements(nlp_analysis):
    """Generate comprehensive improvement suggestions"""
    improvements = []
    
    for bullet in nlp_analysis['bullet_points']:
        if bullet['issues']:
            bullet_improvements = improve_bullet(bullet['text'], bullet['issues'])
            
            improvements.append({
                'original': bullet['text'],
                'issues': [issue['message'] for issue in bullet['issues']],
                'suggestions': bullet_improvements
            })
    
    return improvements

def generate_overall_suggestions(stats, sections):
    """Generate overall suggestions"""
    suggestions = []
    
    # Metrics suggestions
    if stats['metrics_percentage'] < 70:
        suggestions.append({
            'category': 'Quantification',
            'priority': 'high',
            'message': 'Add numbers and metrics to more bullet points',
            'tip': 'Aim for at least 70% of bullets to include quantifiable achievements'
        })
    
    # Action verb suggestions
    if stats['strong_verbs_percentage'] < 80:
        suggestions.append({
            'category': 'Action Verbs',
            'priority': 'high',
            'message': 'Use stronger action verbs',
            'tip': 'Start every bullet with a powerful action verb like Implemented, Led, or Architected'
        })
    
    # Section suggestions
    if sections['missing']:
        suggestions.append({
            'category': 'Structure',
            'priority': 'critical',
            'message': f"Add missing sections: {', '.join(sections['missing'])}",
            'tip': 'Include Experience, Education, and Skills sections at minimum'
        })
    
    return suggestions

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
        
        # Analyze text
        nlp_analysis = analyze_text(parsed['text'])
        
        # Generate improvements
        improvements = generate_improvements(nlp_analysis)
        overall_suggestions = generate_overall_suggestions(
            nlp_analysis['statistics'],
            nlp_analysis['sections']
        )
        
        result = {
            'success': True,
            'improvements': improvements,
            'bulletAnalysis': nlp_analysis['bullet_points'],
            'overallSuggestions': overall_suggestions
        }
        
        print(json.dumps(result))
        
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()
