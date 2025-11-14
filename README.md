# Resume Reviewer Platform

A comprehensive web platform that analyzes and improves resumes using NLP and machine learning, matching the core functionality of Resume Worded.

## Features

- **Resume Scoring & Review**: Upload your resume and get a comprehensive score (0-100) based on:
  - ATS compatibility (formatting, structure, readability)
  - Content quality (action verbs, quantification, impact)
  - Keyword optimization
  - Structure and organization

- **Targeted Resume Matching**: Compare your resume against a job description to:
  - Extract and match keywords
  - Identify missing skills/keywords
  - Calculate match percentage
  - Get targeted suggestions for improvement

- **AI-Powered Improvements**: Get line-by-line feedback including:
  - Stronger action verb suggestions
  - Quantification opportunities
  - Clarity and impact improvements
  - Before/after examples

## Architecture

- **Frontend**: React with Vite, modern UI with Lucide icons
- **Backend**: Express.js API server with file upload handling
- **AI Processing**: Python scripts for NLP analysis
- **File Handling**: PDF and DOCX parsing with validation

## Tech Stack

### Backend
- Node.js with Express.js
- Multer for file uploads
- Child process for Python integration
- Automatic file cleanup

### Frontend
- React 18
- React Router for navigation
- Axios for API calls
- Lucide React for icons
- Vite for build tooling

### Python/AI
- pdfplumber (PDF text extraction)
- PyPDF2 (PDF validation & sanitization)
- python-docx (DOCX parsing)
- spaCy/NLTK (NLP analysis)
- scikit-learn (ML classifiers)
- Pillow (image detection)

## Installation

### Prerequisites
- Node.js (v16 or higher)
- Python 3.8+
- npm or yarn

### Setup Instructions

1. **Clone the repository**
   ```bash
   cd dontgethired
   ```

2. **Install Backend Dependencies**
   ```bash
   cd backend
   npm install
   ```

3. **Install Frontend Dependencies**
   ```bash
   cd ../frontend
   npm install
   ```

4. **Install Python Dependencies**
   ```bash
   cd ../python
   pip install -r requirements.txt
   
   # Download spaCy language model (if using spaCy)
   python -m spacy download en_core_web_sm
   ```

