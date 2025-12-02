"""
RBOTzilla Client Library — Helper for communicating with FastAPI backend
Use this to integrate bot control into other scripts/applications.
"""

import requests
import json
import logging
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

# =====================================================================
# DATA CLASSES
# =====================================================================

@dataclass
class BotStatus:
    """Bot status snapshot"""
    status: str  # "running", "stopped", "paused", "error"
    uptime_seconds: float
    logs: List[Dict[str, Any]]
    current_metrics: Optional[Dict[str, Any]]
    error_message: Optional[str] = None

@dataclass
class MetricSnapshot:
    """Single metric point in time"""
    timestamp: str
    trades_open: int
    trades_closed: int
    pnl: float
    equity: float
    margin_used: float
    margin_available: float
    leverage: float
    last_action: Optional[str] = None

# =====================================================================
# CLIENT
# =====================================================================

class RBOTzillaClient:
    """Client for RBOTzilla FastAPI backend"""
    
    def __init__(self, backend_url: str = "http://127.0.0.1:8000", timeout: int = 10):
        """
        Initialize RBOTzilla client
        
        Args:
            backend_url: Base URL of FastAPI backend
            timeout: Request timeout in seconds
        """
        self.backend_url = backend_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict] = None,
        raise_on_error: bool = True
    ) -> Optional[Dict]:
        """
        Make HTTP request to backend
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            json_data: JSON body for POST/PUT
            raise_on_error: Raise exception on non-2xx response
        
        Returns:
            Response JSON or None if error
        """
        url = f"{self.backend_url}{endpoint}"
        
        try:
            if method == "GET":
                resp = self.session.get(url, timeout=self.timeout)
            elif method == "POST":
                resp = self.session.post(url, json=json_data, timeout=self.timeout)
            else:
                logger.error(f"Unsupported method: {method}")
                return None
            
            if raise_on_error:
                resp.raise_for_status()
            
            return resp.json()
        
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error to {url}: {e}")
            if raise_on_error:
                raise
            return None
        
        except requests.exceptions.Timeout as e:
            logger.error(f"Request timeout to {url}: {e}")
            if raise_on_error:
                raise
            return None
        
        except Exception as e:
            logger.error(f"Request error: {e}")
            if raise_on_error:
                raise
            return None
    
    # =====================================================================
    # BOT CONTROL
    # =====================================================================
    
    def start_bot(self, config: Optional[Dict] = None) -> bool:
        """
        Start the trading bot
        
        Args:
            config: Optional bot configuration dict
        
        Returns:
            True if started, False otherwise
        """
        try:
            result = self._make_request("POST", "/api/bot/start", config)
            if result and "pid" in result:
                logger.info(f"Bot started (PID: {result['pid']})")
                return True
            return False
        except Exception:
            return False
    
    def stop_bot(self) -> bool:
        """
        Stop the trading bot
        
        Returns:
            True if stopped, False otherwise
        """
        try:
            result = self._make_request("POST", "/api/bot/stop")
            if result and result.get("status") == "stopped":
                logger.info("Bot stopped")
                return True
            return False
        except Exception:
            return False
    
    def get_status(self) -> Optional[BotStatus]:
        """
        Get current bot status
        
        Returns:
            BotStatus object or None if error
        """
        try:
            result = self._make_request("GET", "/api/bot/status")
            if result:
                return BotStatus(
                    status=result.get("status"),
                    uptime_seconds=result.get("uptime_seconds", 0),
                    logs=result.get("logs", []),
                    current_metrics=result.get("current_metrics"),
                    error_message=result.get("error_message")
                )
            return None
        except Exception:
            return None
    
    def is_running(self) -> bool:
        """
        Check if bot is running
        
        Returns:
            True if running, False otherwise
        """
        status = self.get_status()
        return status and status.status == "running"
    
    # =====================================================================
    # METRICS
    # =====================================================================
    
    def get_metrics(self) -> Optional[MetricSnapshot]:
        """
        Get current metrics
        
        Returns:
            MetricSnapshot or None
        """
        status = self.get_status()
        if status and status.current_metrics:
            metrics = status.current_metrics
            return MetricSnapshot(
                timestamp=metrics.get("timestamp"),
                trades_open=metrics.get("trades_open", 0),
                trades_closed=metrics.get("trades_closed", 0),
                pnl=metrics.get("pnl", 0),
                equity=metrics.get("equity", 0),
                margin_used=metrics.get("margin_used", 0),
                margin_available=metrics.get("margin_available", 0),
                leverage=metrics.get("leverage", 0),
                last_action=metrics.get("last_action")
            )
        return None
    
    def get_pnl(self) -> float:
        """Get current P&L"""
        metrics = self.get_metrics()
        return metrics.pnl if metrics else 0.0
    
    def get_equity(self) -> float:
        """Get current equity"""
        metrics = self.get_metrics()
        return metrics.equity if metrics else 0.0
    
    def get_uptime_seconds(self) -> float:
        """Get bot uptime in seconds"""
        status = self.get_status()
        return status.uptime_seconds if status else 0.0
    
    def get_uptime_formatted(self) -> str:
        """Get formatted uptime string"""
        uptime = self.get_uptime_seconds()
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        seconds = int(uptime % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    # =====================================================================
    # LOGS
    # =====================================================================
    
    def get_logs(self, limit: int = 50) -> List[Dict]:
        """
        Get recent logs
        
        Args:
            limit: Max logs to return
        
        Returns:
            List of log dicts
        """
        status = self.get_status()
        if status:
            return status.logs[-limit:]
        return []
    
    def get_errors(self) -> List[Dict]:
        """
        Get only ERROR level logs
        
        Returns:
            List of error log dicts
        """
        logs = self.get_logs()
        return [l for l in logs if l.get("level") == "ERROR"]
    
    def get_warnings(self) -> List[Dict]:
        """
        Get only WARNING level logs
        
        Returns:
            List of warning log dicts
        """
        logs = self.get_logs()
        return [l for l in logs if l.get("level") == "WARNING"]
    
    # =====================================================================
    # BROKER APIs
    # =====================================================================
    
    def get_oanda_account(self) -> Optional[Dict]:
        """
        Get OANDA account summary
        
        Returns:
            Account dict or None
        """
        try:
            return self._make_request("GET", "/api/broker/oanda/account")
        except Exception:
            return None
    
    def get_oanda_trades(self) -> Optional[List[Dict]]:
        """
        Get OANDA open trades
        
        Returns:
            List of trade dicts or None
        """
        try:
            result = self._make_request("GET", "/api/broker/oanda/trades")
            return result.get("trades") if result else None
        except Exception:
            return None
    
    def get_coinbase_account(self) -> Optional[Dict]:
        """
        Get Coinbase account summary
        
        Returns:
            Account dict or None
        """
        try:
            return self._make_request("GET", "/api/broker/coinbase/account")
        except Exception:
            return None
    
    # =====================================================================
    # HEALTH
    # =====================================================================
    
    def health_check(self) -> bool:
        """
        Check backend health
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            result = self._make_request("GET", "/api/health", raise_on_error=False)
            return result and result.get("status") == "ok"
        except Exception:
            return False
    
    def wait_for_backend(self, timeout: int = 60, check_interval: int = 1) -> bool:
        """
        Wait for backend to become available
        
        Args:
            timeout: Max seconds to wait
            check_interval: Seconds between health checks
        
        Returns:
            True if backend became available, False if timeout
        """
        import time
        start = time.time()
        
        while time.time() - start < timeout:
            if self.health_check():
                logger.info("Backend is available")
                return True
            time.sleep(check_interval)
        
        logger.error(f"Backend did not become available within {timeout}s")
        return False

# =====================================================================
# CONVENIENCE FUNCTIONS
# =====================================================================

def create_client(backend_url: str = "http://127.0.0.1:8000") -> RBOTzillaClient:
    """Factory function for creating client"""
    return RBOTzillaClient(backend_url)

# =====================================================================
# EXAMPLE USAGE
# =====================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create client
    client = RBOTzillaClient()
    
    # Check health
    print("\n=== Health Check ===")
    if client.health_check():
        print("✅ Backend is healthy")
    else:
        print("❌ Backend unreachable")
        print("Make sure backend is running: python3 backend.py")
        exit(1)
    
    # Start bot
    print("\n=== Starting Bot ===")
    if client.start_bot():
        print("✅ Bot started")
    else:
        print("❌ Failed to start bot")
    
    # Wait a bit
    import time
    time.sleep(2)
    
    # Get status
    print("\n=== Bot Status ===")
    status = client.get_status()
    if status:
        print(f"Status: {status.status}")
        print(f"Uptime: {client.get_uptime_formatted()}")
        print(f"Recent logs: {len(status.logs)}")
    
    # Get metrics
    print("\n=== Metrics ===")
    metrics = client.get_metrics()
    if metrics:
        print(f"Equity: ${metrics.equity:.2f}")
        print(f"P&L: ${metrics.pnl:.2f}")
        print(f"Trades open: {metrics.trades_open}")
        print(f"Trades closed: {metrics.trades_closed}")
    
    # Get logs
    print("\n=== Recent Logs ===")
    logs = client.get_logs(limit=5)
    for log in logs:
        print(f"[{log['level']}] {log['message']}")
    
    # Stop bot
    print("\n=== Stopping Bot ===")
    if client.stop_bot():
        print("✅ Bot stopped")
    else:
        print("❌ Failed to stop bot")
    
    print("\n✅ Demo complete!")
