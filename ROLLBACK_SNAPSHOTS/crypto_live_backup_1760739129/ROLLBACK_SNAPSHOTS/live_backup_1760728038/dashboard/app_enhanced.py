#!/usr/bin/env python3
"""
Enhanced RICK Trading Dashboard with WebSocket Support
Real-time streaming of trading data, bot activity, and market events
"""

import sys
import os
import json
from datetime import datetime
from flask import Flask, render_template, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from util.rick_live_monitor import get_active_bots_snapshot, get_live_monitor
from util.rick_narrator import get_latest_rick_narration
from util.narration_logger import get_latest_narration
from util.mode_manager import get_mode_info

app = Flask(__name__)
app.config['SECRET_KEY'] = 'rick_trading_secret_841921'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global state
connected_clients = set()
last_broadcast_state = {}

@app.route('/')
def index():
    """Serve the live dashboard"""
    return send_from_directory(os.path.dirname(__file__), 'live_dashboard.html')

@app.route('/api/status')
def api_status():
    """Get system status"""
    try:
        mode_info = get_mode_info()
        monitor = get_live_monitor()
        
        return jsonify({
            'mode': mode_info.get('mode', 'OFF'),
            'active_bots': len(monitor.active_swarm_bots),
            'total_pnl': monitor.total_realized_pnl,
            'trades_today': monitor.total_trades_today,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/swarmbots')
def api_swarmbots():
    """Get active SwarmBot positions"""
    try:
        bots = get_active_bots_snapshot()
        return jsonify(bots)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/regime')
def api_regime():
    """Get current market regime"""
    try:
        monitor = get_live_monitor()
        regime_data = {
            'regime': monitor.current_regime,
            'confidence': monitor.regime_confidence,
            'last_change': monitor.last_regime_change.isoformat() if monitor.last_regime_change else None,
            'active_positions': len(monitor.active_swarm_bots),
            'total_pnl_today': monitor.total_realized_pnl,
            'trades_today': monitor.total_trades_today,
            'wins_today': monitor.wins_today,
            'losses_today': monitor.losses_today,
            'win_rate': (monitor.wins_today / monitor.total_trades_today * 100) if monitor.total_trades_today > 0 else 0,
            'timestamp': datetime.now().isoformat()
        }
        return jsonify(regime_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/narration')
def api_narration():
    """Get Rick's narration"""
    try:
        rick_events = get_latest_rick_narration(n=50)
        if not rick_events:
            rick_events = get_latest_narration(n=50)
        
        for i, event in enumerate(rick_events):
            event['id'] = i
        
        return jsonify(rick_events)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def api_health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'connected_clients': len(connected_clients),
        'timestamp': datetime.now().isoformat()
    })

# WebSocket Events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    connected_clients.add(request.sid)
    print(f"✅ Client connected: {request.sid} (Total: {len(connected_clients)})")
    
    # Send initial data
    try:
        monitor = get_live_monitor()
        initial_data = {
            'swarmbots': get_active_bots_snapshot(),
            'regime': {
                'regime': monitor.current_regime,
                'confidence': monitor.regime_confidence,
                'last_change': monitor.last_regime_change.isoformat() if monitor.last_regime_change else None,
                'active_positions': len(monitor.active_swarm_bots),
                'total_pnl_today': monitor.total_realized_pnl,
                'trades_today': monitor.total_trades_today,
                'wins_today': monitor.wins_today,
                'losses_today': monitor.losses_today,
                'win_rate': (monitor.wins_today / monitor.total_trades_today * 100) if monitor.total_trades_today > 0 else 0
            },
            'narration': get_latest_rick_narration(n=20),
            'timestamp': datetime.now().isoformat()
        }
        emit('initial_data', initial_data)
    except Exception as e:
        print(f"Error sending initial data: {e}")
        emit('error', {'message': str(e)})

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
    
    try:
        if update_type == 'swarmbots' or update_type == 'all':
            emit('swarmbot_update', get_active_bots_snapshot())
        
        if update_type == 'regime' or update_type == 'all':
            monitor = get_live_monitor()
            emit('regime_update', {
                'regime': monitor.current_regime,
                'confidence': monitor.regime_confidence,
                'last_change': monitor.last_regime_change.isoformat() if monitor.last_regime_change else None,
                'active_positions': len(monitor.active_swarm_bots),
                'total_pnl_today': monitor.total_realized_pnl,
                'trades_today': monitor.total_trades_today,
                'wins_today': monitor.wins_today,
                'losses_today': monitor.losses_today,
                'win_rate': (monitor.wins_today / monitor.total_trades_today * 100) if monitor.total_trades_today > 0 else 0
            })
        
        if update_type == 'narration' or update_type == 'all':
            emit('narration_update', get_latest_rick_narration(n=5))
    except Exception as e:
        emit('error', {'message': str(e)})

def broadcast_updates():
    """Background task to broadcast updates to all connected clients"""
    while True:
        try:
            if connected_clients:
                # Get fresh data
                monitor = get_live_monitor()
                swarmbots = get_active_bots_snapshot()
                regime_data = {
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
                narration = get_latest_rick_narration(n=1)
                
                # Check if significant data changed
                current_state = {
                    'bot_count': len(swarmbots),
                    'regime': regime_data['regime'],
                    'pnl': round(regime_data['total_pnl_today'], 2),
                    'trades': regime_data['trades_today']
                }
                
                state_changed = current_state != last_broadcast_state.get('data')
                
                if state_changed or True:  # Always broadcast for now
                    # Broadcast to all connected clients
                    socketio.emit('swarmbot_update', swarmbots, broadcast=True)
                    socketio.emit('regime_update', regime_data, broadcast=True)
                    
                    if narration:
                        socketio.emit('narration_update', narration, broadcast=True)
                    
                    last_broadcast_state['data'] = current_state
                    last_broadcast_state['timestamp'] = datetime.now().isoformat()
                    
                    print(f"📡 Broadcast update to {len(connected_clients)} clients - Bots: {current_state['bot_count']}, P&L: ${current_state['pnl']}")
            
            socketio.sleep(2)  # Update every 2 seconds
            
        except Exception as e:
            print(f"❌ Error in broadcast_updates: {e}")
            socketio.sleep(5)

if __name__ == '__main__':
    print("=" * 80)
    print("🚀 RICK Live Trading Dashboard Starting")
    print("=" * 80)
    print(f"📊 Dashboard: http://127.0.0.1:8080")
    print(f"🔌 WebSocket: http://127.0.0.1:8080 (Socket.IO)")
    print(f"📡 API Endpoints:")
    print(f"   - GET /api/status")
    print(f"   - GET /api/swarmbots")
    print(f"   - GET /api/regime")
    print(f"   - GET /api/narration")
    print(f"   - GET /api/health")
    print("=" * 80)
    
    # Start background update thread
    socketio.start_background_task(broadcast_updates)
    
    # Run the app
    socketio.run(app, host='0.0.0.0', port=8080, debug=False, allow_unsafe_werkzeug=True)
