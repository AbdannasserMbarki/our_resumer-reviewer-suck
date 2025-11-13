const { spawn } = require('child_process');
const path = require('path');

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
   * Parse resume from file
   */
  async parseResume(filePath) {
    return this.executeScript('resume_parser', [filePath]);
  }

  /**
   * Validate and sanitize PDF
   */
  async validatePDF(filePath) {
    return this.executeScript('pdf_validator', [filePath]);
  }

  /**
   * Score resume
   */
  async scoreResume(filePath, jobDescription = '') {
    const args = jobDescription ? [filePath, jobDescription] : [filePath];
    return this.executeScript('resume_scorer', [filePath]);
  }

  /**
   * Extract keywords from text
   */
  async extractKeywords(text) {
    return this.executeScript('keyword_extractor', [text]);
  }

  /**
   * Match resume to job description
   */
  async matchJob(resumePath, jobDescription) {
    return this.executeScript('job_matcher', [resumePath, jobDescription]);
  }

  /**
   * Get improvement suggestions
   */
  async improveResume(filePath) {
    return this.executeScript('text_improver', [filePath]);
  }
}

module.exports = new PythonService();
