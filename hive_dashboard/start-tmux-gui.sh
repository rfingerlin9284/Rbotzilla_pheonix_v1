#!/bin/bash

# Phase 35: TMUX Live Streaming & Rick AI Launcher
# Cross-platform launch script for desktop GUI with live terminal streaming

echo "🚀 Phase 35: TMUX Live Streaming & Rick AI Interface"
echo "=================================================="

# Set working directory
cd "$(dirname "$0")"

# Check if TMUX is installed
if ! command -v tmux &> /dev/null; then
    echo "❌ TMUX is not installed. Installing..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y tmux
    elif command -v yum &> /dev/null; then
        sudo yum install -y tmux
    elif command -v brew &> /dev/null; then
        brew install tmux
    else
        echo "⚠️ Please install TMUX manually and rerun this script"
        exit 1
    fi
fi

# Check if Node.js is available and dependencies installed
if command -v node &> /dev/null && [ -f "node_modules/.bin/concurrently" ]; then
    echo "🎯 Starting TMUX Streaming Server..."
    
    # Start the TMUX streaming server
    echo "📡 WebSocket server will run on ws://localhost:8887"
    echo "🌐 Web interface will be available at http://localhost:4567"
    echo "🤖 Rick AI command interface ready"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""
    
    node tmux_server.js
    
elif command -v python3 &> /dev/null; then
    echo "📡 Node.js dependencies not available, starting Python fallback server..."
    echo "⚠️ TMUX streaming not available in fallback mode"
    echo "🌐 Web interface will be available at http://localhost:4567"
    echo ""
    
    # Python fallback server for basic GUI
    python3 -c "
import http.server
import socketserver
import webbrowser
import os
import threading
import time

PORT = 4567

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '':
            self.path = '/dashboard.html'
        return super().do_GET()
    
    def log_message(self, format, *args):
        pass  # Suppress default logging

def start_server():
    with socketserver.TCPServer(('', PORT), CustomHandler) as httpd:
        print(f'🌐 Python fallback server running at http://localhost:{PORT}')
        print('📊 Dashboard interface available (TMUX streaming disabled)')
        print('Press Ctrl+C to stop')
        httpd.serve_forever()

def open_browser():
    time.sleep(2)
    webbrowser.open(f'http://localhost:{PORT}')

browser_thread = threading.Thread(target=open_browser)
browser_thread.daemon = True
browser_thread.start()

try:
    start_server()
except KeyboardInterrupt:
    print('\n🛑 Server stopped')
"
    
else
    echo "❌ Neither Node.js nor Python3 found. Please install one of them."
    echo "🔧 For full TMUX streaming functionality, install Node.js and run:"
    echo "   npm install"
    echo "   npm start"
    exit 1
fi