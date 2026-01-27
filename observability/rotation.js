/**
 * File Rotation and Retention Management
 *
 * Handles daily rotation and cleanup of observability files
 * based on retention policies.
 */

const fs = require('fs');
const path = require('path');
const { promisify } = require('util');
const zlib = require('zlib');

const readdir = promisify(fs.readdir);
const stat = promisify(fs.stat);
const unlink = promisify(fs.unlink);
const gzip = promisify(zlib.gzip);

/**
 * Rotation Manager
 */
class RotationManager {
  constructor(config) {
    this.config = config;
  }

  /**
   * Run cleanup for all observability directories
   */
  async runCleanup() {
    console.log('Running observability file cleanup...');

    const tasks = [
      this.cleanupDirectory('observability/traces', this.config.exporters.traces.retention_days),
      this.cleanupDirectory('observability/metrics', this.config.exporters.metrics.retention_days),
      this.cleanupDirectory('observability/events', this.config.exporters.events.retention_days),
      this.cleanupDirectory('observability/logs', this.config.exporters.logs.retention_days)
    ];

    await Promise.all(tasks);

    console.log('Cleanup complete');
  }

  /**
   * Cleanup a specific directory
   */
  async cleanupDirectory(dir, retentionDays) {
    if (!fs.existsSync(dir)) {
      return;
    }

    try {
      const files = await readdir(dir);
      const now = Date.now();
      const retentionMs = retentionDays * 24 * 60 * 60 * 1000;
      const compressionThresholdMs = 7 * 24 * 60 * 60 * 1000; // 7 days

      for (const file of files) {
        // Skip .gitkeep
        if (file === '.gitkeep') continue;

        const filePath = path.join(dir, file);
        const stats = await stat(filePath);
        const age = now - stats.mtime.getTime();

        // Delete files older than retention period
        if (age > retentionMs) {
          await unlink(filePath);
          console.log(`  Deleted: ${file} (${Math.floor(age / (24 * 60 * 60 * 1000))} days old)`);
        }
        // Compress files older than 7 days (if not already compressed)
        else if (age > compressionThresholdMs && !file.endsWith('.gz')) {
          await this.compressFile(filePath);
          console.log(`  Compressed: ${file}`);
        }
      }
    } catch (error) {
      console.error(`Cleanup failed for ${dir}:`, error);
    }
  }

  /**
   * Compress a file using gzip
   */
  async compressFile(filePath) {
    try {
      const content = fs.readFileSync(filePath);
      const compressed = await gzip(content);
      fs.writeFileSync(`${filePath}.gz`, compressed);
      await unlink(filePath);
    } catch (error) {
      console.error(`Failed to compress ${filePath}:`, error);
    }
  }

  /**
   * Get file statistics
   */
  async getStats() {
    const stats = {
      traces: await this.getDirectoryStats('observability/traces'),
      metrics: await this.getDirectoryStats('observability/metrics'),
      events: await this.getDirectoryStats('observability/events'),
      logs: await this.getDirectoryStats('observability/logs')
    };

    return stats;
  }

  /**
   * Get statistics for a directory
   */
  async getDirectoryStats(dir) {
    if (!fs.existsSync(dir)) {
      return { files: 0, totalSize: 0, oldestFile: null, newestFile: null };
    }

    try {
      const files = await readdir(dir);
      let totalSize = 0;
      let oldestTime = Infinity;
      let newestTime = 0;
      let fileCount = 0;

      for (const file of files) {
        if (file === '.gitkeep') continue;

        const filePath = path.join(dir, file);
        const stats = await stat(filePath);

        totalSize += stats.size;
        fileCount++;

        if (stats.mtime.getTime() < oldestTime) {
          oldestTime = stats.mtime.getTime();
        }
        if (stats.mtime.getTime() > newestTime) {
          newestTime = stats.mtime.getTime();
        }
      }

      return {
        files: fileCount,
        totalSize: this.formatBytes(totalSize),
        oldestFile: oldestTime !== Infinity ? new Date(oldestTime).toISOString() : null,
        newestFile: newestTime !== 0 ? new Date(newestTime).toISOString() : null
      };
    } catch (error) {
      console.error(`Failed to get stats for ${dir}:`, error);
      return { files: 0, totalSize: 0, oldestFile: null, newestFile: null };
    }
  }

  /**
   * Format bytes to human-readable format
   */
  formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  }
}

/**
 * CLI interface for rotation management
 */
async function main() {
  const configPath = path.join(__dirname, 'otel-config.json');

  if (!fs.existsSync(configPath)) {
    console.error('Configuration file not found:', configPath);
    process.exit(1);
  }

  const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  const manager = new RotationManager(config);

  const command = process.argv[2];

  switch (command) {
    case 'cleanup':
      await manager.runCleanup();
      break;

    case 'stats':
      const stats = await manager.getStats();
      console.log('\nObservability File Statistics:');
      console.log('===============================');
      console.log('\nTraces:');
      console.log(`  Files: ${stats.traces.files}`);
      console.log(`  Total Size: ${stats.traces.totalSize}`);
      console.log(`  Oldest: ${stats.traces.oldestFile || 'N/A'}`);
      console.log(`  Newest: ${stats.traces.newestFile || 'N/A'}`);
      console.log('\nMetrics:');
      console.log(`  Files: ${stats.metrics.files}`);
      console.log(`  Total Size: ${stats.metrics.totalSize}`);
      console.log(`  Oldest: ${stats.metrics.oldestFile || 'N/A'}`);
      console.log(`  Newest: ${stats.metrics.newestFile || 'N/A'}`);
      console.log('\nEvents:');
      console.log(`  Files: ${stats.events.files}`);
      console.log(`  Total Size: ${stats.events.totalSize}`);
      console.log(`  Oldest: ${stats.events.oldestFile || 'N/A'}`);
      console.log(`  Newest: ${stats.events.newestFile || 'N/A'}`);
      console.log('\nLogs:');
      console.log(`  Files: ${stats.logs.files}`);
      console.log(`  Total Size: ${stats.logs.totalSize}`);
      console.log(`  Oldest: ${stats.logs.oldestFile || 'N/A'}`);
      console.log(`  Newest: ${stats.logs.newestFile || 'N/A'}`);
      break;

    default:
      console.log('Usage:');
      console.log('  node rotation.js cleanup  - Run cleanup based on retention policy');
      console.log('  node rotation.js stats    - Show file statistics');
      break;
  }
}

// Run if called directly
if (require.main === module) {
  main().catch(error => {
    console.error('Error:', error);
    process.exit(1);
  });
}

module.exports = { RotationManager };
