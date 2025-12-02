#!/usr/bin/env python3
"""
Narration & PnL Logging Utility
Provides centralized logging for trading narration and P&L tracking
PIN: 841921
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional
import logging

# Project paths
PROJECT_ROOT = Path("/home/ing/RICK/RICK_LIVE_CLEAN")
LOGS_DIR = PROJECT_ROOT / "pre_upgrade" / "headless" / "logs"
NARRATION_FILE = LOGS_DIR / "narration.jsonl"
PNL_FILE = LOGS_DIR / "pnl.jsonl"

logger = logging.getLogger(__name__)

# Ensure log directory exists
LOGS_DIR.mkdir(parents=True, exist_ok=True)

def log_narration(
    event_type: str,
    details: Dict[str, Any],
    symbol: Optional[str] = None,
    venue: Optional[str] = None
) -> None:
    """
    Log trading narration event to narration.jsonl
    
    Args:
        event_type: Type of event (OCO_PLACED, FILL, ERROR, etc.)
        details: Event-specific details dictionary
        symbol: Trading symbol (optional)
        venue: Trading venue (oanda, coinbase, etc.)
    """
    try:
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "symbol": symbol,
            "venue": venue,
            "details": details
        }
        
        with open(NARRATION_FILE, 'a') as f:
            f.write(json.dumps(event) + '\n')
            
        logger.debug(f"Narration logged: {event_type}")
        
    except Exception as e:
        logger.error(f"Failed to log narration: {e}")


def log_pnl(
    symbol: str,
    venue: str,
    entry_price: float,
    exit_price: float,
    units: float,
    gross_pnl: float,
    fees: float,
    net_pnl: float,
    outcome: str,
    duration_seconds: int,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log P&L event to pnl.jsonl
    
    Args:
        symbol: Trading symbol
        venue: Trading venue
        entry_price: Entry price
        exit_price: Exit price
        units: Position size
        gross_pnl: P&L before fees
        fees: Total fees/commissions
        net_pnl: P&L after fees
        outcome: 'win' or 'loss'
        duration_seconds: Trade duration
        details: Optional additional details
    """
    try:
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "symbol": symbol,
            "venue": venue,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "units": units,
            "gross_pnl": gross_pnl,
            "fees": fees,
            "net_pnl": net_pnl,
            "outcome": outcome,
            "duration_seconds": duration_seconds,
            "details": details or {}
        }
        
        with open(PNL_FILE, 'a') as f:
            f.write(json.dumps(event) + '\n')
            
        logger.info(f"P&L logged: {symbol} {outcome} ${net_pnl:.2f}")
        
    except Exception as e:
        logger.error(f"Failed to log P&L: {e}")


def get_latest_narration(n: int = 10) -> list:
    """Get the latest N narration events"""
    try:
        if not NARRATION_FILE.exists():
            return []
        
        events = []
        with open(NARRATION_FILE, 'r') as f:
            for line in f:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        
        return events[-n:]
    
    except Exception as e:
        logger.error(f"Failed to read narration: {e}")
        return []


def get_latest_pnl(n: int = 10) -> list:
    """Get the latest N P&L events"""
    try:
        if not PNL_FILE.exists():
            return []
        
        events = []
        with open(PNL_FILE, 'r') as f:
            for line in f:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        
        return events[-n:]
    
    except Exception as e:
        logger.error(f"Failed to read P&L: {e}")
        return []


def get_session_summary() -> Dict[str, Any]:
    """Get session summary from P&L log"""
    try:
        pnl_events = get_latest_pnl(n=1000)  # Get all recent events
        
        if not pnl_events:
            return {
                "total_trades": 0,
                "wins": 0,
                "losses": 0,
                "win_rate": 0.0,
                "gross_pnl": 0.0,
                "total_fees": 0.0,
                "net_pnl": 0.0
            }
        
        wins = sum(1 for e in pnl_events if e.get("outcome") == "win")
        losses = sum(1 for e in pnl_events if e.get("outcome") == "loss")
        total = len(pnl_events)
        
        gross_pnl = sum(e.get("gross_pnl", 0) for e in pnl_events)
        total_fees = sum(e.get("fees", 0) for e in pnl_events)
        net_pnl = sum(e.get("net_pnl", 0) for e in pnl_events)
        
        return {
            "total_trades": total,
            "wins": wins,
            "losses": losses,
            "win_rate": (wins / total * 100) if total > 0 else 0.0,
            "gross_pnl": gross_pnl,
            "total_fees": total_fees,
            "net_pnl": net_pnl
        }
    
    except Exception as e:
        logger.error(f"Failed to get session summary: {e}")
        return {"error": str(e)}
