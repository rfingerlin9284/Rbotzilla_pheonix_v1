#!/usr/bin/env python3
"""
RICK Dashboard - Static HTML Generator
Generates dashboard.html with current system status
Run this script to update dashboard, then open dashboard.html in browser
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from util.mode_manager import get_mode_info
from util.narration_logger import get_latest_narration, get_session_summary

def generate_dashboard():
    """Generate static HTML dashboard"""
    
    # Get data
    mode_info = get_mode_info()
    pnl_summary = get_session_summary()
    recent_events = get_latest_narration(n=10)
    recent_events.reverse()  # Newest first
    
    # Mode styling
    mode_classes = {
        'OFF': 'mode-off',
        'GHOST': 'mode-ghost',
        'CANARY': 'mode-canary',
        'LIVE': 'mode-live'
    }
    mode_class = mode_classes.get(mode_info['mode'], 'mode-off')
    
    # Generate events HTML
    events_html = ""
    for event in recent_events:
        details_html = ""
        if event.get('details'):
            if event['event_type'] == 'OCO_PLACED':
                details_html = f"""
                    <div style="margin-top: 5px; opacity: 0.7; font-size: 0.85em;">
                        Entry: {event['details'].get('entry_price', 0):.5f} | 
                        Units: {event['details'].get('units', 0)} | 
                        Latency: {event['details'].get('latency_ms', 0):.1f}ms
                    </div>
                """
            elif event['event_type'] == 'GHOST_SESSION_END':
                details_html = f"""
                    <div style="margin-top: 5px; opacity: 0.7; font-size: 0.85em;">
                        Trades: {event['details'].get('total_trades', 0)} | 
                        Win Rate: {event['details'].get('win_rate', 0):.1f}% | 
                        P&L: ${event['details'].get('net_pnl', 0):.2f}
                    </div>
                """
        
        symbol_text = f" | {event.get('symbol')}" if event.get('symbol') else ""
        
        events_html += f"""
        <div class="event">
            <span class="event-type">{event['event_type']}</span>
            <span style="opacity: 0.8;">{symbol_text}</span>
            <span style="opacity: 0.6;"> @ {event.get('venue', 'unknown')}</span>
            <div class="event-time">{event.get('timestamp', '')[:19]}</div>
            {details_html}
        </div>
        """
    
    pnl_color = 'positive' if pnl_summary['net_pnl'] > 0 else 'negative'
    live_color = 'negative' if mode_info['is_live'] else 'positive'
    live_text = 'ACTIVE' if mode_info['is_live'] else 'OFF'
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>RICK Trading Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="10">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #fff;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            padding: 30px 0;
            border-bottom: 2px solid rgba(255,255,255,0.2);
            margin-bottom: 30px;
        }}
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .mode-badge {{
            display: inline-block;
            padding: 8px 20px;
            border-radius: 25px;
            font-weight: bold;
            font-size: 1.1em;
            margin-top: 10px;
        }}
        .mode-off {{ background: #6c757d; }}
        .mode-ghost {{ background: #17a2b8; }}
        .mode-canary {{ background: #ffc107; color: #000; }}
        .mode-live {{ background: #dc3545; animation: pulse 2s infinite; }}
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .card {{
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            border: 1px solid rgba(255,255,255,0.18);
        }}
        .card h2 {{
            font-size: 1.3em;
            margin-bottom: 15px;
            color: #ffd700;
        }}
        .stat {{
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        .stat:last-child {{ border-bottom: none; }}
        .stat-label {{ opacity: 0.8; }}
        .stat-value {{
            font-weight: bold;
            font-size: 1.1em;
        }}
        .positive {{ color: #28a745; }}
        .negative {{ color: #dc3545; }}
        .events-list {{
            max-height: 400px;
            overflow-y: auto;
            margin-top: 15px;
        }}
        .event {{
            background: rgba(0,0,0,0.2);
            padding: 10px;
            margin-bottom: 8px;
            border-radius: 8px;
            font-size: 0.9em;
        }}
        .event-type {{
            font-weight: bold;
            color: #ffd700;
        }}
        .event-time {{
            opacity: 0.6;
            font-size: 0.85em;
        }}
        .refresh-notice {{
            text-align: center;
            opacity: 0.7;
            font-size: 0.9em;
            margin-top: 20px;
        }}
        .timestamp {{
            text-align: center;
            opacity: 0.5;
            font-size: 0.85em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 RICK Trading Dashboard</h1>
            <div class="mode-badge {mode_class}">
                {mode_info['mode']} MODE
            </div>
            <p style="margin-top: 10px; opacity: 0.8;">{mode_info['description']}</p>
        </div>
        
        <div class="grid">
            <!-- Performance Card -->
            <div class="card">
                <h2>📊 Performance</h2>
                <div class="stat">
                    <span class="stat-label">Total Trades</span>
                    <span class="stat-value">{pnl_summary['total_trades']}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Win Rate</span>
                    <span class="stat-value">{pnl_summary['win_rate']:.1f}%</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Wins / Losses</span>
                    <span class="stat-value">{pnl_summary['wins']} / {pnl_summary['losses']}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Net P&L</span>
                    <span class="stat-value {pnl_color}">
                        ${pnl_summary['net_pnl']:.2f}
                    </span>
                </div>
                <div class="stat">
                    <span class="stat-label">Total Fees</span>
                    <span class="stat-value">${pnl_summary['total_fees']:.2f}</span>
                </div>
            </div>
            
            <!-- Environment Card -->
            <div class="card">
                <h2>🔧 Environment</h2>
                <div class="stat">
                    <span class="stat-label">OANDA</span>
                    <span class="stat-value">{mode_info['oanda_environment']}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Coinbase</span>
                    <span class="stat-value">{mode_info['coinbase_environment']}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Live Trading</span>
                    <span class="stat-value {live_color}">
                        {live_text}
                    </span>
                </div>
                <div class="stat">
                    <span class="stat-label">Toggle File</span>
                    <span class="stat-value" style="font-size: 0.8em;">.upgrade_toggle</span>
                </div>
            </div>
            
            <!-- Mode Commands Card -->
            <div class="card">
                <h2>⚙️ Mode Commands</h2>
                <div style="background: rgba(0,0,0,0.3); padding: 15px; border-radius: 8px; font-family: monospace; font-size: 0.9em;">
                    <div style="margin-bottom: 8px;"># Switch to GHOST mode</div>
                    <div style="color: #28a745;">python3 -c "from util.mode_manager import switch_mode; switch_mode('GHOST')"</div>
                    
                    <div style="margin: 15px 0 8px;">## Switch to OFF</div>
                    <div style="color: #28a745;">python3 -c "from util.mode_manager import switch_mode; switch_mode('OFF')"</div>
                    
                    <div style="margin: 15px 0 8px;"># Run ghost test</div>
                    <div style="color: #28a745;">python3 test_ghost_trading.py</div>
                </div>
            </div>
        </div>
        
        <!-- Recent Activity -->
        <div class="card">
            <h2>📝 Recent Activity (Last 10 Events)</h2>
            <div class="events-list">
                {events_html}
            </div>
        </div>
        
        <div class="timestamp">
            Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
        
        <div class="refresh-notice">
            🔄 Dashboard auto-refreshes every 10 seconds
        </div>
    </div>
</body>
</html>"""
    
    # Write to file
    output_file = Path(__file__).parent / 'dashboard.html'
    with open(output_file, 'w') as f:
        f.write(html)
    
    print(f"✅ Dashboard generated: {output_file}")
    print(f"📊 Mode: {mode_info['mode']}")
    print(f"💰 Net P&L: ${pnl_summary['net_pnl']:.2f}")
    print(f"📈 Win Rate: {pnl_summary['win_rate']:.1f}%")
    print(f"\n🌐 Open in browser: file://{output_file.absolute()}")

if __name__ == '__main__':
    generate_dashboard()