5. **Configure Environment Variables**
   
   Create a `.env` file in the `backend` directory:
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env with your specific configuration
   ```
   
   **Minimum required configuration:**
   ```env
   PORT=5000
   NODE_ENV=development
   PYTHON_PATH=python
   ```
   
   **Optional services (for enhanced features):**
   ```env
   # Redis (for caching - improves performance)
   REDIS_HOST=localhost
   REDIS_PORT=6379
   
   # PostgreSQL (for analytics and usage tracking)
   DATABASE_URL=postgresql://user:password@localhost:5432/resume_reviewer
   ```

## Running the Application

### Development Mode

1. **Start the Backend Server**
   ```bash
   cd backend
   npm run dev
   ```
   Server will run on http://localhost:5000

2. **Start the Frontend (in a new terminal)**
   ```bash
   cd frontend
   npm run dev
   ```
   Frontend will run on http://localhost:3000

3. **Access the Application**
   Open your browser and navigate to http://localhost:3000

## API Endpoints

### Health Check
- **GET** `/api/health`
  - Check if the API is running
  - Returns service status and timestamp

### Resume Scoring
- **POST** `/api/resume/score`
  - Upload: PDF or DOCX file (max 2MB)
  - Returns: Score, breakdown, feedback, and recommendations

### Job Matching
- **POST** `/api/resume/target`
  - Upload: Resume file + job description (text)
  - Returns: Match percentage, matched/missing keywords, suggestions

### Resume Improvement
- **POST** `/api/resume/improve`
  - Upload: PDF or DOCX file
  - Returns: Bullet-by-bullet improvements and overall suggestions

## File Structure

```
dontgethired/
├── backend/                  # Express API
│   ├── routes/
│   │   ├── resume.js        # Resume analysis endpoints
│   │   └── health.js        # Health check
│   ├── middleware/
│   │   └── upload.js        # Multer file upload config
│   ├── services/
│   │   ├── pythonService.js # Python script execution
│   │   └── fileCleanup.js   # Temporary file cleanup
│   ├── uploads/temp/        # Temporary file storage
│   ├── server.js
│   └── package.json
├── frontend/                 # React application
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/           # Page components
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
├── python/                   # NLP/AI scripts
│   ├── resume_parser.py     # Extract text from files
│   ├── pdf_validator.py     # Validate & sanitize PDFs
│   ├── nlp_analyzer.py      # Traditional NLP detection
│   ├── bullet_classifier.py # ML-based bullet classification
│   ├── recommendation_engine.py # Generate recommendations
│   ├── keyword_extractor.py # Extract keywords
│   ├── job_matcher.py       # Match resume to job
│   ├── resume_scorer.py     # Score resume
│   ├── text_improver.py     # Suggest improvements
│   └── requirements.txt
└── README.md
```

## Key Features Implementation

### PDF Security & Validation
- Sanitizes PDFs to remove JavaScript and malicious content
- Validates file size (≤ 2MB) and text extractability
- Detects and rejects image-based/scanned PDFs
- Ensures text-based PDFs for optimal analysis

### NLP Analysis
- **Traditional NLP**: Detects missing metrics, weak action verbs, missing sections
- **ML Classifiers**: P(Strong) and P(Relevant) predictions for bullet points
- **Recommendation Engine**: Maps detected issues to actionable recommendations

### Resume Scoring Algorithm
- ATS Compatibility: 0-25 points
- Content Quality: 0-40 points
- Keyword Optimization: 0-20 points
- Structure: 0-15 points
- **Total**: 0-100 points

### File Cleanup
- Automatic cleanup of temporary files after processing
- Background cleanup job for orphaned files
- Graceful error handling with guaranteed cleanup

## Supported File Formats

- **PDF**: Text-based PDFs from Word, Google Docs, LaTeX, Canva
- **DOCX**: Microsoft Word documents
- **Max Size**: 2MB
- **Not Supported**: Scanned PDFs, image-based PDFs, complex layouts

## Development

### Backend Development
```bash
cd backend
npm run dev  # Uses nodemon for auto-reload
```

### Frontend Development
```bash
cd frontend
npm run dev  # Vite dev server with HMR
```

### Python Script Testing
```bash
cd python
python resume_parser.py path/to/resume.pdf
python resume_scorer.py path/to/resume.pdf
```

## Production Build

### Frontend Build
```bash
cd frontend
npm run build
# Output in frontend/dist/
```

### Backend Production
```bash
cd backend
npm start
```

## Troubleshooting

### Python Scripts Not Running
- Ensure Python is installed and in PATH
- Check `PYTHON_PATH` in backend `.env` file
- Try using `python3` instead of `python`

### File Upload Errors
- Check file size (must be ≤ 2MB)
- Ensure file is PDF or DOCX format
- Verify uploads/temp directory exists and is writable

### PDF Parsing Issues
- PDFs must be text-based (not scanned images)
- Some complex layouts may not parse correctly
- Try exporting from Word/Google Docs for best results

### Performance Issues
- **Enable Redis**: Install Redis for significant performance improvements
- **Check Logs**: Review logs in `backend/logs/` for detailed error information
- **Monitor Health**: Use `/api/health` endpoint to check service status

## Enhanced Features

This platform includes several production-ready enhancements:

### 🚀 **Performance Features**
- **Redis Caching**: Dramatically improves response times for repeated analyses
- **Rate Limiting**: Protects against abuse and ensures fair usage
- **Structured Logging**: Comprehensive logging for debugging and monitoring

### 📊 **Analytics & Monitoring**
- **Health Checks**: Comprehensive service monitoring at `/api/health`
- **Usage Analytics**: Optional PostgreSQL integration for usage tracking
- **Performance Metrics**: Detailed timing and performance data

### 🔒 **Production Ready**
- **Error Handling**: Graceful fallbacks when optional services are unavailable
- **Security**: Rate limiting and input validation
- **Scalability**: Designed for horizontal scaling

For detailed information about these enhancements, see [ENHANCEMENTS.md](./ENHANCEMENTS.md).

## Contributing

Contributions are welcome! Please follow these guidelines:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - feel free to use this project for personal or commercial purposes.

## Acknowledgments

- Inspired by Resume Worded
- Built with modern web technologies
- NLP powered by Python ecosystem

## Support

For issues or questions, please open an issue on GitHub.
