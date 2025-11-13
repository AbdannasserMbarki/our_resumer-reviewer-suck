const express = require('express');
const router = express.Router();
const upload = require('../middleware/upload');
const pythonService = require('../services/pythonService');
const fileCleanup = require('../services/fileCleanup');
const path = require('path');

// Start periodic cleanup of temp files (every 30 minutes, delete files older than 1 hour)
const tempDir = path.join(__dirname, '..', 'uploads', 'temp');
fileCleanup.startPeriodicCleanup(tempDir, 1800000, 3600000);

/**
 * POST /api/resume/score
 * Upload and score resume
 */
router.post('/score', upload.single('resume'), async (req, res) => {
  let filePath = null;
  
  try {
    if (!req.file) {
      return res.status(400).json({
        success: false,
        error: 'No file uploaded. Please upload a PDF or DOCX file.'
      });
    }

    filePath = req.file.path;
    console.log(`Processing resume: ${req.file.originalname}`);

    // Step 1: Validate PDF if it's a PDF file
    if (path.extname(req.file.originalname).toLowerCase() === '.pdf') {
      console.log('Validating PDF...');
      const validation = await pythonService.validatePDF(filePath);
      
      if (!validation.success) {
        await fileCleanup.deleteFile(filePath);
        return res.status(400).json({
          success: false,
          error: validation.error || 'PDF validation failed',
          details: validation
        });
      }
      
      console.log('PDF validation passed');
    }

    // Step 2: Parse resume
    console.log('Parsing resume...');
    const parsedResume = await pythonService.parseResume(filePath);
    
    if (!parsedResume.success) {
      await fileCleanup.deleteFile(filePath);
      return res.status(400).json({
        success: false,
        error: parsedResume.error || 'Failed to parse resume'
      });
    }

    // Step 3: Score resume
    console.log('Scoring resume...');
    const scoreResult = await pythonService.scoreResume(filePath);
    
    if (!scoreResult.success) {
      await fileCleanup.deleteFile(filePath);
      return res.status(500).json({
        success: false,
        error: scoreResult.error || 'Failed to score resume'
      });
    }

    // Clean up file
    await fileCleanup.deleteFile(filePath);

    // Return results
    res.json({
      success: true,
      data: {
        filename: req.file.originalname,
        text: parsedResume.text,
        score: scoreResult.score,
        breakdown: scoreResult.breakdown,
        feedback: scoreResult.feedback,
        recommendations: scoreResult.recommendations
      }
    });

  } catch (error) {
    console.error('Error in /score endpoint:', error);
    
    // Clean up file on error
    if (filePath) {
      await fileCleanup.deleteFile(filePath);
    }

    res.status(500).json({
      success: false,
      error: error.message || 'Internal server error'
    });
  }
});

/**
 * POST /api/resume/target
 * Match resume to job description
 */
router.post('/target', upload.single('resume'), async (req, res) => {
  let filePath = null;
  
  try {
    if (!req.file) {
      return res.status(400).json({
        success: false,
        error: 'No file uploaded. Please upload a PDF or DOCX file.'
      });
    }

    const { jobDescription } = req.body;
    
    if (!jobDescription || jobDescription.trim().length === 0) {
      await fileCleanup.deleteFile(req.file.path);
      return res.status(400).json({
        success: false,
        error: 'Job description is required'
      });
    }

    filePath = req.file.path;
    console.log(`Matching resume: ${req.file.originalname}`);

    // Step 1: Validate PDF if applicable
    if (path.extname(req.file.originalname).toLowerCase() === '.pdf') {
      const validation = await pythonService.validatePDF(filePath);
      
      if (!validation.success) {
        await fileCleanup.deleteFile(filePath);
        return res.status(400).json({
          success: false,
          error: validation.error || 'PDF validation failed'
        });
      }
    }

    // Step 2: Match job
    console.log('Matching resume to job description...');
    const matchResult = await pythonService.matchJob(filePath, jobDescription);
    
    if (!matchResult.success) {
      await fileCleanup.deleteFile(filePath);
      return res.status(500).json({
        success: false,
        error: matchResult.error || 'Failed to match resume'
      });
    }

    // Clean up file
    await fileCleanup.deleteFile(filePath);

    // Return results
    res.json({
      success: true,
      data: {
        filename: req.file.originalname,
        matchPercentage: matchResult.matchPercentage,
        resumeKeywords: matchResult.resumeKeywords,
        jobKeywords: matchResult.jobKeywords,
        missingKeywords: matchResult.missingKeywords,
        matchedKeywords: matchResult.matchedKeywords,
        suggestions: matchResult.suggestions
      }
    });

  } catch (error) {
    console.error('Error in /target endpoint:', error);
    
    if (filePath) {
      await fileCleanup.deleteFile(filePath);
    }

    res.status(500).json({
      success: false,
      error: error.message || 'Internal server error'
    });
  }
});

/**
 * POST /api/resume/improve
 * Get improvement suggestions for resume
 */
router.post('/improve', upload.single('resume'), async (req, res) => {
  let filePath = null;
  
  try {
    if (!req.file) {
      return res.status(400).json({
        success: false,
        error: 'No file uploaded. Please upload a PDF or DOCX file.'
      });
    }

    filePath = req.file.path;
    console.log(`Analyzing resume for improvements: ${req.file.originalname}`);

    // Step 1: Validate PDF if applicable
    if (path.extname(req.file.originalname).toLowerCase() === '.pdf') {
      const validation = await pythonService.validatePDF(filePath);
      
      if (!validation.success) {
        await fileCleanup.deleteFile(filePath);
        return res.status(400).json({
          success: false,
          error: validation.error || 'PDF validation failed'
        });
      }
    }

    // Step 2: Get improvements
    console.log('Generating improvement suggestions...');
    const improveResult = await pythonService.improveResume(filePath);
    
    if (!improveResult.success) {
      await fileCleanup.deleteFile(filePath);
      return res.status(500).json({
        success: false,
        error: improveResult.error || 'Failed to generate improvements'
      });
    }

    // Clean up file
    await fileCleanup.deleteFile(filePath);

    // Return results
    res.json({
      success: true,
      data: {
        filename: req.file.originalname,
        improvements: improveResult.improvements,
        bulletAnalysis: improveResult.bulletAnalysis,
        overallSuggestions: improveResult.overallSuggestions
      }
    });

  } catch (error) {
    console.error('Error in /improve endpoint:', error);
    
    if (filePath) {
      await fileCleanup.deleteFile(filePath);
    }

    res.status(500).json({
      success: false,
      error: error.message || 'Internal server error'
    });
  }
});

module.exports = router;
