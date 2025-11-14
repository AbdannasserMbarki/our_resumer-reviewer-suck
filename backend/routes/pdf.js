const express = require('express');
const multer = require('multer');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const router = express.Router();

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const uploadDir = path.join(__dirname, '../uploads/temp');
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, 'pdf-' + uniqueSuffix + path.extname(file.originalname));
  }
});

const upload = multer({ 
  storage: storage,
  fileFilter: (req, file, cb) => {
    if (file.mimetype === 'application/pdf') {
      cb(null, true);
    } else {
      cb(new Error('Only PDF files are allowed'), false);
    }
  },
  limits: {
    fileSize: 10 * 1024 * 1024 // 10MB limit
  }
});

// Extract text from PDF
router.post('/extract-text', upload.single('pdf'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({
        success: false,
        error: 'No PDF file provided'
      });
    }

    const filePath = req.file.path;
    const pythonScriptPath = path.join(__dirname, '../../python/resume_parser.py');
    
    // Use Python script to extract text from PDF with virtual environment
    const pythonPath = path.join(__dirname, '../../resume_env/Scripts/python.exe');
    const pythonProcess = spawn(pythonPath, [pythonScriptPath, filePath], {
      cwd: path.join(__dirname, '../../')
    });

    let output = '';
    let errorOutput = '';

    pythonProcess.stdout.on('data', (data) => {
      output += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      errorOutput += data.toString();
    });

    pythonProcess.on('close', (code) => {
      // Clean up uploaded file
      fs.unlink(filePath, (err) => {
        if (err) console.error('Error deleting temp file:', err);
      });

      if (code !== 0) {
        console.error('Python script error:', errorOutput);
        return res.status(500).json({
          success: false,
          error: 'Failed to extract text from PDF'
        });
      }

      try {
        const result = JSON.parse(output);
        if (result.success) {
          res.json({
            success: true,
            text: result.text,
            pages: result.pages || 1
          });
        } else {
          res.status(400).json(result);
        }
      } catch (parseError) {
        console.error('Error parsing Python output:', parseError);
        res.status(500).json({
          success: false,
          error: 'Failed to parse extraction result'
        });
      }
    });

  } catch (error) {
    console.error('PDF extraction error:', error);
    
    // Clean up file if it exists
    if (req.file && req.file.path) {
      fs.unlink(req.file.path, (err) => {
        if (err) console.error('Error deleting temp file:', err);
      });
    }
    
    res.status(500).json({
      success: false,
      error: 'Internal server error during PDF processing'
    });
  }
});

module.exports = router;
