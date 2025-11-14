#!/usr/bin/env python3
"""
Bullet Classifier - ML-based classification for bullet point strength and relevance
"""
import json
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import numpy as np

# Training data for P(Strong) classifier
STRONG_BULLETS_TRAINING = [
    # Technology & Engineering
    "Implemented microservices architecture reducing system latency by 40%",
    "Led team of 5 engineers to deliver product 2 weeks ahead of schedule",
    "Developed automated testing framework increasing code coverage from 60% to 95%",
    "Architected scalable solution handling 1M+ daily active users",
    "Optimized database queries reducing load time by 65%",
    "Launched new feature generating $500K additional annual revenue",
    "Managed cross-functional team of 12 delivering 3 major releases",
    "Increased customer satisfaction score from 3.2 to 4.7 out of 5",
    "Designed and deployed CI/CD pipeline reducing deployment time by 80%",
    "Built machine learning model achieving 94% accuracy in fraud detection",
    "Migrated legacy system to cloud infrastructure saving $200K annually",
    "Established coding standards adopted by 50+ developers across 3 teams",
    "Created API documentation reducing support tickets by 60%",
    "Automated manual processes saving 15 hours per week",
    "Refactored codebase improving performance by 3x",
    "Integrated third-party services increasing platform capabilities by 40%",
    
    # Sales & Marketing
    "Generated $2.5M in new business revenue through strategic partnerships",
    "Exceeded quarterly sales targets by 125% for 6 consecutive quarters",
    "Developed go-to-market strategy resulting in 300% user growth",
    "Launched digital marketing campaign achieving 15% conversion rate",
    "Negotiated contracts worth $1.8M with Fortune 500 clients",
    "Built sales pipeline generating 200+ qualified leads monthly",
    "Increased market share from 12% to 28% in target demographic",
    "Reduced customer acquisition cost by 45% through optimization",
    "Created content strategy driving 500K monthly website visitors",
    "Established brand partnerships generating $800K in co-marketing value",
    
    # Operations & Management
    "Streamlined operations reducing processing time by 50%",
    "Implemented quality control system decreasing defects by 75%",
    "Managed $5M budget while maintaining 98% cost efficiency",
    "Reduced operational costs by $300K through process improvements",
    "Coordinated logistics for 500+ person conference with 99% satisfaction",
    "Established vendor relationships saving 20% on procurement costs",
    "Developed training program improving employee retention by 35%",
    "Led organizational restructuring improving productivity by 25%",
    "Implemented safety protocols reducing workplace incidents by 90%",
    "Optimized supply chain reducing delivery time by 3 days",
    
    # Finance & Analytics
    "Analyzed financial data identifying $1.2M in cost savings opportunities",
    "Built financial models supporting $10M investment decisions",
    "Reduced accounts receivable by 40% through improved collection processes",
    "Implemented budgeting system improving forecast accuracy by 85%",
    "Conducted market analysis informing $5M product development strategy",
    "Automated reporting processes saving 20 hours weekly",
    "Identified revenue opportunities worth $750K through data analysis",
    "Managed portfolio of investments generating 18% annual returns",
    
    # Human Resources & Training
    "Recruited and onboarded 25 high-performing team members",
    "Designed employee development program improving promotion rates by 60%",
    "Implemented diversity initiative increasing representation by 40%",
    "Reduced employee turnover from 25% to 8% through retention strategies",
    "Created performance management system adopted company-wide",
    "Facilitated leadership training for 100+ managers",
    "Negotiated benefits package saving company $150K annually",
    
    # Customer Success & Support
    "Improved customer satisfaction scores from 3.1 to 4.8 out of 5",
    "Reduced average response time from 24 hours to 2 hours",
    "Implemented customer success program increasing retention by 45%",
    "Resolved 95% of escalated issues within 24-hour SLA",
    "Created self-service portal reducing support tickets by 70%",
    "Trained customer service team improving first-call resolution by 50%",
    "Developed customer feedback system driving product improvements"
]

