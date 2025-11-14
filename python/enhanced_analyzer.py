"""
Enhanced Resume Analyzer - Comprehensive evaluation system
"""
import re
import spacy
import nltk
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from textstat import flesch_reading_ease, flesch_kincaid_grade
import json

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class EnhancedResumeAnalyzer:
    def __init__(self):
        # Load spaCy model for NER
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Warning: spaCy model not found. NER features will be limited.")
            self.nlp = None
        
        # Define section patterns and keywords
        self.section_patterns = {
            'contact': ['contact', 'personal information', 'header', 'email:', 'phone:', 'tel:', 'mobile:', 'address:'],
            'summary': ['summary', 'objective', 'profile', 'about', 'overview'],
            'experience': ['experience', 'work experience', 'employment', 'professional experience', 'career', 'work history'],
            'education': ['education', 'academic background', 'academic', 'qualifications'],
            'skills': ['skills', 'competencies', 'technologies', 'technical skills', 'core competencies'],
            'projects': ['projects', 'portfolio', 'personal projects'],
            'certifications': ['certifications', 'certificates', 'credentials', 'licenses'],
            'languages': ['languages', 'language skills'],
            'awards': ['awards', 'honors', 'achievements', 'recognition', 'accomplishments']
        }
        
        # Logical section order
        self.logical_order = ['contact', 'summary', 'experience', 'education', 'skills', 'projects', 'certifications', 'languages', 'awards']
        
        # Strong action verbs categorized
        # Each category groups verbs with similar intent to help score impact and variety
        self.strong_verbs = {
            'leadership': [
                'led', 'managed', 'directed', 'supervised', 'coordinated', 'oversaw',
                'guided', 'mentored', 'headed', 'chaired', 'orchestrated', 'facilitated',
                'delegated', 'coached', 'superintended'
            ],
            'achievement': [
                'achieved', 'accomplished', 'exceeded', 'delivered', 'completed',
                'attained', 'surpassed', 'earned', 'secured', 'won'
            ],
            'development': [
                'developed', 'created', 'built', 'designed', 'implemented', 'engineered',
                'constructed', 'launched', 'deployed', 'prototyped', 'pioneered',
                'established', 'architected'
            ],
            'improvement': [
                'improved', 'enhanced', 'optimized', 'streamlined', 'increased',
                'reduced', 'minimized', 'boosted', 'accelerated', 'upgraded',
                'refined', 'simplified'
            ],
            'analysis': [
                'analyzed', 'evaluated', 'assessed', 'researched', 'investigated',
                'examined', 'studied', 'audited', 'diagnosed', 'modeled',
                'forecasted'
            ]
        }
        
        # Weak verbs to flag
        self.weak_verbs = ['responsible', 'worked', 'helped', 'assisted', 'participated', 'involved', 'handled', 'dealt']
        
        # Informal/unprofessional words
        self.informal_words = ['awesome', 'cool', 'stuff', 'things', 'lot', 'tons', 'loads', 'super', 'really', 'very']
        
        # Vague phrases
        self.vague_phrases = ['responsible for', 'worked on', 'dealt with', 'helped with', 'involved in', 'participated in']
        
        # Enhanced buzzwords list with severity levels and patterns
        self.buzzwords = {
            # Critical buzzwords (major red flags)
            'critical': [
                'guru', 'ninja', 'rockstar', 'superhero', 'wizard', 'god', 'master', 'expert',
                'thought leader', 'visionary', 'game-changer', 'disruptor', 'revolutionary',
                'cutting-edge', 'bleeding-edge', 'world-class', 'best-in-class', 'top-notch'
            ],
            # High impact buzzwords (commonly overused)
            'high': [
                'motivated', 'results-driven', 'results oriented', 'goal-oriented', 'goal oriented',
                'detail-oriented', 'detail oriented', 'self-starter', 'self motivated', 'go-getter',
                'team player', 'team-oriented', 'people person', 'hard worker', 'fast learner',
                'quick learner', 'highly motivated', 'self-motivated', 'proactive', 'dynamic'
            ],
            # Medium impact buzzwords (vague descriptors)
            'medium': [
                'innovative', 'creative', 'passionate', 'dedicated', 'reliable', 'flexible',
                'adaptable', 'versatile', 'strategic', 'tactical', 'hands-on', 'customer-focused',
                'client-focused', 'solution-oriented', 'problem solver', 'multitasker',
                'excellent communication', 'strong communication', 'great communication'
            ],
            # Low impact buzzwords (overused phrases)
            'low': [
                'synergy', 'leverage', 'utilize', 'seamlessly', 'holistic', 'robust',
                'scalable', 'optimization', 'best practices', 'core competencies',
                'value-added', 'end-to-end', 'turnkey', 'mission-critical', 'paradigm shift',
                'think outside the box', 'low-hanging fruit', 'move the needle'
            ]
        }
        
        # Buzzword patterns for more sophisticated detection
        self.buzzword_patterns = [
            r'\b(?:highly|extremely|very)\s+(?:motivated|skilled|experienced|qualified)\b',
            r'\b(?:excellent|outstanding|exceptional|superior)\s+(?:communication|leadership|problem.solving)\s+skills?\b',
            r'\b(?:proven|demonstrated|strong)\s+(?:track record|ability|experience|background)\b',
            r'\b(?:results?.driven|goal.oriented|detail.oriented|customer.focused)\b',
            r'\b(?:team\s+player|self.starter|go.getter|people\s+person)\b'
        ]
        
        # Impact measurement patterns (enhanced)
        self.impact_patterns = {
            'percentages': r'\d+\.?\d*%',
            'dollar_amounts': r'\$[\d,]+(?:\.\d+)?[KMB]?',
            'large_numbers': r'\d+[KMB]|\d{1,3}(?:,\d{3})+',
            'time_saved': r'(?:saved|reduced|decreased).*?(\d+).*?(hours?|days?|weeks?|months?)',
            'performance_metrics': r'(?:increased|improved|enhanced|boosted|grew).*?(\d+\.?\d*)%?',
            'team_sizes': r'(?:team|group) of (\d+)|led (\d+)|managed (\d+)',
            'customer_metrics': r'(\d+)\+?\s*(?:customers?|clients?|users?|requests?)',
            'project_scope': r'(\d+)\+?\s*(?:projects?|initiatives?|campaigns?)'
        }
        
        # Date patterns (comprehensive and robust)
        self.date_patterns = [
            # Full month names with years
            r'(?P<month>January|February|March|April|May|June|July|August|September|October|November|December)\s+(?P<year>\d{4})',
            # Abbreviated month names with years
            r'(?P<month>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+(?P<year>\d{4})',
            # Numeric dates MM/YYYY or MM-YYYY
            r'(?P<month>\d{1,2})[\/\-](?P<year>\d{4})',
            # Year only ranges
            r'(?P<year>\d{4})\s*[-–—]\s*(?P<end_year>\d{4}|present|current|now)',
            # Full date ranges with months
            r'(?P<start_month>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+(?P<start_year>\d{4})\s*[-–—]\s*(?P<end_month>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+(?P<end_year>\d{4})',
            # Years with "to" keyword
            r'(?P<year>\d{4})\s+to\s+(?P<end_year>\d{4}|present|current)',
            # Graduation years (common format)
            r'graduated?\s+(?P<year>\d{4})',
            r'class\s+of\s+(?P<year>\d{4})',
            # Employment duration patterns
            r'(?P<start_year>\d{4})\s*-\s*(?P<end_year>\d{4})',
            # Isolated 4-digit years (but be careful not to match other numbers)
            r'\b(?P<year>19[5-9]\d|20[0-4]\d)\b',
            # Seasons with years
            r'(?P<season>Spring|Summer|Fall|Winter|Autumn)\s+(?P<year>\d{4})',
        ]
        
        # Summary quality indicators
        self.generic_summary_phrases = [
            'seeking opportunities', 'looking for', 'hard worker', 'team player',
            'results driven', 'detail oriented', 'fast learner', 'motivated individual',
            'excellent communication skills', 'problem solver', 'self starter'
        ]

    def analyze_resume(self, text, metadata=None):
        """Perform comprehensive resume analysis"""
        analysis = {
            'sections': self.analyze_sections(text),
            'readability': self.analyze_readability(text),
            'writing_quality': self.analyze_writing_quality(text),
            'action_verbs': self.analyze_action_verbs(text),
            'quantification': self.analyze_quantification_enhanced(text),  # Enhanced version
            'skills_analysis': self.analyze_skills_enhanced(text),  # Enhanced version
            'chronology': self.analyze_chronology_enhanced(text),  # Enhanced version
            'summary_analysis': self.analyze_summary_quality(text),  # New
            'buzzwords_analysis': self.analyze_buzzwords(text),  # New
            'impact_analysis': self.analyze_impact_metrics(text),  # New
            'date_consistency': self.analyze_date_consistency(text),  # New
            'unnecessary_sections': self.analyze_unnecessary_sections(text),  # New
            'entities': self.extract_entities(text),
            'tone_analysis': self.analyze_tone(text),
            'formatting': self.analyze_formatting(text),
            'final_score': {}
        }
        
        # Calculate final weighted score
        analysis['final_score'] = self.calculate_final_score(analysis)
        
        # Generate structured criteria for frontend display
        analysis['criteria'] = self.generate_criteria_summary(analysis)
        
        return analysis

    def detect_explicit_headers_only(self, text):
        """Detect only explicit section headers (no content-based inference) for validation"""
        import re
        
        detected_headers = []
        
        # Handle both multi-line and single-line formats (some PDFs parse as one long line)
        # First try to split by lines, then also look for section patterns within text
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Section header patterns to match - look for these as standalone headers
        section_patterns = {
            'experience': [r'\bexperience\b', r'\bwork experience\b', r'\bprofessional experience\b', r'\bemployment\b', r'\bcareer history\b'],
            'projects': [r'\bprojects\b', r'\bpersonal projects\b', r'\bportfolio\b'],
            'education': [r'\beducation\b', r'\bacademic background\b', r'\bacademic qualifications\b'],
            'skills': [r'\bskills\b', r'\btechnical skills\b', r'\bcore competencies\b', r'\bcompetencies\b'],
            'contact': [r'\bcontact information\b', r'\bcontact\b', r'\bpersonal information\b'],
            'summary': [r'\bsummary\b', r'\bprofessional summary\b', r'\bobjective\b', r'\bprofile\b', r'\babout me\b', r'\boverview\b'],
            'certifications': [r'\bcertifications\b', r'\bcertificates\b', r'\bcredentials\b', r'\blicenses\b'],
            'languages': [r'\blanguages\b', r'\blanguage skills\b'],
            'awards': [r'\bawards\b', r'\bhonors\b', r'\bachievements\b', r'\brecognition\b']
        }
        
        # Check each line first (normal case)
        for line in lines:
            line_lower = line.lower().strip()
            
            # Look for section headers that appear to be standalone or at start of content blocks
            for section, patterns in section_patterns.items():
                for pattern in patterns:
                    # Match if it's a short line that's just the header, or if it appears with bullet/separator
                    if (re.match(f'^{pattern}$', line_lower) or  # Exact match
                        re.match(f'^{pattern}\\s*[•·▪▫‣⁃]', line_lower) or  # Header with bullet
                        (len(line.split()) <= 3 and re.search(pattern, line_lower))):  # Short line containing pattern
                        if section not in detected_headers:
                            detected_headers.append(section)
                        break
        
        # Also check for patterns within the full text (for single-line PDFs)
        text_lower = text.lower()
        for section, patterns in section_patterns.items():
            for pattern in patterns:
                # Look for section headers followed by bullets or at natural break points
                if re.search(f'\\b{pattern}\\s*[•·▪▫‣⁃]', text_lower):
                    if section not in detected_headers:
                        detected_headers.append(section)
                    break
        
        return detected_headers  # Return list of explicitly detected section headers

    def analyze_sections(self, text):
        """Analyze section completeness and order"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        detected_sections = []
        section_positions = {}
        
        # First pass: detect explicit section headers only (no content-based inference)
        for i, line in enumerate(lines):
            section = self.identify_section(line)
            if section:
                detected_sections.append(section)
                if section not in section_positions:
                    section_positions[section] = i
        
        # Post-processing: infer sections from content when headers are missing
        if 'contact' not in detected_sections:
            # Look for contact patterns in the first 10 lines (typical contact area)
            contact_patterns = [
                r'\b\w+@\w+\.\w+\b',  # Email
                r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # Phone
                r'\b(linkedin|github)\.com\b',  # Social profiles
                r'\b\d+\s+\w+\s+(street|ave|avenue|road|rd|blvd|boulevard)\b'  # Address
            ]
            
            for i, line in enumerate(lines[:10]):
                if any(re.search(pattern, line.lower()) for pattern in contact_patterns):
                    if 'contact' not in detected_sections:  # Only add if not already detected
                        detected_sections.insert(0, 'contact')  # Add at beginning
                        section_positions['contact'] = 0
                    break
        
        # Infer other sections from content keywords
        full_text = text.lower()
        
        # Education indicators
        if 'education' not in detected_sections:
            education_indicators = [
                r'\b(university|college|school|institute)\b',
                r'\b(bachelor|master|phd|degree|diploma)\b',
                r'\b(gpa|grade|graduated|graduation)\b'
            ]
            if any(re.search(pattern, full_text) for pattern in education_indicators):
                detected_sections.append('education')
                section_positions['education'] = len(detected_sections)
        
        # Skills indicators
        if 'skills' not in detected_sections:
            skills_indicators = [
                r'\b(programming languages?|technical skills?|tools?)\b',
                r'\b(python|java|javascript|html|css|react|sql)\b',
                r'\b(frameworks?|libraries|databases?)\b'
            ]
            if any(re.search(pattern, full_text) for pattern in skills_indicators):
                detected_sections.append('skills')
                section_positions['skills'] = len(detected_sections)
        
        # Projects indicators
        if 'projects' not in detected_sections:
            projects_indicators = [
                r'\bprojects?\b',
                r'\b(built|developed|created|designed)\s+.*(app|application|website|system)\b',
                r'\bsource code\b'
            ]
            if any(re.search(pattern, full_text) for pattern in projects_indicators):
                detected_sections.append('projects')
                section_positions['projects'] = len(detected_sections)
        
        # Check required sections
        required_sections = ['contact', 'experience', 'education', 'skills']
        missing_required = [s for s in required_sections if s not in detected_sections]
        
        # Check optional sections
        optional_sections = ['projects', 'certifications', 'languages', 'awards']
        present_optional = [s for s in optional_sections if s in detected_sections]
        
        # Check section order
        order_analysis = self.analyze_section_order(detected_sections, section_positions)
        
        # Detect duplicated sections
        duplicates = [section for section, count in Counter(detected_sections).items() if count > 1]
        
        return {
            'detected_sections': list(set(detected_sections)),  # Remove duplicates for this list
            'missing_required': missing_required,
            'present_optional': present_optional,
            'duplicated_sections': duplicates,
            'order_analysis': order_analysis,
            'section_positions': section_positions
        }

    def identify_section(self, line):
        """Identify if a line is a section header"""
        line_lower = line.lower().strip()
        original_line = line.strip()
        
        # Skip very short lines or lines with too many characters (likely content, not headers)
        if len(line) < 2 or len(line) > 60:
            return None
        
        # Check if line is all caps (common for section headers)
        is_caps = original_line.isupper()
        
        # Special handling for contact information detection
        contact_patterns = [
            r'\b\w+@\w+\.\w+\b',  # Email pattern
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # Phone pattern
            r'\b(phone|email|mobile|tel|address):\s*',  # Explicit contact labels
        ]
        
        # If line contains contact info, mark previous context as contact section
        if any(re.search(pattern, line_lower) for pattern in contact_patterns):
            return 'contact'
        
        # Check for exact section header matches (prioritize exact matches)
        section_exact_matches = {
            'contact': ['contact information', 'contact', 'personal information'],
            'summary': ['summary', 'professional summary', 'objective', 'profile', 'about me', 'overview'],
            'experience': ['experience', 'work experience', 'professional experience', 'employment', 'career history', 'work', 'professional'],
            'education': ['education', 'academic background', 'academic qualifications'],
            'skills': ['skills', 'technical skills', 'core competencies', 'competencies'],
            'projects': ['projects', 'personal projects', 'portfolio', 'project'],
            'certifications': ['certifications', 'certificates', 'credentials', 'licenses'],
            'languages': ['languages', 'language skills'],
            'awards': ['awards', 'honors', 'achievements', 'recognition']
        }
        
        # Check for exact section matches first (more reliable)
        for section, exact_keywords in section_exact_matches.items():
            for keyword in exact_keywords:
                if line_lower == keyword or (is_caps and line_lower == keyword.upper()):
                    return section
        
        # Check for partial matches with better pattern matching
        if (is_caps and len(line.split()) <= 4) or len(line.split()) <= 2:
            for section, keywords in self.section_patterns.items():
                for keyword in keywords:
                    if keyword in line_lower:
                        # Additional validation to reduce false positives
                        if section == 'education':
                            # Don't match degree names or GPAs as education headers
                            if any(term in line_lower for term in ['gpa', 'bachelor', 'master', 'degree', 'university of', 'class', 'semester']):
                                continue
                        return section
        
        # Special handling for common patterns that might not be in caps
        special_patterns = {
            'skills': [r'^technical skills', r'^programming languages', r'^tools', r'^frameworks'],
            'education': [r'^education', r'^academic'],
            'projects': [r'^projects', r'^personal projects'],
            'experience': [r'^work experience', r'^professional experience'],
            'certifications': [r'^certifications', r'^certificates'],
            'languages': [r'^languages'],
            'awards': [r'^awards', r'^honors']
        }
        
        for section, patterns in special_patterns.items():
            for pattern in patterns:
                if re.match(pattern, line_lower):
                    return section
        
        return None

    def analyze_section_order(self, sections, positions):
        """Analyze if section order is logical"""
        issues = []
        recommendations = []
        
        # Get positions of detected sections in logical order
        logical_positions = {}
        for section in sections:
            if section in self.logical_order:
                logical_positions[section] = self.logical_order.index(section)
        
        # Check if sections appear in logical order
        actual_order = sorted(logical_positions.items(), key=lambda x: positions.get(x[0], 0))
        expected_order = sorted(logical_positions.items(), key=lambda x: x[1])
        
        if actual_order != expected_order:
            issues.append("Section order is not optimal")
            recommendations.append("Consider reordering sections: Summary → Experience → Education → Skills → Optional sections")
        
        return {
            'issues': issues,
            'recommendations': recommendations,
            'is_logical': len(issues) == 0
        }

    def analyze_readability(self, text):
        """Analyze readability and sentence complexity"""
        try:
            flesch_score = flesch_reading_ease(text)
            grade_level = flesch_kincaid_grade(text)
        except:
            flesch_score = 50  # Default moderate score
            grade_level = 10
        
        # Analyze sentence lengths
        sentences = nltk.sent_tokenize(text)
        sentence_lengths = [len(sentence.split()) for sentence in sentences]
        
        avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0
        long_sentences = [s for s in sentences if len(s.split()) > 25]
        
        # Analyze bullet points
        bullet_pattern = r'[•·▪▫‣⁃]\s*(.+)'
        bullets = re.findall(bullet_pattern, text)
        bullet_lengths = [len(bullet.split()) for bullet in bullets]
        avg_bullet_length = sum(bullet_lengths) / len(bullet_lengths) if bullet_lengths else 0
        
        return {
            'flesch_score': flesch_score,
            'grade_level': grade_level,
            'avg_sentence_length': avg_sentence_length,
            'long_sentences_count': len(long_sentences),
            'avg_bullet_length': avg_bullet_length,
            'readability_grade': self.get_readability_grade(flesch_score),
            'recommendations': self.get_readability_recommendations(flesch_score, avg_sentence_length, len(long_sentences))
        }

    def get_readability_grade(self, score):
        """Convert Flesch score to grade"""
        if score >= 90: return "Very Easy"
        elif score >= 80: return "Easy"
        elif score >= 70: return "Fairly Easy"
        elif score >= 60: return "Standard"
        elif score >= 50: return "Fairly Difficult"
        elif score >= 30: return "Difficult"
        else: return "Very Difficult"

    def get_readability_recommendations(self, score, avg_length, long_count):
        """Generate readability recommendations"""
        recommendations = []
        
        if score < 60:
            recommendations.append("Simplify sentence structure for better readability")
        
        if avg_length > 20:
            recommendations.append("Reduce average sentence length (aim for 15-20 words)")
        
        if long_count > 5:
            recommendations.append(f"Break down {long_count} overly long sentences")
        
        return recommendations

    def analyze_writing_quality(self, text):
        """Analyze grammar, spelling, and professional tone"""
        issues = []
        
        # Check for informal words
        text_lower = text.lower()
        informal_found = [word for word in self.informal_words if word in text_lower]
        
        # Check for vague phrases
        vague_found = [phrase for phrase in self.vague_phrases if phrase in text_lower]
        
        # Check for passive voice patterns
        passive_patterns = [r'\b(was|were|is|are|been|being)\s+\w+ed\b', r'\b(was|were|is|are)\s+\w+en\b']
        passive_count = sum(len(re.findall(pattern, text, re.IGNORECASE)) for pattern in passive_patterns)
        
        # Check for pronoun usage
        pronoun_pattern = r'\b(I|me|my|we|our|us)\b'
        pronoun_count = len(re.findall(pronoun_pattern, text, re.IGNORECASE))
        
        return {
            'informal_words': informal_found,
            'vague_phrases': vague_found,
            'passive_voice_count': passive_count,
            'pronoun_count': pronoun_count,
            'professionalism_score': self.calculate_professionalism_score(informal_found, vague_found, passive_count, pronoun_count)
        }

    def calculate_professionalism_score(self, informal, vague, passive, pronouns):
        """Calculate professionalism score out of 100"""
        score = 100
        
        # Deduct for issues
        score -= len(informal) * 5  # 5 points per informal word
        score -= len(vague) * 3     # 3 points per vague phrase
        score -= min(passive * 2, 20)  # Up to 20 points for passive voice
        score -= min(pronouns * 1, 15)  # Up to 15 points for pronouns
        
        return max(score, 0)

    def analyze_action_verbs(self, text):
        """Enhanced action verb analysis with categorization and impact scoring"""
        # Extract bullet points with multiple patterns
        bullet_patterns = [
            r'[•·▪▫‣⁃]\s*(.+)',  # Standard bullets
            r'^[\s]*[\-\*]\s+(.+)',  # Dash and asterisk bullets
            r'^\s*\d+\.\s+(.+)',  # Numbered lists
            r'^\s*[➤►▶]\s*(.+)'  # Arrow bullets
        ]
        
        bullets = []
        for pattern in bullet_patterns:
            bullets.extend(re.findall(pattern, text, re.MULTILINE))
        
        # Remove duplicates while preserving order
        seen = set()
        unique_bullets = []
        for bullet in bullets:
            bullet_clean = bullet.strip()
            if bullet_clean and bullet_clean not in seen:
                seen.add(bullet_clean)
                unique_bullets.append(bullet_clean)
        bullets = unique_bullets
        
        strong_verb_bullets = []
        weak_verb_bullets = []
        no_verb_bullets = []
        verb_categories_used = {}
        
        # Flatten all strong verbs for quick lookup
        all_strong_verbs = []
        for category, verbs in self.strong_verbs.items():
            all_strong_verbs.extend(verbs)
            verb_categories_used[category] = 0
        
        for bullet in bullets:
            words = bullet.strip().split()
            if not words:
                no_verb_bullets.append(bullet)
                continue
                
            first_word = words[0].lower()
            # Also check first two words for phrases like "responsible for"
            first_two = ' '.join(words[:2]).lower() if len(words) > 1 else first_word
            
            # Check for strong verbs
            if first_word in all_strong_verbs:
                strong_verb_bullets.append({
                    'text': bullet,
                    'verb': first_word,
                    'category': self.get_verb_category(first_word),
                    'impact_score': self.calculate_verb_impact(bullet)
                })
                # Track category usage
                category = self.get_verb_category(first_word)
                if category:
                    verb_categories_used[category] += 1
            # Check for weak verbs and phrases
            elif first_word in self.weak_verbs or first_two in ['responsible for', 'worked on', 'helped with']:
                weak_verb_bullets.append({
                    'text': bullet,
                    'verb': first_two if first_two in ['responsible for', 'worked on', 'helped with'] else first_word,
                    'suggestions': self.get_strong_verb_suggestions(first_word)
                })
            else:
                no_verb_bullets.append({
                    'text': bullet,
                    'suggestions': ['Start with a strong action verb like: Led, Developed, Implemented, Created']
                })
        
        total_bullets = len(bullets)
        strong_count = len(strong_verb_bullets)
        weak_count = len(weak_verb_bullets)
        no_verb_count = len(no_verb_bullets)
        
        strong_percentage = (strong_count / max(total_bullets, 1)) * 100
        weak_percentage = (weak_count / max(total_bullets, 1)) * 100
        
        # Calculate diversity score (how many different verb categories used)
        categories_used_count = sum(1 for count in verb_categories_used.values() if count > 0)
        diversity_score = (categories_used_count / len(self.strong_verbs)) * 100
        
        # Calculate overall action verb score
        action_verb_score = self.calculate_action_verb_score(strong_percentage, weak_percentage, diversity_score, total_bullets)
        
        return {
            'total_bullets': total_bullets,
            'strong_verb_count': strong_count,
            'weak_verb_count': weak_count,
            'no_verb_count': no_verb_count,
            'strong_percentage': strong_percentage,
            'weak_percentage': weak_percentage,
            'diversity_score': diversity_score,
            'categories_used': verb_categories_used,
            'action_verb_score': action_verb_score,
            'strong_verb_bullets': strong_verb_bullets,
            'weak_verb_bullets': weak_verb_bullets,
            'no_verb_bullets': no_verb_bullets,
            'recommendations': self.generate_verb_recommendations(weak_verb_bullets, no_verb_bullets, verb_categories_used)
        }
    
    def get_verb_category(self, verb):
        """Get the category of a strong verb"""
        for category, verbs in self.strong_verbs.items():
            if verb in verbs:
                return category
        return None
    
    def calculate_verb_impact(self, bullet_text):
        """Calculate impact score for a bullet point with strong verb"""
        score = 70  # Base score for having a strong verb
        
        # Check for quantification
        if re.search(r'\d+[%$KMB]?', bullet_text):
            score += 20
        
        # Check for specific metrics
        if re.search(r'(?:increased|improved|reduced|saved|generated).*?\d+', bullet_text, re.IGNORECASE):
            score += 10
        
        return min(score, 100)
    
    def calculate_action_verb_score(self, strong_pct, weak_pct, diversity_score, bullet_count):
        """Calculate overall action verb score"""
        if bullet_count == 0:
            return 0
        
        # Base score from strong verb percentage
        base_score = strong_pct * 0.8  # Max 80 points for 100% strong verbs
        
        # Bonus for diversity (using different verb categories)
        diversity_bonus = diversity_score * 0.15  # Max 15 points for full diversity
        
        # Penalty for weak verbs
        weak_penalty = weak_pct * 0.3  # Deduct up to 30 points for all weak verbs
        
        # Bonus for having sufficient bullet points
        quantity_bonus = min(bullet_count / 8, 1) * 5  # Max 5 points for 8+ bullets
        
        final_score = base_score + diversity_bonus + quantity_bonus - weak_penalty
        return max(min(final_score, 100), 0)
    
    def get_strong_verb_suggestions(self, weak_verb):
        """Get strong verb suggestions for weak verbs"""
        suggestions = {
            'responsible': ['Led', 'Managed', 'Directed', 'Oversaw', 'Supervised'],
            'worked': ['Collaborated', 'Developed', 'Implemented', 'Executed', 'Delivered'],
            'helped': ['Assisted', 'Facilitated', 'Enabled', 'Supported', 'Guided'],
            'handled': ['Managed', 'Processed', 'Resolved', 'Coordinated', 'Administered'],
            'participated': ['Contributed', 'Collaborated', 'Engaged', 'Partnered', 'Supported'],
            'involved': ['Engaged', 'Participated', 'Contributed', 'Collaborated', 'Led'],
            'dealt': ['Managed', 'Resolved', 'Addressed', 'Handled', 'Processed']
        }
        return suggestions.get(weak_verb, ['Led', 'Developed', 'Implemented', 'Created', 'Managed'])

    def generate_verb_recommendations(self, weak_bullets, no_verb_bullets, categories_used):
        """Generate comprehensive recommendations for improving action verbs"""
        recommendations = []
        
        # Address weak verbs
        if weak_bullets:
            recommendations.append(f"Replace {len(weak_bullets)} weak verbs with strong action verbs")
            # Show specific examples from weak bullets
            for weak_bullet in weak_bullets[:2]:  # Show first 2 examples
                verb = weak_bullet['verb']
                suggestions = weak_bullet['suggestions'][:3]  # First 3 suggestions
                recommendations.append(f"Replace '{verb}' with: {', '.join(suggestions)}")
        
        # Address missing verbs
        if no_verb_bullets:
            recommendations.append(f"Add strong action verbs to {len(no_verb_bullets)} bullet points")
            recommendations.append("Start each bullet with verbs like: Led, Developed, Implemented, Created, Managed")
        
        # Address verb diversity
        unused_categories = [cat for cat, count in categories_used.items() if count == 0]
        if len(unused_categories) > 2:
            recommendations.append(f"Use more diverse action verbs. Consider adding: {', '.join(unused_categories[:3])}")
            
            # Suggest specific verbs for unused categories
            category_examples = {
                'leadership': ['Led', 'Managed', 'Directed', 'Supervised'],
                'achievement': ['Achieved', 'Exceeded', 'Delivered', 'Accomplished'],
                'development': ['Developed', 'Created', 'Built', 'Designed'],
                'improvement': ['Improved', 'Enhanced', 'Optimized', 'Streamlined'],
                'analysis': ['Analyzed', 'Evaluated', 'Researched', 'Investigated']
            }
            
            for category in unused_categories[:2]:  # Show examples for first 2 unused categories
                if category in category_examples:
                    examples = category_examples[category][:3]
                    recommendations.append(f"{category.title()} verbs: {', '.join(examples)}")
        
        # Positive feedback for good verb usage
        if not weak_bullets and not no_verb_bullets and len(unused_categories) <= 1:
            recommendations.append("Excellent use of strong, diverse action verbs!")
            recommendations.append("Your resume demonstrates varied leadership and technical capabilities")
        
        return recommendations

    def analyze_quantification(self, text):
        """Analyze quantifiable achievements and metrics"""
        # Patterns for numbers and metrics
        number_patterns = [
            r'\d+%',  # Percentages
            r'\$[\d,]+',  # Dollar amounts
            r'\d+\s*(million|thousand|k|m)\b',  # Large numbers
            r'\d+\s*(hours?|days?|weeks?|months?|years?)\b',  # Time
            r'\d+\s*(people|users|customers|clients|projects)\b',  # Scale
            r'\b(increased|decreased|improved|reduced|saved|generated)\s+.*?\d+',  # Impact verbs with numbers
        ]
        
        bullets = re.findall(r'[•·▪▫‣⁃]\s*(.+)', text)
        quantified_bullets = []
        
        for bullet in bullets:
            if any(re.search(pattern, bullet, re.IGNORECASE) for pattern in number_patterns):
                quantified_bullets.append(bullet)
        
        total_bullets = len(bullets)
        quantified_count = len(quantified_bullets)
        quantification_percentage = (quantified_count / total_bullets * 100) if total_bullets > 0 else 0
        
        return {
            'total_bullets': total_bullets,
            'quantified_count': quantified_count,
            'quantification_percentage': quantification_percentage,
            'quantified_examples': quantified_bullets[:3],  # Show first 3 examples
            'meets_threshold': quantification_percentage >= 30,
            'recommendations': self.get_quantification_recommendations(quantification_percentage)
        }

    def get_quantification_recommendations(self, percentage):
        """Generate quantification recommendations"""
        recommendations = []
        
        if percentage < 30:
            recommendations.append(f"Add more quantifiable metrics (current: {percentage:.1f}%, target: 30%+)")
            recommendations.append("Include percentages, dollar amounts, team sizes, timeframes")
            recommendations.append("Example: 'Improved system performance by 45%', 'Managed team of 12'")
        
        return recommendations

    def analyze_skills(self, text):
        """Analyze and categorize skills"""
        # Define skill categories
        technical_skills_patterns = [
            'python', 'java', 'javascript', 'c++', 'sql', 'html', 'css', 'react', 'angular',
            'docker', 'kubernetes', 'aws', 'azure', 'git', 'linux', 'machine learning'
        ]
        
        soft_skills_patterns = [
            'leadership', 'communication', 'teamwork', 'problem solving', 'analytical',
            'creative', 'adaptable', 'organized', 'detail-oriented'
        ]
        
        # Extract skills from text
        text_lower = text.lower()
        technical_found = [skill for skill in technical_skills_patterns if skill in text_lower]
        soft_found = [skill for skill in soft_skills_patterns if skill in text_lower]
        
        return {
            'technical_skills': technical_found,
            'soft_skills': soft_found,
            'total_skills': len(technical_found) + len(soft_found),
            'skill_balance': self.analyze_skill_balance(technical_found, soft_found)
        }

    def analyze_skill_balance(self, technical, soft):
        """Analyze balance between technical and soft skills"""
        total = len(technical) + len(soft)
        if total == 0:
            return {'balance': 'no_skills', 'recommendation': 'Add both technical and soft skills'}
        
        tech_ratio = len(technical) / total
        
        if tech_ratio > 0.8:
            return {'balance': 'tech_heavy', 'recommendation': 'Add more soft skills for balance'}
        elif tech_ratio < 0.3:
            return {'balance': 'soft_heavy', 'recommendation': 'Add more technical skills'}
        else:
            return {'balance': 'balanced', 'recommendation': 'Good balance of skills'}

    def analyze_chronology(self, text):
        """Analyze chronological consistency in dates"""
        # Extract date patterns
        date_patterns = [
            r'(\d{4})\s*[-–—]\s*(\d{4})',  # 2020-2023
            r'(\d{4})\s*[-–—]\s*(present|current)',  # 2020-present
            r'(\w+)\s+(\d{4})\s*[-–—]\s*(\w+)\s+(\d{4})',  # Jan 2020 - Dec 2023
        ]
        
        dates_found = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            dates_found.extend(matches)
        
        # Analyze for gaps, overlaps, and logical progression
        issues = []
        if len(dates_found) > 1:
            # Basic chronology check (simplified)
            issues = self.detect_chronology_issues(dates_found)
        
        return {
            'dates_found': len(dates_found),
            'chronological_order_issues': issues,
            'has_gaps': 'gaps' in str(issues),
            'has_overlaps': 'overlap' in str(issues)
        }

    def detect_chronology_issues(self, dates):
        """Detect chronological issues (simplified implementation)"""
        issues = []
        
        # This is a simplified version - in practice, you'd need more sophisticated date parsing
        try:
            years = []
            for date_match in dates:
                if len(date_match) >= 2:
                    start_year = int(date_match[0]) if date_match[0].isdigit() else 2020
                    years.append(start_year)
            
            if years:
                years.sort()
                for i in range(1, len(years)):
                    gap = years[i] - years[i-1]
                    if gap > 2:
                        issues.append(f"Potential gap between {years[i-1]} and {years[i]}")
        
        except (ValueError, IndexError):
            pass
        
        return issues

    def extract_entities(self, text):
        """Extract named entities using spaCy NER"""
        entities = {
            'organizations': [],
            'locations': [],
            'dates': [],
            'skills': [],
            'degrees': []
        }
        
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ == "ORG":
                    entities['organizations'].append(ent.text)
                elif ent.label_ in ["GPE", "LOC"]:
                    entities['locations'].append(ent.text)
                elif ent.label_ == "DATE":
                    entities['dates'].append(ent.text)
        
        return entities

    def analyze_tone(self, text):
        """Analyze tone and professionalism"""
        # Check for emotional language
        emotional_words = ['amazing', 'incredible', 'fantastic', 'terrible', 'awful', 'hate', 'love']
        emotional_found = [word for word in emotional_words if word in text.lower()]
        
        # Check confidence indicators
        confidence_words = ['achieved', 'accomplished', 'delivered', 'exceeded', 'successful']
        confidence_found = [word for word in confidence_words if word in text.lower()]
        
        return {
            'emotional_language': emotional_found,
            'confidence_indicators': confidence_found,
            'tone_score': self.calculate_tone_score(emotional_found, confidence_found)
        }

    def calculate_tone_score(self, emotional, confidence):
        """Calculate tone appropriateness score"""
        score = 50  # Base score
        
        # Add points for confidence
        score += len(confidence) * 5
        
        # Subtract points for emotional language
        score -= len(emotional) * 10
        
        return max(min(score, 100), 0)

    def analyze_formatting(self, text):
        """Analyze formatting consistency"""
        lines = text.split('\n')
        
        # Check bullet consistency
        bullet_styles = []
        for line in lines:
            if re.match(r'^\s*[•·▪▫‣⁃]', line):
                bullet_styles.append(line.strip()[0])
        
        bullet_consistency = len(set(bullet_styles)) <= 1 if bullet_styles else True
        
        # Check date formats
        date_formats = re.findall(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\w+ \d{4}|\d{4}', text)
        date_consistency = len(set([self.normalize_date_format(d) for d in date_formats])) <= 2
        
        return {
            'bullet_consistency': bullet_consistency,
            'date_consistency': date_consistency,
            'formatting_score': self.calculate_formatting_score(bullet_consistency, date_consistency)
        }

    def normalize_date_format(self, date_str):
        """Normalize date format for consistency check"""
        if re.match(r'\d{4}', date_str):
            return 'year_only'
        elif re.match(r'\w+ \d{4}', date_str):
            return 'month_year'
        else:
            return 'full_date'

    def calculate_formatting_score(self, bullet_consistency, date_consistency):
        """Calculate formatting consistency score"""
        score = 100
        
        if not bullet_consistency:
            score -= 25
        
        if not date_consistency:
            score -= 25
        
        return score

    def analyze_quantification_enhanced(self, text):
        """Enhanced quantification analysis with detailed impact measurement"""
        bullets = re.findall(r'[•·▪▫‣⁃]\s*(.+)', text)
        
        quantified_bullets = []
        vague_bullets = []
        impact_examples = []
        
        for bullet in bullets:
            has_metrics = False
            found_patterns = []
            
            # Check for each type of impact pattern
            for pattern_type, pattern in self.impact_patterns.items():
                if re.search(pattern, bullet, re.IGNORECASE):
                    has_metrics = True
                    found_patterns.append(pattern_type)
            
            if has_metrics:
                quantified_bullets.append({
                    'text': bullet,
                    'patterns': found_patterns
                })
                impact_examples.append(bullet)
            else:
                # Check if bullet is task-focused without results
                task_indicators = ['managed', 'handled', 'worked on', 'responsible for', 'involved in']
                if any(indicator in bullet.lower() for indicator in task_indicators):
                    vague_bullets.append(bullet)
        
        total_bullets = len(bullets)
        quantification_percentage = (len(quantified_bullets) / total_bullets * 100) if total_bullets > 0 else 0
        
        # Generate specific improvement suggestions
        suggestions = []
        if quantification_percentage < 30:
            suggestions.extend([
                "Add specific numbers to show your impact",
                "Include percentages for improvements or growth",
                "Mention team sizes you managed or led",
                "Quantify customer interactions or project scope"
            ])
        
        # Provide examples for vague bullets
        improvement_examples = []
        for vague in vague_bullets[:3]:  # Show first 3
            if 'managed' in vague.lower():
                improvement_examples.append(f"'{vague}' → Add team size: 'Managed team of 8 developers'")
            elif 'improved' in vague.lower():
                improvement_examples.append(f"'{vague}' → Add percentage: 'Improved system performance by 25%'")
            else:
                improvement_examples.append(f"'{vague}' → Add metrics: Include numbers, percentages, or scope")
        
        return {
            'total_bullets': total_bullets,
            'quantified_count': len(quantified_bullets),
            'quantification_percentage': quantification_percentage,
            'vague_bullets': vague_bullets[:5],  # Show first 5
            'quantified_examples': impact_examples[:3],  # Show first 3
            'improvement_suggestions': improvement_examples,
            'meets_threshold': quantification_percentage >= 30,
            'recommendations': suggestions,
            'pattern_analysis': self.analyze_impact_patterns(quantified_bullets)
        }

    def analyze_impact_patterns(self, quantified_bullets):
        """Analyze what types of impact patterns are being used"""
        pattern_counts = {}
        for bullet_data in quantified_bullets:
            for pattern in bullet_data['patterns']:
                pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        
        return {
            'pattern_distribution': pattern_counts,
            'most_used': max(pattern_counts.items(), key=lambda x: x[1]) if pattern_counts else None,
            'missing_patterns': [p for p in self.impact_patterns.keys() if p not in pattern_counts]
        }

    def analyze_summary_quality(self, text):
        """Analyze professional summary/objective quality"""
        # Split text into non-empty, stripped lines
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Find summary section by looking for an explicit header first
        summary_start = -1  # Index where summary starts
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            # Look for common summary headers
            if any(keyword in line_lower for keyword in ['summary', 'objective', 'profile', 'about']):
                # Treat very short lines as section headers
                if len(line.split()) <= 5:
                    summary_start = i
                    break
        
        summary_lines = []  # Lines that will form the summary block
        
        if summary_start == -1:
            # Fallback: infer summary from top-of-resume content when no header exists
            # Skip the very first 1-2 lines (usually name/title) and look for 1-3 non-section lines
            start_index = 1 if len(lines) > 1 else 0
            end_index = min(start_index + 6, len(lines))  # Look at a small window near the top
            candidate_block = []
            
            for i in range(start_index, end_index):
                line = lines[i]
                # Stop if we hit something that looks like a section header
                if self.identify_section(line):
                    break
                candidate_block.append(line)
                # Limit to 3 lines of inferred summary
                if len(candidate_block) >= 3:
                    break
            
            inferred_text = ' '.join(candidate_block)
            word_count = len(inferred_text.split())
            
            # Treat as summary only if it has a reasonable length
            if 15 <= word_count <= 80:
                summary_lines = candidate_block
            else:
                # No suitable inferred summary found
                return {
                    'has_summary': False,
                    'quality_score': 0,
                    'issues': ['No professional summary found'],
                    'recommendations': [
                        'Add a professional summary (2-4 lines)',
                        'Include relevant skills and experience',
                        'Tailor summary to target job role',
                        'Avoid generic phrases and buzzwords'
                    ]
                }
        else:
            # Explicit header found: extract 2–6 lines after header as summary content
            for i in range(summary_start + 1, min(summary_start + 7, len(lines))):
                if i < len(lines) and lines[i] and not self.identify_section(lines[i]):
                    summary_lines.append(lines[i])
                else:
                    break
        
        # Join all summary lines into a single text block for analysis
        summary_text = ' '.join(summary_lines)
        
        # Analyze summary quality
        issues = []  # Collect specific issues detected
        quality_score = 100  # Start from a perfect score and subtract for issues
        
        # Check length (should be 2-4 lines, 50-150 words)
        word_count = len(summary_text.split())
        if word_count < 20:
            issues.append('Summary too short (should be 20-100 words)')
            quality_score -= 20
        elif word_count > 100:
            issues.append('Summary too long (should be 20-100 words)')
            quality_score -= 15
        
        # Check for generic phrases
        generic_found = []
        for phrase in self.generic_summary_phrases:
            if phrase in summary_text.lower():
                generic_found.append(phrase)
        
        if generic_found:
            issues.append(f'Contains generic phrases: {", ".join(generic_found)}')
            quality_score -= len(generic_found) * 10
        
        # Check for specific skills/experience mentions
        has_specific_skills = bool(re.search(r'\b(python|java|sql|marketing|sales|engineering|management)\b', summary_text, re.IGNORECASE))
        if not has_specific_skills:
            issues.append('Summary lacks specific skills or technical expertise')
            quality_score -= 15
        
        # Check for quantifiable achievements in summary
        has_metrics = any(re.search(pattern, summary_text) for pattern in self.impact_patterns.values())
        if not has_metrics:
            issues.append('Consider adding quantifiable achievements in summary')
            quality_score -= 10
        
        return {
            'has_summary': True,
            'summary_text': summary_text,
            'word_count': word_count,
            'quality_score': max(quality_score, 0),
            'issues': issues,
            'generic_phrases_found': generic_found,
            'has_specific_skills': has_specific_skills,
            'has_metrics': has_metrics,
            'recommendations': self.generate_summary_recommendations(issues, summary_text)
        }

    def generate_summary_recommendations(self, issues, summary_text):
        """Generate specific recommendations for summary improvement"""
        recommendations = []
        
        if 'too short' in str(issues):
            recommendations.append('Expand summary to 2-3 sentences with more detail about your expertise')
        if 'too long' in str(issues):
            recommendations.append('Condense summary to 2-3 impactful sentences')
        if 'generic phrases' in str(issues):
            recommendations.append('Replace buzzwords with specific skills and achievements')
        if 'lacks specific skills' in str(issues):
            recommendations.append('Include relevant technical skills and industry expertise')
        if 'quantifiable achievements' in str(issues):
            recommendations.append('Add numbers to demonstrate your impact (e.g., "5+ years experience")')
        
        if not recommendations:
            recommendations.append('Good summary! Consider tailoring it to each specific job application')
        
        return recommendations

    def analyze_buzzwords(self, text):
        """Detect and analyze buzzword usage with severity levels"""
        text_lower = text.lower()
        found_buzzwords = []
        total_penalty = 0
        
        # Check for direct buzzword matches
        for severity, buzzword_list in self.buzzwords.items():
            for buzzword in buzzword_list:
                if buzzword.lower() in text_lower:
                    count = text_lower.count(buzzword.lower())
                    if count > 0:
                        penalty = self.get_severity_penalty(severity) * count
                        total_penalty += penalty
                        found_buzzwords.append({
                            'word': buzzword,
                            'count': count,
                            'severity': severity,
                            'penalty': penalty,
                            'suggestions': self.get_buzzword_alternatives(buzzword)
                        })
        
        # Check for pattern-based buzzwords
        for pattern in self.buzzword_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                total_penalty += 8  # Medium penalty for pattern matches
                found_buzzwords.append({
                    'word': match if isinstance(match, str) else ' '.join(match),
                    'count': 1,
                    'severity': 'pattern',
                    'penalty': 8,
                    'suggestions': ['Replace with specific achievements and metrics']
                })
        
        # Calculate score (0-100, with penalties)
        buzzword_score = max(100 - total_penalty, 0)
        
        return {
            'buzzwords_found': found_buzzwords,
            'total_buzzwords': len(found_buzzwords),
            'total_penalty': total_penalty,
            'buzzword_score': buzzword_score,
            'severity': self.get_buzzword_severity(len(found_buzzwords)),
            'recommendations': self.generate_buzzword_recommendations(found_buzzwords)
        }
    
    def get_severity_penalty(self, severity):
        """Get penalty points based on severity level"""
        penalties = {
            'critical': 15,  # Major penalty
            'high': 10,      # High penalty
            'medium': 6,     # Medium penalty
            'low': 3,        # Light penalty
            'pattern': 8     # Pattern-based penalty
        }
        return penalties.get(severity, 5)

    def get_buzzword_alternatives(self, buzzword):
        """Provide specific alternatives for common buzzwords with actionable suggestions"""
        alternatives = {
            'motivated': ['achieved 150% of sales quota', 'completed 5 certifications in 6 months', 'exceeded performance targets by 25%'],
            'results-driven': ['increased sales by 30%', 'reduced costs by $50K annually', 'delivered 12 projects on time'],
            'team player': ['collaborated with 8-person cross-functional team', 'led joint initiatives with marketing team'],
            'hard worker': ['managed 15 projects simultaneously', 'maintained 99.5% uptime for critical systems'],
            'detail-oriented': ['identified 200+ code bugs', 'improved data accuracy by 40%', 'achieved 99.9% error-free processing'],
            'fast learner': ['mastered Python in 3 weeks', 'completed AWS certification in 2 months'],
            'problem solver': ['resolved 50+ customer escalations', 'debugged critical production issues in <2 hours'],
            'problem solving': ['resolved 50+ customer escalations', 'debugged critical production issues in <2 hours'],
            'innovative': ['developed automated testing framework', 'created solution that saved $100K annually'],
            'dynamic': ['adapted to 3 different project methodologies', 'successfully transitioned team to remote work'],
            'adaptability': ['successfully worked across 4 different tech stacks', 'managed projects in 3 different time zones'],
            'adaptable': ['successfully worked across 4 different tech stacks', 'managed projects in 3 different time zones'],
            'strategic': ['developed 3-year product roadmap', 'identified market opportunity worth $2M'],
            'leverage': ['used advanced analytics to increase conversion by 15%', 'applied machine learning to reduce processing time by 50%'],
            'utilize': ['used advanced analytics to increase conversion by 15%', 'applied machine learning to reduce processing time by 50%'],
            'hands-on': ['directly coded 80% of the application', 'personally trained 12 new team members'],
            'guru': ['expert in Python with 5 years experience', '10+ years experience in database optimization'],
            'ninja': ['expert in Python with 5 years experience', 'specialized in performance optimization'],
            'rockstar': ['top performer (achieved 150% of quota)', 'recognized as employee of the month 3 times']
        }
        return alternatives.get(buzzword.lower(), ['Replace with specific achievements and metrics'])

    def get_buzzword_severity(self, count):
        """Determine severity of buzzword usage"""
        if count == 0:
            return 'excellent'
        elif count <= 2:
            return 'good'
        elif count <= 5:
            return 'moderate'
        else:
            return 'high'

    def generate_buzzword_recommendations(self, found_buzzwords):
        """Generate recommendations for reducing buzzword usage"""
        if not found_buzzwords:
            return ['Great! No generic buzzwords detected']
        
        recommendations = [
            f'Replace "{bw["word"]}" with specific achievements or metrics'
            for bw in found_buzzwords[:3]  # Show first 3
        ]
        
        recommendations.append('Use action verbs with quantifiable results instead of generic descriptors')
        
        if len(found_buzzwords) > 5:
            recommendations.append('Consider rewriting sections with too many generic terms')
        
        return recommendations

    def analyze_skills_enhanced(self, text):
        """Enhanced skills analysis with categorization and relevance checking"""
        # Enhanced skill patterns with more comprehensive lists
        technical_skills = {
            'programming': ['python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift'],
            'web_technologies': ['html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask'],
            'databases': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sqlite'],
            'cloud_platforms': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform'],
            'tools': ['git', 'jenkins', 'jira', 'confluence', 'slack', 'trello', 'figma', 'photoshop']
        }
        
        soft_skills = [
            'leadership', 'communication', 'teamwork', 'problem solving', 'analytical thinking',
            'project management', 'time management', 'adaptability', 'creativity', 'negotiation'
        ]
        
        # Extract skills from text
        text_lower = text.lower()
        found_skills = {
            'programming': [],
            'web_technologies': [],
            'databases': [],
            'cloud_platforms': [],
            'tools': [],
            'soft_skills': []
        }
        
        # Check technical skills by category
        for category, skills_list in technical_skills.items():
            for skill in skills_list:
                if skill in text_lower:
                    found_skills[category].append(skill)
        
        # Check soft skills
        for skill in soft_skills:
            if skill in text_lower:
                found_skills['soft_skills'].append(skill)
        
        # Detect skill section quality
        skills_section_analysis = self.analyze_skills_section_format(text)
        
        # Check for irrelevant or outdated skills
        outdated_skills = ['internet explorer', 'flash', 'silverlight', 'windows 95', 'dos']
        outdated_found = [skill for skill in outdated_skills if skill in text_lower]
        
        return {
            'skills_by_category': found_skills,
            'total_technical_skills': sum(len(skills) for category, skills in found_skills.items() if category != 'soft_skills'),
            'total_soft_skills': len(found_skills['soft_skills']),
            'skills_section_quality': skills_section_analysis,
            'outdated_skills': outdated_found,
            'skill_balance': self.analyze_enhanced_skill_balance(found_skills),
            'recommendations': self.generate_enhanced_skills_recommendations(found_skills, outdated_found)
        }

    def analyze_skills_section_format(self, text):
        """Analyze how skills are formatted and organized"""
        lines = text.split('\n')
        skills_section_found = False
        skills_lines = []
        
        for i, line in enumerate(lines):
            if 'skills' in line.lower() and len(line.split()) <= 3:
                skills_section_found = True
                # Collect next few lines as skills content
                for j in range(i + 1, min(i + 10, len(lines))):
                    if lines[j].strip() and not self.identify_section(lines[j]):
                        skills_lines.append(lines[j].strip())
                    else:
                        break
                break
        
        if not skills_section_found:
            return {
                'has_dedicated_section': False,
                'is_well_organized': False,
                'issues': ['No dedicated skills section found']
            }
        
        skills_text = ' '.join(skills_lines)
        
        # Check organization
        has_categories = any(indicator in skills_text.lower() for indicator in 
                           ['programming', 'technical', 'languages', 'frameworks', 'tools'])
        
        # Check for proper formatting (commas, bullets, etc.)
        well_formatted = ',' in skills_text or '•' in skills_text or '|' in skills_text
        
        return {
            'has_dedicated_section': True,
            'is_well_organized': has_categories,
            'is_well_formatted': well_formatted,
            'skills_content': skills_text,
            'issues': self.identify_skills_formatting_issues(skills_text, has_categories, well_formatted)
        }

    def identify_skills_formatting_issues(self, skills_text, has_categories, well_formatted):
        """Identify specific formatting issues in skills section"""
        issues = []
        
        if not has_categories:
            issues.append('Skills are not organized into categories (e.g., Programming, Tools, Frameworks)')
        
        if not well_formatted:
            issues.append('Skills lack clear formatting (use commas, bullets, or separators)')
        
        if len(skills_text) < 50:
            issues.append('Skills section appears too brief')
        
        return issues

    def analyze_enhanced_skill_balance(self, found_skills):
        """Enhanced analysis of skill balance"""
        total_technical = sum(len(skills) for category, skills in found_skills.items() if category != 'soft_skills')
        total_soft = len(found_skills['soft_skills'])
        total_skills = total_technical + total_soft
        
        if total_skills == 0:
            return {'balance': 'no_skills', 'recommendation': 'Add both technical and soft skills'}
        
        tech_ratio = total_technical / total_skills if total_skills > 0 else 0
        
        # More detailed balance assessment
        if total_technical == 0:
            return {'balance': 'no_technical', 'recommendation': 'Add relevant technical skills for your field'}
        elif total_soft == 0:
            return {'balance': 'no_soft', 'recommendation': 'Include important soft skills like leadership or communication'}
        elif tech_ratio > 0.85:
            return {'balance': 'tech_heavy', 'recommendation': 'Add more soft skills to show well-rounded abilities'}
        elif tech_ratio < 0.3:
            return {'balance': 'soft_heavy', 'recommendation': 'Include more technical skills relevant to your field'}
        else:
            return {'balance': 'balanced', 'recommendation': 'Good balance of technical and soft skills'}

    def generate_enhanced_skills_recommendations(self, found_skills, outdated_skills):
        """Generate detailed recommendations for skills section"""
        recommendations = []
        
        total_technical = sum(len(skills) for category, skills in found_skills.items() if category != 'soft_skills')
        
        if total_technical < 5:
            recommendations.append('Add more relevant technical skills for your field')
        
        if len(found_skills['soft_skills']) < 3:
            recommendations.append('Include important soft skills like communication, teamwork, or leadership')
        
        if outdated_skills:
            recommendations.append(f'Remove outdated skills: {", ".join(outdated_skills)}')
        
        # Category-specific recommendations
        if not found_skills['programming'] and (found_skills['web_technologies'] or found_skills['databases']):
            recommendations.append('Add programming languages that complement your other technical skills')
        
        if not found_skills['tools'] and total_technical > 0:
            recommendations.append('Include relevant development tools and software you use')
        
        recommendations.append('Organize skills into categories: Programming Languages, Frameworks, Tools, etc.')
        recommendations.append('Only include skills you can confidently discuss in an interview')
        
        return recommendations

    def analyze_chronology_enhanced(self, text):
        """Enhanced chronological analysis with detailed date checking"""
        # Extract all date ranges from text
        date_ranges = []
        date_formats = set()
        
        for pattern in self.date_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                date_info = {
                    'match_text': match.group(0),
                    'format_type': self.classify_date_format(match.group(0)),
                    'groups': match.groupdict()
                }
                date_ranges.append(date_info)
                date_formats.add(date_info['format_type'])
        
        # Special handling for no dates found
        if len(date_ranges) == 0:
            return {
                'total_date_ranges': 0,
                'date_formats_used': [],
                'format_consistency': False,
                'consistency_issues': ['No dates found on resume'],
                'missing_dates': self.check_missing_dates(text),
                'chronological_order_issues': ['Cannot verify date order - no dates detected'],
                'has_dates': False,
                'recommendations': [
                    'CRITICAL: Add dates to all work experience and education entries',
                    'Include at least the year (e.g., "2020-2023" or "Jan 2020 - Dec 2023")',
                    'Format dates consistently throughout your resume',
                    'Use format like "Jan 2020 - Present" for current positions'
                ],
                'severity': 'critical'
            }
        
        # Analyze consistency and issues
        consistency_issues = []
        format_consistency = len(date_formats) <= 2  # Allow up to 2 different formats
        
        if not format_consistency:
            consistency_issues.append(f'Multiple date formats used: {", ".join(date_formats)}')
        
        # Check for missing dates in experience/education sections
        missing_dates = self.check_missing_dates(text)
        
        # Detect chronological order issues
        order_issues = self.check_chronological_order(date_ranges)
        
        return {
            'total_date_ranges': len(date_ranges),
            'date_formats_used': list(date_formats),
            'format_consistency': format_consistency,
            'consistency_issues': consistency_issues,
            'missing_dates': missing_dates,
            'chronological_order_issues': order_issues,
            'has_dates': True,
            'recommendations': self.generate_chronology_recommendations(consistency_issues, missing_dates, order_issues),
            'severity': 'low' if format_consistency and not missing_dates and not order_issues else 'medium'
        }

    def classify_date_format(self, date_text):
        """Classify the format of a date string"""
        if re.match(r'[A-Za-z]{3}\s+\d{4}', date_text):
            return 'Month_Year'
        elif re.match(r'\d{1,2}[\/\-]\d{4}', date_text):
            return 'Numeric_Short'
        elif re.match(r'\d{4}\s*[-–—]', date_text):
            return 'Year_Range'
        else:
            return 'Other'

    def check_missing_dates(self, text):
        """Check for entries that might be missing dates"""
        lines = text.split('\n')
        missing_dates = []
        
        # Look for job titles or company names without associated dates
        job_indicators = ['engineer', 'manager', 'analyst', 'developer', 'coordinator', 'specialist', 'director']
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(indicator in line_lower for indicator in job_indicators):
                # Check if this line or nearby lines contain dates
                context_lines = lines[max(0, i-1):i+3]  # Current line + 1 before + 2 after
                context_text = ' '.join(context_lines)
                
                has_nearby_date = any(re.search(pattern, context_text) for pattern in self.date_patterns)
                
                if not has_nearby_date:
                    missing_dates.append(line.strip())
        
        return missing_dates[:3]  # Return first 3 examples

    def check_chronological_order(self, date_ranges):
        """Check if dates are in reverse chronological order (most recent first)"""
        issues = []
        
        # This is a simplified implementation
        # In practice, you'd parse dates and sort them properly
        years = []
        for date_range in date_ranges:
            if 'year' in date_range['groups']:
                try:
                    year = int(date_range['groups']['year'])
                    years.append(year)
                except (ValueError, TypeError):
                    continue
        
        if len(years) > 1:
            # Check if years are in descending order (most recent first)
            is_descending = all(years[i] >= years[i+1] for i in range(len(years)-1))
            if not is_descending:
                issues.append('Dates may not be in reverse chronological order (most recent first)')
        
        return issues

    def generate_chronology_recommendations(self, consistency_issues, missing_dates, order_issues):
        """Generate recommendations for chronology improvements"""
        recommendations = []
        
        if consistency_issues:
            recommendations.append('Use consistent date format throughout (e.g., "Jan 2022 – Dec 2024")')
        
        if missing_dates:
            recommendations.append('Add dates to all work experience and education entries')
            recommendations.append(f'Missing dates detected for: {", ".join(missing_dates[:2])}')
        
        if order_issues:
            recommendations.extend(order_issues)
            recommendations.append('List experience in reverse chronological order (most recent first)')
        
        if not recommendations:
            recommendations.append('Good chronological consistency!')
        
        return recommendations

    def analyze_date_consistency(self, text):
        """Specific analysis for date format consistency"""
        date_examples = []
        
        for pattern in self.date_patterns:
            matches = re.findall(pattern, text)
            date_examples.extend(matches[:2])  # Get first 2 examples of each pattern
        
        # Analyze format consistency
        formats_found = [self.classify_date_format(str(date)) for date in date_examples]
        unique_formats = list(set(formats_found))
        
        consistency_score = 100 if len(unique_formats) <= 1 else max(50, 100 - (len(unique_formats) * 20))
        
        return {
            'date_examples': [str(d) for d in date_examples[:5]],
            'formats_found': unique_formats,
            'consistency_score': consistency_score,
            'is_consistent': len(unique_formats) <= 1,
            'recommendations': [
                'Use consistent date format throughout resume',
                'Recommended format: "Jan 2022 – Dec 2024"',
                'Ensure all positions have start and end dates'
            ] if len(unique_formats) > 1 else ['Date formatting is consistent']
        }

    def analyze_impact_metrics(self, text):
        """Analyze the usage and variety of impact metrics"""
        bullets = re.findall(r'[•·▪▫‣⁃]\s*(.+)', text)
        
        impact_analysis = {
            'percentages': [],
            'dollar_amounts': [],
            'large_numbers': [],
            'time_metrics': [],
            'team_sizes': [],
            'customer_metrics': []
        }
        
        for bullet in bullets:
            for metric_type, pattern in self.impact_patterns.items():
                matches = re.findall(pattern, bullet, re.IGNORECASE)
                if matches:
                    if metric_type not in impact_analysis:
                        impact_analysis[metric_type] = []
                    impact_analysis[metric_type].extend(matches[:1])  # One example per bullet
        
        # Calculate impact diversity score
        metrics_used = sum(1 for metrics in impact_analysis.values() if metrics)
        diversity_score = min(100, metrics_used * 20)  # Up to 5 types * 20 points each
        
        return {
            'impact_metrics': impact_analysis,
            'metrics_diversity': metrics_used,
            'diversity_score': diversity_score,
            'strongest_metric_type': max(impact_analysis.items(), key=lambda x: len(x[1]))[0] if any(impact_analysis.values()) else None,
            'recommendations': self.generate_impact_recommendations(impact_analysis, metrics_used)
        }

    def generate_impact_recommendations(self, impact_analysis, metrics_used):
        """Generate recommendations for improving impact metrics"""
        recommendations = []
        
        if metrics_used == 0:
            recommendations.extend([
                'Add quantifiable metrics to demonstrate impact',
                'Include percentages for improvements (e.g., "increased efficiency by 25%")',
                'Mention dollar amounts for cost savings or revenue generation',
                'Specify team sizes and project scope'
            ])
        elif metrics_used < 3:
            missing_types = []
            if not impact_analysis.get('percentages'):
                missing_types.append('percentages')
            if not impact_analysis.get('dollar_amounts'):
                missing_types.append('dollar amounts')
            if not impact_analysis.get('team_sizes'):
                missing_types.append('team sizes')
            
            if missing_types:
                recommendations.append(f'Consider adding {", ".join(missing_types)} to diversify your impact metrics')
        else:
            recommendations.append('Excellent variety of quantifiable metrics!')
        
        return recommendations

    def analyze_unnecessary_sections(self, text):
        """Analyze for outdated/unnecessary resume sections"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Define outdated sections to detect
        outdated_sections = {
            'references': {
                'patterns': ['references', 'reference available', 'references upon request', 'references provided'],
                'description': 'References section is outdated - employers will ask directly if needed',
                'severity': 'medium',
                'recommendation': 'Remove references section. Employers will request references if needed during the interview process.'
            },
            'objective': {
                'patterns': ['objective', 'career objective', 'professional objective'],
                'description': 'Objective sections are considered outdated in 2025',
                'severity': 'medium', 
                'recommendation': 'Replace objective with a professional summary that highlights your skills and experience.'
            },
            'personal_info': {
                'patterns': ['date of birth', 'age:', 'marital status', 'married', 'single', 'religion', 'nationality', 'gender:', 'photo', 'picture'],
                'description': 'Personal information is unnecessary and may lead to discrimination',
                'severity': 'high',
                'recommendation': 'Remove personal information like age, marital status, religion, or photos.'
            },
            'hobbies_interests': {
                'patterns': ['hobbies', 'interests', 'personal interests', 'activities'],
                'description': 'Hobbies and interests sections are generally unnecessary unless directly relevant',
                'severity': 'low',
                'recommendation': 'Consider removing hobbies/interests unless they directly relate to the job or show leadership.'
            },
            'salary_expectations': {
                'patterns': ['salary', 'compensation', 'expected salary', 'salary range'],
                'description': 'Salary information should not be included in resumes',
                'severity': 'high',
                'recommendation': 'Remove salary information - discuss compensation during interviews.'
            }
        }
        
        found_sections = []
        passed_checks = []
        
        text_lower = text.lower()
        
        # Check each outdated section type
        for section_type, config in outdated_sections.items():
            section_found = False
            detected_patterns = []
            
            for pattern in config['patterns']:
                # Check if pattern appears as a section header (standalone line)
                for line in lines:
                    line_lower = line.lower().strip()
                    if (pattern in line_lower and 
                        len(line.split()) <= 4 and  # Likely a header
                        line_lower.replace(':', '').replace('-', '').strip() == pattern):
                        section_found = True
                        detected_patterns.append(pattern)
                        break
                
                # Also check for references in content (not just headers)
                if section_type == 'references' and 'references' in text_lower:
                    if any(ref_phrase in text_lower for ref_phrase in ['available upon request', 'provided upon request', 'furnished upon request']):
                        section_found = True
                        detected_patterns.append('references available upon request')
            
            if section_found:
                found_sections.append({
                    'type': section_type,
                    'patterns_found': detected_patterns,
                    'description': config['description'],
                    'severity': config['severity'],
                    'recommendation': config['recommendation']
                })
            else:
                # Add to passed checks for positive feedback
                if section_type in ['references', 'objective']:
                    passed_checks.append({
                        'type': section_type,
                        'description': f'Great! No {section_type} section found - this follows modern resume standards.'
                    })
        
        # Calculate overall score
        total_issues = len(found_sections)
        severity_weights = {'high': 3, 'medium': 2, 'low': 1}
        severity_score = sum(severity_weights.get(section['severity'], 1) for section in found_sections)
        
        # Score out of 100 (deduct based on issues found)
        modernization_score = max(100 - (severity_score * 10), 0)
        
        return {
            'unnecessary_sections_found': found_sections,
            'passed_checks': passed_checks,
            'total_issues': total_issues,
            'modernization_score': modernization_score,
            'has_outdated_sections': len(found_sections) > 0,
            'recommendations': self.generate_modernization_recommendations(found_sections, passed_checks),
            'summary': self.generate_modernization_summary(found_sections, passed_checks)
        }

    def generate_modernization_recommendations(self, found_sections, passed_checks):
        """Generate specific recommendations for modernizing resume"""
        recommendations = []
        
        if not found_sections:
            recommendations.append('Excellent! Your resume follows modern standards with no outdated sections.')
            return recommendations
        
        # Group by severity
        high_severity = [s for s in found_sections if s['severity'] == 'high']
        medium_severity = [s for s in found_sections if s['severity'] == 'medium']
        low_severity = [s for s in found_sections if s['severity'] == 'low']
        
        # High priority recommendations
        if high_severity:
            recommendations.append('URGENT: Remove these sections immediately as they may hurt your application:')
            for section in high_severity:
                recommendations.append(f"• {section['recommendation']}")
        
        # Medium priority recommendations  
        if medium_severity:
            recommendations.append('Important modernization updates:')
            for section in medium_severity:
                recommendations.append(f"• {section['recommendation']}")
        
        # Low priority recommendations
        if low_severity:
            recommendations.append('Consider these improvements:')
            for section in low_severity:
                recommendations.append(f"• {section['recommendation']}")
        
        # General modernization advice
        recommendations.append('Modern resume best practice: Focus on achievements, skills, and relevant experience that directly relate to your target job.')
        
        return recommendations

    def generate_modernization_summary(self, found_sections, passed_checks):
        """Generate summary of modernization analysis"""
        if not found_sections:
            return 'Great! No unnecessary sections found. Your resume follows modern hiring standards.'
        
        summary_parts = []
        
        if found_sections:
            section_types = [s['type'].replace('_', ' ').title() for s in found_sections]
            summary_parts.append(f"Found {len(found_sections)} outdated section(s): {', '.join(section_types)}")
        
        if passed_checks:
            summary_parts.append(f"✓ Passed {len(passed_checks)} modern standards checks")
        
        return '. '.join(summary_parts) + '.'

    def generate_criteria_summary(self, analysis):
        """Generate standardized criteria summary for frontend display"""
        criteria = []
        
        # 1. Quantify Impact
        quant_percentage = analysis['quantification']['quantification_percentage']
        quant_score = min(5, int((quant_percentage / 20)))  # 0-100% -> 0-5 scale
        
        quant_desc = f"Your resume has {quant_percentage:.1f}% quantified achievements. "
        if quant_score <= 1:
            quant_desc += "Add specific numbers, percentages, and metrics to demonstrate your impact."
        elif quant_score <= 3:
            quant_desc += "Good start! Add more measurable results to strengthen your achievements."
        else:
            quant_desc += "Excellent use of quantifiable metrics and results!"
        
        criteria.append({
            "name": "Quantify Impact",
            "score": quant_score,
            "description": quant_desc
        })
        
        # 2. Dates
        dates_analysis = analysis['chronology']
        if dates_analysis.get('has_dates') == False:
            date_score = 0
            date_desc = "No dates found on your resume. Add start and end dates to all work experience and education entries."
        elif dates_analysis.get('format_consistency', True) and not dates_analysis.get('chronological_order_issues', []):
            date_score = 5
            date_desc = f"Found {dates_analysis['total_date_ranges']} properly formatted dates with good consistency."
        elif dates_analysis.get('format_consistency', True):
            date_score = 3
            date_desc = f"Found {dates_analysis['total_date_ranges']} dates but check chronological order and formatting consistency."
        else:
            date_score = 2
            date_desc = f"Found {dates_analysis['total_date_ranges']} dates but they need consistent formatting throughout."
        
        criteria.append({
            "name": "Dates",
            "score": date_score,
            "description": date_desc
        })
        
        # 3. Summary
        summary_analysis = analysis['summary_analysis']
        if not summary_analysis['has_summary']:
            summary_score = 0
            summary_desc = "No professional summary found. Add a 2-3 line summary highlighting your skills and experience."
        else:
            summary_score = min(5, int(summary_analysis['quality_score'] / 20))
            if summary_score <= 1:
                summary_desc = f"Summary needs improvement. Issues: {', '.join(summary_analysis['issues'][:2])}"
            elif summary_score <= 3:
                summary_desc = f"Good summary foundation. Consider: {summary_analysis['recommendations'][0] if summary_analysis['recommendations'] else 'adding more specific skills'}"
            else:
                summary_desc = "Excellent professional summary! Well-written and specific."
        
        criteria.append({
            "name": "Summary",
            "score": summary_score,
            "description": summary_desc
        })
        
        # 4. Action Verbs (NEW - Enhanced Analysis)
        action_verbs_analysis = analysis['action_verbs']
        action_verb_score = min(5, int(action_verbs_analysis.get('action_verb_score', 0) / 20))
        
        strong_pct = action_verbs_analysis['strong_percentage']
        diversity_score = action_verbs_analysis.get('diversity_score', 0)
        
        if action_verb_score >= 4:
            categories_used = action_verbs_analysis.get('categories_used', {})
            if isinstance(categories_used, dict):
                categories_count = len([c for c in categories_used.values() if c > 0])
                action_verb_desc = f"Excellent! {strong_pct:.1f}% strong action verbs with good diversity across {categories_count} categories."
            else:
                action_verb_desc = f"Excellent! {strong_pct:.1f}% strong action verbs with good usage patterns."
        elif action_verb_score >= 3:
            action_verb_desc = f"Good use of action verbs ({strong_pct:.1f}% strong). Consider diversifying verb categories for better impact."
        elif action_verb_score >= 2:
            action_verb_desc = f"Moderate action verb usage ({strong_pct:.1f}% strong). Replace weak verbs like 'responsible for' with stronger alternatives."
        else:
            action_verb_desc = f"Poor action verb usage ({strong_pct:.1f}% strong). Start bullets with powerful verbs like 'Led', 'Developed', 'Achieved'."
        
        criteria.append({
            "name": "Action Verbs",
            "score": action_verb_score,
            "description": action_verb_desc
        })

        # 5. Buzzwords (Enhanced Detection)
        buzzwords_analysis = analysis['buzzwords_analysis']
        buzzword_score = min(5, int(buzzwords_analysis['buzzword_score'] / 20))
        
        total_buzzwords = buzzwords_analysis['total_buzzwords']
        if total_buzzwords == 0:
            buzzword_desc = "Excellent! No generic buzzwords detected. Your resume uses specific, professional language."
        elif total_buzzwords <= 2:
            if buzzwords_analysis['buzzwords_found']:
                example_word = buzzwords_analysis['buzzwords_found'][0]['word']
                severity = buzzwords_analysis['buzzwords_found'][0].get('severity', 'medium')
                buzzword_desc = f"Found {total_buzzwords} buzzwords ('{example_word}'). Replace with specific achievements and metrics."
            else:
                buzzword_desc = f"Found {total_buzzwords} generic phrases. Good overall language usage."
        else:
            critical_buzzwords = [b for b in buzzwords_analysis['buzzwords_found'] if b.get('severity') == 'critical']
            if critical_buzzwords:
                buzzword_desc = f"Found {total_buzzwords} buzzwords including critical ones like '{critical_buzzwords[0]['word']}'. Replace with quantified achievements."
            else:
                buzzword_desc = f"Found {total_buzzwords} buzzwords. Focus on specific achievements rather than generic descriptors."
        
        criteria.append({
            "name": "Buzzwords",
            "score": buzzword_score,
            "description": buzzword_desc
        })
        
        # 5. Skills Section
        skills_analysis = analysis['skills_analysis']
        total_skills = skills_analysis['total_technical_skills'] + skills_analysis['total_soft_skills']
        
        if total_skills == 0:
            skills_score = 0
            skills_desc = "No skills section found. Add technical and soft skills relevant to your target role."
        elif total_skills < 5:
            skills_score = 2
            skills_desc = f"Found {total_skills} skills. Add more relevant technical skills and organize them into categories."
        elif skills_analysis['skill_balance']['balance'] == 'balanced':
            skills_score = 5
            skills_desc = f"Excellent! Found {total_skills} well-balanced skills across technical and soft skill categories."
        else:
            skills_score = 3
            skills_desc = f"Found {total_skills} skills. {skills_analysis['skill_balance']['recommendation']}"
        
        criteria.append({
            "name": "Skills Section",
            "score": skills_score,
            "description": skills_desc
        })
        
        # 6. Experience & Projects (combined criterion)
        sections_analysis = analysis['sections']
        detected_sections = sections_analysis.get('detected_sections', [])  # List of section names detected in the resume
        has_experience = 'experience' in detected_sections  # Check if an Experience/Work section exists
        has_projects = 'projects' in detected_sections      # Check if a Projects section exists

        # Score logic:
        # - 0: neither experience nor projects present (critical issue)
        # - 3: only projects present (good for students/early career, but missing work history)
        # - 4: only experience present (acceptable but projects could strengthen the profile)
        # - 5: both experience and projects present (ideal)
        if not has_experience and not has_projects:
            exp_proj_score = 0
            exp_proj_desc = (
                "No Experience or Projects section found. Add a Work Experience section and/or a Projects section "
                "highlighting what you built, your responsibilities, and your impact."
            )
        elif has_experience and has_projects:
            exp_proj_score = 5
            exp_proj_desc = (
                "Great! Your resume includes both Experience and Projects sections. This gives recruiters a clear view "
                "of your professional history and hands-on work."
            )
        elif has_experience:
            exp_proj_score = 4
            exp_proj_desc = (
                "Experience section found but no dedicated Projects section. Consider adding a Projects section to "
                "showcase key work, personal, or academic projects."
            )
        else:  # has_projects only
            exp_proj_score = 3
            exp_proj_desc = (
                "Projects section found but no Experience section. This is common for students or early-career profiles. "
                "When possible, add internships, part-time roles, or relevant experience to strengthen your resume."
            )

        criteria.append({
            "name": "Experience & Projects",
            "score": exp_proj_score,
            "description": exp_proj_desc
        })
        
        # 7. ATS Compatibility
        formatting_analysis = analysis['formatting']
        readability_score = analysis['readability']['flesch_score']
        buzzword_count = analysis['buzzwords_analysis']['total_buzzwords']
        
        # Calculate ATS score based on multiple factors
        ats_score_factors = []
        
        # Formatting consistency (25%)
        if formatting_analysis['formatting_score'] >= 90:
            ats_score_factors.append(5)
        elif formatting_analysis['formatting_score'] >= 70:
            ats_score_factors.append(4)
        elif formatting_analysis['formatting_score'] >= 50:
            ats_score_factors.append(3)
        else:
            ats_score_factors.append(2)
        
        # Readability (25%)
        if readability_score >= 60:
            ats_score_factors.append(5)
        elif readability_score >= 40:
            ats_score_factors.append(4)
        elif readability_score >= 20:
            ats_score_factors.append(3)
        else:
            ats_score_factors.append(2)
        
        # Keyword usage vs buzzwords (25%)
        if buzzword_count <= 2:
            ats_score_factors.append(5)
        elif buzzword_count <= 4:
            ats_score_factors.append(4)
        elif buzzword_count <= 6:
            ats_score_factors.append(3)
        else:
            ats_score_factors.append(2)
        
        # Section presence (25%) - get missing sections count for ATS calculation
        sections_analysis = analysis['sections']
        missing_count = len(sections_analysis['missing_required'])  # Count of missing required sections
        if missing_count == 0:
            ats_score_factors.append(5)
        elif missing_count == 1:
            ats_score_factors.append(4)
        elif missing_count == 2:
            ats_score_factors.append(3)
        else:
            ats_score_factors.append(2)
        
        ats_score = round(sum(ats_score_factors) / len(ats_score_factors))
        
        if ats_score >= 5:
            ats_desc = "Excellent ATS compatibility! Clean formatting, good readability, minimal buzzwords, and complete sections."
        elif ats_score >= 4:
            ats_desc = "Good ATS compatibility. Minor improvements in formatting or keyword usage could help."
        elif ats_score >= 3:
            ats_desc = "Moderate ATS compatibility. Focus on cleaner formatting and reducing buzzwords."
        else:
            ats_desc = "Poor ATS compatibility. Needs better formatting, structure, and keyword optimization."
        
        criteria.append({
            "name": "ATS Compatibility",
            "score": ats_score,
            "description": ats_desc
        })
        
        # 8. Writing Quality (Missing Criterion)
        writing_quality = analysis['writing_quality']
        writing_score = min(5, int(writing_quality['professionalism_score'] / 20))
        
        informal_count = len(writing_quality.get('informal_words', []))
        passive_count = writing_quality.get('passive_voice_count', 0)
        pronoun_count = writing_quality.get('pronoun_count', 0)
        
        if writing_score >= 4:
            writing_desc = f"Excellent writing quality! Professional tone with minimal issues. Professionalism score: {writing_quality['professionalism_score']}/100."
        elif writing_score >= 3:
            writing_desc = f"Good writing quality with room for improvement. Consider reducing passive voice ({passive_count}) and pronouns ({pronoun_count})."
        else:
            issues = []
            if informal_count > 0:
                issues.append(f"{informal_count} informal words")
            if passive_count > 3:
                issues.append(f"{passive_count} passive voice instances")
            if pronoun_count > 5:
                issues.append(f"{pronoun_count} personal pronouns")
            writing_desc = f"Writing needs improvement. Issues: {', '.join(issues) if issues else 'multiple areas need attention'}."
        
        criteria.append({
            "name": "Writing Quality",
            "score": writing_score,
            "description": writing_desc
        })
        
        # 9. Readability (Missing Criterion)
        readability = analysis['readability']
        readability_score = min(5, max(1, int(readability['flesch_score'] / 20)))
        
        flesch = readability['flesch_score']
        grade_level = readability.get('grade_level', 12)
        
        if readability_score >= 4:
            readability_desc = f"Excellent readability! Flesch score: {flesch:.1f} (easy to read), Grade level: {grade_level:.1f}."
        elif readability_score >= 3:
            readability_desc = f"Good readability with Flesch score: {flesch:.1f}. Consider simplifying complex sentences for better clarity."
        else:
            readability_desc = f"Poor readability. Flesch score: {flesch:.1f} (difficult to read). Simplify sentences and use clearer language."
        
        criteria.append({
            "name": "Readability",
            "score": readability_score,
            "description": readability_desc
        })
        
        # 10. Formatting (Missing Criterion)
        formatting = analysis['formatting']
        formatting_score = min(5, int(formatting['formatting_score'] / 20))
        
        bullet_consistent = formatting.get('bullet_consistency', True)
        date_consistent = formatting.get('date_consistency', True)
        
        if formatting_score >= 4:
            formatting_desc = f"Excellent formatting! Consistent bullets and dates. Formatting score: {formatting['formatting_score']}/100."
        elif formatting_score >= 3:
            formatting_desc = "Good formatting with minor inconsistencies. Ensure consistent bullet styles and date formats throughout."
        else:
            issues = []
            if not bullet_consistent:
                issues.append("inconsistent bullet styles")
            if not date_consistent:
                issues.append("inconsistent date formats")
            formatting_desc = f"Formatting needs improvement: {', '.join(issues) if issues else 'multiple formatting issues detected'}."
        
        criteria.append({
            "name": "Formatting",
            "score": formatting_score,
            "description": formatting_desc
        })
        
        # 11. Chronology (Missing Criterion - corresponds to dates but with different focus)
        chronology = analysis['chronology']
        chronology_issues = len(chronology.get('chronological_order_issues', []))
        chronology_score = min(5, max(1, int((100 - chronology_issues * 15) / 20)))
        
        has_dates = chronology.get('has_dates', False)
        date_ranges = chronology.get('total_date_ranges', 0)
        format_consistent = chronology.get('format_consistency', True)
        
        if not has_dates:
            chronology_desc = "No dates found. Add chronological information to work experience and education sections."
        elif chronology_issues == 0 and format_consistent:
            chronology_desc = f"Excellent chronological organization! {date_ranges} date ranges in proper order with consistent formatting."
        elif chronology_issues == 0:
            chronology_desc = f"Good chronological order with {date_ranges} date ranges. Improve date format consistency for better presentation."
        else:
            chronology_desc = f"Chronological issues detected: {chronology_issues} order problems. Review timeline consistency and date formatting."
        
        criteria.append({
            "name": "Chronology",
            "score": chronology_score,
            "description": chronology_desc
        })
        
        # 12. Unnecessary Sections (Modernization check)
        unnecessary_sections = analysis['unnecessary_sections']
        modernization_score = unnecessary_sections.get('modernization_score', 100)  # 0-100 modernization score
        total_issues = unnecessary_sections.get('total_issues', 0)  # Count of outdated sections found
        has_outdated = unnecessary_sections.get('has_outdated_sections', False)  # Boolean flag for outdated content
        
        # Convert 0-100 modernization score to 0-5 scale for criterion display
        unnecessary_score = min(5, int(modernization_score / 20))
        
        if modernization_score >= 90:
            unnecessary_desc = "Excellent! No outdated sections detected. Your resume follows modern hiring standards."
        elif modernization_score >= 70:
            unnecessary_desc = f"Good modernization with {total_issues} minor issues. Consider removing outdated elements for a cleaner presentation."
        elif modernization_score >= 50:
            unnecessary_desc = f"Found {total_issues} outdated sections. Remove references, objectives, and other unnecessary elements to modernize your resume."
        else:
            unnecessary_desc = f"Multiple outdated sections detected ({total_issues} issues). Focus on removing references, personal photos, and irrelevant personal information."

        criteria.append({
            "name": "Unnecessary Sections",
            "score": unnecessary_score,
            "description": unnecessary_desc
        })
        
        return criteria

    def calculate_final_score(self, analysis):
        """Calculate weighted final score using individual criteria"""
        # Individual weights for criteria contributing to the final score (must sum to 1.0)
        # Note: Readability, buzzwords, and formatting still have their own criteria and scores,
        #       but their impact on the final score now flows only through ats_compatibility.
        weights = {
            'quantify_impact': 0.12,      # Quantification and metrics
            'dates': 0.08,               # Date completeness and formatting  
            'summary': 0.06,             # Professional summary quality
            'action_verbs': 0.10,        # Action verb strength and diversity
            'skills_section': 0.10,      # Skills analysis and balance
            'structure': 0.12,           # Section completeness and order
            'ats_compatibility': 0.24,   # ATS optimization (includes readability, buzzwords, formatting)
            'writing_quality': 0.08,     # Grammar, tone, professionalism
            'chronology': 0.06,          # Timeline consistency
            'unnecessary_sections': 0.04 # Modernization and outdated section avoidance
        }
        
        scores = {}
        
        # 1. Quantify Impact score
        quant_percentage = analysis['quantification']['quantification_percentage']
        scores['quantify_impact'] = min(quant_percentage * 2, 100)  # Scale 0-50% to 0-100
        
        # 2. Dates score
        dates_analysis = analysis['chronology']
        if dates_analysis.get('has_dates') == False:
            scores['dates'] = 0
        elif dates_analysis.get('format_consistency', True) and not dates_analysis.get('chronological_order_issues', []):
            scores['dates'] = 100
        elif dates_analysis.get('format_consistency', True):
            scores['dates'] = 60
        else:
            scores['dates'] = 40
        
        # 3. Summary score
        summary_analysis = analysis['summary_analysis']
        if not summary_analysis['has_summary']:
            scores['summary'] = 0
        else:
            scores['summary'] = min(summary_analysis['quality_score'], 100)
        
        # 4. Action Verbs score
        scores['action_verbs'] = analysis['action_verbs'].get('action_verb_score', 0)
        
        # 5. Buzzwords score
        scores['buzzwords'] = analysis['buzzwords_analysis']['buzzword_score']
        
        # 6. Skills Section score
        total_skills = analysis['skills_analysis']['total_technical_skills'] + analysis['skills_analysis']['total_soft_skills']
        scores['skills_section'] = min(total_skills * 6, 100)  # 6 points per skill, max 100
        
        # 7. Structure score
        sections = analysis['sections']
        structure_score = 100
        structure_score -= len(sections['missing_required']) * 20  # 20 points per missing required section
        structure_score -= len(sections['duplicated_sections']) * 10  # 10 points per duplicate
        structure_score -= 15 if not sections['order_analysis']['is_logical'] else 0
        scores['structure'] = max(structure_score, 0)
        
        # 8. ATS Compatibility score
        formatting_analysis = analysis['formatting']
        readability_score = analysis['readability']['flesch_score']
        buzzword_count = analysis['buzzwords_analysis']['total_buzzwords']
        missing_sections = len(sections['missing_required'])
        
        # Calculate ATS score based on multiple factors
        ats_factors = []
        ats_factors.append(min(formatting_analysis['formatting_score'], 100))
        ats_factors.append(min(max(readability_score, 0), 100))
        ats_factors.append(max(100 - (buzzword_count * 10), 0))
        ats_factors.append(max(100 - (missing_sections * 25), 0))
        scores['ats_compatibility'] = sum(ats_factors) / len(ats_factors)
        
        # 9. Writing Quality score
        scores['writing_quality'] = analysis['writing_quality']['professionalism_score']
        
        # 10. Readability score
        flesch_score = analysis['readability']['flesch_score']
        scores['readability'] = min(max(flesch_score, 0), 100)
        
        # 11. Formatting score
        scores['formatting'] = analysis['formatting']['formatting_score']
        
        # 12. Chronology score
        chronology_issues = len(analysis['chronology'].get('chronological_order_issues', []))
        scores['chronology'] = max(100 - (chronology_issues * 15), 0)
        
        # 13. Unnecessary Sections score
        unnecessary_sections_analysis = analysis['unnecessary_sections']
        modernization_score = unnecessary_sections_analysis.get('modernization_score', 100)  # Already 0-100 scale
        scores['unnecessary_sections'] = modernization_score  # Use modernization score directly as it's already 0-100
        
        # Calculate weighted final score
        final_score = sum(scores[criterion] * weights[criterion] for criterion in weights)
        
        return {
            'category_scores': scores,
            'weights': weights,
            'final_score': round(final_score, 2),
            'grade': self.get_score_grade(final_score)
        }

    def get_score_grade(self, score):
        """Convert score to letter grade"""
        if score >= 90: return 'A'
        elif score >= 80: return 'B'
        elif score >= 70: return 'C'
        elif score >= 60: return 'D'
        else: return 'F'
