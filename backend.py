"""
RBOTzilla Backend Server — FastAPI + WebSocket for real-time bot control & monitoring
Handles bot lifecycle, metrics streaming, and broker API integration.
"""

import os
import json
import logging
import asyncio
import queue
import multiprocessing as mp
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from enum import Enum
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Broker imports (with error handling for placeholders)
try:
    from oandapyV20 import API
    from oandapyV20.endpoints.accounts import AccountSummary, AccountDetails
    from oandapyV20.endpoints.trades import TradesList, TradeDetails
    OANDA_AVAILABLE = True
except ImportError:
    OANDA_AVAILABLE = False
    logging.warning("oandapyV20 not installed. OANDA features disabled.")

try:
    from coinbase.client import CoinbaseClient
    COINBASE_AVAILABLE = True
except ImportError:
    COINBASE_AVAILABLE = False
    logging.warning("coinbase-advancedtrade-python not installed. Coinbase features disabled.")

# =====================================================================
# LOGGING SETUP
# =====================================================================

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('rbotzilla_backend.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# =====================================================================
# ENUMS & DATA MODELS
# =====================================================================

class BotStatus(str, Enum):
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"

class BotCommand(str, Enum):
    START = "start"
    STOP = "stop"
    PAUSE = "pause"
    RESUME = "resume"

class LogEntry(BaseModel):
    timestamp: str
    level: str
    message: str
    source: str = "bot"

class MetricSnapshot(BaseModel):
    timestamp: str
    trades_open: int
    trades_closed: int
    pnl: float
    equity: float
    margin_used: float
    margin_available: float
    leverage: float
    last_action: Optional[str] = None

class StatusResponse(BaseModel):
    status: BotStatus
    uptime_seconds: float
    logs: List[LogEntry]
    current_metrics: Optional[MetricSnapshot]
    error_message: Optional[str] = None

class BotConfig(BaseModel):
    risk_per_trade: float = 0.02
    max_concurrent_trades: int = 3
    enable_oanda: bool = True
    enable_coinbase: bool = False
    log_level: str = "INFO"

# =====================================================================
# BOT PROCESS & NODE SYSTEM
# =====================================================================

class BotNode:
    """Base class for bot nodes (data fetch, signal gen, execution, etc.)"""
    
    def __init__(self, name: str):
        self.name = name
        self.last_run = None
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Override in subclasses. Returns results dict."""
        return {"node": self.name, "status": "success"}

class DataFetchNode(BotNode):
    """Placeholder: Fetch market data (OHLC, ticks, etc.)"""
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        self.last_run = datetime.now(timezone.utc)
        return {
            "node": self.name,
            "status": "success",
            "data": {
                "pairs": ["EURUSD", "GBPUSD", "BTCUSD"],
                "candle_count": 100,
                "timestamp": self.last_run.isoformat()
            }
        }

class SignalGenerationNode(BotNode):
    """Placeholder: Generate trading signals from market data"""
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        self.last_run = datetime.now(timezone.utc)
        return {
            "node": self.name,
            "status": "success",
            "signals": [
                {"pair": "EURUSD", "signal": "BUY", "strength": 0.85},
                {"pair": "GBPUSD", "signal": "HOLD", "strength": 0.55}
            ]
        }

class ExecutionNode(BotNode):
    """Placeholder: Execute trades based on signals"""
    
    def __init__(self, name: str, oanda_client=None, coinbase_client=None):
        super().__init__(name)
        self.oanda_client = oanda_client
        self.coinbase_client = coinbase_client
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        self.last_run = datetime.now(timezone.utc)
        return {
            "node": self.name,
            "status": "success",
            "executed_trades": [
                {
                    "pair": "EURUSD",
                    "direction": "BUY",
                    "units": 10000,
                    "entry_price": 1.0850,
                    "trade_id": "trade_001"
                }
            ]
        }

def bot_process_worker(
    command_queue: mp.Queue,
    log_queue: mp.Queue,
    metric_queue: mp.Queue,
    config: BotConfig,
    oanda_client=None,
    coinbase_client=None
):
    """
    Main bot loop running in a separate process.
    - Reads commands from command_queue
    - Executes nodes in sequence
    - Sends logs & metrics to respective queues
    """
    
    status = BotStatus.STOPPED
    logger_proc = logging.getLogger(f"bot-process")
    
    # Initialize nodes
    nodes = [
        DataFetchNode("DataFetch"),
        SignalGenerationNode("SignalGen"),
        ExecutionNode("Execution", oanda_client, coinbase_client)
    ]
    
    loop_count = 0
    trades_open = 0
    trades_closed = 0
    
    try:
        while True:
            # Check for commands
            try:
                cmd = command_queue.get_nowait()
                if cmd == BotCommand.START:
                    status = BotStatus.RUNNING
                    msg = f"Bot started. Running {len(nodes)} nodes."
                    logger_proc.info(msg)
                    log_queue.put(LogEntry(
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        level="INFO",
                        message=msg,
                        source="bot"
                    ))
                elif cmd == BotCommand.STOP:
                    status = BotStatus.STOPPED
                    msg = "Bot stopped."
                    logger_proc.info(msg)
                    log_queue.put(LogEntry(
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        level="INFO",
                        message=msg,
                        source="bot"
                    ))
                elif cmd == BotCommand.PAUSE:
                    status = BotStatus.PAUSED
                elif cmd == BotCommand.RESUME:
                    status = BotStatus.RUNNING
            except queue.Empty:
                pass
            
            # Execute bot nodes if running
            if status == BotStatus.RUNNING:
                try:
                    loop_count += 1
                    context = {
                        "loop": loop_count,
                        "trades_open": trades_open,
                        "trades_closed": trades_closed
                    }
                    
                    for node in nodes:
                        result = node.execute(context)
                        msg = f"[{node.name}] Executed: {result['status']}"
                        logger_proc.debug(msg)
                        log_queue.put(LogEntry(
                            timestamp=datetime.now(timezone.utc).isoformat(),
                            level="DEBUG",
                            message=msg,
                            source=node.name
                        ))
                    
                    # Simulate trade activity
                    if loop_count % 5 == 0:
                        trades_open += 1
                    if loop_count % 10 == 0 and trades_open > 0:
                        trades_closed += 1
                        trades_open -= 1
                    
                    # Send metrics
                    metric_queue.put(MetricSnapshot(
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        trades_open=trades_open,
                        trades_closed=trades_closed,
                        pnl=trades_closed * 150.0,  # Placeholder
                        equity=10000.0 + (trades_closed * 150.0),
                        margin_used=trades_open * 5000.0,
                        margin_available=50000.0 - (trades_open * 5000.0),
                        leverage=2.0,
                        last_action=f"Loop {loop_count}"
                    ))
                    
                except Exception as e:
                    status = BotStatus.ERROR
                    error_msg = f"Bot error in node execution: {str(e)}"
                    logger_proc.error(error_msg)
                    log_queue.put(LogEntry(
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        level="ERROR",
                        message=error_msg,
                        source="bot"
                    ))
            
            # Sleep to avoid CPU spinning
            asyncio.run(asyncio.sleep(1))
    
    except KeyboardInterrupt:
        logger_proc.info("Bot process interrupted.")
    except Exception as e:
        logger_proc.error(f"Critical bot process error: {str(e)}")

# =====================================================================
# BROKER CLIENTS
# =====================================================================

class OandaWrapper:
    """Wrapper for OANDA API integration"""
    
    def __init__(self, access_token: str, account_id: str):
        self.access_token = access_token
        self.account_id = account_id
        self.available = OANDA_AVAILABLE
        
        if self.available:
            try:
                self.client = API(
                    access_token=access_token,
                    environment="practice"  # Use practice by default
                )
                logger.info("OANDA client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize OANDA client: {e}")
                self.available = False
        else:
            logger.warning("OANDA client not available (library not installed)")
    
    def get_account_summary(self) -> Optional[Dict]:
        """Fetch account summary"""
        if not self.available:
            return None
        
        try:
            req = AccountSummary(self.account_id)
            resp = self.client.request(req)
            return resp
        except Exception as e:
            logger.error(f"OANDA account summary error: {e}")
            return None
    
    def get_open_trades(self) -> Optional[List[Dict]]:
        """Fetch open trades"""
        if not self.available:
            return None
        
        try:
            req = TradesList(self.account_id)
            resp = self.client.request(req)
            return resp.get("trades", [])
        except Exception as e:
            logger.error(f"OANDA trades list error: {e}")
            return None

class CoinbaseWrapper:
    """Wrapper for Coinbase Advanced API integration"""
    
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.available = COINBASE_AVAILABLE
        
        if self.available:
            try:
                self.client = CoinbaseClient(
                    api_key=api_key,
                    api_secret=api_secret
                )
                logger.info("Coinbase client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Coinbase client: {e}")
                self.available = False
        else:
            logger.warning("Coinbase client not available (library not installed)")
    
    def get_account_summary(self) -> Optional[Dict]:
        """Fetch account summary"""
        if not self.available:
            return None
        
        try:
            # Placeholder: actual endpoint call would go here
            return {"account_uuid": "placeholder", "status": "ok"}
        except Exception as e:
            logger.error(f"Coinbase account error: {e}")
            return None

# =====================================================================
# FASTAPI APP
# =====================================================================

# Global state
bot_process: Optional[mp.Process] = None
command_queue: Optional[mp.Queue] = None
log_queue: Optional[mp.Queue] = None
metric_queue: Optional[mp.Queue] = None
bot_start_time: Optional[datetime] = None
oanda_client: Optional[OandaWrapper] = None
coinbase_client: Optional[CoinbaseWrapper] = None
current_status = BotStatus.STOPPED
recent_logs: List[LogEntry] = []
current_metrics: Optional[MetricSnapshot] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic"""
    global oanda_client, coinbase_client
    
    # Load env vars
    oanda_token = os.getenv("OANDA_ACCESS_TOKEN", "PLACEHOLDER_OANDA_TOKEN")
    oanda_account_id = os.getenv("OANDA_ACCOUNT_ID", "PLACEHOLDER_ACCOUNT_ID")
    coinbase_key = os.getenv("COINBASE_API_KEY", "PLACEHOLDER_CB_KEY")
    coinbase_secret = os.getenv("COINBASE_API_SECRET", "PLACEHOLDER_CB_SECRET")
    
    # Initialize clients
    oanda_client = OandaWrapper(oanda_token, oanda_account_id)
    coinbase_client = CoinbaseWrapper(coinbase_key, coinbase_secret)
    
    logger.info("Backend startup complete")
    yield
    logger.info("Backend shutdown")

app = FastAPI(title="RBOTzilla Backend", version="1.0", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================================
# REST ENDPOINTS
# =====================================================================

@app.post("/api/bot/start")
async def start_bot(config: BotConfig = None):
    """Start the bot"""
    global bot_process, command_queue, log_queue, metric_queue, bot_start_time, current_status
    
    if current_status == BotStatus.RUNNING:
        raise HTTPException(status_code=400, detail="Bot already running")
    
    try:
        # Create queues
        command_queue = mp.Queue()
        log_queue = mp.Queue()
        metric_queue = mp.Queue()
        
        # Start bot process
        bot_process = mp.Process(
            target=bot_process_worker,
            args=(command_queue, log_queue, metric_queue, config or BotConfig(),
                  oanda_client, coinbase_client),
            daemon=False
        )
        bot_process.start()
        bot_start_time = datetime.now(timezone.utc)
        current_status = BotStatus.RUNNING
        
        logger.info("Bot process started")
        return {"status": "started", "pid": bot_process.pid}
    
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        current_status = BotStatus.ERROR
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/bot/stop")
async def stop_bot():
    """Stop the bot"""
    global bot_process, command_queue, current_status
    
    if current_status == BotStatus.STOPPED:
        raise HTTPException(status_code=400, detail="Bot not running")
    
    try:
        if command_queue:
            command_queue.put(BotCommand.STOP)
        
        if bot_process and bot_process.is_alive():
            bot_process.terminate()
            bot_process.join(timeout=5)
            if bot_process.is_alive():
                bot_process.kill()
        
        current_status = BotStatus.STOPPED
        logger.info("Bot stopped")
        return {"status": "stopped"}
    
    except Exception as e:
        logger.error(f"Failed to stop bot: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/bot/status")
async def get_status() -> StatusResponse:
    """Get current bot status & metrics"""
    global current_status, bot_start_time, recent_logs, current_metrics, log_queue, metric_queue
    
    # Drain queues
    if log_queue:
        while not log_queue.empty():
            try:
                entry = log_queue.get_nowait()
                recent_logs.append(entry)
                if len(recent_logs) > 100:  # Keep last 100 logs
                    recent_logs.pop(0)
            except queue.Empty:
                break
    
    if metric_queue:
        try:
            while not metric_queue.empty():
                current_metrics = metric_queue.get_nowait()
        except queue.Empty:
            pass
    
    uptime = 0.0
    if bot_start_time:
        uptime = (datetime.now(timezone.utc) - bot_start_time).total_seconds()
    
    return StatusResponse(
        status=current_status,
        uptime_seconds=uptime,
        logs=recent_logs[-20:],  # Last 20 logs
        current_metrics=current_metrics
    )

@app.get("/api/broker/oanda/account")
async def get_oanda_account():
    """Get OANDA account summary"""
    if not oanda_client or not oanda_client.available:
        raise HTTPException(status_code=503, detail="OANDA client not available")
    
    try:
        summary = oanda_client.get_account_summary()
        return summary or {"error": "Failed to fetch account"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/broker/oanda/trades")
async def get_oanda_trades():
    """Get OANDA open trades"""
    if not oanda_client or not oanda_client.available:
        raise HTTPException(status_code=503, detail="OANDA client not available")
    
    try:
        trades = oanda_client.get_open_trades()
        return {"trades": trades or []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/broker/coinbase/account")
async def get_coinbase_account():
    """Get Coinbase account summary"""
    if not coinbase_client or not coinbase_client.available:
        raise HTTPException(status_code=503, detail="Coinbase client not available")
    
    try:
        summary = coinbase_client.get_account_summary()
        return summary or {"error": "Failed to fetch account"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health():
    """Health check"""
    return {
        "status": "ok",
        "bot_status": current_status,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# =====================================================================
# WEBSOCKET ENDPOINT
# =====================================================================

active_connections: List[WebSocket] = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time log & metric streaming"""
    await websocket.accept()
    active_connections.append(websocket)
    
    logger.info(f"WebSocket client connected. Total: {len(active_connections)}")
    
    try:
        while True:
            # Broadcast logs & metrics from queues
            data_to_send = {"type": "update"}
            
            if log_queue and not log_queue.empty():
                try:
                    log_entry = log_queue.get_nowait()
                    data_to_send["log"] = log_entry.dict()
                except queue.Empty:
                    pass
            
            if metric_queue and not metric_queue.empty():
                try:
                    metric = metric_queue.get_nowait()
                    data_to_send["metric"] = metric.dict()
                except queue.Empty:
                    pass
            
            # Send to client
            if "log" in data_to_send or "metric" in data_to_send:
                await websocket.send_json(data_to_send)
            
            await asyncio.sleep(0.5)
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        active_connections.remove(websocket)
        logger.info(f"WebSocket client disconnected. Total: {len(active_connections)}")

@app.on_event("startup")
async def startup():
    """Periodic task to broadcast metrics"""
    async def broadcast_task():
        while True:
            for connection in active_connections:
                try:
                    await connection.send_json({
                        "type": "ping",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                except Exception as e:
                    logger.error(f"Broadcast error: {e}")
            
            await asyncio.sleep(5)
    
    asyncio.create_task(broadcast_task())

# =====================================================================
# ENTRY POINT
# =====================================================================

if __name__ == "__main__":
    # Load env vars from .env if available
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    logger.info("Starting RBOTzilla backend server...")
    uvicorn.run(
        "backend:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
