#!/usr/bin/env node
/**
 * a_domain Developer Portal Server
 * Serves static files, provides test execution API, and WebSocket streaming
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const sqlite3 = require('sqlite3').verbose();
const WebSocket = require('ws');

const PORT = process.env.PORT || 3001;
const HOST = '0.0.0.0';

// Serve from project root (one level up from web-portal)
const PROJECT_ROOT = path.join(__dirname, '..');
const DB_PATH = path.join(PROJECT_ROOT, '.logs', 'test_results.db');

// Ensure .logs directory exists
const logsDir = path.join(PROJECT_ROOT, '.logs');
if (!fs.existsSync(logsDir)) {
    fs.mkdirSync(logsDir, { recursive: true });
}

// Initialize SQLite database
const db = new sqlite3.Database(DB_PATH);

// Create test_results table if it doesn't exist
db.run(`
    CREATE TABLE IF NOT EXISTS test_results (
        run_id TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL,
        suite TEXT NOT NULL,
        pattern TEXT,
        exit_code INTEGER,
        duration REAL,
        status TEXT,
        output TEXT
    )
`);

const MIME_TYPES = {
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'application/javascript',
    '.json': 'application/json',
    '.md': 'text/markdown',
    '.txt': 'text/plain',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
};

// Store active test runs and WebSocket clients
const activeRuns = new Map();
const wsClients = new Set();

// Create HTTP server
const server = http.createServer((req, res) => {
    // Handle POST requests
    if (req.method === 'POST') {
        handlePostRequest(req, res);
        return;
    }

    // Handle GET requests
    handleGetRequest(req, res);
});

// Create WebSocket server
const wss = new WebSocket.Server({ server, path: '/ws' });

wss.on('connection', (ws) => {
    console.log('WebSocket client connected');
    wsClients.add(ws);

    ws.on('close', () => {
        console.log('WebSocket client disconnected');
        wsClients.delete(ws);
    });

    ws.on('error', (error) => {
        console.error('WebSocket error:', error);
        wsClients.delete(ws);
    });
});

function broadcastToClients(message) {
    const data = JSON.stringify(message);
    wsClients.forEach((client) => {
        if (client.readyState === WebSocket.OPEN) {
            client.send(data);
        }
    });
}

function handlePostRequest(req, res) {
    const url = req.url.split('?')[0];

    if (url === '/api/tests/run') {
        handleTestRun(req, res);
    } else {
        res.writeHead(404, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ success: false, message: 'Endpoint not found' }));
    }
}

function handleGetRequest(req, res) {
    const url = req.url.split('?')[0];

    // Handle API routes
    if (url === '/api/tests/history') {
        handleTestHistory(req, res);
        return;
    }

    if (url.startsWith('/api/tests/output/')) {
        handleTestOutput(req, res);
        return;
    }

    // Handle static file serving
    let filePath = url === '/' ? '/web-portal/index.html' : url;

    // Map /tests-dashboard to the HTML file
    if (url === '/tests-dashboard') {
        filePath = '/web-portal/tests-dashboard.html';
    }

    // Security: prevent directory traversal
    if (filePath.includes('..')) {
        res.writeHead(403);
        res.end('Forbidden');
        return;
    }

    // Determine full file path
    const fullPath = path.join(PROJECT_ROOT, filePath);

    // Security check
    const resolvedPath = path.resolve(fullPath);
    const resolvedRoot = path.resolve(PROJECT_ROOT);
    if (!resolvedPath.startsWith(resolvedRoot)) {
        res.writeHead(403);
        res.end('Forbidden');
        return;
    }

    const ext = path.extname(fullPath);
    const mimeType = MIME_TYPES[ext] || 'application/octet-stream';

    // Read and serve file
    fs.readFile(fullPath, (err, content) => {
        if (err) {
            if (err.code === 'ENOENT') {
                res.writeHead(404);
                res.end('404 Not Found: ' + url);
            } else {
                res.writeHead(500);
                res.end('Internal Server Error');
            }
        } else {
            res.writeHead(200, { 'Content-Type': mimeType });
            res.end(content);
        }
    });
}

function handleTestRun(req, res) {
    let body = '';

    req.on('data', (chunk) => {
        body += chunk.toString();
    });

    req.on('end', () => {
        try {
            const { suite, pattern } = JSON.parse(body);
            const runId = `run-${Date.now()}`;
            const timestamp = new Date().toISOString();

            // Build test command
            let command = 'make';
            let args = [];

            switch (suite) {
                case 'all':
                    args = ['test-all'];
                    break;
                case 'unit':
                    args = ['test-unit'];
                    break;
                case 'integration':
                    args = ['test-integration'];
                    break;
                case 'functional':
                    args = ['test-functional'];
                    break;
                default:
                    args = ['test-all'];
            }

            // Start test execution
            const startTime = Date.now();
            const testProcess = spawn(command, args, {
                cwd: PROJECT_ROOT,
                env: process.env
            });

            let outputBuffer = '';

            // Store active run
            activeRuns.set(runId, {
                process: testProcess,
                suite: suite,
                pattern: pattern,
                timestamp: timestamp,
                startTime: startTime
            });

            // Capture stdout
            testProcess.stdout.on('data', (data) => {
                const text = data.toString();
                outputBuffer += text;
                broadcastToClients({
                    type: 'output',
                    stream: 'stdout',
                    data: text,
                    runId: runId
                });
            });

            // Capture stderr
            testProcess.stderr.on('data', (data) => {
                const text = data.toString();
                outputBuffer += text;
                broadcastToClients({
                    type: 'output',
                    stream: 'stderr',
                    data: text,
                    runId: runId
                });
            });

            // Handle completion
            testProcess.on('close', (exitCode) => {
                const duration = ((Date.now() - startTime) / 1000).toFixed(2);
                const status = exitCode === 0 ? 'passed' : 'failed';

                // Save to database
                db.run(
                    `INSERT INTO test_results (run_id, timestamp, suite, pattern, exit_code, duration, status, output)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
                    [runId, timestamp, suite, pattern, exitCode, duration, status, outputBuffer],
                    (err) => {
                        if (err) {
                            console.error('Failed to save test result:', err);
                        }
                    }
                );

                // Broadcast completion
                broadcastToClients({
                    type: 'complete',
                    runId: runId,
                    suite: suite,
                    exitCode: exitCode,
                    duration: duration,
                    status: status
                });

                // Clean up
                activeRuns.delete(runId);
            });

            // Handle errors
            testProcess.on('error', (error) => {
                console.error('Test process error:', error);
                broadcastToClients({
                    type: 'error',
                    runId: runId,
                    message: error.message
                });
                activeRuns.delete(runId);
            });

            // Send success response
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({
                success: true,
                runId: runId,
                message: 'Test execution started'
            }));

        } catch (error) {
            console.error('Error parsing request:', error);
            res.writeHead(400, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({
                success: false,
                message: 'Invalid request: ' + error.message
            }));
        }
    });
}

function handleTestHistory(req, res) {
    db.all(
        `SELECT run_id, timestamp, suite, pattern, exit_code, duration, status
         FROM test_results
         ORDER BY timestamp DESC
         LIMIT 50`,
        [],
        (err, rows) => {
            if (err) {
                console.error('Database error:', err);
                res.writeHead(500, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({
                    success: false,
                    message: 'Database error'
                }));
                return;
            }

            // Format results
            const history = rows.map(row => ({
                runId: row.run_id,
                timestamp: row.timestamp,
                suite: row.suite,
                pattern: row.pattern,
                exitCode: row.exit_code,
                duration: row.duration,
                status: row.status
            }));

            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({
                success: true,
                history: history
            }));
        }
    );
}

function handleTestOutput(req, res) {
    const runId = req.url.split('/').pop();

    db.get(
        'SELECT output FROM test_results WHERE run_id = ?',
        [runId],
        (err, row) => {
            if (err) {
                console.error('Database error:', err);
                res.writeHead(500, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({
                    success: false,
                    message: 'Database error'
                }));
                return;
            }

            if (!row) {
                res.writeHead(404, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({
                    success: false,
                    message: 'Test run not found'
                }));
                return;
            }

            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({
                success: true,
                output: row.output
            }));
        }
    );
}

// Start server
server.listen(PORT, HOST, () => {
    console.log('');
    console.log('🚀 a_domain Developer Portal');
    console.log('════════════════════════════════════════');
    console.log(`✓ Server running at http://localhost:${PORT}`);
    console.log(`✓ Serving from: ${PROJECT_ROOT}`);
    console.log('✓ WebSocket enabled at ws://localhost:${PORT}/ws');
    console.log(`✓ Test database: ${DB_PATH}`);
    console.log('✓ Press Ctrl+C to stop');
    console.log('');
    console.log('Services:');
    console.log('  • Developer Portal:  http://localhost:3001');
    console.log('  • Testing Dashboard: http://localhost:3001/tests-dashboard');
    console.log('  • Report Explorer:   http://localhost:3000');
    console.log('  • DataOps API:       http://localhost:8000/docs');
    console.log('════════════════════════════════════════');
    console.log('');
});

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('Shutting down gracefully...');
    server.close(() => {
        db.close();
        process.exit(0);
    });
});
