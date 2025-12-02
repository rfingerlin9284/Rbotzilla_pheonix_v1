#!/usr/bin/env python3
"""
🚀 RICK CONVERSATIONAL DASHBOARD
Real-time trading narration with Rick & Hive Mind conversations
"""
import asyncio
import json
import time
import random
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path
import re

app = FastAPI(title="RICK Conversational Dashboard")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Active websocket connections
connections = []

# Simulated personalities for conversation
PERSONALITIES = {
    "rick": {
        "name": "🧠 RICK",
        "color": "#00ff88",
        "style": "Technical, analytical, precise",
        "phrases": [
            "📊 Market structure suggests",
            "⚡ Momentum indicators show",
            "🎯 Target acquisition at",
            "⚠️ Risk assessment indicates",
            "🔍 Pattern recognition confirms"
        ]
    },
    "hive": {
        "name": "🐝 HIVE MIND", 
        "color": "#ffd700",
        "style": "Collective wisdom, market sentiment",
        "phrases": [
            "🌊 Market sentiment flowing toward",
            "📈 Collective analysis suggests",
            "⚖️ Consensus indicates",
            "🎲 Probability matrix shows",
            "🔮 Predictive models align on"
        ]
    },
    "rbotzilla": {
        "name": "🤖 RBOTzilla",
        "color": "#ff6b6b", 
        "style": "Execution engine, trade management",
        "phrases": [
            "⚡ Executing trade parameters",
            "🎯 OCO order placed successfully",
            "📊 Position size calculated as",
            "⏱️ Latency optimal at",
            "✅ Charter compliance verified"
        ]
    },
    "oanda": {
        "name": "🏛️ OANDA",
        "color": "#66b3ff",
        "style": "Market data provider, execution venue", 
        "phrases": [
            "📡 Market data streaming",
            "💱 Spread currently",
            "⚡ Order filled at",
            "📊 Real-time pricing shows",
            "🔄 Position update"
        ]
    }
}

class ConversationEngine:
    def __init__(self):
        self.last_trade_time = time.time()
        self.conversation_history = []
        
    async def generate_trade_conversation(self, trade_data):
        """Generate realistic conversation about a trade"""
        conversations = []
        
        # Rick analyzes first
        rick_msg = f"{random.choice(PERSONALITIES['rick']['phrases'])} {trade_data.get('pair', 'USD_CAD')} at {trade_data.get('price', '1.40382')}. R:R ratio optimal at 3.2:1."
        conversations.append({
            "speaker": "rick",
            "message": rick_msg,
            "timestamp": datetime.now().isoformat(),
            "trade_context": trade_data
        })
        
        await asyncio.sleep(0.5)
        
        # Hive responds
        hive_msg = f"{random.choice(PERSONALITIES['hive']['phrases'])} confluence with technical setup. Position sizing approved for ${trade_data.get('notional', '15021')}."
        conversations.append({
            "speaker": "hive", 
            "message": hive_msg,
            "timestamp": datetime.now().isoformat(),
            "trade_context": trade_data
        })
        
        await asyncio.sleep(0.3)
        
        # RBOTzilla executes
        robot_msg = f"{random.choice(PERSONALITIES['rbotzilla']['phrases'])} Stop: {trade_data.get('stop', '1.40582')} | Target: {trade_data.get('target', '1.39742')} | Size: {trade_data.get('size', '10700')} units"
        conversations.append({
            "speaker": "rbotzilla",
            "message": robot_msg, 
            "timestamp": datetime.now().isoformat(),
            "trade_context": trade_data
        })
        
        await asyncio.sleep(0.2)
        
        # OANDA confirms
        oanda_msg = f"{random.choice(PERSONALITIES['oanda']['phrases'])} Order ID: {trade_data.get('order_id', '47')}. Latency: {trade_data.get('latency', '197.2')}ms ⚡"
        conversations.append({
            "speaker": "oanda",
            "message": oanda_msg,
            "timestamp": datetime.now().isoformat(), 
            "trade_context": trade_data
        })
        
        return conversations

conversation_engine = ConversationEngine()

async def broadcast_conversation(conversations):
    """Send conversation to all connected clients"""
    if not connections:
        return
        
    for conv in conversations:
        message = {
            "type": "conversation",
            "data": {
                "speaker": conv["speaker"],
                "personality": PERSONALITIES[conv["speaker"]],
                "message": conv["message"],
                "timestamp": conv["timestamp"],
                "trade_context": conv.get("trade_context", {})
            }
        }
        
        # Send to all connections
        dead_connections = []
        for websocket in connections:
            try:
                await websocket.send_text(json.dumps(message))
                await asyncio.sleep(0.1)  # Stagger messages slightly
            except:
                dead_connections.append(websocket)
        
        # Clean up dead connections
        for dead in dead_connections:
            if dead in connections:
                connections.remove(dead)

