// tmux_server.js - TMUX WebSocket Streaming Server
const express = require('express');
const WebSocket = require('ws');
const { exec, spawn } = require('child_process');
const path = require('path');

const app = express();
const PORT = 4567;

// JSON body parsing for Rick commands
app.use(express.json());
app.use(express.static('.'));

// WebSocket server
const wss = new WebSocket.Server({ port: 8887 });
console.log('🔧 TMUX WebSocket Server running on ws://localhost:8887');

// Track TMUX session and active connections
let tmuxSession = null;
let activeTmuxProcess = null;
const activeConnections = new Set();

// Create or attach to TMUX session named 'rbotmaster'
function ensureTmuxSession() {
    return new Promise((resolve, reject) => {
        exec('tmux has-session -t rbotmaster 2>/dev/null', (error) => {
            if (error) {
                // Session doesn't exist, create it
                console.log('🚀 Creating new TMUX session: rbotmaster');
                exec('tmux new-session -d -s rbotmaster', (createError) => {
                    if (createError) {
                        reject(createError);
                        return;
                    }
                    console.log('✅ TMUX session "rbotmaster" created');
                    resolve('rbotmaster');
                });
            } else {
                console.log('🔄 TMUX session "rbotmaster" already exists');
                resolve('rbotmaster');
            }
        });
    });
}

// Stream TMUX output via pipe
function streamTmuxOutput() {
    const tmuxCapture = spawn('tmux', ['capture-pane', '-t', 'rbotmaster', '-p', '-S', '-10'], {
        stdio: ['ignore', 'pipe', 'pipe']
    });
    
    tmuxCapture.stdout.on('data', (data) => {
        const output = data.toString();
        broadcastToClients({
            type: 'tmux_output',
            data: output,
            timestamp: Date.now()
        });
    });
    
    // Refresh capture every 500ms for live streaming
    setTimeout(() => {
        if (activeConnections.size > 0) {
            streamTmuxOutput();
        }
    }, 500);
}

// Broadcast message to all connected WebSocket clients
function broadcastToClients(message) {
    activeConnections.forEach(ws => {
        if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify(message));
        }
    });
}

// Send command to TMUX session
function sendToTmux(command) {
    return new Promise((resolve, reject) => {
        exec(`tmux send-keys -t rbotmaster "${command}" Enter`, (error, stdout, stderr) => {
            if (error) {
                reject(error);
                return;
            }
            resolve(stdout);
        });
    });
}

// WebSocket connection handler
wss.on('connection', (ws) => {
    console.log('🌊 New WebSocket connection established');
    activeConnections.add(ws);
    
    // Initialize TMUX session on first connection
    if (activeConnections.size === 1) {
        ensureTmuxSession().then(() => {
            streamTmuxOutput();
            ws.send(JSON.stringify({
                type: 'system_message',
                message: '🔗 Connected to TMUX session: rbotmaster'
            }));
        }).catch(error => {
            ws.send(JSON.stringify({
                type: 'error',
                message: `TMUX initialization failed: ${error.message}`
            }));
        });
    } else {
        ws.send(JSON.stringify({
            type: 'system_message',
            message: '🔗 Connected to existing TMUX stream'
        }));
    }
    
    // Handle incoming messages
    ws.on('message', (message) => {
        try {
            const data = JSON.parse(message);
            
            if (data.type === 'command') {
                console.log(`📤 Sending command to TMUX: ${data.command}`);
                sendToTmux(data.command).catch(error => {
                    ws.send(JSON.stringify({
                        type: 'error',
                        message: `Command failed: ${error.message}`
                    }));
                });
            }
        } catch (error) {
            ws.send(JSON.stringify({
                type: 'error',
                message: `Invalid message format: ${error.message}`
            }));
        }
    });
    
    ws.on('close', () => {
        console.log('🌊 WebSocket connection closed');
        activeConnections.delete(ws);
    });
});

