const winston = require('winston');
const DailyRotateFile = require('winston-daily-rotate-file');
const path = require('path');
const fs = require('fs-extra');

// Ensure logs directory exists
const logsDir = path.join(__dirname, '..', 'logs');
fs.ensureDirSync(logsDir);

// Custom format for logs
const logFormat = winston.format.combine(
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  winston.format.errors({ stack: true }),
  winston.format.json(),
  winston.format.prettyPrint()
);

// Console format for development
const consoleFormat = winston.format.combine(
  winston.format.colorize(),
  winston.format.timestamp({ format: 'HH:mm:ss' }),
  winston.format.printf(({ timestamp, level, message, ...meta }) => {
    let msg = `${timestamp} [${level}]: ${message}`;
    if (Object.keys(meta).length > 0) {
      msg += ` ${JSON.stringify(meta)}`;
    }
    return msg;
  })
);

// Create logger instance
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: logFormat,
  defaultMeta: { service: 'resume-reviewer-api' },
  transports: [
    // Error log file
    new DailyRotateFile({
      filename: path.join(logsDir, 'error-%DATE%.log'),
      datePattern: 'YYYY-MM-DD',
      level: 'error',
      maxSize: '20m',
      maxFiles: '14d',
      zippedArchive: true
    }),
    
    // Combined log file
    new DailyRotateFile({
      filename: path.join(logsDir, 'combined-%DATE%.log'),
      datePattern: 'YYYY-MM-DD',
      maxSize: '20m',
      maxFiles: '14d',
      zippedArchive: true
    }),
    
    // Console output for development
    new winston.transports.Console({
      format: process.env.NODE_ENV === 'production' ? logFormat : consoleFormat,
      level: process.env.NODE_ENV === 'production' ? 'warn' : 'debug'
    })
  ],
  
  // Handle uncaught exceptions
  exceptionHandlers: [
    new DailyRotateFile({
      filename: path.join(logsDir, 'exceptions-%DATE%.log'),
      datePattern: 'YYYY-MM-DD',
      maxSize: '20m',
      maxFiles: '14d'
    })
  ],
  
  // Handle unhandled promise rejections
  rejectionHandlers: [
    new DailyRotateFile({
      filename: path.join(logsDir, 'rejections-%DATE%.log'),
      datePattern: 'YYYY-MM-DD',
      maxSize: '20m',
      maxFiles: '14d'
    })
  ]
});

// Add request logging middleware
const requestLogger = (req, res, next) => {
  const start = Date.now();
  
  // Log request
  logger.info('HTTP Request', {
    method: req.method,
    url: req.url,
    userAgent: req.get('User-Agent'),
    ip: req.ip,
    timestamp: new Date().toISOString()
  });
  
  // Override res.end to log response
  const originalEnd = res.end;
  res.end = function(...args) {
    const duration = Date.now() - start;
    
    logger.info('HTTP Response', {
      method: req.method,
      url: req.url,
      statusCode: res.statusCode,
      duration: `${duration}ms`,
      timestamp: new Date().toISOString()
    });
    
    originalEnd.apply(this, args);
  };
  
  next();
};

// Performance monitoring
const performanceLogger = {
  startTimer: (operation) => {
    const start = process.hrtime.bigint();
    return {
      end: () => {
        const end = process.hrtime.bigint();
        const duration = Number(end - start) / 1000000; // Convert to milliseconds
        
        logger.info('Performance Metric', {
          operation,
          duration: `${duration.toFixed(2)}ms`,
          timestamp: new Date().toISOString()
        });
        
        return duration;
      }
    };
  }
};

// Error logging helper
const logError = (error, context = {}) => {
  logger.error('Application Error', {
    message: error.message,
    stack: error.stack,
    ...context,
    timestamp: new Date().toISOString()
  });
};

// Cache operation logging
const logCacheOperation = (operation, key, hit = null) => {
  logger.debug('Cache Operation', {
    operation,
    key,
    hit,
    timestamp: new Date().toISOString()
  });
};

// Python script execution logging
const logPythonExecution = (script, args, duration, success, error = null) => {
  const logData = {
    script,
    args: args.length > 0 ? args : undefined,
    duration: `${duration}ms`,
    success,
    timestamp: new Date().toISOString()
  };
  
  if (error) {
    logData.error = error;
  }
  
  logger.info('Python Script Execution', logData);
};

module.exports = {
  logger,
  requestLogger,
  performanceLogger,
  logError,
  logCacheOperation,
  logPythonExecution
};
