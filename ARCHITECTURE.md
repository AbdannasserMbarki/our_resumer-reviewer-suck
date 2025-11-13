# Architecture Documentation

## System Overview

The Resume Reviewer Platform is a full-stack web application that analyzes resumes using Natural Language Processing (NLP) and Machine Learning techniques.

## Architecture Diagram

```
┌─────────────────┐
│   React Frontend │
│   (Vite + React) │
└────────┬─────────┘
         │ HTTP/REST
         │ (Axios)
┌────────▼─────────┐
│  Express Backend │
│   (Node.js API)  │
└────────┬─────────┘
         │ Child Process
         │ (spawn)
┌────────▼─────────┐
│  Python Scripts  │
│  (NLP/ML Engine) │
└──────────────────┘
```

## Component Details

### Frontend Layer (React + Vite)

**Technology Stack:**
- React 18 for UI components
- React Router for navigation
- Axios for API communication
- Lucide React for icons
- CSS for styling

**Key Components:**
- `FileUpload`: Drag-and-drop file upload with validation
- `ScoreCard`: Visual score display with breakdown
- `FeedbackList`: Expandable list of issues and recommendations
- `JobDescriptionInput`: Textarea for job description input

**Pages:**
- `Home`: Landing page with feature overview
- `ScoreResume`: Resume scoring and analysis
- `TargetResume`: Job matching functionality

**State Management:**
- React Hooks (useState, useEffect)
- Component-level state (no global state management)

### Backend Layer (Express.js)

**Technology Stack:**
- Express.js for REST API
- Multer for file upload handling
- Child Process for Python script execution
- fs-extra for file operations

**Architecture Patterns:**
- Route-based organization
- Service layer for business logic
- Middleware for cross-cutting concerns

**Key Services:**
- `pythonService`: Executes Python scripts and parses JSON results
- `fileCleanup`: Manages temporary file lifecycle

**API Design:**
- RESTful endpoints
- Multipart form data for file uploads
- JSON responses with consistent structure

**File Flow:**
1. Client uploads file via multipart/form-data
2. Multer saves to temp directory with unique name
3. Backend passes file path to Python script
4. Python processes and returns JSON
5. Backend responds to client
6. Temp file is deleted (success or error)

### Python/NLP Layer

**Technology Stack:**
- pdfplumber: PDF text extraction
- PyPDF2: PDF manipulation and sanitization
- python-docx: DOCX parsing
- spaCy/NLTK: Natural language processing
- scikit-learn: Machine learning classifiers

**Script Architecture:**

```
resume_parser.py
    ├─ Extracts text from PDF/DOCX
    └─ Returns: {success, text, pages}

pdf_validator.py
    ├─ Validates PDF security and quality
    ├─ Sanitizes dangerous content
    └─ Returns: {success, warnings, metrics}

nlp_analyzer.py
    ├─ Detects missing metrics
    ├─ Checks action verbs
    ├─ Validates sections
    └─ Returns: {sections, bullet_points, statistics}

bullet_classifier.py
    ├─ ML-based classification
    ├─ P(Strong) - bullet strength
    ├─ P(Relevant) - job relevance
    └─ Returns: {classifications}

recommendation_engine.py
    ├─ Maps issues to recommendations
    ├─ Prioritizes by impact
    └─ Returns: {recommendations, feedback}

keyword_extractor.py
    ├─ Extracts technical skills
    ├─ Identifies soft skills
    └─ Returns: {keywords}

job_matcher.py
    ├─ Compares resume to job description
    ├─ Calculates match percentage
    └─ Returns: {matchPercentage, keywords}

resume_scorer.py
    ├─ Orchestrates analysis pipeline
    ├─ Calculates weighted score
    └─ Returns: {score, breakdown, feedback}

text_improver.py
    ├─ Generates improvement suggestions
    ├─ Suggests verb replacements
    └─ Returns: {improvements, suggestions}
```

## Data Flow

### Resume Scoring Flow

