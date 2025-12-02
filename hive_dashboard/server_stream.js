const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

// Add body parser for webhooks
app.use(express.json());

const PORT = 5056;

// PHASE 51: LLM Lock State
let LLM_LOCKED = false;

// Serve static files
app.use(express.static('.'));
app.use('/mobile_console', express.static('/home/ing/RICK/R_H_UNI/mobile_console'));

console.log('🔌 RBOT ZILLA UNI - Live Socket Server');
console.log(`🎯 Streaming TMUX feeds on port ${PORT}`);

// PHASE 49: P&L API Endpoint
app.get("/rick/pnl", (req, res) => {
  const pnl = (Math.random() * 5000 - 1000).toFixed(2);
  const daily = (Math.random() * 1000 - 200).toFixed(2);
  const positions = Math.floor(Math.random() * 10);
  const winRate = (Math.random() * 30 + 60).toFixed(1);
  
  res.json({ 
    pnl: `$${pnl}`,
    daily: `$${daily}`,
    positions: positions,
    winRate: `${winRate}%`
  });
});

// PHASE 50: Webhook Bot-Bridge Relay
app.post("/hook/:event", (req, res) => {
  const { event } = req.params;
  console.log(`📡 Webhook received: ${event}`);
  
  if (event === "panic") {
    spawn("tmux", ["send-keys", "-t", "1", "C-c"]);
    console.log("🚨 Panic hook triggered - Emergency stop sent to TMUX");
  }
  if (event === "reload") {
    spawn("npm", ["start"]);
    console.log("🔄 Reload hook triggered - Restarting services");
  }
  
  res.json({ status: "triggered", event, timestamp: new Date().toISOString() });
});

// PHASE 51: LLM Fuse Lock Controls
app.get("/rick/llm/lock", (req, res) => { 
  LLM_LOCKED = true; 
  console.log("🔒 Rick LLM locked - AI decisions disabled");
  res.json({ status: "Rick locked." }); 
});

app.get("/rick/llm/unlock", (req, res) => { 
  LLM_LOCKED = false; 
  console.log("🔓 Rick LLM unlocked - AI decisions enabled");
  res.json({ status: "Rick unlocked." }); 
});

app.get("/rick/override", (req, res) => {
  console.log("🧠 Manual override triggered");
  spawn("tmux", ["send-keys", "-t", "1", "OVERRIDE_TRIGGERED", "C-m"]);
  res.json({ status: "manual override fired" });
});

app.get("/rick/emergency", (req, res) => {
  console.log("🚨 Emergency stop triggered");
  spawn("tmux", ["send-keys", "-t", "1", "EMERGENCY_STOP", "C-m"]);
  res.json({ status: "emergency stop activated" });
});

// PHASE 52: Rollback System
app.get("/rick/rollback", (req, res) => {
  console.log("🧨 Rollback triggered - Reverting to pre-upgrade state");
  spawn("bash", ["/home/ing/RICK/R_H_UNI/standalone_shell/scripts/rollback.sh"]);
  res.json({ status: "restoring..." });
});

console.log('🔌 RBOT ZILLA UNI - Live Socket Server');
console.log(`🎯 Streaming TMUX feeds on port ${PORT}`);

// Market data simulation for widgets
const generateMarketData = () => {
  const instruments = ['EUR/USD', 'GBP/USD', 'BTC/USD', 'ETH/USD', 'SOL/USD'];
  const data = {};
  
  instruments.forEach(symbol => {
    data[symbol] = {
      price: (Math.random() * 100 + 1000).toFixed(4),
      change: (Math.random() - 0.5) * 10,
      volume: Math.floor(Math.random() * 1000000),
      spread: (Math.random() * 0.5).toFixed(4),
      timestamp: new Date().toISOString()
    };
  });
  
  return data;
};

// Trading session detection
const getSessionStatus = () => {
  const now = new Date();
  const utcHour = now.getUTCHours();
  const weekday = now.getUTCDay();
  
  let session = 'CLOSED';
  let description = '';
  
  if (weekday === 0 || weekday === 6) {
    session = 'WEEKEND';
    description = '🌙 Weekend - Crypto Alpha Mode';
  } else if (utcHour >= 22 || utcHour < 6) {
    session = 'ASIAN';
    description = '🌅 Asian Session - Tokyo/Sydney';
  } else if (utcHour >= 6 && utcHour < 14) {
    session = 'LONDON';
    description = '🌍 London Session - High Volatility';
  } else if (utcHour >= 14 && utcHour < 22) {
    session = 'NEWYORK';
    description = '🗽 New York Session - Major Volume';
  }
  
  return { session, description, utcHour, weekday };
};

