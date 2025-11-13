const express = require('express');
const cors = require('cors');
const path = require('path');
const fs = require('fs-extra');
require('dotenv').config();

const resumeRoutes = require('./routes/resume');
const healthRoutes = require('./routes/health');

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Ensure uploads/temp directory exists
const uploadsDir = path.join(__dirname, 'uploads', 'temp');
fs.ensureDirSync(uploadsDir);

// Routes
app.use('/api/resume', resumeRoutes);
app.use('/api/health', healthRoutes);

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Error:', err);
  
  // Handle Multer errors
  if (err.code === 'LIMIT_FILE_SIZE') {
    return res.status(400).json({
      success: false,
      error: 'File too large. Maximum size is 2MB.'
    });
  }
  
  if (err.code === 'LIMIT_UNEXPECTED_FILE') {
    return res.status(400).json({
      success: false,
      error: 'Unexpected field in file upload.'
    });
  }
  
  res.status(err.status || 500).json({
    success: false,
    error: err.message || 'Internal server error'
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`Uploads directory: ${uploadsDir}`);
});

module.exports = app;
