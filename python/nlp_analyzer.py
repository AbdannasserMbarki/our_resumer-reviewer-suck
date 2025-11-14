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

REQUIRED_SECTIONS = ['experience', 'skills', 'contact']
CRITICAL_SECTIONS = ['experience', 'skills', 'contact']  # Must have all three for non-zero score

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
    """Enhanced check for quantifiable metrics"""
    patterns = [
        r'\d+%',  # Percentages
        r'\$[\d,]+',  # Dollar amounts with commas
        r'\d+\s*(million|thousand|k|m|billion)',  # Large numbers
        r'\d+\s*(users|customers|clients|projects|people|employees|team members)',  # Count of things
        r'\d+\s*(years?|months?|weeks?|days?)',  # Time periods
        r'(increased|decreased|improved|reduced|generated|saved|exceeded).*\d+',  # Improvement metrics
        r'\d+\s*(hours?|minutes?)',  # Time savings
        r'\d+x\s*(faster|better|more)',  # Multiplier improvements
        r'(over|under|within)\s*\d+',  # Comparative metrics
        r'\d+\s*(awards?|certifications?|patents?)',  # Achievements count
    ]
    
    return any(re.search(pattern, text.lower()) for pattern in patterns)

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
        'experience': [r'\bexperience\b', r'\bwork history\b', r'\bemployment\b', r'\bwork experience\b', r'\bprofessional experience\b'],
        'education': [r'\beducation\b', r'\bacademic\b', r'\bdegree\b'],
        'skills': [r'\bskills\b', r'\bcompetencies\b', r'\btechnical skills\b', r'\bcore competencies\b', r'\bprofessional skills\b'],
        'contact': [r'\bcontact\b', r'\bemail\b', r'\bphone\b', r'\baddress\b', r'\bmobile\b', r'\btel\b', r'@\w+\.\w+', r'\(\d{3}\)', r'\d{3}-\d{3}-\d{4}', r'\+\d+'],
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
    
    # Check if all critical sections are present
    critical_sections_missing = [section for section in CRITICAL_SECTIONS if section not in sections_found]
    has_all_critical_sections = len(critical_sections_missing) == 0
    
    return {
        'found': sections_found,
        'missing': sections_missing,
        'critical_missing': critical_sections_missing,
        'has_all_critical': has_all_critical_sections
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
        
        # Basic grammar/spelling checks (with very low severity weight)
        bullet_lower = bullet.lower()
        
        # Check for common grammar issues (minimal penalty)
        grammar_issues = []
        
        # Double spaces
        if '  ' in bullet:
            grammar_issues.append('Remove extra spaces')
        
        # Missing periods at end (if bullet is long enough)
        if word_count > 8 and not bullet.rstrip().endswith('.'):
            grammar_issues.append('Consider adding period at end of sentence')
        
        # Common typos (very basic check)
        common_typos = {
            'recieve': 'receive',
            'seperate': 'separate', 
            'occured': 'occurred',
            'managment': 'management',
            'sucessful': 'successful'
        }
        
        for typo, correction in common_typos.items():
            if typo in bullet_lower:
                grammar_issues.append(f'Possible typo: "{typo}" should be "{correction}"')
        
        # Add grammar issues with very low severity (minimal impact on score)
        for issue in grammar_issues:
            bullet_analysis['issues'].append({
                'type': 'grammar_spelling',
                'message': issue,
                'severity': 'low'  # Low severity = minimal score impact
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