// Rick AI Command Interface
app.post('/prompt', (req, res) => {
    const { prompt, context } = req.body;
    
    if (!prompt) {
        return res.status(400).json({ error: 'Prompt is required' });
    }
    
    console.log(`🤖 Rick AI received prompt: "${prompt}"`);
    
    // Process Rick command and convert to shell/python commands
    const rickResponse = processRickCommand(prompt, context);
    
    // Send command to TMUX if it's executable
    if (rickResponse.executable && rickResponse.command) {
        sendToTmux(rickResponse.command).then(() => {
            broadcastToClients({
                type: 'rick_command',
                prompt: prompt,
                response: rickResponse.response,
                command: rickResponse.command,
                timestamp: Date.now()
            });
        }).catch(error => {
            console.error('Failed to execute Rick command:', error);
        });
    }
    
    res.json(rickResponse);
});

// Rick AI Command Processor
function processRickCommand(prompt, context = {}) {
    const lowerPrompt = prompt.toLowerCase();
    
    // System control commands
    if (lowerPrompt.includes('start') && lowerPrompt.includes('system')) {
        return {
            response: "🚀 Starting RBOTzilla UNI system...",
            command: "cd /home/ing/RICK/R_H_UNI && python scripts/system_startup.py",
            executable: true
        };
    }
    
    if (lowerPrompt.includes('status') || lowerPrompt.includes('health')) {
        return {
            response: "🔍 Checking system status...",
            command: "cd /home/ing/RICK/R_H_UNI && python -c \"from scripts.system_startup import show_health; show_health()\"",
            executable: true
        };
    }
    
    // Historical analysis
    if (lowerPrompt.includes('historical') || lowerPrompt.includes('backtest')) {
        return {
            response: "📊 Running historical analysis...",
            command: "cd /home/ing/RICK/R_H_UNI && python backtesting/replay/runner.py",
            executable: true
        };
    }
    
    // Trading commands
    if (lowerPrompt.includes('start trading') || lowerPrompt.includes('launch trading')) {
        return {
            response: "💹 Launching trading systems...",
            command: "cd /home/ing/RICK/R_H_UNI && python -m strategies.multi_venue_launcher",
            executable: true
        };
    }
    
    // Risk monitoring
    if (lowerPrompt.includes('risk') && lowerPrompt.includes('check')) {
        return {
            response: "⚠️ Running risk analysis...",
            command: "cd /home/ing/RICK/R_H_UNI && python risk/shield_monitor.py",
            executable: true
        };
    }
    
    // File operations
    if (lowerPrompt.includes('list') && (lowerPrompt.includes('file') || lowerPrompt.includes('dir'))) {
        return {
            response: "📁 Listing current directory...",
            command: "ls -la",
            executable: true
        };
    }
    
    // Navigation
    if (lowerPrompt.startsWith('cd ') || lowerPrompt.includes('navigate to')) {
        const path = lowerPrompt.replace(/cd |navigate to /g, '').trim();
        return {
            response: `📂 Navigating to ${path}...`,
            command: `cd ${path} && pwd`,
            executable: true
        };
    }
    
    // Python execution
    if (lowerPrompt.includes('run python') || lowerPrompt.includes('execute python')) {
        const pythonCode = prompt.replace(/run python|execute python/gi, '').trim();
        return {
            response: "🐍 Executing Python code...",
            command: `python -c "${pythonCode}"`,
            executable: true
        };
    }
    
    // Default conversational response
    return {
        response: `🤖 Rick AI: I understand you said "${prompt}". I can help with system control, trading operations, risk analysis, file management, and Python execution. Try commands like "start system", "check status", "run historical analysis", or "launch trading".`,
        command: null,
        executable: false
    };
}

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({
        status: 'online',
        tmux_session: tmuxSession,
        active_connections: activeConnections.size,
        timestamp: Date.now()
    });
});

// Start Express server
app.listen(PORT, () => {
    console.log(`🎯 TMUX Streaming Server running on http://localhost:${PORT}`);
    console.log('🤖 Rick AI endpoint available at POST /prompt');
    console.log('📊 Health check available at GET /health');
});

process.on('SIGINT', () => {
    console.log('\n🛑 Shutting down TMUX streaming server...');
    process.exit(0);
});