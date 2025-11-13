#!/usr/bin/env python3
"""
NLP Analyzer - Traditional NLP detection for resume analysis
"""
import re
import json

# Strong action verbs list
STRONG_ACTION_VERBS = {
    'achieved', 'improved', 'trained', 'mentored', 'managed', 'created', 'designed',
    'built', 'implemented', 'developed', 'launched', 'established', 'founded',
    'spearheaded', 'pioneered', 'transformed', 'orchestrated', 'executed', 'directed',
    'coordinated', 'administered', 'analyzed', 'optimized', 'streamlined', 'enhanced',
    'increased', 'decreased', 'reduced', 'generated', 'delivered', 'exceeded',
    'led', 'drove', 'initiated', 'accelerated', 'expanded', 'restructured',
    'automated', 'integrated', 'migrated', 'scaled', 'modernized', 'architected'
}

WEAK_ACTION_VERBS = {
    'responsible for', 'worked on', 'helped with', 'participated in', 'involved in',
    'assisted', 'tried', 'attempted', 'helped', 'supported'
}

REQUIRED_SECTIONS = ['experience', 'education', 'skills']

def extract_bullet_points(text):
    """Extract bullet points from resume text"""
    bullets = []
    
    # Common bullet patterns
    patterns = [
        r'[•\-\*]\s+(.+)',  # Bullet symbols
        r'^\s*[\d]+\.\s+(.+)',  # Numbered lists
    ]
    
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
        
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                bullets.append(match.group(1).strip())
                break
    
    return bullets

def has_quantification(text):
    """Check if text contains numbers/metrics"""
    # Look for numbers, percentages, dollar amounts, time periods
    patterns = [
        r'\d+%',  # Percentages
        r'\$[\d,]+',  # Dollar amounts
        r'\d+[\+]?\s*(years?|months?|weeks?|days?)',  # Time periods
        r'\d+[\+]?\s*(people|members|users|customers|clients)',  # People counts
        r'\d+x',  # Multipliers
        r'\d{1,3}(,\d{3})*',  # Large numbers with commas
        r'\b\d+\b',  # Any number
    ]
    
    for pattern in patterns:
        if re.search(pattern, text.lower()):
            return True
    return False

def check_action_verb(text):
    """Check if text starts with a strong action verb"""
    words = text.lower().split()
    if not words:
        return {'has_verb': False, 'is_strong': False, 'verb': None}
    
    first_word = words[0]
    
    # Check for weak phrases
    first_two = ' '.join(words[:2]) if len(words) > 1 else ''
    first_three = ' '.join(words[:3]) if len(words) > 2 else ''
    
    if first_two in WEAK_ACTION_VERBS or first_three in WEAK_ACTION_VERBS:
        return {'has_verb': True, 'is_strong': False, 'verb': first_two or first_three}
    
    # Check if starts with strong verb
    if first_word in STRONG_ACTION_VERBS:
        return {'has_verb': True, 'is_strong': True, 'verb': first_word}
    
    return {'has_verb': False, 'is_strong': False, 'verb': first_word}

def detect_sections(text):
    """Detect which resume sections are present"""
    text_lower = text.lower()
    
    sections_found = []
    sections_missing = []
    
    section_patterns = {
        'experience': [r'\bexperience\b', r'\bwork history\b', r'\bemployment\b'],
        'education': [r'\beducation\b', r'\bacademic\b', r'\bdegree\b'],
        'skills': [r'\bskills\b', r'\bcompetencies\b', r'\btechnical skills\b'],
        'summary': [r'\bsummary\b', r'\bobjective\b', r'\bprofile\b'],
        'projects': [r'\bprojects\b', r'\bportfolio\b'],
        'certifications': [r'\bcertifications\b', r'\bcertificates\b']
    }
    
    for section, patterns in section_patterns.items():
        found = any(re.search(pattern, text_lower) for pattern in patterns)
        if found:
            sections_found.append(section)
        elif section in REQUIRED_SECTIONS:
            sections_missing.append(section)
    
    return {
        'found': sections_found,
        'missing': sections_missing
    }

def analyze_bullets(bullets):
    """Analyze bullet points for NLP issues"""
    analysis = []
    
    for bullet in bullets:
        bullet_analysis = {
            'text': bullet,
            'issues': [],
            'has_quantification': has_quantification(bullet),
            'action_verb': check_action_verb(bullet)
        }
        
        # Check for missing quantification
        if not bullet_analysis['has_quantification']:
            bullet_analysis['issues'].append({
                'type': 'missing_metrics',
                'message': 'Add numbers to quantify your achievements',
                'severity': 'medium'
            })
        
        # Check for weak or missing action verbs
        if not bullet_analysis['action_verb']['has_verb']:
            bullet_analysis['issues'].append({
                'type': 'missing_action_verb',
                'message': 'Start with a strong action verb',
                'severity': 'high'
            })
        elif not bullet_analysis['action_verb']['is_strong']:
            bullet_analysis['issues'].append({
                'type': 'weak_action_verb',
                'message': f"Replace '{bullet_analysis['action_verb']['verb']}' with a stronger action verb like 'Implemented', 'Led', or 'Developed'",
                'severity': 'medium'
            })
        
        # Check bullet length
        word_count = len(bullet.split())
        if word_count < 5:
            bullet_analysis['issues'].append({
                'type': 'too_short',
                'message': 'Bullet point is too short. Add more detail about your impact.',
                'severity': 'low'
            })
        elif word_count > 30:
            bullet_analysis['issues'].append({
                'type': 'too_long',
                'message': 'Bullet point is too long. Consider breaking it into multiple points.',
                'severity': 'low'
            })
        
        analysis.append(bullet_analysis)
    
    return analysis

def analyze_text(text):
    """Main NLP analysis function"""
    bullets = extract_bullet_points(text)
    sections = detect_sections(text)
    bullet_analysis = analyze_bullets(bullets)
    
    # Calculate statistics
    total_bullets = len(bullets)
    bullets_with_metrics = sum(1 for b in bullet_analysis if b['has_quantification'])
    bullets_with_strong_verbs = sum(1 for b in bullet_analysis if b['action_verb']['is_strong'])
    
    return {
        'success': True,
        'sections': sections,
        'bullet_points': bullet_analysis,
        'statistics': {
            'total_bullets': total_bullets,
            'bullets_with_metrics': bullets_with_metrics,
            'bullets_with_strong_verbs': bullets_with_strong_verbs,
            'metrics_percentage': round((bullets_with_metrics / total_bullets * 100) if total_bullets > 0 else 0, 1),
            'strong_verbs_percentage': round((bullets_with_strong_verbs / total_bullets * 100) if total_bullets > 0 else 0, 1)
        }
    }

def main():
    import sys
    
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "No text provided"}))
        sys.exit(1)
    
    text = sys.argv[1]
    result = analyze_text(text)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
