const express = require('express');
const cors = require('cors');
const path = require('path');
const fs = require('fs-extra');
require('dotenv').config();

const { logger, requestLogger, logError } = require('./services/logger');
const { generalLimiter } = require('./middleware/rateLimiter');
const cacheService = require('./services/cacheService');

const resumeRoutes = require('./routes/resume');
const healthRoutes = require('./routes/health');
const pdfRoutes = require('./routes/pdf');

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors({
  origin: process.env.CORS_ORIGIN || 'http://localhost:3000',
  credentials: true
}));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Request logging
app.use(requestLogger);

// Rate limiting
app.use(generalLimiter);

// Ensure uploads/temp directory exists
const uploadsDir = path.join(__dirname, 'uploads', 'temp');
fs.ensureDirSync(uploadsDir);

logger.info('Server initialization', {
  uploadsDir,
  nodeEnv: process.env.NODE_ENV,
  port: PORT
});

// Routes
app.use('/api/resume', resumeRoutes);
app.use('/api/health', healthRoutes);
app.use('/api/pdf', pdfRoutes);

// Error handling middleware
app.use((err, req, res, next) => {
  // Log error with context
  logError(err, {
    url: req.url,
    method: req.method,
    ip: req.ip,
    userAgent: req.get('User-Agent')
  });
  
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
  
  // Handle rate limiting errors
  if (err.status === 429) {
    return res.status(429).json({
      success: false,
      error: 'Too many requests, please try again later.'
    });
  }
  
  res.status(err.status || 500).json({
    success: false,
    error: process.env.NODE_ENV === 'production' ? 'Internal server error' : err.message
  });
});

// Graceful shutdown
process.on('SIGTERM', async () => {
  logger.info('SIGTERM received, shutting down gracefully');
  await cacheService.close();
  process.exit(0);
});

process.on('SIGINT', async () => {
  logger.info('SIGINT received, shutting down gracefully');
  await cacheService.close();
  process.exit(0);
});

// Start server
app.listen(PORT, () => {
  logger.info('Server started successfully', {
    port: PORT,
    environment: process.env.NODE_ENV || 'development',
    uploadsDirectory: uploadsDir
  });
});

module.exports = app;