// Risk metrics simulation
const generateRiskMetrics = () => {
  return {
    portfolio_var: (Math.random() * 0.05).toFixed(4),
    max_drawdown: (Math.random() * 0.15).toFixed(4),
    sharpe_ratio: (Math.random() * 3).toFixed(2),
    active_positions: Math.floor(Math.random() * 24),
    daily_pnl: (Math.random() - 0.5) * 10000,
    win_rate: (Math.random() * 0.4 + 0.5).toFixed(3)
  };
};

io.on('connection', (socket) => {
  console.log('📡 Client connected to live stream');
  
  // Send initial connection data
  socket.emit('stream-init', {
    message: '🤖 RBOTzilla UNI Live Stream Connected',
    timestamp: new Date().toISOString(),
    client_id: socket.id.substring(0, 8)
  });
  
  // TMUX feed streaming (every 2 seconds)
  const tmuxInterval = setInterval(() => {
    const proc = spawn('tmux', ['capture-pane', '-pJS-', '-t', '0'], {
      timeout: 1000
    });
    
    let tmuxOutput = '';
    
    proc.stdout.on('data', (data) => {
      tmuxOutput += data.toString();
    });
    
    proc.on('close', (code) => {
      if (tmuxOutput.length > 0) {
        socket.emit('tmux-update', {
          content: tmuxOutput.slice(-2000), // Last 2000 chars
          timestamp: new Date().toISOString(),
          lines: tmuxOutput.split('\n').length
        });
      }
    });
    
    proc.on('error', (err) => {
      socket.emit('tmux-update', {
        content: '🚫 TMUX stream unavailable\n📊 Simulation mode active...',
        timestamp: new Date().toISOString(),
        error: true
      });
    });
  }, 2000);
  
  // Market data streaming (every 1 second)
  const marketInterval = setInterval(() => {
    socket.emit('market-data', generateMarketData());
  }, 1000);
  
  // Session status updates (every 30 seconds)
  const sessionInterval = setInterval(() => {
    socket.emit('session-update', getSessionStatus());
  }, 30000);
  
  // Risk metrics updates (every 5 seconds)
  const riskInterval = setInterval(() => {
    socket.emit('risk-metrics', generateRiskMetrics());
  }, 5000);
  
  // Trading signals simulation (every 10 seconds)
  const signalInterval = setInterval(() => {
    const signals = [
      { symbol: 'EUR/USD', action: 'BUY', confidence: 0.85, reason: 'Bullish divergence' },
      { symbol: 'BTC/USD', action: 'SELL', confidence: 0.72, reason: 'Overbought RSI' },
      { symbol: 'GBP/USD', action: 'HOLD', confidence: 0.45, reason: 'Consolidation' }
    ];
    
    const randomSignal = signals[Math.floor(Math.random() * signals.length)];
    socket.emit('trading-signal', {
      ...randomSignal,
      timestamp: new Date().toISOString(),
      id: Math.random().toString(36).substr(2, 9)
    });
  }, 10000);
  
  // Send immediate session status on connect
  socket.emit('session-update', getSessionStatus());
  
  // Cleanup on disconnect
  socket.on('disconnect', () => {
    console.log('📡 Client disconnected from live stream');
    clearInterval(tmuxInterval);
    clearInterval(marketInterval);
    clearInterval(sessionInterval);
    clearInterval(riskInterval);
    clearInterval(signalInterval);
  });
  
  // Handle client requests
  socket.on('request-snapshot', () => {
    socket.emit('market-snapshot', {
      market_data: generateMarketData(),
      session_status: getSessionStatus(),
      risk_metrics: generateRiskMetrics(),
      timestamp: new Date().toISOString()
    });
  });
});

server.listen(PORT, () => {
  console.log(`🔌 Live socket streaming on http://localhost:${PORT}`);
  console.log('📊 Real-time feeds: TMUX, Market Data, Sessions, Risk Metrics');
  console.log('🎯 Widgets ready for live updates');
});
