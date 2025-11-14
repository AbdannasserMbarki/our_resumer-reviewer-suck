const express = require('express');
const router = express.Router();
const cacheService = require('../services/cacheService');
const database = require('../services/database');
const { healthCheckLimiter } = require('../middleware/rateLimiter');
const { logger } = require('../services/logger');
const fs = require('fs-extra');
const path = require('path');

router.get('/', healthCheckLimiter, async (req, res) => {
  const healthCheck = {
    success: true,
    status: 'healthy',
    timestamp: new Date().toISOString(),
    service: 'Resume Reviewer API',
    version: process.env.npm_package_version || '1.0.0',
    environment: process.env.NODE_ENV || 'development',
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    services: {}
  };

  try {
    // Check cache service
    try {
      const cacheStats = await cacheService.getStats();
      healthCheck.services.cache = {
        status: cacheStats.connected ? 'healthy' : 'unavailable',
        connected: cacheStats.connected,
        details: cacheStats.connected ? 'Redis connection active' : 'Redis not available'
      };
    } catch (error) {
      healthCheck.services.cache = {
        status: 'error',
        connected: false,
        error: error.message
      };
    }

    // Check database service
    healthCheck.services.database = {
      status: database.isConnected ? 'healthy' : 'unavailable',
      connected: database.isConnected,
      details: database.isConnected ? 'PostgreSQL connection active' : 'Database not configured'
    };

    // Check uploads directory
    const uploadsDir = path.join(__dirname, '..', 'uploads', 'temp');
    try {
      await fs.access(uploadsDir);
      const stats = await fs.stat(uploadsDir);
      healthCheck.services.fileSystem = {
        status: 'healthy',
        uploadsDirectory: uploadsDir,
        accessible: true,
        isDirectory: stats.isDirectory()
      };
    } catch (error) {
      healthCheck.services.fileSystem = {
        status: 'error',
        uploadsDirectory: uploadsDir,
        accessible: false,
        error: error.message
      };
      healthCheck.success = false;
      healthCheck.status = 'degraded';
    }

    // Check Python availability
    try {
      const pythonPath = process.env.PYTHON_PATH || 'python';
      healthCheck.services.python = {
        status: 'unknown',
        path: pythonPath,
        details: 'Python availability not tested in health check'
      };
    } catch (error) {
      healthCheck.services.python = {
        status: 'error',
        error: error.message
      };
    }

    // Overall health assessment
    const serviceStatuses = Object.values(healthCheck.services).map(s => s.status);
    if (serviceStatuses.includes('error')) {
      healthCheck.status = 'degraded';
      healthCheck.success = false;
    } else if (serviceStatuses.includes('unavailable')) {
      healthCheck.status = 'partial';
    }

    // Log health check if there are issues
    if (healthCheck.status !== 'healthy') {
      logger.warn('Health check shows degraded status', healthCheck);
    }

    res.status(healthCheck.success ? 200 : 503).json(healthCheck);

  } catch (error) {
    logger.error('Health check failed:', error);
    res.status(500).json({
      success: false,
      status: 'error',
      timestamp: new Date().toISOString(),
      service: 'Resume Reviewer API',
      error: error.message
    });
  }
});

// Detailed health endpoint for monitoring systems
router.get('/detailed', healthCheckLimiter, async (req, res) => {
  try {
    const detailed = {
      timestamp: new Date().toISOString(),
      service: 'Resume Reviewer API',
      system: {
        nodeVersion: process.version,
        platform: process.platform,
        arch: process.arch,
        uptime: process.uptime(),
        memory: process.memoryUsage(),
        cpu: process.cpuUsage(),
        pid: process.pid
      },
      environment: {
        nodeEnv: process.env.NODE_ENV,
        port: process.env.PORT,
        pythonPath: process.env.PYTHON_PATH
      }
    };

    // Add usage statistics if database is available
    if (database.isConnected) {
      try {
        const usageStats = await database.getUsageStats(7);
        detailed.usage = {
          last7Days: usageStats
        };
      } catch (error) {
        detailed.usage = { error: 'Failed to fetch usage statistics' };
      }
    }

    res.json(detailed);
  } catch (error) {
    logger.error('Detailed health check failed:', error);
    res.status(500).json({
      error: 'Failed to generate detailed health report',
      timestamp: new Date().toISOString()
    });
  }
});

module.exports = router;
