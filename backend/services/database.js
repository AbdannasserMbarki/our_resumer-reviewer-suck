const { Pool } = require('pg');
const { logger } = require('./logger');

class DatabaseService {
  constructor() {
    this.pool = null;
    this.isConnected = false;
    this.errorLogged = false; // Track if we've already logged the error
    this.init();
  }

  async init() {
    try {
      // Only initialize if DATABASE_URL is provided
      if (!process.env.DATABASE_URL && !process.env.DB_HOST) {
        logger.info('No database configuration found. Running without persistence.');
        return;
      }

      this.pool = new Pool({
        connectionString: process.env.DATABASE_URL,
        host: process.env.DB_HOST,
        port: process.env.DB_PORT || 5432,
        database: process.env.DB_NAME,
        user: process.env.DB_USER,
        password: process.env.DB_PASSWORD,
        ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false,
        max: 20,
        idleTimeoutMillis: 30000,
        connectionTimeoutMillis: 2000,
      });

      // Test connection
      const client = await this.pool.connect();
      await client.query('SELECT NOW()');
      client.release();

      this.isConnected = true;
      logger.info('Database connected successfully');

      // Create tables if they don't exist
      await this.createTables();
    } catch (error) {
      if (!this.errorLogged) {
        logger.warn('Database initialization failed. Running without persistence:', error.message);
        this.errorLogged = true;
      }
      this.isConnected = false;
    }
  }

  async createTables() {
    if (!this.isConnected) return;

    const createTablesQuery = `
      -- Analysis sessions table
      CREATE TABLE IF NOT EXISTS analysis_sessions (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        session_id VARCHAR(255),
        file_name VARCHAR(255),
        file_size INTEGER,
        file_type VARCHAR(10),
        analysis_type VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ip_address INET,
        user_agent TEXT
      );

      -- Analysis results table
      CREATE TABLE IF NOT EXISTS analysis_results (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        session_id UUID REFERENCES analysis_sessions(id) ON DELETE CASCADE,
        analysis_type VARCHAR(50) NOT NULL,
        score INTEGER,
        breakdown JSONB,
        feedback JSONB,
        recommendations JSONB,
        statistics JSONB,
        job_description TEXT,
        match_percentage DECIMAL(5,2),
        processing_time_ms INTEGER,
        cache_hit BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );

      -- System metrics table
      CREATE TABLE IF NOT EXISTS system_metrics (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        metric_name VARCHAR(100) NOT NULL,
        metric_value DECIMAL(10,2),
        metric_unit VARCHAR(20),
        tags JSONB,
        recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );

      -- Create indexes for better performance
      CREATE INDEX IF NOT EXISTS idx_analysis_sessions_created_at ON analysis_sessions(created_at);
      CREATE INDEX IF NOT EXISTS idx_analysis_sessions_ip ON analysis_sessions(ip_address);
      CREATE INDEX IF NOT EXISTS idx_analysis_results_session_id ON analysis_results(session_id);
      CREATE INDEX IF NOT EXISTS idx_analysis_results_type ON analysis_results(analysis_type);
      CREATE INDEX IF NOT EXISTS idx_system_metrics_name_time ON system_metrics(metric_name, recorded_at);
    `;

    try {
      await this.pool.query(createTablesQuery);
      logger.info('Database tables created/verified successfully');
    } catch (error) {
      if (!this.errorLogged) {
        logger.error('Failed to create database tables:', error);
        this.errorLogged = true;
      }
    }
  }

  /**
   * Create a new analysis session
   */
  async createSession(sessionData) {
    if (!this.isConnected) return null;

    try {
      const query = `
        INSERT INTO analysis_sessions (session_id, file_name, file_size, file_type, analysis_type, ip_address, user_agent)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING id
      `;
      
      const values = [
        sessionData.sessionId,
        sessionData.fileName,
        sessionData.fileSize,
        sessionData.fileType,
        sessionData.analysisType,
        sessionData.ipAddress,
        sessionData.userAgent
      ];

      const result = await this.pool.query(query, values);
      return result.rows[0].id;
    } catch (error) {
      logger.error('Failed to create analysis session:', error);
      return null;
    }
  }

  /**
   * Save analysis results
   */
  async saveAnalysisResult(sessionId, resultData) {
    if (!this.isConnected || !sessionId) return null;

    try {
      const query = `
        INSERT INTO analysis_results (
          session_id, analysis_type, score, breakdown, feedback, recommendations, 
          statistics, job_description, match_percentage, processing_time_ms, cache_hit
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        RETURNING id
      `;

      const values = [
        sessionId,
        resultData.analysisType,
        resultData.score || null,
        resultData.breakdown ? JSON.stringify(resultData.breakdown) : null,
        resultData.feedback ? JSON.stringify(resultData.feedback) : null,
        resultData.recommendations ? JSON.stringify(resultData.recommendations) : null,
        resultData.statistics ? JSON.stringify(resultData.statistics) : null,
        resultData.jobDescription || null,
        resultData.matchPercentage || null,
        resultData.processingTimeMs || null,
        resultData.cacheHit || false
      ];

      const result = await this.pool.query(query, values);
      return result.rows[0].id;
    } catch (error) {
      logger.error('Failed to save analysis result:', error);
      return null;
    }
  }

  /**
   * Record system metrics
   */
  async recordMetric(metricName, value, unit = null, tags = {}) {
    if (!this.isConnected) return;

    try {
      const query = `
        INSERT INTO system_metrics (metric_name, metric_value, metric_unit, tags)
        VALUES ($1, $2, $3, $4)
      `;

      await this.pool.query(query, [metricName, value, unit, JSON.stringify(tags)]);
    } catch (error) {
      logger.error('Failed to record metric:', error);
    }
  }

  /**
   * Get usage statistics
   */
  async getUsageStats(days = 7) {
    if (!this.isConnected) return null;

    try {
      const query = `
        SELECT 
          DATE(created_at) as date,
          COUNT(*) as total_analyses,
          COUNT(DISTINCT ip_address) as unique_users,
          analysis_type,
          AVG(CASE WHEN ar.processing_time_ms IS NOT NULL THEN ar.processing_time_ms END) as avg_processing_time
        FROM analysis_sessions s
        LEFT JOIN analysis_results ar ON s.id = ar.session_id
        WHERE s.created_at >= CURRENT_DATE - INTERVAL '${days} days'
        GROUP BY DATE(created_at), analysis_type
        ORDER BY date DESC, analysis_type
      `;

      const result = await this.pool.query(query);
      return result.rows;
    } catch (error) {
      logger.error('Failed to get usage stats:', error);
      return null;
    }
  }

  /**
   * Close database connection
   */
  async close() {
    if (this.pool) {
      await this.pool.end();
      this.isConnected = false;
      logger.info('Database connection closed');
    }
  }
}

module.exports = new DatabaseService();
