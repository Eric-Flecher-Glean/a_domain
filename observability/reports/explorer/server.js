#!/usr/bin/env node

/**
 * Report Explorer Server
 * Simple Node.js backend to browse and explore workflow timeline reports
 */

const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Paths
const REPORTS_DIR = path.join(__dirname, '../../reports-output');
const EXPLORER_DIR = __dirname;

// Serve static files (HTML, CSS, JS)
app.use(express.static(EXPLORER_DIR));

// Serve report files
app.use('/reports', express.static(REPORTS_DIR));

/**
 * Extract metadata from HTML report file
 */
function extractMetadataFromHtml(htmlContent, filename) {
  try {
    // Extract TIMELINE_DATA JSON from script tag
    const match = htmlContent.match(/const TIMELINE_DATA = ({.*?});/s);
    if (!match) {
      console.warn(`No TIMELINE_DATA found in ${filename}`);
      return null;
    }

    const timelineData = JSON.parse(match[1]);
    const sessionId = filename.replace('-timeline.html', '');

    // Calculate total duration from rows
    const totalDuration = timelineData.rows.reduce((sum, row) => sum + (row.duration || 0), 0);

    // Determine overall status
    const hasErrors = timelineData.rows.some(row => row.status === 'error');
    const status = hasErrors ? 'error' : 'success';

    // Get quality score if available
    const validationRow = timelineData.rows.find(row => row.type === 'validation');
    const qualityScore = validationRow?.attributes?.['validation.quality_score'] || null;

    // Extract errors
    const errors = timelineData.rows
      .filter(row => row.error)
      .map(row => ({
        stage: row.name,
        message: row.error.message,
        type: row.error.type
      }));

    return {
      sessionId: timelineData.sessionId || sessionId,
      date: timelineData.startTime,
      task: timelineData.task || 'Unknown Task',
      status: status,
      duration: Math.round(totalDuration),
      workflowId: 'prompt-generation',
      attempts: 1, // TODO: Extract from metadata if available
      qualityScore: qualityScore,
      errors: errors,
      stages: timelineData.rows.map(row => ({
        name: row.name,
        duration: Math.round(row.duration || 0),
        status: row.status
      })),
      outputPath: timelineData.outputPath || null,
      reportPath: `/reports/${filename}`,
      filename: filename
    };
  } catch (error) {
    console.error(`Error parsing ${filename}:`, error.message);
    return null;
  }
}

/**
 * Scan reports directory and extract metadata
 */
function scanReports() {
  try {
    if (!fs.existsSync(REPORTS_DIR)) {
      console.warn(`Reports directory not found: ${REPORTS_DIR}`);
      return [];
    }

    const files = fs.readdirSync(REPORTS_DIR)
      .filter(file => file.endsWith('-timeline.html'))
      .sort()
      .reverse(); // Newest first

    const reports = [];

    for (const file of files) {
      const filePath = path.join(REPORTS_DIR, file);
      const htmlContent = fs.readFileSync(filePath, 'utf-8');
      const metadata = extractMetadataFromHtml(htmlContent, file);

      if (metadata) {
        // Get file stats for creation time
        const stats = fs.statSync(filePath);
        metadata.fileCreated = stats.mtime;
        reports.push(metadata);
      }
    }

    return reports;
  } catch (error) {
    console.error('Error scanning reports:', error);
    return [];
  }
}

/**
 * Calculate summary statistics
 */
function calculateStats(reports) {
  const total = reports.length;
  const successCount = reports.filter(r => r.status === 'success').length;
  const errorCount = reports.filter(r => r.status === 'error').length;
  const successRate = total > 0 ? Math.round((successCount / total) * 100) : 0;

  const totalDuration = reports.reduce((sum, r) => sum + r.duration, 0);
  const avgDuration = total > 0 ? Math.round(totalDuration / total) : 0;

  // Count runs by day
  const runsByDay = {};
  reports.forEach(r => {
    const date = new Date(r.date).toISOString().split('T')[0];
    runsByDay[date] = (runsByDay[date] || 0) + 1;
  });

  // Count errors by type
  const errorsByType = {};
  reports.forEach(r => {
    r.errors.forEach(e => {
      errorsByType[e.type] = (errorsByType[e.type] || 0) + 1;
    });
  });

  return {
    totalRuns: total,
    successCount: successCount,
    errorCount: errorCount,
    successRate: successRate,
    avgDuration: avgDuration,
    runsByDay: runsByDay,
    errorsByType: errorsByType
  };
}

/**
 * Filter reports based on query parameters
 */
