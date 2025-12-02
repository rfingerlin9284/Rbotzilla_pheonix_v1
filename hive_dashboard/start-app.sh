#!/bin/bash
echo "🌐 Starting RBOTzilla web server..."
node -e "
const express = require('express');
const path = require('path');
const app = express();

app.use(express.static(__dirname));

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'dashboard.html'));
});

app.get('/api/status', (req, res) => {
    res.json({
        status: 'operational',
        timestamp: new Date().toISOString(),
        system: 'RBOTzilla UNI',
        version: '1.0.0'
    });
});

const server = app.listen(3000, () => {
    console.log('🚀 RBOTzilla dashboard running at: http://localhost:3000');
    console.log('📊 Open the URL above in your browser to access the control center');
    console.log('⏹️  Press Ctrl+C to stop the server');
});

process.on('SIGINT', () => {
    console.log('\n👋 Shutting down RBOTzilla dashboard...');
    server.close();
    process.exit();
});
"
