const redis = require('redis');
const crypto = require('crypto');
const fs = require('fs-extra');

class CacheService {
  constructor() {
    this.client = null;
    this.isConnected = false;
    this.errorLogged = false; // Track if we've already logged the error
    this.init();
  }

  async init() {
    try {
      this.client = redis.createClient({
        host: process.env.REDIS_HOST || 'localhost',
        port: process.env.REDIS_PORT || 6379,
        password: process.env.REDIS_PASSWORD || undefined,
        db: process.env.REDIS_DB || 0,
        retry_strategy: (options) => {
          if (options.error && options.error.code === 'ECONNREFUSED') {
            if (!this.errorLogged) {
              console.warn('Redis connection refused. Running without cache.');
              this.errorLogged = true;
            }
            return undefined; // Don't retry
          }
          if (options.total_retry_time > 1000 * 60 * 60) {
            return new Error('Retry time exhausted');
          }
          if (options.attempt > 10) {
            return undefined;
          }
          return Math.min(options.attempt * 100, 3000);
        }
      });

      this.client.on('error', (err) => {
        if (!this.errorLogged) {
          console.warn('Redis Client Error:', err.message);
          this.errorLogged = true;
        }
        this.isConnected = false;
      });

      this.client.on('connect', () => {
        console.log('Redis connected successfully');
        this.isConnected = true;
      });

      this.client.on('ready', () => {
        console.log('Redis client ready');
        this.isConnected = true;
      });

      await this.client.connect();
    } catch (error) {
      if (!this.errorLogged) {
        console.warn('Redis initialization failed. Running without cache:', error.message);
        this.errorLogged = true;
      }
      this.isConnected = false;
    }
  }

  /**
   * Generate cache key based on file content hash
   * @param {Buffer} fileBuffer - File buffer
   * @param {string} operation - Operation type (score, parse, improve, etc.)
   * @param {string} additionalData - Additional data like job description
   * @returns {string} Cache key
   */
  generateCacheKey(fileBuffer, operation, additionalData = '') {
    const fileHash = crypto.createHash('md5').update(fileBuffer).digest('hex');
    const dataHash = additionalData ? crypto.createHash('md5').update(additionalData).digest('hex') : '';
    return `${operation}:${fileHash}:${dataHash}`;
  }

  /**
   * Get cached result
   * @param {string} key - Cache key
   * @returns {Promise<Object|null>} Cached result or null
   */
  async get(key) {
    if (!this.isConnected) {
      return null;
    }

    try {
      const result = await this.client.get(key);
      return result ? JSON.parse(result) : null;
    } catch (error) {
      console.warn('Cache get error:', error.message);
      return null;
    }
  }

  /**
   * Set cache result
   * @param {string} key - Cache key
   * @param {Object} value - Value to cache
   * @param {number} ttl - Time to live in seconds (default: 1 hour)
   */
  async set(key, value, ttl = 3600) {
    if (!this.isConnected) {
      return;
    }

    try {
      await this.client.setEx(key, ttl, JSON.stringify(value));
    } catch (error) {
      console.warn('Cache set error:', error.message);
    }
  }

  /**
   * Delete cache entry
   * @param {string} key - Cache key
   */
  async del(key) {
    if (!this.isConnected) {
      return;
    }

    try {
      await this.client.del(key);
    } catch (error) {
      console.warn('Cache delete error:', error.message);
    }
  }

  /**
   * Get cache statistics
   * @returns {Promise<Object>} Cache statistics
   */
  async getStats() {
    if (!this.isConnected) {
      return { connected: false };
    }

    try {
      const info = await this.client.info('memory');
      const keyspace = await this.client.info('keyspace');
      
      return {
        connected: true,
        memory: info,
        keyspace: keyspace
      };
    } catch (error) {
      console.warn('Cache stats error:', error.message);
      return { connected: false, error: error.message };
    }
  }

  /**
   * Clear all cache entries
   */
  async flush() {
    if (!this.isConnected) {
      return;
    }

    try {
      await this.client.flushDb();
      console.log('Cache flushed successfully');
    } catch (error) {
      console.warn('Cache flush error:', error.message);
    }
  }

  /**
   * Close Redis connection
   */
  async close() {
    if (this.client && this.isConnected) {
      await this.client.quit();
      this.isConnected = false;
    }
  }
}

module.exports = new CacheService();