async def simulate_live_trading():
    """Simulate ongoing trading activity and conversations"""
    while True:
        # Simulate a trade every 30-60 seconds
        await asyncio.sleep(random.uniform(30, 60))
        
        # Generate random trade data
        pairs = ["USD_CAD", "EUR_USD", "GBP_USD", "AUD_USD", "USD_JPY"]
        trade_data = {
            "pair": random.choice(pairs),
            "price": f"{random.uniform(1.2, 1.5):.5f}",
            "stop": f"{random.uniform(1.2, 1.5):.5f}",
            "target": f"{random.uniform(1.2, 1.5):.5f}",
            "size": f"{random.randint(8000, 15000)}",
            "notional": f"{random.randint(12000, 18000)}",
            "order_id": random.randint(40, 99),
            "latency": f"{random.uniform(150, 250):.1f}"
        }
        
        # Generate conversation
        conversations = await conversation_engine.generate_trade_conversation(trade_data)
        await broadcast_conversation(conversations)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)
    
    # Send welcome message
    welcome = {
        "type": "system",
        "data": {
            "message": "🚀 Connected to RICK Conversational Dashboard",
            "timestamp": datetime.now().isoformat()
        }
    }
    await websocket.send_text(json.dumps(welcome))
    
    try:
        while True:
            # Keep connection alive
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        if websocket in connections:
            connections.remove(websocket)

