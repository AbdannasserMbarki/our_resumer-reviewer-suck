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
    "Implemented microservices architecture reducing system latency by 40%",
    "Led team of 5 engineers to deliver product 2 weeks ahead of schedule",
    "Developed automated testing framework increasing code coverage from 60% to 95%",
    "Architected scalable solution handling 1M+ daily active users",
    "Optimized database queries reducing load time by 65%",
    "Launched new feature generating $500K additional annual revenue",
    "Managed cross-functional team of 12 delivering 3 major releases",
    "Increased customer satisfaction score from 3.2 to 4.7 out of 5",
]

WEAK_BULLETS_TRAINING = [
    "Responsible for writing code",
    "Worked on various projects",
    "Helped with testing",
    "Participated in team meetings",
    "Assisted senior developers",
    "Involved in the development process",
    "Supported the engineering team",
    "Contributed to codebase",
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