WEAK_BULLETS_TRAINING = [
    # Vague responsibilities
    "Responsible for writing code",
    "Worked on various projects",
    "Helped with testing",
    "Participated in team meetings",
    "Assisted senior developers",
    "Involved in the development process",
    "Supported the engineering team",
    "Contributed to codebase",
    "Responsible for customer service",
    "Worked with clients",
    "Helped with sales activities",
    "Participated in marketing campaigns",
    "Assisted with project management",
    "Involved in daily operations",
    "Supported management team",
    "Contributed to team goals",
    "Responsible for data entry",
    "Worked on administrative tasks",
    "Helped with documentation",
    "Participated in training sessions",
    "Assisted with research",
    "Involved in planning meetings",
    "Supported various initiatives",
    "Contributed to company objectives",
    
    # Passive language
    "Was responsible for maintaining systems",
    "Was involved in project planning",
    "Was part of the development team",
    "Was assigned to handle customer inquiries",
    "Was tasked with updating documentation",
    "Was given responsibility for quality assurance",
    "Was asked to assist with training",
    "Was required to attend meetings",
    "Was expected to follow procedures",
    "Was directed to support operations",
    
    # No impact or metrics
    "Performed software development tasks",
    "Handled customer complaints",
    "Managed team activities",
    "Conducted market research",
    "Maintained database systems",
    "Organized team events",
    "Prepared reports",
    "Attended conferences",
    "Reviewed documents",
    "Coordinated schedules",
    "Monitored performance",
    "Updated procedures",
    "Processed applications",
    "Answered phone calls",
    "Filed paperwork",
    "Scheduled appointments",
    "Collected data",
    "Distributed materials",
    "Observed operations",
    "Followed instructions"
]

class BulletClassifier:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=100, ngram_range=(1, 2))
        self.strength_classifier = MultinomialNB()
        self._train_strength_classifier()
    
    def _train_strength_classifier(self):
        """Train P(Strong) classifier with sample data"""
        # Combine training data
        X_train = STRONG_BULLETS_TRAINING + WEAK_BULLETS_TRAINING
        y_train = [1] * len(STRONG_BULLETS_TRAINING) + [0] * len(WEAK_BULLETS_TRAINING)
        
        # Train
        X_vectorized = self.vectorizer.fit_transform(X_train)
        self.strength_classifier.fit(X_vectorized, y_train)
    
    def predict_strength(self, bullet_text):
        """Predict P(Strong) for a bullet point"""
        try:
            X = self.vectorizer.transform([bullet_text])
            proba = self.strength_classifier.predict_proba(X)[0]
            return float(proba[1])  # Probability of being strong
        except:
            return 0.5  # Default to neutral if classification fails
    
    def predict_relevance(self, bullet_text, job_keywords):
        """Predict P(Relevant) based on keyword overlap with job description"""
        if not job_keywords:
            return 0.5  # No job description provided
        
        bullet_lower = bullet_text.lower()
        
        # Count keyword matches
        matches = sum(1 for keyword in job_keywords if keyword.lower() in bullet_lower)
        
        # Calculate relevance score
        if len(job_keywords) == 0:
            return 0.5
        
        relevance = min(1.0, matches / len(job_keywords) * 2)  # Scale so 50% match = 1.0
        return relevance

def classify_bullets(bullets, job_keywords=None):
    """Classify bullet points for strength and relevance"""
    classifier = BulletClassifier()
    
    results = []
    for bullet in bullets:
        p_strong = classifier.predict_strength(bullet)
        p_relevant = classifier.predict_relevance(bullet, job_keywords) if job_keywords else None
        
        classification = {
            'text': bullet,
            'p_strong': round(p_strong, 3),
            'strength_label': 'strong' if p_strong > 0.6 else 'weak' if p_strong < 0.4 else 'moderate'
        }
        
        if p_relevant is not None:
            classification['p_relevant'] = round(p_relevant, 3)
            classification['relevance_label'] = 'relevant' if p_relevant > 0.5 else 'not_relevant'
        
        results.append(classification)
    
    return results

def main():
    import sys
    
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "No bullets provided"}))
        sys.exit(1)
    
    bullets_json = sys.argv[1]
    try:
        data = json.loads(bullets_json)
        bullets = data.get('bullets', [])
        job_keywords = data.get('job_keywords', None)
        
        results = classify_bullets(bullets, job_keywords)
        
        print(json.dumps({
            "success": True,
            "classifications": results
        }))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()
