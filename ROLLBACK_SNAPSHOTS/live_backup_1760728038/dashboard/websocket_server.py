#!/usr/bin/env python3
"""
WebSocket Server for Real-Time Dashboard Updates
Streams live trading data, bot activity, and market events
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from flask import Flask
from flask_socketio import SocketIO, emit

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from util.rick_live_monitor import get_active_bots_snapshot, get_live_monitor
from util.rick_narrator import get_latest_rick_narration
from util.narration_logger import get_latest_narration

app = Flask(__name__)
app.config['SECRET_KEY'] = 'rick_trading_secret_841921'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global state
connected_clients = set()
last_broadcast = {}

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    connected_clients.add(request.sid)
    print(f"✅ Client connected: {request.sid} (Total: {len(connected_clients)})")
    
    # Send initial data
    emit('initial_data', {
        'swarmbots': get_active_bots_snapshot(),
        'regime': get_regime_data(),
        'narration': get_latest_rick_narration(n=20),
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    if request.sid in connected_clients:
        connected_clients.remove(request.sid)
    print(f"❌ Client disconnected: {request.sid} (Total: {len(connected_clients)})")

@socketio.on('request_update')
def handle_update_request(data):
    """Handle manual update request from client"""
    update_type = data.get('type', 'all')
    
    if update_type == 'swarmbots' or update_type == 'all':
        emit('swarmbot_update', get_active_bots_snapshot())
    
    if update_type == 'regime' or update_type == 'all':
        emit('regime_update', get_regime_data())
    
    if update_type == 'narration' or update_type == 'all':
        emit('narration_update', get_latest_rick_narration(n=5))

def get_regime_data():
    """Get current market regime data"""
    try:
        monitor = get_live_monitor()
        return {
            'regime': monitor.current_regime,
            'confidence': monitor.regime_confidence,
            'last_change': monitor.last_regime_change.isoformat() if monitor.last_regime_change else None,
            'active_positions': len(monitor.active_swarm_bots),
            'total_pnl_today': monitor.total_realized_pnl,
            'trades_today': monitor.total_trades_today,
            'wins_today': monitor.wins_today,
            'losses_today': monitor.losses_today,
            'win_rate': (monitor.wins_today / monitor.total_trades_today * 100) if monitor.total_trades_today > 0 else 0
        }
    except Exception as e:
        print(f"Error getting regime data: {e}")
        return {
            'regime': 'UNKNOWN',
            'confidence': 0,
            'active_positions': 0,
            'total_pnl_today': 0,
            'trades_today': 0,
            'win_rate': 0
        }

def broadcast_updates():
    """Background task to broadcast updates to all connected clients"""
    while True:
        try:
            if connected_clients:
                # Get fresh data
                swarmbots = get_active_bots_snapshot()
                regime = get_regime_data()
                narration = get_latest_rick_narration(n=1)
                
                # Check if data changed
                current_state = json.dumps({
                    'bots': len(swarmbots),
                    'regime': regime['regime'],
                    'pnl': regime['total_pnl_today']
                })
                
                if current_state != last_broadcast.get('state'):
                    # Broadcast to all connected clients
                    socketio.emit('swarmbot_update', swarmbots)
                    socketio.emit('regime_update', regime)
                    
                    if narration:
                        socketio.emit('narration_update', narration)
                    
                    last_broadcast['state'] = current_state
                    last_broadcast['timestamp'] = datetime.now().isoformat()
                    
                    print(f"📡 Broadcast update to {len(connected_clients)} clients")
            
            socketio.sleep(2)  # Update every 2 seconds
            
        except Exception as e:
            print(f"Error in broadcast_updates: {e}")
            socketio.sleep(5)

if __name__ == '__main__':
    # Start background update thread
    socketio.start_background_task(broadcast_updates)
    
    print("🚀 WebSocket server starting on http://0.0.0.0:5001")
    socketio.run(app, host='0.0.0.0', port=5001, debug=False)
