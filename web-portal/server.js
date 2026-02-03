#!/usr/bin/env node
/**
 * Simple static file server for the a_domain Developer Portal
 * Serves the unified landing page at http://localhost:3001
 * Also serves project files for documentation links
 */

const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 3001;
const HOST = '0.0.0.0';

// Serve from project root (one level up from web-portal)
const PROJECT_ROOT = path.join(__dirname, '..');

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

const server = http.createServer((req, res) => {
    // Parse URL
    let filePath = req.url === '/' ? '/web-portal/index.html' : req.url;

    // Remove query parameters
    const urlPath = filePath.split('?')[0];

    // Security: prevent directory traversal outside project
    if (urlPath.includes('..')) {
        res.writeHead(403);
        res.end('Forbidden');
        return;
    }

    // Determine full file path from project root
    const fullPath = path.join(PROJECT_ROOT, urlPath);

    // Security check: ensure path is within project root
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
                res.end('404 Not Found: ' + urlPath);
            } else {
                res.writeHead(500);
                res.end('Internal Server Error');
            }
        } else {
            res.writeHead(200, { 'Content-Type': mimeType });
            res.end(content);
        }
    });
});

server.listen(PORT, HOST, () => {
    console.log('');
    console.log('🚀 a_domain Developer Portal');
    console.log('════════════════════════════════════════');
    console.log(`✓ Server running at http://localhost:${PORT}`);
    console.log('✓ Serving from: ${PROJECT_ROOT}');
    console.log('✓ Press Ctrl+C to stop');
    console.log('');
    console.log('Services:');
    console.log('  • Developer Portal:  http://localhost:3001');
    console.log('  • Report Explorer:   http://localhost:3000');
    console.log('  • DataOps API:       http://localhost:8000/docs');
    console.log('════════════════════════════════════════');
    console.log('');
});