function filterReports(reports, query) {
  let filtered = [...reports];

  // Filter by status
  if (query.status && query.status !== 'all') {
    filtered = filtered.filter(r => r.status === query.status);
  }

  // Search in task description
  if (query.search) {
    const searchLower = query.search.toLowerCase();
    filtered = filtered.filter(r =>
      r.task.toLowerCase().includes(searchLower) ||
      r.sessionId.toLowerCase().includes(searchLower)
    );
  }

  // Filter by date range
  if (query.dateFrom) {
    const fromDate = new Date(query.dateFrom);
    filtered = filtered.filter(r => new Date(r.date) >= fromDate);
  }

  if (query.dateTo) {
    const toDate = new Date(query.dateTo);
    filtered = filtered.filter(r => new Date(r.date) <= toDate);
  }

  // Date preset filters (today, week, month)
  if (query.dateRange) {
    const now = new Date();
    let cutoffDate;

    switch (query.dateRange) {
      case 'today':
        cutoffDate = new Date(now.setHours(0, 0, 0, 0));
        break;
      case 'week':
        cutoffDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        break;
      case 'month':
        cutoffDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
        break;
      default:
        cutoffDate = null;
    }

    if (cutoffDate) {
      filtered = filtered.filter(r => new Date(r.date) >= cutoffDate);
    }
  }

  return filtered;
}

/**
 * Paginate results
 */
function paginateResults(items, page = 1, limit = 20) {
  const offset = (page - 1) * limit;
  const paginated = items.slice(offset, offset + limit);

  return {
    total: items.length,
    page: parseInt(page),
    limit: parseInt(limit),
    totalPages: Math.ceil(items.length / limit),
    data: paginated
  };
}

// =============================================================================
// API ROUTES
// =============================================================================

/**
 * GET /api/reports
 * List all reports with optional filtering and pagination
 */
app.get('/api/reports', (req, res) => {
  try {
    const allReports = scanReports();
    const filtered = filterReports(allReports, req.query);

    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 20;

    const result = paginateResults(filtered, page, limit);

    res.json({
      ...result,
      reports: result.data
    });
  } catch (error) {
    console.error('Error in /api/reports:', error);
    res.status(500).json({ error: 'Failed to fetch reports' });
  }
});

/**
 * GET /api/reports/:sessionId
 * Get detailed metadata for a specific report
 */
app.get('/api/reports/:sessionId', (req, res) => {
  try {
    const { sessionId } = req.params;
    const filename = `${sessionId}-timeline.html`;
    const filePath = path.join(REPORTS_DIR, filename);

    if (!fs.existsSync(filePath)) {
      return res.status(404).json({ error: 'Report not found' });
    }

    const htmlContent = fs.readFileSync(filePath, 'utf-8');
    const metadata = extractMetadataFromHtml(htmlContent, filename);

    if (!metadata) {
      return res.status(500).json({ error: 'Failed to parse report' });
    }

    res.json(metadata);
  } catch (error) {
    console.error('Error in /api/reports/:sessionId:', error);
    res.status(500).json({ error: 'Failed to fetch report details' });
  }
});

/**
 * GET /api/stats
 * Get summary statistics across all reports
 */
app.get('/api/stats', (req, res) => {
  try {
    const allReports = scanReports();
    const filtered = filterReports(allReports, req.query);
    const stats = calculateStats(filtered);

    res.json(stats);
  } catch (error) {
    console.error('Error in /api/stats:', error);
    res.status(500).json({ error: 'Failed to calculate statistics' });
  }
});

/**
 * GET /api/refresh
 * Force refresh of report cache (useful after generating new reports)
 */
app.get('/api/refresh', (req, res) => {
  try {
    const reports = scanReports();
    res.json({
      success: true,
      count: reports.length,
      message: `Refreshed ${reports.length} reports`
    });
  } catch (error) {
    console.error('Error in /api/refresh:', error);
    res.status(500).json({ error: 'Failed to refresh reports' });
  }
});

// Root route - serve the main app
app.get('/', (req, res) => {
  res.sendFile(path.join(EXPLORER_DIR, 'index.html'));
});

// =============================================================================
// START SERVER
// =============================================================================

app.listen(PORT, () => {
  console.log('');
  console.log('📊 Workflow Report Explorer');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log(`🚀 Server running at: http://localhost:${PORT}`);
  console.log(`📂 Reports directory: ${REPORTS_DIR}`);
  console.log('');

  // Initial scan
  const reports = scanReports();
  console.log(`✅ Loaded ${reports.length} reports`);

  if (reports.length === 0) {
    console.log('');
    console.log('⚠️  No reports found. Generate some workflows first:');
    console.log('   make xml-prompt-ab TASK="your task"');
  }

  console.log('');
  console.log('Press Ctrl+C to stop');
  console.log('');
});
