#!/usr/bin/env python3
"""
Recommendation Engine - Map detected issues to specific recommendations
"""
import json

# Comprehensive recommendation templates based on resume best practices
RECOMMENDATIONS = {
    # FORMATTING & CONSISTENCY
    'formatting_consistency': {
        'priority': 'high',
        'category': 'formatting',
        'message': 'Maintain consistent formatting throughout your resume',
        'details': [
            'Use consistent font sizes, bold/italic formatting, and bullet styles',
            'Standardize date formats (e.g., "Jan 2020 - Dec 2022")',
            'Align text consistently and maintain proper spacing',
            'Keep bullet points to 1-2 lines each'
        ]
    },
    'simple_template': {
        'priority': 'medium',
        'category': 'formatting', 
        'message': 'Use a simple, ATS-optimized template',
        'details': [
            'Avoid complex layouts, graphics, or tables that ATS cannot parse',
            'Content is more important than fancy design',
            'Use a clean, professional layout with clear section headers'
        ]
    },
    'font_readability': {
        'priority': 'high',
        'category': 'formatting',
        'message': 'Use a simple, machine-readable font',
        'recommendations': [
            'Stick to standard fonts: Times New Roman, Arial, Calibri',
            'Use font size 10-12 points for body text',
            'Avoid decorative or script fonts that ATS cannot read'
        ]
    },
    'one_page_rule': {
        'priority': 'medium',
        'category': 'formatting',
        'message': 'Follow the one-page rule for optimal impact',
        'guidelines': [
            'One page if you have <5-10 years of relevant experience',
            'Two pages maximum if you have >10 years of experience',
            'Prioritize most relevant and impactful experiences'
        ]
    },
    
    # STRUCTURE & ORGANIZATION
    'resume_structure_student': {
        'priority': 'high',
        'category': 'structure',
        'message': 'Structure your resume properly for student/recent graduate',
        'recommended_order': [
            '1. Name & Contact Information',
            '2. Education', 
            '3. Work Experience',
            '4. Leadership/Extra-curricular Activities',
            '5. Additional Info (Skills, Languages, Interests)'
        ]
    },
    'resume_structure_experienced': {
        'priority': 'high',
        'category': 'structure', 
        'message': 'Structure your resume properly for experienced professionals',
        'recommended_order': [
            '1. Name & Contact Information',
            '2. Work Experience',
            '3. Projects/Activities (Optional)',
            '4. Education',
            '5. Additional Info (Skills, Languages, Interests)'
        ]
    },
    'remove_summary_objective': {
        'priority': 'medium',
        'category': 'structure',
        'message': 'Remove Summary and Objective sections',
        'rationale': [
            'Summary wastes space and provides no additional value',
            'Objective is obvious from your job application',
            'Use the space for more impactful content'
        ]
    },
    'remove_unnecessary_items': {
        'priority': 'high',
        'category': 'structure',
        'message': 'Remove unnecessary personal information',
        'items_to_remove': [
            'Photo (can lead to bias or auto-rejection)',
            'References or "References available upon request"',
            'Personal details: religion, marital status, ethnicity, age, gender',
            'Irrelevant hobbies or interests'
        ]
    },
    
    # QUANTIFICATION & METRICS
    'missing_metrics': {
        'priority': 'critical',
        'category': 'quantification',
        'message': 'Quantify your achievements with specific numbers and metrics',
        'examples': [
            'Instead of "Improved system performance" → "Improved system performance by 45%"',
            'Instead of "Managed a team" → "Managed a team of 8 engineers"',
            'Instead of "Increased sales" → "Increased sales by $2.3M annually"',
            'Instead of "Reduced costs" → "Reduced operational costs by 30% ($50K savings)"'
        ],
        'metric_ideas': [
            'Percentages: "increased efficiency by 25%"',
            'Dollar amounts: "generated $1.2M in revenue"', 
            'Time savings: "reduced processing time by 15 hours/week"',
            'Team sizes: "led cross-functional team of 12"',
            'Scale: "managed portfolio of 50+ clients"'
        ]
    },
    # ACTION VERBS & LANGUAGE
    'missing_action_verb': {
        'priority': 'critical',
        'category': 'action_verbs',
        'message': 'Start bullet points with strong action verbs in past tense',
        'strong_verbs': [
            'Leadership: Led, Managed, Directed, Supervised, Coordinated',
            'Development: Developed, Built, Designed, Created, Implemented',
            'Analysis: Analyzed, Researched, Evaluated, Assessed, Investigated', 
            'Achievement: Achieved, Accomplished, Delivered, Exceeded, Surpassed',
            'Improvement: Optimized, Enhanced, Streamlined, Improved, Increased'
        ],
        'avoid': ['Responsible for', 'Worked on', 'Duties included', 'Helped with']
    },
    'weak_action_verb': {
        'priority': 'high',
        'category': 'action_verbs',
        'message': 'Replace weak verbs with stronger action verbs',
        'replacements': {
            'helped': ['Assisted', 'Supported', 'Facilitated', 'Enabled'],
            'worked on': ['Developed', 'Built', 'Implemented', 'Created'],
            'responsible for': ['Led', 'Managed', 'Directed', 'Oversaw'],
            'participated in': ['Contributed to', 'Collaborated on', 'Drove'],
            'involved in': ['Executed', 'Delivered', 'Spearheaded'],
            'handled': ['Managed', 'Coordinated', 'Executed', 'Oversaw']
        }
    },
    'avoid_adverbs_pronouns': {
        'priority': 'medium',
        'category': 'language',
        'message': 'Avoid adverbs and personal pronouns',
        'guidelines': [
            'Remove adverbs like "skillfully", "effectively", "successfully"',
            'Remove personal pronouns like "I", "my", "we"',
            'Instead of "I skillfully managed" → "Managed"',
            'Let your quantified results speak for effectiveness'
        ]
    },
    
    # WORK EXPERIENCE
    'accomplishment_vs_responsibility': {
        'priority': 'critical',
        'category': 'content',
        'message': 'Focus on accomplishments, not job responsibilities',
        'good_example': 'Managed a process re-engineering project to improve end-to-end service processes; restructured communication flow among 10 departments and cut paperwork by 75%',
        'poor_example': 'Responsible for the coordinated management of multiple related projects directed toward strategic business and organizational objectives',
        'tips': [
            'Show impact and results, not just what you did',
            'Use specific examples with quantified outcomes',
            'Focus on achievements that demonstrate your value'
        ]
    },
    'chronological_order': {
        'priority': 'medium',
        'category': 'structure',
        'message': 'List work experience in reverse chronological order',
        'details': 'Your current or most recent job should appear first, followed by previous positions in reverse chronological order'
    },
    'bullet_importance_order': {
        'priority': 'medium', 
        'category': 'structure',
        'message': 'Organize bullet points by importance and relevance',
        'strategy': [
            'First bullet should be your most impactful achievement',
            'Or the experience most relevant to target job',
            'Order remaining bullets by decreasing impact/relevance'
        ]
    },
    'company_description': {
        'priority': 'low',
        'category': 'content',
        'message': 'Include brief company descriptions for lesser-known employers',
        'example': 'TechStartup Inc. (Series B fintech startup, $50M funding) - Software Engineer'
    },
    'ats_keywords': {
        'priority': 'high',
        'category': 'optimization',
        'message': 'Include relevant keywords for ATS systems',
        'strategy': [
            'Mirror keywords from the job description',
            'Include technical skills and industry terms naturally',
            'Don\'t overdo it - context matters more than keyword density',
            'Focus on skills and achievements that match the role'
        ]
    },
    # EDUCATION SECTION
    'education_format': {
        'priority': 'medium',
        'category': 'education',
        'message': 'Format education section properly',
        'include': [
            'Institution name and location',
            'Degree type, major, and minor',
            'Graduation year (or expected graduation)',
            'GPA if above 3.0 (specify if in-major GPA)'
        ],
        'example': 'Bachelor of Science in Computer Science | State University | May 2023 | GPA: 3.7/4.0'
    },
    'standardized_test_scores': {
        'priority': 'low',
        'category': 'education', 
        'message': 'Include standardized test scores only if in top 20th percentile',
        'details': 'SAT, GMAT, GRE scores should only be included if they\'re competitive for your field'
    },
    
    # PROJECTS & LEADERSHIP
    'projects_relevance': {
        'priority': 'medium',
        'category': 'content',
        'message': 'Include relevant projects and leadership experiences',
        'guidelines': [
            'Especially important for students and recent graduates',
            'Include university projects, leadership roles, volunteering',
            'Focus on experiences relevant to your target role',
            'Use same accomplishment-focused approach as work experience'
        ]
    },
    
    # ADDITIONAL INFORMATION
    'skills_section': {
        'priority': 'high',
        'category': 'skills',
        'message': 'Include a well-organized skills section',
        'categories': [
            'Technical Skills: Programming languages, software, tools',
            'Languages: List proficiency levels if relevant',
            'Certifications: Industry-relevant certifications',
            'Professional Memberships: Relevant professional societies'
        ],
        'honesty_note': 'Never lie about your skill levels - you will be tested in interviews'
    },
    'interests_section': {
        'priority': 'low',
        'category': 'additional',
        'message': 'Include relevant interests that add value',
        'tips': [
            'Choose interests that show relevant skills or cultural fit',
            'Interviewers often use interests as conversation starters',
            'Avoid controversial or irrelevant hobbies'
        ]
    },
    
    # FINAL CHECKS & BEST PRACTICES
    'proofreading': {
        'priority': 'critical',
        'category': 'quality',
        'message': 'Thoroughly proofread your resume',
        'checklist': [
            'Check for spelling and grammar errors',
            'Verify all dates, company names, and contact information',
            'Have at least one other person review your resume',
            'Read your resume aloud to catch awkward phrasing'
        ]
    },
    'tailoring': {
        'priority': 'high',
        'category': 'optimization',
        'message': 'Tailor your resume for each application',
        'strategies': [
            'Adjust keywords and skills to match job description',
            'Reorder bullet points to emphasize relevant experience',
            'Don\'t use identical resume for different industries',
            'Highlight experiences most relevant to target role'
        ]
    },
    'pdf_format': {
        'priority': 'high',
        'category': 'formatting',
        'message': 'Submit resume in PDF format',
        'reasons': [
            'Ensures consistent formatting across all devices',
            'Prevents text from shifting or reformatting',
            'More professional than Word documents',
            'Use filename: FirstName-LastName-Resume.pdf'
        ]
    },
    'contact_information': {
        'priority': 'critical',
        'category': 'structure',
        'message': 'Include complete contact information in header',
        'required': [
            'Full name (larger font, prominent placement)',
            'Professional email address',
            'Phone number with area code',
            'LinkedIn profile URL',
            'Location (city, state - no full address needed)'
        ]
    },
    'white_space': {
        'priority': 'medium',
        'category': 'formatting',
        'message': 'Maintain proper white space and margins',
        'guidelines': [
            'Leave sufficient margins for recruiter notes',
            'Don\'t cram too much content - readability matters',
            'Use white space to create visual hierarchy',
            'Keep bullet points to 1-2 lines maximum'
        ]
    },
    
    # CRITICAL REQUIREMENTS
    'section_missing': {
        'priority': 'critical',
        'category': 'structure',
        'message': 'Include all required resume sections',
        'required_sections': [
            'Contact Information (Name, phone, email)',
            'Work Experience (or relevant projects for students)',
            'Education',
            'Skills (technical and relevant soft skills)'
        ],
        'optional_sections': ['Projects', 'Leadership', 'Interests', 'Certifications']
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

def generate_comprehensive_recommendations(resume_data, statistics, sections):
    """Generate comprehensive recommendations based on resume best practices"""
    recommendations = []
    
    # CRITICAL CHECKS
    # Check for required sections
    required_sections = ['experience', 'education', 'skills', 'contact']
    missing_sections = []
    for section in required_sections:
        if section not in sections or not sections[section].get('found', False):
            missing_sections.append(section)
    
    if missing_sections:
        rec = RECOMMENDATIONS['section_missing'].copy()
        rec['missing'] = missing_sections
        recommendations.append(rec)
    
    # Check contact information
    contact_info = sections.get('contact', {})
    if not contact_info.get('email') or not contact_info.get('phone'):
        recommendations.append(RECOMMENDATIONS['contact_information'])
    
    # QUANTIFICATION & METRICS
    metrics_pct = statistics.get('metrics_percentage', 0)
    if metrics_pct < 30:
        recommendations.append(RECOMMENDATIONS['missing_metrics'])
    
    # ACTION VERBS
    strong_verbs_pct = statistics.get('strong_verbs_percentage', 0)
    if strong_verbs_pct < 60:
        recommendations.append(RECOMMENDATIONS['missing_action_verb'])
    
    # FORMATTING & STRUCTURE
    # Check for common formatting issues
    resume_text = resume_data.get('text', '')
    
    # Check for objective/summary sections (should be removed)
    if any(word in resume_text.lower() for word in ['objective:', 'summary:', 'career objective']):
        recommendations.append(RECOMMENDATIONS['remove_summary_objective'])
    
    # Check for unnecessary personal info
    personal_indicators = ['married', 'single', 'age:', 'religion', 'references available']
    if any(indicator in resume_text.lower() for indicator in personal_indicators):
        recommendations.append(RECOMMENDATIONS['remove_unnecessary_items'])
    
    # Check for adverbs and pronouns
    adverbs = ['skillfully', 'effectively', 'successfully', 'efficiently']
    pronouns = [' i ', ' my ', ' we ', ' our ']
    text_lower = ' ' + resume_text.lower() + ' '
    
    if any(adverb in text_lower for adverb in adverbs) or any(pronoun in text_lower for pronoun in pronouns):
        recommendations.append(RECOMMENDATIONS['avoid_adverbs_pronouns'])
    
    # CONTENT QUALITY
    # Check for accomplishment vs responsibility focus
    responsibility_phrases = ['responsible for', 'duties included', 'tasked with']
    if any(phrase in resume_text.lower() for phrase in responsibility_phrases):
        recommendations.append(RECOMMENDATIONS['accomplishment_vs_responsibility'])
    
    # EDUCATION SECTION
    education = sections.get('education', {})
    if education and not education.get('gpa') and not education.get('graduation_year'):
        recommendations.append(RECOMMENDATIONS['education_format'])
    
    # FINAL RECOMMENDATIONS
    # Always recommend these best practices
    recommendations.extend([
        RECOMMENDATIONS['proofreading'],
        RECOMMENDATIONS['tailoring'], 
        RECOMMENDATIONS['pdf_format'],
        RECOMMENDATIONS['ats_keywords']
    ])
    
    # FORMATTING RECOMMENDATIONS
    recommendations.extend([
        RECOMMENDATIONS['formatting_consistency'],
        RECOMMENDATIONS['white_space']
    ])
    
    # Remove duplicates and sort by priority
    unique_recs = []
    seen_messages = set()
    for rec in recommendations:
        if rec['message'] not in seen_messages:
            unique_recs.append(rec)
            seen_messages.add(rec['message'])
    
    # Sort by priority
    priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    unique_recs.sort(key=lambda x: priority_order.get(x.get('priority', 'low'), 3))
    
    return unique_recs

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
