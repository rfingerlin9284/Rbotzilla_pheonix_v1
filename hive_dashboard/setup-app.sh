#!/bin/bash
# RBOTzilla UNI Desktop App Launcher
# Phase 34: Standalone App Shell Setup

echo "🚀 RBOTzilla UNI Desktop App Launcher"
echo "====================================="

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Run from standalone_shell directory."
    exit 1
fi

echo "📦 Installing dependencies..."

# Try to install dependencies without Electron first
npm install express ws --save

echo "🔧 Setting up Electron manually..."

# Create a simple start script that doesn't require Electron installation in WSL
cat > start-app.sh << 'SCRIPT'
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
SCRIPT

chmod +x start-app.sh

echo "✅ Setup complete!"
echo ""
echo "🚀 To start RBOTzilla desktop dashboard:"
echo "   ./start-app.sh"
echo ""
echo "📊 Then open: http://localhost:3000 in your browser"
echo "   (The dashboard will look like a sci-fi control center!)"