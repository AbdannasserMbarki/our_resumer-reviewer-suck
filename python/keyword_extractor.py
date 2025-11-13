#!/usr/bin/env python3
"""
Keyword Extractor - Extract important keywords and skills from text
"""
import sys
import json
import re
from collections import Counter

# Common tech skills and keywords
TECH_KEYWORDS = {
    'python', 'java', 'javascript', 'typescript', 'react', 'angular', 'vue', 'node',
    'express', 'django', 'flask', 'spring', 'docker', 'kubernetes', 'aws', 'azure',
    'gcp', 'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'redis', 'git',
    'ci/cd', 'jenkins', 'terraform', 'ansible', 'linux', 'agile', 'scrum', 'rest',
    'api', 'microservices', 'machine learning', 'ai', 'data science', 'tensorflow',
    'pytorch', 'spark', 'hadoop', 'pandas', 'numpy', 'scikit-learn'
}

SOFT_SKILLS = {
    'leadership', 'communication', 'teamwork', 'problem-solving', 'analytical',
    'creative', 'organized', 'detail-oriented', 'collaborative', 'adaptable'
}

def extract_keywords(text):
    """Extract keywords from text"""
    text_lower = text.lower()
    
    # Extract tech keywords
    tech_found = []
    for keyword in TECH_KEYWORDS:
        if keyword in text_lower:
            tech_found.append(keyword)
    
    # Extract soft skills
    skills_found = []
    for skill in SOFT_SKILLS:
        if skill in text_lower:
            skills_found.append(skill)
    
    # Extract years of experience
    exp_pattern = r'(\d+)\+?\s*(years?|yrs?)'
    exp_matches = re.findall(exp_pattern, text_lower)
    experience_years = [int(match[0]) for match in exp_matches]
    
    # Extract degree/education
    degrees = []
    degree_patterns = ['bachelor', 'master', 'phd', 'mba', 'bs', 'ms', 'ba', 'ma']
    for degree in degree_patterns:
        if degree in text_lower:
            degrees.append(degree)
    
    return {
        'success': True,
        'technical_skills': tech_found,
        'soft_skills': skills_found,
        'experience_years': max(experience_years) if experience_years else None,
        'education_levels': degrees,
        'total_keywords': len(tech_found) + len(skills_found)
    }

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "No text provided"}))
        sys.exit(1)
    
    text = sys.argv[1]
    result = extract_keywords(text)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
