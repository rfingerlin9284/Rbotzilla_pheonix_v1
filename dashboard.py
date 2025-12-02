"""
RBOTzilla Dashboard — Real-time bot monitoring & control via Streamlit
Displays logs, metrics, charts, account info, and provides buttons for bot control.
"""

import os
import json
import logging
import requests
import websocket
import streamlit as st
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import pandas as pd
import plotly.graph_objects as go
from functools import wraps
import threading
import time

# =====================================================================
# CONFIGURATION
# =====================================================================

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
WEBSOCKET_URL = os.getenv("WEBSOCKET_URL", "ws://127.0.0.1:8000/ws")
REFRESH_INTERVAL = 2  # seconds

# =====================================================================
# LOGGING
# =====================================================================

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# =====================================================================
# STREAMLIT PAGE CONFIG
# =====================================================================

st.set_page_config(
    page_title="RBOTzilla Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for theme
st.markdown("""
    <style>
    body { background-color: #0f1419; color: #e0e0e0; }
    .stMetric { background-color: #1e2329; border-radius: 8px; padding: 10px; }
    .status-running { color: #00ff00; font-weight: bold; }
    .status-stopped { color: #ff4444; font-weight: bold; }
    .status-error { color: #ff0000; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# HELPER FUNCTIONS
# =====================================================================

@st.cache_resource
def init_session_state():
    """Initialize Streamlit session state"""
    if "logs" not in st.session_state:
        st.session_state.logs = []
    if "metrics_history" not in st.session_state:
        st.session_state.metrics_history = []
    if "bot_status" not in st.session_state:
        st.session_state.bot_status = "unknown"
    if "current_metrics" not in st.session_state:
        st.session_state.current_metrics = None
    if "ws_thread" not in st.session_state:
        st.session_state.ws_thread = None

def safe_api_call(func):
    """Decorator for safe API calls with error handling"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.ConnectionError:
            st.error("❌ Backend not reachable. Ensure backend is running at " + BACKEND_URL)
            logger.error(f"Connection error to {BACKEND_URL}")
            return None
        except Exception as e:
            st.error(f"❌ API Error: {str(e)}")
            logger.error(f"API error in {func.__name__}: {str(e)}")
            return None
    return wrapper

@safe_api_call
def get_bot_status():
    """Fetch bot status from backend"""
    response = requests.get(f"{BACKEND_URL}/api/bot/status", timeout=5)
    response.raise_for_status()
    return response.json()

@safe_api_call
def start_bot():
    """Start the bot"""
    response = requests.post(f"{BACKEND_URL}/api/bot/start", timeout=5)
    response.raise_for_status()
    return response.json()

@safe_api_call
def stop_bot():
    """Stop the bot"""
    response = requests.post(f"{BACKEND_URL}/api/bot/stop", timeout=5)
    response.raise_for_status()
    return response.json()

@safe_api_call
def get_oanda_account():
    """Get OANDA account info"""
    response = requests.get(f"{BACKEND_URL}/api/broker/oanda/account", timeout=10)
    response.raise_for_status()
    return response.json()

@safe_api_call
def get_oanda_trades():
    """Get OANDA open trades"""
    response = requests.get(f"{BACKEND_URL}/api/broker/oanda/trades", timeout=10)
    response.raise_for_status()
    return response.json()

@safe_api_call
def get_coinbase_account():
    """Get Coinbase account info"""
    response = requests.get(f"{BACKEND_URL}/api/broker/coinbase/account", timeout=10)
    response.raise_for_status()
    return response.json()

@safe_api_call
def health_check():
    """Check backend health"""
    response = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
    response.raise_for_status()
    return response.json()

def websocket_listener():
    """Connect to WebSocket and listen for updates"""
    try:
        ws = websocket.WebSocketApp(
            WEBSOCKET_URL,
            on_message=lambda ws, msg: handle_ws_message(msg),
            on_error=lambda ws, err: logger.error(f"WebSocket error: {err}"),
            on_close=lambda ws: logger.info("WebSocket closed")
        )
        ws.run_forever()
    except Exception as e:
        logger.error(f"WebSocket connection failed: {e}")

def handle_ws_message(message: str):
    """Handle incoming WebSocket message"""
    try:
        data = json.loads(message)
        
        if "log" in data:
            st.session_state.logs.append(data["log"])
            if len(st.session_state.logs) > 500:  # Keep last 500
                st.session_state.logs = st.session_state.logs[-500:]
        
        if "metric" in data:
            metric = data["metric"]
            st.session_state.current_metrics = metric
            st.session_state.metrics_history.append(metric)
            if len(st.session_state.metrics_history) > 1000:  # Keep last 1000
                st.session_state.metrics_history = st.session_state.metrics_history[-1000:]
    
    except json.JSONDecodeError:
        logger.error(f"Failed to parse WebSocket message: {message}")

# =====================================================================
# STREAMLIT UI
# =====================================================================

def render_header():
    """Render dashboard header"""
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.title("🤖 RBOTzilla Dashboard")
    
    with col2:
        health = health_check()
        if health:
            status = health.get("bot_status", "unknown")
            if status == "running":
                st.markdown('<p class="status-running">🟢 RUNNING</p>', unsafe_allow_html=True)
            elif status == "stopped":
                st.markdown('<p class="status-stopped">🔴 STOPPED</p>', unsafe_allow_html=True)
            else:
                st.markdown('<p class="status-error">⚠️ ERROR</p>', unsafe_allow_html=True)
    
    with col3:
        if st.button("🔄 Refresh", key="refresh_btn", use_container_width=True):
            st.rerun()

def render_control_panel():
    """Render bot control buttons"""
    st.subheader("Bot Control")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("▶️ Start Bot", key="start_btn", use_container_width=True):
            result = start_bot()
            if result:
                st.success(f"✅ Bot started (PID: {result.get('pid')})")
            else:
                st.error("❌ Failed to start bot")
    
    with col2:
        if st.button("⏹️ Stop Bot", key="stop_btn", use_container_width=True):
            result = stop_bot()
            if result:
                st.success("✅ Bot stopped")
            else:
                st.error("❌ Failed to stop bot")
    
    with col3:
        auto_refresh = st.checkbox("Auto-refresh", value=True, key="auto_refresh")
        if auto_refresh:
            st.session_state.auto_refresh = True

def render_metrics():
    """Render current metrics"""
    st.subheader("📊 Performance Metrics")
    
    status = get_bot_status()
    if not status:
        st.warning("Unable to fetch metrics")
        return
    
    metrics = status.get("current_metrics")
    if metrics:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Open Trades",
                int(metrics.get("trades_open", 0)),
                delta=None
            )
        
        with col2:
            st.metric(
                "Closed Trades",
                int(metrics.get("trades_closed", 0)),
                delta=None
            )
        
        with col3:
            pnl = metrics.get("pnl", 0)
            st.metric(
                "P&L",
                f"${pnl:.2f}",
                delta=None,
                delta_color="normal" if pnl >= 0 else "inverse"
            )
        
        with col4:
            equity = metrics.get("equity", 0)
            st.metric(
                "Equity",
                f"${equity:.2f}",
                delta=None
            )
        
        col5, col6, col7 = st.columns(3)
        
        with col5:
            st.metric(
                "Margin Used",
                f"${metrics.get('margin_used', 0):.2f}",
                delta=None
            )
        
        with col6:
            st.metric(
                "Margin Available",
                f"${metrics.get('margin_available', 0):.2f}",
                delta=None
            )
        
        with col7:
            st.metric(
                "Leverage",
                f"{metrics.get('leverage', 0):.1f}x",
                delta=None
            )
        
        uptime = status.get("uptime_seconds", 0)
        st.metric("Uptime", f"{int(uptime // 3600)}h {int((uptime % 3600) // 60)}m")
    else:
        st.info("No metrics available yet. Start the bot.")

def render_metrics_chart():
    """Render metrics over time"""
    st.subheader("📈 Equity Curve")
    
    if st.session_state.metrics_history:
        df = pd.DataFrame(st.session_state.metrics_history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['equity'],
            mode='lines',
            name='Equity',
            line=dict(color='#00ff00', width=2)
        ))
        
        fig.update_layout(
            title="Equity Over Time",
            xaxis_title="Time",
            yaxis_title="Equity ($)",
            hovermode='x unified',
            template="plotly_dark",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No historical data yet.")

def render_logs():
    """Render logs display"""
    st.subheader("📋 Recent Logs")
    
    # Log level filter
    log_levels = ["ALL", "DEBUG", "INFO", "WARNING", "ERROR"]
    selected_level = st.selectbox("Filter by level:", log_levels, key="log_level_filter")
    
    # Get logs
    status = get_bot_status()
    if status:
        logs = status.get("logs", [])
        st.session_state.logs.extend(logs)
    
    # Filter
    display_logs = st.session_state.logs
    if selected_level != "ALL":
        display_logs = [l for l in display_logs if l.get("level") == selected_level]
    
    # Display
    if display_logs:
        log_df = pd.DataFrame(display_logs[-50:])  # Last 50
        
        # Format for display
        for idx, log in enumerate(reversed(log_df.to_dict('records'))):
            timestamp = log.get("timestamp", "N/A")
            level = log.get("level", "INFO")
            message = log.get("message", "")
            source = log.get("source", "bot")
            
            # Color by level
            if level == "ERROR":
                st.error(f"**[{timestamp}] [{level}] [{source}]** {message}")
            elif level == "WARNING":
                st.warning(f"**[{timestamp}] [{level}] [{source}]** {message}")
            elif level == "DEBUG":
                st.caption(f"[{timestamp}] [{level}] [{source}] {message}")
            else:
                st.text(f"[{timestamp}] [{level}] [{source}] {message}")
    else:
        st.info("No logs yet.")

def render_broker_info():
    """Render broker account info"""
    st.subheader("🏦 Broker Accounts")
    
    # OANDA
    with st.expander("OANDA Account", expanded=False):
        if st.button("Fetch OANDA Account", key="fetch_oanda"):
            oanda_data = get_oanda_account()
            if oanda_data:
                st.json(oanda_data)
            else:
                st.error("Failed to fetch OANDA account")
        
        if st.button("Fetch OANDA Trades", key="fetch_oanda_trades"):
            trades = get_oanda_trades()
            if trades:
                st.json(trades)
            else:
                st.error("Failed to fetch OANDA trades")
    
    # Coinbase
    with st.expander("Coinbase Account", expanded=False):
        if st.button("Fetch Coinbase Account", key="fetch_cb"):
            cb_data = get_coinbase_account()
            if cb_data:
                st.json(cb_data)
            else:
                st.error("Failed to fetch Coinbase account")

def render_config_panel():
    """Render configuration panel"""
    with st.sidebar:
        st.subheader("⚙️ Configuration")
        
        # Bot parameters
        with st.expander("Bot Parameters", expanded=False):
            risk_per_trade = st.slider(
                "Risk per trade (%)",
                min_value=0.1,
                max_value=5.0,
                value=2.0,
                step=0.1,
                key="risk_per_trade"
            )
            
            max_trades = st.number_input(
                "Max concurrent trades",
                min_value=1,
                max_value=10,
                value=3,
                key="max_trades"
            )
            
            if st.button("Apply Config", key="apply_config"):
                st.success(f"✅ Config applied: Risk={risk_per_trade}%, Max Trades={max_trades}")
        
        # API Keys (for demo, not recommended for production)
        with st.expander("API Configuration", expanded=False):
            st.warning("⚠️ Use environment variables in production, not input fields.")
            
            oanda_token = st.text_input(
                "OANDA Access Token",
                value=os.getenv("OANDA_ACCESS_TOKEN", ""),
                type="password",
                key="oanda_token_input"
            )
            
            oanda_account = st.text_input(
                "OANDA Account ID",
                value=os.getenv("OANDA_ACCOUNT_ID", ""),
                key="oanda_account_input"
            )
            
            coinbase_key = st.text_input(
                "Coinbase API Key",
                value=os.getenv("COINBASE_API_KEY", ""),
                type="password",
                key="cb_key_input"
            )
        
        # About
        st.markdown("---")
        st.markdown("""
        ### 📖 About RBOTzilla
        
        **Version**: 1.0  
        **Backend**: FastAPI + WebSockets  
        **Frontend**: Streamlit  
        **Brokers**: OANDA, Coinbase  
        
        **Docs**: [GitHub](https://github.com) | [Docs](https://docs.example.com)
        """)

# =====================================================================
# MAIN APP
# =====================================================================

def main():
    """Main app logic"""
    init_session_state()
    
    # Header
    render_header()
    
    # Control panel
    render_control_panel()
    
    # Metrics tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Metrics",
        "📈 Charts",
        "📋 Logs",
        "🏦 Brokers"
    ])
    
    with tab1:
        render_metrics()
    
    with tab2:
        render_metrics_chart()
    
    with tab3:
        render_logs()
    
    with tab4:
        render_broker_info()
    
    # Config panel
    render_config_panel()
    
    # Auto-refresh
    if st.session_state.get("auto_refresh", False):
        st.empty()
        time.sleep(REFRESH_INTERVAL)
        st.rerun()

if __name__ == "__main__":
    main()