```
1. User uploads resume
   ↓
2. Frontend → POST /api/resume/score (multipart/form-data)
   ↓
3. Multer saves file to uploads/temp/
   ↓
4. Backend → pdf_validator.py (if PDF)
   ↓
5. Backend → resume_parser.py
   ↓
6. Backend → resume_scorer.py
   ↓
7. Python returns JSON with score and feedback
   ↓
8. Backend deletes temp file
   ↓
9. Backend → Frontend (JSON response)
   ↓
10. Frontend renders ScoreCard + FeedbackList
```

### Job Matching Flow

```
1. User uploads resume + job description
   ↓
2. Frontend → POST /api/resume/target
   ↓
3. Multer saves file
   ↓
4. Backend → job_matcher.py (file + job desc)
   ↓
5. Python:
   - Parses resume
   - Extracts keywords from both
   - Calculates match
   ↓
6. Backend deletes temp file
   ↓
7. Backend → Frontend (match results)
   ↓
8. Frontend renders match score + keywords
```

## Security Considerations

### PDF Sanitization
- Strips JavaScript and embedded scripts
- Removes forms and interactive elements
- Validates file structure
- Prevents code execution attacks

### File Upload Security
- File size limits (2MB)
- File type validation (PDF, DOCX only)
- Unique temporary filenames
- Automatic cleanup
- No direct file access from frontend

### API Security
- CORS configuration
- Input validation
- Error handling without exposing internals
- File path sanitization

## Scalability Considerations

### Current Limitations
- Synchronous Python script execution
- Single server architecture
- No request queuing
- Limited concurrent processing

### Future Improvements
- **Queue System**: Use Bull/Redis for job queue
- **Worker Processes**: Multiple Python workers
- **Caching**: Cache common analyses
- **CDN**: Serve static assets from CDN
- **Load Balancer**: Horizontal scaling
- **Database**: Store analysis history
- **Microservices**: Separate analysis service

## Performance Optimization

### Frontend
- Code splitting by route
- Lazy loading of components
- Image optimization
- Minification and bundling (Vite)

### Backend
- Connection pooling
- Response compression
- Static file caching
- Efficient file streaming

### Python
- Batch processing capabilities
- Model caching (if using ML models)
- Efficient text parsing

## Error Handling Strategy

### Frontend
- User-friendly error messages
- Loading states
- Retry mechanisms
- Form validation

### Backend
- Try-catch blocks
- Graceful degradation
- Error logging
- File cleanup on error

### Python
- JSON error responses
- Validation before processing
- Fallback mechanisms

## Monitoring & Logging

### Recommended Additions
- Application monitoring (e.g., Sentry)
- Performance monitoring (e.g., New Relic)
- Log aggregation (e.g., ELK stack)
- Uptime monitoring
- Error rate tracking
- API response time metrics

## Deployment Architecture

### Development
```
localhost:3000 (Frontend - Vite)
     ↓
localhost:5000 (Backend - Express)
```

### Production
```
CDN (Static Assets)
     ↓
Nginx (Reverse Proxy)
     ↓
Node.js (Express API)
     ↓
Python (NLP Engine)
```

## Technology Choices Rationale

### Why React?
- Component reusability
- Large ecosystem
- Developer experience
- Performance (Virtual DOM)

### Why Vite?
- Fast development server
- Optimized builds
- Modern tooling
- HMR support

### Why Express?
- Lightweight and flexible
- Large middleware ecosystem
- Easy integration with Python
- Well-documented

### Why Python for NLP?
- Rich NLP ecosystem (spaCy, NLTK)
- ML libraries (scikit-learn)
- PDF/DOCX parsing libraries
- Easy text processing

### Why Child Process?
- Language flexibility
- Process isolation
- Resource management
- Error containment

## Future Enhancements

1. **Authentication System**: User accounts and saved analyses
2. **Database Integration**: Store analysis history
3. **Advanced ML Models**: Better classifiers with more training data
4. **Real-time Analysis**: WebSocket for streaming results
5. **Multiple File Support**: Analyze multiple resumes at once
6. **Export Features**: PDF reports of analysis
7. **A/B Testing**: Compare resume versions
8. **Industry Templates**: Pre-built templates by industry
9. **LinkedIn Integration**: Import from LinkedIn
10. **Mobile App**: React Native version
