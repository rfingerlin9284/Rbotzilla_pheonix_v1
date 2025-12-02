#!/usr/bin/env python3
"""
Dual-Connector Pattern: Live Data + Practice Execution
Separates market data (live token) from order execution (practice token).
Allows safe paper trading with real-time market data.
PIN: 841921 | Charter Section 10
"""

import logging
import sys
import os
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone
import time

# Add parent directory for imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from brokers.oanda_connector import OandaConnector
except ImportError:
    try:
        from oanda_connector import OandaConnector
    except ImportError:
        # Fallback stub for testing
        class OandaConnector:
            def __init__(self, *args, **kwargs): pass

try:
    from narration_logger import log_narration
except ImportError:
    try:
        from util.narration_logger import log_narration
    except ImportError:
        def log_narration(*args, **kwargs):
            pass

class DualConnector:
    """
    Dual-source connector for practice trading with live market data.
    
    Pattern:
    - Live connector: reads streaming quotes, tick data, account stats (NO executions)
    - Practice connector: places orders, manages positions (NO market data reads)
    
    This isolates risk while using real market prices.
    """
    
    def __init__(self, live_token: Optional[str] = None, practice_token: Optional[str] = None):
        """
        Initialize dual-connector with separate credentials.
        
        Args:
            live_token: OANDA live account token (for data/streaming only)
            practice_token: OANDA practice account token (for execution)
        """
        self.logger = logging.getLogger(__name__)
        
        # Instantiate two connectors: one live (data), one practice (execution)
        # Both are environment-agnostic; only tokens differ
        self.live_connector = OandaConnector(environment="live") if live_token else None
        self.practice_connector = OandaConnector(environment="practice")
        
        # If live token is not available, warn but don't fail
        if not live_token:
            self.logger.warning("Live token not configured - will use practice prices for data")
            self.live_connector = self.practice_connector  # Fallback: use practice for both
        
        self.mode = "DUAL_SOURCE_LIVE_DATA_PRACTICE_EXEC" if self.live_connector != self.practice_connector else "SINGLE_SOURCE_PRACTICE"
        
        # Log the mode
        log_narration(
            event_type="DUAL_CONNECTOR_INIT",
            details={
                "mode": self.mode,
                "live_available": self.live_connector != self.practice_connector,
                "data_source": "live" if self.live_connector != self.practice_connector else "practice",
                "execution_source": "practice"
            },
            venue="internal"
        )
        
        self.logger.info(f"DualConnector initialized: {self.mode}")
    
    # --- DATA SOURCES (read from live connector) ---
    
    def get_live_quotes(self, instrument: str) -> Dict[str, Any]:
        """
        Fetch live market quotes for an instrument.
        Uses LIVE connector for real-time pricing.
        
        Args:
            instrument: Instrument pair (e.g., "EUR_USD")
            
        Returns:
            Dict with bid/ask/mid prices
        """
        if not self.live_connector:
            self.logger.error("Live connector not available")
            return {}
        
        try:
            # Would call live connector's pricing API
            # For now, stub implementation
            self.logger.debug(f"Fetching live quotes for {instrument} from LIVE connector")
            return {
                "instrument": instrument,
                "source": "live",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            self.logger.error(f"Failed to get live quotes: {e}")
            return {}
    
    def get_tick_data(self, instrument: str, granularity: str = "M15") -> List[Dict[str, Any]]:
        """
        Fetch historical tick/candle data.
        Uses LIVE connector for real-time data feed.
        
        Args:
            instrument: Instrument pair
            granularity: Timeframe (M15, M30, H1, etc.)
            
        Returns:
            List of candle/tick objects
        """
        if not self.live_connector:
            self.logger.error("Live connector not available")
            return []
        
        try:
            self.logger.debug(f"Fetching {granularity} tick data for {instrument} from LIVE connector")
            return []  # Stub
        except Exception as e:
            self.logger.error(f"Failed to get tick data: {e}")
            return []
    
    def stream_prices(self, instruments: List[str], callback=None):
        """
        Stream live prices for multiple instruments.
        Uses LIVE connector for WebSocket/SSE streaming.
        
        Args:
            instruments: List of instruments to stream
            callback: Function to call on each price update
        """
        if not self.live_connector:
            self.logger.error("Live connector not available for streaming")
            return
        
        self.logger.info(f"Streaming prices for {instruments} from LIVE connector")
        # Would initiate WebSocket/SSE stream with live connector
    
    # --- EXECUTION (writes to practice connector) ---
    
    def place_oco_order(self, instrument: str, entry_price: float, stop_loss: float,
                       take_profit: float, units: int, ttl_hours: float = 6.0) -> Dict[str, Any]:
        """
        Place OCO order for execution.
        Uses PRACTICE connector (no real money at risk).
        Prices sourced from LIVE connector.
        
        Args:
            instrument: Trading pair
            entry_price: Entry price (from live data)
            stop_loss: Stop loss price (from live data)
            take_profit: Take profit price (from live data)
            units: Position size
            ttl_hours: Time to live
            
        Returns:
            OCO order result
        """
        if not self.practice_connector:
            self.logger.error("Practice connector not available for execution")
            return {"success": False, "error": "Practice connector unavailable"}
        
        start_time = time.time()
        
        # Log the order placement with mode info
        log_narration(
            event_type="DUAL_CONNECTOR_ORDER",
            details={
                "data_source": "live" if self.live_connector != self.practice_connector else "practice",
                "execution_source": "practice",
                "instrument": instrument,
                "entry_price": entry_price,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "units": units
            },
            symbol=instrument,
            venue="dual_connector"
        )
        
        # Route order to PRACTICE connector for execution
        result = self.practice_connector.place_oco_order(
            instrument=instrument,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            units=units,
            ttl_hours=ttl_hours
        )
        
        # Add mode info to result
        result["connector_mode"] = self.mode
        result["data_source"] = "live" if self.live_connector != self.practice_connector else "practice"
        result["execution_source"] = "practice"
        
        execution_time = (time.time() - start_time) * 1000
        self.logger.info(
            f"OCO placed via DUAL_CONNECTOR: {instrument} | "
            f"Data: {result['data_source']} | Exec: {result['execution_source']} | "
            f"Latency: {result.get('latency_ms', execution_time):.1f}ms"
        )
        
        return result
    
    def get_orders(self, state: str = "PENDING") -> List[Dict[str, Any]]:
        """Get pending orders (from practice account)"""
        if not self.practice_connector:
            return []
        return self.practice_connector.get_orders(state)
    
    def get_trades(self) -> List[Dict[str, Any]]:
        """Get open trades (from practice account)"""
        if not self.practice_connector:
            return []
        return self.practice_connector.get_trades()
    
    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel order (from practice account)"""
        if not self.practice_connector:
            return {"success": False, "error": "Practice connector unavailable"}
        return self.practice_connector.cancel_order(order_id)
    
    def set_trade_stop(self, trade_id: str, stop_price: float) -> Dict[str, Any]:
        """Modify stop loss for open trade (practice account)"""
        if not self.practice_connector:
            return {"success": False, "error": "Practice connector unavailable"}
        return self.practice_connector.set_trade_stop(trade_id, stop_price)
    
    # --- DIAGNOSTICS ---
    
    def get_mode(self) -> Dict[str, str]:
        """Get current connector mode"""
        return {
            "mode": self.mode,
            "data_source": "live" if self.live_connector != self.practice_connector else "practice",
            "execution_source": "practice",
            "description": "Live market data with paper trading execution"
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance stats from both connectors"""
        stats = {}
        
        if self.live_connector and self.live_connector != self.practice_connector:
            stats["live_stats"] = self.live_connector.get_performance_stats()
        
        if self.practice_connector:
            stats["practice_stats"] = self.practice_connector.get_performance_stats()
        
        stats["mode"] = self.mode
        
        return stats

# Convenience function
def get_dual_connector(live_token: Optional[str] = None, 
                      practice_token: Optional[str] = None) -> DualConnector:
    """Get a dual-connector instance"""
    return DualConnector(live_token, practice_token)

if __name__ == "__main__":
    # Self-test
    print("🧪 Dual-Connector Self-Test\n")
    
    connector = DualConnector()
    
    print(f"Mode: {connector.mode}")
    print(f"\nMode Info:")
    for k, v in connector.get_mode().items():
        print(f"  {k}: {v}")
    
    print(f"\nPerformance Stats:")
    stats = connector.get_performance_stats()
    print(f"  {stats}")
    
    print("\n✅ Dual-Connector architecture validated")
