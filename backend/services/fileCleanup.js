const fs = require('fs-extra');
const path = require('path');

class FileCleanupService {
  /**
   * Delete a file safely
   * @param {string} filePath - Path to file to delete
   */
  async deleteFile(filePath) {
    try {
      if (await fs.pathExists(filePath)) {
        await fs.unlink(filePath);
        console.log(`Deleted file: ${filePath}`);
      }
    } catch (error) {
      console.error(`Error deleting file ${filePath}:`, error.message);
    }
  }

  /**
   * Delete multiple files
   * @param {Array<string>} filePaths - Array of file paths to delete
   */
  async deleteFiles(filePaths) {
    await Promise.all(filePaths.map(fp => this.deleteFile(fp)));
  }

  /**
   * Clean up old temporary files (older than specified age)
   * @param {string} directory - Directory to clean
   * @param {number} maxAgeMs - Maximum age in milliseconds (default: 1 hour)
   */
  async cleanupOldFiles(directory, maxAgeMs = 3600000) {
    try {
      const files = await fs.readdir(directory);
      const now = Date.now();

      for (const file of files) {
        if (file === '.gitkeep') continue;
        
        const filePath = path.join(directory, file);
        const stats = await fs.stat(filePath);
        
        const fileAge = now - stats.mtimeMs;
        
        if (fileAge > maxAgeMs) {
          await this.deleteFile(filePath);
        }
      }
    } catch (error) {
      console.error(`Error cleaning up directory ${directory}:`, error.message);
    }
  }

  /**
   * Start periodic cleanup job
   * @param {string} directory - Directory to clean
   * @param {number} intervalMs - Cleanup interval in milliseconds (default: 30 minutes)
   * @param {number} maxAgeMs - Maximum file age in milliseconds (default: 1 hour)
   */
  startPeriodicCleanup(directory, intervalMs = 1800000, maxAgeMs = 3600000) {
    setInterval(() => {
      this.cleanupOldFiles(directory, maxAgeMs);
    }, intervalMs);
    
    // Run immediately on start
    this.cleanupOldFiles(directory, maxAgeMs);
  }
}

module.exports = new FileCleanupService();
