# Quick Setup Guide

## 1. Install Dependencies

### Backend
```bash
cd backend
npm install
```

### Frontend
```bash
cd frontend
npm install
```

### Python
```bash
cd python
pip install -r requirements.txt
```

## 2. Start Development Servers

### Terminal 1 - Backend
```bash
cd backend
npm run dev
```
Backend runs on: http://localhost:5000

### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```
Frontend runs on: http://localhost:3000

## 3. Test the Application

1. Open browser to http://localhost:3000
2. Navigate to "Score Resume"
3. Upload a test resume (PDF or DOCX)
4. Click "Analyze Resume"
5. View your results!

## Common Issues

### "Python not found"
- Windows: Install Python from python.org
- Check: `python --version` or `python3 --version`
- Update `.env` in backend: `PYTHON_PATH=python3`

### "Cannot upload file"
- Check file size (max 2MB)
- Ensure file is PDF or DOCX
- Check backend/uploads/temp exists

### "Module not found" (Python)
- Install dependencies: `pip install -r python/requirements.txt`
- Use virtual environment recommended:
  ```bash
  python -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate
  pip install -r python/requirements.txt
  ```

### Port already in use
- Backend (5000): Change PORT in backend/.env
- Frontend (3000): Vite will suggest alternate port

## Testing Individual Components

### Test Python Scripts
```bash
cd python
python resume_parser.py path/to/test.pdf
python pdf_validator.py path/to/test.pdf
```

### Test Backend API
```bash
# Health check
curl http://localhost:5000/api/health
```

### Test Frontend
- Navigate pages: Home → Score Resume → Job Match
- Test file upload
- Check browser console for errors

## Next Steps

1. Customize scoring algorithm in `python/resume_scorer.py`
2. Add more action verbs in `python/nlp_analyzer.py`
3. Improve ML classifiers with training data
4. Customize UI colors and branding
5. Add more keyword categories

## Production Deployment

### Backend
- Set NODE_ENV=production
- Use process manager (PM2)
- Configure reverse proxy (nginx)

### Frontend
- Build: `npm run build`
- Serve dist/ folder
- Configure API endpoint

### Security
- Add rate limiting
- Implement authentication (if needed)
- Use HTTPS
- Validate file types server-side
- Set up monitoring