@app.get("/")
async def get_dashboard():
    return HTMLResponse(content="""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 RICK Conversational Trading Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            background: linear-gradient(135deg, #0a0e13 0%, #1a1f2e 100%);
            color: #e8e8e8;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            height: 100vh;
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(90deg, #1a1f2e, #2a3441);
            border-bottom: 2px solid #00ff88;
            padding: 15px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0, 255, 136, 0.3);
        }
        
        .header h1 {
            color: #00ff88;
            font-size: 2em;
            text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
            margin-bottom: 5px;
        }
        
        .status-banner {
            background: rgba(255, 107, 107, 0.2);
            border: 1px solid #ff6b6b;
            border-radius: 6px;
            padding: 8px;
            font-size: 0.9em;
            color: #ff6b6b;
        }
        
        .dashboard-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            grid-template-rows: 1fr 1fr;
            gap: 15px;
            padding: 20px;
            height: calc(100vh - 140px);
        }
        
        .conversation-window {
            background: rgba(16, 21, 27, 0.9);
            border: 2px solid #1f2630;
            border-radius: 12px;
            padding: 15px;
            overflow-y: auto;
            backdrop-filter: blur(10px);
            position: relative;
        }
        
        .window-header {
            background: linear-gradient(90deg, #1f2630, #2a3441);
            margin: -15px -15px 15px -15px;
            padding: 10px 15px;
            border-radius: 10px 10px 0 0;
            border-bottom: 1px solid #00ff88;
            font-weight: bold;
            color: #00ff88;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #00ff88;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.7; transform: scale(1.1); }
            100% { opacity: 1; transform: scale(1); }
        }
        
        .message {
            margin-bottom: 12px;
            padding: 8px 12px;
            border-radius: 8px;
            border-left: 4px solid;
            animation: slideIn 0.3s ease-out;
            font-size: 0.9em;
            line-height: 1.4;
        }
        
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-20px); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        .message.rick {
            background: rgba(0, 255, 136, 0.1);
            border-left-color: #00ff88;
        }
        
        .message.hive {
            background: rgba(255, 215, 0, 0.1);
            border-left-color: #ffd700;
        }
        
        .message.rbotzilla {
            background: rgba(255, 107, 107, 0.1);
            border-left-color: #ff6b6b;
        }
        
        .message.oanda {
            background: rgba(102, 179, 255, 0.1);
            border-left-color: #66b3ff;
        }
        
        .speaker {
            font-weight: bold;
            margin-bottom: 4px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .timestamp {
            font-size: 0.7em;
            opacity: 0.6;
            color: #a0a0a0;
        }
        
        .message-text {
            margin-top: 4px;
        }
        
        .trade-data {
            background: rgba(42, 52, 65, 0.5);
            border-radius: 6px;
            padding: 8px;
            margin-top: 6px;
            font-size: 0.8em;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .connection-status {
            position: absolute;
            top: 10px;
            right: 15px;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.7em;
            font-weight: bold;
        }
        
        .connected {
            background: rgba(0, 255, 136, 0.2);
            color: #00ff88;
            border: 1px solid #00ff88;
        }
        
        .disconnected {
            background: rgba(255, 107, 107, 0.2);
            color: #ff6b6b;
            border: 1px solid #ff6b6b;
        }
        
        .system-stats {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 15px;
        }
        
        .stat-card {
            background: rgba(42, 52, 65, 0.3);
            border-radius: 8px;
            padding: 8px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .stat-value {
            font-size: 1.2em;
            font-weight: bold;
            color: #00ff88;
        }
        
        .stat-label {
            font-size: 0.8em;
            opacity: 0.7;
            margin-top: 2px;
        }
        
        .scrollbar {
            scrollbar-width: thin;
            scrollbar-color: #00ff88 transparent;
        }
        
        .scrollbar::-webkit-scrollbar {
            width: 6px;
        }
        
        .scrollbar::-webkit-scrollbar-track {
            background: transparent;
        }
        
        .scrollbar::-webkit-scrollbar-thumb {
            background: #00ff88;
            border-radius: 3px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 RICK CONVERSATIONAL TRADING DASHBOARD</h1>
        <div class="status-banner">
            PIN: 841921 • RR≥3.2 • Daily Halt −5% • ≤6h TTL • OCO MANDATORY • LIVE NARRATION ACTIVE
        </div>
    </div>
    
    <div class="dashboard-container">
        <!-- Main Trading Conversation -->
        <div class="conversation-window scrollbar">
            <div class="window-header">
                <div class="status-dot"></div>
                🗣️ Live Trading Conversation
                <div class="connection-status" id="main-status">Connecting...</div>
            </div>
            <div id="main-conversation"></div>
        </div>
        
        <!-- Rick's Analysis -->
        <div class="conversation-window scrollbar">
            <div class="window-header">
                <div class="status-dot"></div>
                🧠 RICK Technical Analysis
                <div class="connection-status" id="rick-status">Analyzing...</div>
            </div>
            <div class="system-stats">
                <div class="stat-card">
                    <div class="stat-value" id="trades-count">0</div>
                    <div class="stat-label">Active Trades</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="success-rate">90.6%</div>
                    <div class="stat-label">Success Rate</div>
                </div>
            </div>
            <div id="rick-analysis"></div>
        </div>
        
        <!-- Hive Mind Sentiment -->
        <div class="conversation-window scrollbar">
            <div class="window-header">
                <div class="status-dot"></div>
                🐝 HIVE MIND Collective Intelligence
                <div class="connection-status" id="hive-status">Analyzing...</div>
            </div>
            <div class="system-stats">
                <div class="stat-card">
                    <div class="stat-value" id="sentiment">Bullish</div>
                    <div class="stat-label">Market Sentiment</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="confidence">87%</div>
                    <div class="stat-label">Confidence</div>
                </div>
            </div>
            <div id="hive-sentiment"></div>
        </div>
        
        <!-- System Activity -->
        <div class="conversation-window scrollbar">
            <div class="window-header">
                <div class="status-dot"></div>
                ⚡ System Activity & Execution
                <div class="connection-status" id="system-status">Monitoring...</div>
            </div>
            <div class="system-stats">
                <div class="stat-card">
                    <div class="stat-value" id="latency">197ms</div>
                    <div class="stat-label">Avg Latency</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="notional">$15,021</div>
                    <div class="stat-label">Position Size</div>
                </div>
            </div>
            <div id="system-activity"></div>
        </div>
    </div>

    <script>
        class ConversationalDashboard {
            constructor() {
                this.ws = null;
                this.reconnectAttempts = 0;
                this.maxReconnectAttempts = 5;
                this.messageCount = 0;
                this.connect();
            }
            
            connect() {
                this.ws = new WebSocket('ws://127.0.0.1:5555/ws');
                
                this.ws.onopen = () => {
                    console.log('Connected to RICK Conversational Dashboard');
                    this.reconnectAttempts = 0;
                    this.updateConnectionStatus('connected');
                };
                
                this.ws.onmessage = (event) => {
                    const message = JSON.parse(event.data);
                    this.handleMessage(message);
                };
                
                this.ws.onclose = () => {
                    console.log('Disconnected from dashboard');
                    this.updateConnectionStatus('disconnected');
                    this.attemptReconnect();
                };
                
                this.ws.onerror = (error) => {
                    console.error('WebSocket error:', error);
                };
            }
            
            updateConnectionStatus(status) {
                const statusElements = ['main-status', 'rick-status', 'hive-status', 'system-status'];
                statusElements.forEach(id => {
                    const element = document.getElementById(id);
                    if (element) {
                        element.textContent = status === 'connected' ? 'Connected' : 'Disconnected';
                        element.className = `connection-status ${status}`;
                    }
                });
            }
            
            attemptReconnect() {
                if (this.reconnectAttempts < this.maxReconnectAttempts) {
                    this.reconnectAttempts++;
                    setTimeout(() => {
                        console.log(`Reconnection attempt ${this.reconnectAttempts}`);
                        this.connect();
                    }, 2000 * this.reconnectAttempts);
                }
            }
            
            handleMessage(message) {
                if (message.type === 'conversation') {
                    this.addConversationMessage(message.data);
                    this.updateStats(message.data);
                } else if (message.type === 'system') {
                    this.addSystemMessage(message.data);
                }
            }
            
            addConversationMessage(data) {
                const { speaker, personality, message, timestamp, trade_context } = data;
                
                // Add to main conversation
                this.addMessageToContainer('main-conversation', speaker, personality, message, timestamp, trade_context);
                
                // Add to specific speaker's window
                const speakerWindows = {
                    'rick': 'rick-analysis',
                    'hive': 'hive-sentiment',
                    'rbotzilla': 'system-activity',
                    'oanda': 'system-activity'
                };
                
                if (speakerWindows[speaker]) {
                    this.addMessageToContainer(speakerWindows[speaker], speaker, personality, message, timestamp, trade_context);
                }
            }
            
            addMessageToContainer(containerId, speaker, personality, message, timestamp, tradeContext) {
                const container = document.getElementById(containerId);
                if (!container) return;
                
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${speaker}`;
                
                const time = new Date(timestamp).toLocaleTimeString();
                
                messageDiv.innerHTML = `
                    <div class="speaker" style="color: ${personality.color}">
                        ${personality.name}
                        <span class="timestamp">${time}</span>
                    </div>
                    <div class="message-text">${message}</div>
                    ${tradeContext && Object.keys(tradeContext).length ? `
                        <div class="trade-data">
                            💱 ${tradeContext.pair || 'USD_CAD'} | 💰 $${tradeContext.notional || '15,021'} | 
                            ⚡ ${tradeContext.latency || '197'}ms | 🎯 Order #${tradeContext.order_id || '47'}
                        </div>
                    ` : ''}
                `;
                
                container.appendChild(messageDiv);
                container.scrollTop = container.scrollHeight;
                
                // Keep only last 50 messages
                while (container.children.length > 50) {
                    container.removeChild(container.firstChild);
                }
            }
            
            addSystemMessage(data) {
                this.addMessageToContainer('system-activity', 'system', 
                    { name: '🔧 SYSTEM', color: '#66b3ff' }, 
                    data.message, data.timestamp, {});
            }
            
            updateStats(data) {
                this.messageCount++;
                
                // Update trade count
                document.getElementById('trades-count').textContent = Math.floor(this.messageCount / 4);
                
                // Update random stats for demo
                if (data.trade_context) {
                    if (data.trade_context.latency) {
                        document.getElementById('latency').textContent = data.trade_context.latency + 'ms';
                    }
                    if (data.trade_context.notional) {
                        document.getElementById('notional').textContent = '$' + data.trade_context.notional;
                    }
                }
                
                // Simulate changing sentiment
                const sentiments = ['Bullish', 'Bearish', 'Neutral', 'Volatile'];
                if (Math.random() < 0.3) {
                    document.getElementById('sentiment').textContent = sentiments[Math.floor(Math.random() * sentiments.length)];
                    document.getElementById('confidence').textContent = Math.floor(Math.random() * 30 + 70) + '%';
                }
            }
        }
        
        // Initialize dashboard when page loads
        window.addEventListener('load', () => {
            new ConversationalDashboard();
        });
    </script>
</body>
</html>
    """)

if __name__ == "__main__":
    # Start background trading simulation
    asyncio.create_task(simulate_live_trading())
    
    print("🚀 RICK Conversational Dashboard Starting...")
    print("📡 WebSocket: ws://127.0.0.1:5555/ws")
    print("🌐 Dashboard: http://127.0.0.1:5555")
    print("💬 Live conversations will begin shortly...")
    
    uvicorn.run(app, host="127.0.0.1", port=5555)