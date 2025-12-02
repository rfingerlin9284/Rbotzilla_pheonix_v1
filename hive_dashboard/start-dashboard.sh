#!/bin/bash
# RBOTzilla UNI Web Dashboard Launcher
echo "🌐 Starting RBOTzilla web server..."

# Simple Python web server as fallback
if command -v python3 &> /dev/null; then
    echo "🐍 Using Python web server"
    cd /home/ing/RICK/R_H_UNI/standalone_shell
    python3 -c "
import http.server
import socketserver
import webbrowser
import time
from threading import Timer

PORT = 3000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()
    
    def do_GET(self):
        if self.path == '/':
            self.path = '/dashboard.html'
        elif self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            import json
            from datetime import datetime
            response = {
                'status': 'operational',
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'system': 'RBOTzilla UNI',
                'version': '1.0.0',
                'phases': '30-33 Complete',
                'signals': 940,
                'confidence': 66.3
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
            return
        return super().do_GET()

def open_browser():
    print('🚀 Opening RBOTzilla Control Center...')
    webbrowser.open('http://localhost:' + str(PORT))

with socketserver.TCPServer(('', PORT), MyHTTPRequestHandler) as httpd:
    print(f'🌐 RBOTzilla dashboard server running on port {PORT}')
    print(f'🔗 Dashboard URL: http://localhost:{PORT}')
    print(f'📊 Sci-fi control center interface loaded')
    print(f'⏹️  Press Ctrl+C to stop')
    
    # Auto-open browser after 1 second
    Timer(1.0, open_browser).start()
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\n👋 Shutting down RBOTzilla dashboard server...')
        httpd.shutdown()
"
else
    echo "❌ Python3 not available, using basic server"
    # Fallback: basic file server
    cd /home/ing/RICK/RICK_LIVE_CLEAN/hive_dashboard
    php -S localhost:3000 2>/dev/null || python -m http.server 3000 || echo "Please install Python3 or PHP to run the server"
fi