#!/usr/bin/env python3
"""
Job Matcher - Match resume to job description
"""
import sys
import json
from resume_parser import parse_pdf, parse_docx
from keyword_extractor import extract_keywords

def calculate_match(resume_keywords, job_keywords):
    """Calculate match percentage between resume and job"""
    resume_set = set(resume_keywords['technical_skills'] + resume_keywords['soft_skills'])
    job_set = set(job_keywords['technical_skills'] + job_keywords['soft_skills'])
    
    if not job_set:
        return 0
    
    matched = resume_set.intersection(job_set)
    missing = job_set.difference(resume_set)
    
    match_percentage = (len(matched) / len(job_set)) * 100 if job_set else 0
    
    return {
        'match_percentage': round(match_percentage, 1),
        'matched_keywords': list(matched),
        'missing_keywords': list(missing),
        'resume_unique_keywords': list(resume_set.difference(job_set))
    }

def main():
    if len(sys.argv) < 3:
        print(json.dumps({"success": False, "error": "Resume path and job description required"}))
        sys.exit(1)
    
    resume_path = sys.argv[1]
    job_description = sys.argv[2]
    
    try:
        # Parse resume
        if resume_path.endswith('.pdf'):
            resume_data = parse_pdf(resume_path)
        elif resume_path.endswith('.docx'):
            resume_data = parse_docx(resume_path)
        else:
            print(json.dumps({"success": False, "error": "Unsupported file type"}))
            sys.exit(1)
        
        if not resume_data['success']:
            print(json.dumps(resume_data))
            sys.exit(1)
        
        # Extract keywords from both
        resume_keywords = extract_keywords(resume_data['text'])
        job_keywords = extract_keywords(job_description)
        
        # Calculate match
        match_result = calculate_match(resume_keywords, job_keywords)
        
        # Generate suggestions
        suggestions = []
        if match_result['match_percentage'] < 70:
            suggestions.append("Add more relevant keywords from the job description")
        if match_result['missing_keywords']:
            suggestions.append(f"Consider adding these skills: {', '.join(match_result['missing_keywords'][:5])}")
        
        result = {
            'success': True,
            'matchPercentage': match_result['match_percentage'],
            'resumeKeywords': resume_keywords['technical_skills'] + resume_keywords['soft_skills'],
            'jobKeywords': job_keywords['technical_skills'] + job_keywords['soft_skills'],
            'matchedKeywords': match_result['matched_keywords'],
            'missingKeywords': match_result['missing_keywords'],
            'suggestions': suggestions
        }
        
        print(json.dumps(result))
        
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()
