const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs-extra');
const cacheService = require('./cacheService');

class PythonService {
  constructor() {
    this.pythonPath = process.env.PYTHON_PATH ;
    this.scriptsDir = path.join(__dirname, '..', '..', 'python');
  }

  /**
   * Execute a Python script and return parsed JSON result
   * @param {string} scriptName - Name of the Python script (without .py)
   * @param {Array} args - Arguments to pass to the script
   * @returns {Promise} - Resolves with parsed JSON result
   */
  async executeScript(scriptName, args = []) {
    return new Promise((resolve, reject) => {
      const scriptPath = path.join(this.scriptsDir, `${scriptName}.py`);
      
      const pythonProcess = spawn(this.pythonPath, [scriptPath, ...args]);
      
      let stdoutData = '';
      let stderrData = '';

      pythonProcess.stdout.on('data', (data) => {
        stdoutData += data.toString();
      });

      pythonProcess.stderr.on('data', (data) => {
        stderrData += data.toString();
      });

      pythonProcess.on('close', (code) => {
        if (code !== 0) {
          console.error(`Python script ${scriptName} failed with code ${code}`);
          console.error('stderr:', stderrData);
          return reject(new Error(`Python script failed: ${stderrData || 'Unknown error'}`));
        }

        try {
          const result = JSON.parse(stdoutData);
          resolve(result);
        } catch (error) {
          console.error('Failed to parse Python output:', stdoutData);
          reject(new Error(`Invalid JSON output from Python script: ${error.message}`));
        }
      });

      pythonProcess.on('error', (error) => {
        reject(new Error(`Failed to start Python process: ${error.message}`));
      });
    });
  }

  /**
   * Parse resume from file with caching
   */
  async parseResume(filePath) {
    try {
      const fileBuffer = await fs.readFile(filePath);
      const cacheKey = cacheService.generateCacheKey(fileBuffer, 'parse');
      
      // Try to get from cache first
      const cachedResult = await cacheService.get(cacheKey);
      if (cachedResult) {
        console.log('Cache hit for resume parsing');
        return cachedResult;
      }

      // Execute script if not in cache
      const result = await this.executeScript('resume_parser', [filePath]);
      
      // Cache the result if successful
      if (result.success) {
        await cacheService.set(cacheKey, result, 3600); // Cache for 1 hour
      }
      
      return result;
    } catch (error) {
      // Fallback to direct execution if caching fails
      console.warn('Cache operation failed, executing directly:', error.message);
      return this.executeScript('resume_parser', [filePath]);
    }
  }

  /**
   * Validate and sanitize PDF
   */
  async validatePDF(filePath) {
    return this.executeScript('pdf_validator', [filePath]);
  }

  /**
   * Score resume with caching
   */
  async scoreResume(filePath, jobDescription = '') {
    try {
      const fileBuffer = await fs.readFile(filePath);
      const cacheKey = cacheService.generateCacheKey(fileBuffer, 'score', jobDescription);
      
      // Try to get from cache first
      const cachedResult = await cacheService.get(cacheKey);
      if (cachedResult) {
        console.log('Cache hit for resume scoring');
        return cachedResult;
      }

      // Execute script if not in cache
      const result = await this.executeScript('resume_scorer', [filePath]);
      
      // Cache the result if successful
      if (result.success) {
        await cacheService.set(cacheKey, result, 1800); // Cache for 30 minutes
      }
      
      return result;
    } catch (error) {
      // Fallback to direct execution if caching fails
      console.warn('Cache operation failed, executing directly:', error.message);
      return this.executeScript('resume_scorer', [filePath]);
    }
  }

  /**
   * Extract keywords from text
   */
  async extractKeywords(text) {
    return this.executeScript('keyword_extractor', [text]);
  }

  /**
   * Match resume to job description with caching
   */
  async matchJob(resumePath, jobDescription) {
    try {
      const fileBuffer = await fs.readFile(resumePath);
      const cacheKey = cacheService.generateCacheKey(fileBuffer, 'match', jobDescription);
      
      // Try to get from cache first
      const cachedResult = await cacheService.get(cacheKey);
      if (cachedResult) {
        console.log('Cache hit for job matching');
        return cachedResult;
      }

      // Execute script if not in cache
      const result = await this.executeScript('job_matcher', [resumePath, jobDescription]);
      
      // Cache the result if successful
      if (result.success) {
        await cacheService.set(cacheKey, result, 1800); // Cache for 30 minutes
      }
      
      return result;
    } catch (error) {
      // Fallback to direct execution if caching fails
      console.warn('Cache operation failed, executing directly:', error.message);
      return this.executeScript('job_matcher', [resumePath, jobDescription]);
    }
  }

  /**
   * Get improvement suggestions with caching
   */
  async improveResume(filePath) {
    try {
      const fileBuffer = await fs.readFile(filePath);
      const cacheKey = cacheService.generateCacheKey(fileBuffer, 'improve');
      
      // Try to get from cache first
      const cachedResult = await cacheService.get(cacheKey);
      if (cachedResult) {
        console.log('Cache hit for resume improvement');
        return cachedResult;
      }

      // Execute script if not in cache
      const result = await this.executeScript('text_improver', [filePath]);
      
      // Cache the result if successful
      if (result.success) {
        await cacheService.set(cacheKey, result, 1800); // Cache for 30 minutes
      }
      
      return result;
    } catch (error) {
      // Fallback to direct execution if caching fails
      console.warn('Cache operation failed, executing directly:', error.message);
      return this.executeScript('text_improver', [filePath]);
    }
  }
}

module.exports = new PythonService();
