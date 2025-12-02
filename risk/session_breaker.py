#!/usr/bin/env python3
"""
RBOTzilla UNI - Session Breaker Engine
Phase 25 - Final risk circuit breaker beyond daily breaker
PIN: 841921

This module implements the final session breaker system that provides ultimate risk protection
by monitoring cumulative P&L and halting the trading engine when critical thresholds are breached.
It integrates with the Phase 22 alerting system and Phase 23 watchdog for comprehensive protection.

Engineer (65%): Circuit breaker logic, session monitoring, system shutdown procedures
Prof_Quant (25%): Risk calculation, P&L analysis, threshold management
Trader_Psych (10%): Risk psychology, session confidence, trading discipline
"""

import os
import sys
import json
import time
import signal
import threading
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

try:
    from monitoring.alerting import send_system_alert
    ALERTING_AVAILABLE = True
except ImportError:
    ALERTING_AVAILABLE = False
    print("⚠️  Phase 22 alerting system not available - using fallback logging")

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('session_breaker')

@dataclass
class SessionStats:
    """Session statistics for breaker monitoring"""
    session_start: str
    total_trades: int
    winning_trades: int
    losing_trades: int
    gross_pnl: float
    net_pnl: float
    max_drawdown: float
    current_drawdown: float
    win_rate: float
    risk_score: float
    
@dataclass
class BreakerEvent:
    """Session breaker event record"""
    timestamp: str
    event_type: str  # 'THRESHOLD_BREACH', 'CONSECUTIVE_TRIGGER', 'MANUAL_STOP'
    trigger_reason: str
    pnl_at_trigger: float
    drawdown_at_trigger: float
    session_stats: SessionStats
    action_taken: str

class SessionBreakerEngine:
    """
    Session Breaker Engine - Final risk circuit breaker system
    
    This class provides ultimate risk protection by monitoring session-level metrics
    and implementing circuit breaker functionality to halt trading when critical
    thresholds are breached.
    """
    
    def __init__(self,
                 pnl_threshold_pct: float = -0.05,  # -5% cumulative P&L halt
                 consecutive_trigger_limit: int = 3,  # 3 consecutive breaker triggers
                 session_reset_hours: int = 24,      # 24 hours for session reset
                 monitoring_interval: int = 60):     # 60 seconds monitoring interval
        """
        Initialize Session Breaker Engine
        
        Args:
            pnl_threshold_pct: Cumulative intraday P&L threshold (-5% default)
            consecutive_trigger_limit: Max consecutive breaker triggers (3 default)
            session_reset_hours: Hours after which session resets (24 default)
            monitoring_interval: Monitoring frequency in seconds (60 default)
        """
        
        self.pnl_threshold_pct = pnl_threshold_pct
        self.consecutive_trigger_limit = consecutive_trigger_limit
        self.session_reset_hours = session_reset_hours
        self.monitoring_interval = monitoring_interval
        # Optional per-session trade limit (BOT_MAX_TRADES env var)
        try:
            self.max_trades_limit = int(os.getenv('BOT_MAX_TRADES', '0'))
        except Exception:
            self.max_trades_limit = 0
        # Per-venue overrides
        try:
            self.max_trades_limit_oanda = int(os.getenv('BOT_MAX_TRADES_OANDA', '0'))
        except Exception:
            self.max_trades_limit_oanda = 0
        try:
            self.max_trades_limit_ibkr = int(os.getenv('BOT_MAX_TRADES_IBKR', '0'))
        except Exception:
            self.max_trades_limit_ibkr = 0
        
        # File paths
        self.project_root = PROJECT_ROOT
        self.breaker_lock_file = Path(PROJECT_ROOT) / ".session_breaker.lock"
        self.breaker_log_file = Path(PROJECT_ROOT) / "logs" / "session_breaker.jsonl"
        self.session_stats_file = Path(PROJECT_ROOT) / "logs" / "session_stats.json"
        
        # Ensure log directory exists
        self.breaker_log_file.parent.mkdir(exist_ok=True)
        
        # Session state
        self.session_start_time = datetime.now(timezone.utc)
        self.is_breaker_active = False
        self.consecutive_triggers = 0
        self.breaker_history = []
        self.monitoring_active = False
        
        # Load previous state if exists
        self._load_session_state()
        
        logger.info("Session Breaker Engine initialized")
        logger.info(f"P&L threshold: {pnl_threshold_pct:.1%}")
        logger.info(f"Consecutive trigger limit: {consecutive_trigger_limit}")
        logger.info(f"Session reset hours: {session_reset_hours}")
        logger.info(f"Monitoring interval: {monitoring_interval}s")
    
    def check_breaker(self, current_pnl: float, account_balance: Optional[float] = None, 
                     trade_stats: Optional[Dict] = None) -> bool:
        """
        Main breaker check function - returns False if engine should halt
        
        Args:
            current_pnl: Current cumulative P&L
            account_balance: Account balance for percentage calculation
            trade_stats: Optional trade statistics dictionary
            
        Returns:
            bool: True to continue trading, False to halt engine
        """
        try:
            logger.debug(f"Checking session breaker - P&L: {current_pnl}")
            
            # Check if breaker is already active
            if self.is_breaker_active:
                logger.warning("Session breaker is active - trading halted")
                return False
            
            # Calculate percentage P&L if balance provided
            pnl_pct = 0.0
            if account_balance and account_balance > 0:
                pnl_pct = current_pnl / account_balance
            
            # Create current session stats
            session_stats = self._create_session_stats(current_pnl, pnl_pct, trade_stats)
            
            # Check global trade cap if set (BOT_MAX_TRADES)
            if self.max_trades_limit and session_stats.total_trades >= self.max_trades_limit:
                return self._trigger_breaker(
                    "TRADE_LIMIT_REACHED",
                    f"Trades per session {session_stats.total_trades} reached BOT_MAX_TRADES {self.max_trades_limit}",
                    current_pnl,
                    session_stats
                )

            # If trade_stats is provided and has a per-venue breakdown, enforce per-venue caps
            if trade_stats and isinstance(trade_stats, dict):
                by_venue = trade_stats.get('by_venue', {})
                if self.max_trades_limit_oanda and by_venue.get('OANDA', 0) >= self.max_trades_limit_oanda:
                    return self._trigger_breaker(
                        "TRADE_LIMIT_REACHED_OANDA",
                        f"Trades on OANDA {by_venue.get('OANDA', 0)} reached BOT_MAX_TRADES_OANDA {self.max_trades_limit_oanda}",
                        current_pnl,
                        session_stats
                    )
                if self.max_trades_limit_ibkr and by_venue.get('IBKR', 0) >= self.max_trades_limit_ibkr:
                    return self._trigger_breaker(
                        "TRADE_LIMIT_REACHED_IBKR",
                        f"Trades on IBKR {by_venue.get('IBKR', 0)} reached BOT_MAX_TRADES_IBKR {self.max_trades_limit_ibkr}",
                        current_pnl,
                        session_stats
                    )

            # Check P&L threshold breach
            if pnl_pct <= self.pnl_threshold_pct:
                return self._trigger_breaker(
                    "THRESHOLD_BREACH",
                    f"Cumulative P&L ({pnl_pct:.1%}) breached threshold ({self.pnl_threshold_pct:.1%})",
                    current_pnl,
                    session_stats
                )
            
            # Check consecutive trigger limit
            if self.consecutive_triggers >= self.consecutive_trigger_limit:
                return self._trigger_breaker(
                    "CONSECUTIVE_TRIGGER", 
                    f"Consecutive trigger limit reached ({self.consecutive_triggers})",
                    current_pnl,
                    session_stats
                )
            
            # Check for session reset
            self._check_session_reset()
            
            # Update session stats
            self._update_session_stats(session_stats)
            
            # All checks passed - continue trading
            return True
            
        except Exception as e:
            logger.error(f"Error in breaker check: {e}")
            # Fail safe - halt trading on error
            return False
    
    def _trigger_breaker(self, event_type: str, reason: str, pnl: float, 
                        session_stats: SessionStats) -> bool:
        """Trigger the session breaker"""
        
        try:
            logger.critical(f"🚨 SESSION BREAKER TRIGGERED: {reason}")
            
            # Update state
            self.is_breaker_active = True
            self.consecutive_triggers += 1
            
            # Create breaker event
            breaker_event = BreakerEvent(
                timestamp=datetime.now(timezone.utc).isoformat(),
                event_type=event_type,
                trigger_reason=reason,
                pnl_at_trigger=pnl,
                drawdown_at_trigger=session_stats.current_drawdown,
                session_stats=session_stats,
                action_taken="ENGINE_HALT"
            )
            
            # Log the event
            self._log_breaker_event(breaker_event)
            self.breaker_history.append(breaker_event)
            
            # Create breaker lock file
            self._create_breaker_lock(breaker_event)
            
            # Send critical alert
            self._send_breaker_alert(breaker_event)
            
            logger.critical("Trading engine halt initiated - session breaker active")
            
            # Return False to halt engine
            return False
            
        except Exception as e:
            logger.error(f"Error triggering breaker: {e}")
            return False
    
    def _create_session_stats(self, current_pnl: float, pnl_pct: float, 
                             trade_stats: Optional[Dict] = None) -> SessionStats:
        """Create current session statistics"""
        
        # Default stats if not provided
        if trade_stats is None:
            trade_stats = {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'max_drawdown': 0.0,
                'current_drawdown': abs(min(0, current_pnl))
            }
        
        total_trades = trade_stats.get('total_trades', 0)
        winning_trades = trade_stats.get('winning_trades', 0)
        win_rate = (winning_trades / max(1, total_trades)) * 100
        
        # Calculate risk score based on multiple factors
        risk_score = self._calculate_risk_score(pnl_pct, win_rate, trade_stats)
        
        return SessionStats(
            session_start=self.session_start_time.isoformat(),
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=trade_stats.get('losing_trades', 0),
            gross_pnl=current_pnl,
            net_pnl=current_pnl,  # Simplified - could subtract fees
            max_drawdown=trade_stats.get('max_drawdown', 0.0),
            current_drawdown=trade_stats.get('current_drawdown', 0.0),
            win_rate=win_rate,
            risk_score=risk_score
        )
    
    def _calculate_risk_score(self, pnl_pct: float, win_rate: float, 
                             trade_stats: Dict) -> float:
        """Calculate composite risk score (0-100, higher = more risky)"""
        
        # P&L component (0-40 points)
        pnl_risk = max(0, min(40, abs(pnl_pct) * 800))  # -5% = 40 points
        
        # Win rate component (0-30 points) 
        win_rate_risk = max(0, 30 - (win_rate * 0.6))  # 50% win rate = 0 points
        
        # Drawdown component (0-30 points)
        current_dd = trade_stats.get('current_drawdown', 0.0)
        max_dd = trade_stats.get('max_drawdown', 1.0)
        dd_risk = (current_dd / max(1.0, max_dd)) * 30
        
        return min(100, pnl_risk + win_rate_risk + dd_risk)
    
    def _create_breaker_lock(self, breaker_event: BreakerEvent):
        """Create session breaker lock file"""
        try:
            lock_data = {
                "breaker_active": True,
                "trigger_time": breaker_event.timestamp,
                "trigger_reason": breaker_event.trigger_reason,
                "pnl_at_trigger": breaker_event.pnl_at_trigger,
                "consecutive_triggers": self.consecutive_triggers,
                "session_start": self.session_start_time.isoformat(),
                "lock_file_version": "1.0"
            }
            
            with open(self.breaker_lock_file, 'w') as f:
                json.dump(lock_data, f, indent=2)
            
            logger.info(f"Session breaker lock created: {self.breaker_lock_file}")
            
        except Exception as e:
            logger.error(f"Failed to create breaker lock file: {e}")
    
    def _log_breaker_event(self, event: BreakerEvent):
        """Log breaker event to audit trail"""
        try:
            log_entry = {
                "timestamp": event.timestamp,
                "event_type": event.event_type,
                "trigger_reason": event.trigger_reason,
                "pnl_at_trigger": event.pnl_at_trigger,
                "drawdown_at_trigger": event.drawdown_at_trigger,
                "action_taken": event.action_taken,
                "session_stats": asdict(event.session_stats),
                "consecutive_triggers": self.consecutive_triggers
            }
            
            with open(self.breaker_log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
            
            logger.info(f"Breaker event logged to {self.breaker_log_file}")
            
        except Exception as e:
            logger.error(f"Failed to log breaker event: {e}")
    
    def _update_session_stats(self, stats: SessionStats):
        """Update session statistics file"""
        try:
            stats_data = {
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "session_stats": asdict(stats),
                "breaker_status": {
                    "is_active": self.is_breaker_active,
                    "consecutive_triggers": self.consecutive_triggers,
                    "last_check": datetime.now(timezone.utc).isoformat()
                }
            }
            
            with open(self.session_stats_file, 'w') as f:
                json.dump(stats_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to update session stats: {e}")
    
    def _send_breaker_alert(self, event: BreakerEvent):
        """Send critical session breaker alert"""
        
        alert_message = f"🚨 SESSION BREAKER ACTIVATED 🚨"
        alert_details = (
            f"{alert_message}\n"
            f"Reason: {event.trigger_reason}\n"
            f"P&L at trigger: {event.pnl_at_trigger:+.2f}\n"
            f"Drawdown: {event.drawdown_at_trigger:.1%}\n"
            f"Consecutive triggers: {self.consecutive_triggers}\n"
            f"Trading engine halted immediately"
        )
        
        # Send via Phase 22 alerting system
        if ALERTING_AVAILABLE:
            send_system_alert("SESSION_BREAKER", alert_details)
        
        logger.critical(f"Session Breaker Alert: {alert_details}")
    
    def _load_session_state(self):
        """Load previous session state if exists"""
        try:
            if self.breaker_lock_file.exists():
                with open(self.breaker_lock_file, 'r') as f:
                    lock_data = json.load(f)
                
                # Check if lock is still valid (within session reset period)
                trigger_time = datetime.fromisoformat(lock_data['trigger_time'].replace('Z', '+00:00'))
                time_since_trigger = datetime.now(timezone.utc) - trigger_time
                
                if time_since_trigger.total_seconds() < (self.session_reset_hours * 3600):
                    self.is_breaker_active = True
                    self.consecutive_triggers = lock_data.get('consecutive_triggers', 0)
                    logger.warning("Loaded active session breaker from previous session")
                else:
                    # Lock expired - remove it
                    self.breaker_lock_file.unlink()
                    logger.info("Expired session breaker lock removed")
            
        except Exception as e:
            logger.error(f"Error loading session state: {e}")
    
    def _check_session_reset(self):
        """Check if session should reset"""
        session_duration = datetime.now(timezone.utc) - self.session_start_time
        
        if session_duration.total_seconds() >= (self.session_reset_hours * 3600):
            logger.info("Session reset period reached - resetting session")
            self.reset_session()
    
    def reset_session(self):
        """Reset session breaker state"""
        try:
            logger.info("Resetting session breaker state")
            
            # Reset state
            self.session_start_time = datetime.now(timezone.utc)
            self.is_breaker_active = False
            self.consecutive_triggers = 0
            
            # Remove lock file
            if self.breaker_lock_file.exists():
                self.breaker_lock_file.unlink()
                logger.info("Session breaker lock file removed")
            
            # Send reset alert
            if ALERTING_AVAILABLE:
                send_system_alert("SESSION_RESET", "Session breaker state reset - trading re-enabled")
            
            logger.info("Session reset complete")
            
        except Exception as e:
            logger.error(f"Error resetting session: {e}")
    
    def manual_stop(self, reason: str = "Manual stop triggered"):
        """Manually trigger the session breaker"""
        logger.warning(f"Manual session breaker trigger: {reason}")
        
        # Create basic session stats
        session_stats = self._create_session_stats(0.0, 0.0, None)
        
        return self._trigger_breaker("MANUAL_STOP", reason, 0.0, session_stats)
    
    def get_session_status(self) -> Dict:
        """Get current session breaker status"""
        return {
            "is_breaker_active": self.is_breaker_active,
            "consecutive_triggers": self.consecutive_triggers,
            "session_start": self.session_start_time.isoformat(),
            "session_duration_hours": (datetime.now(timezone.utc) - self.session_start_time).total_seconds() / 3600,
            "pnl_threshold_pct": self.pnl_threshold_pct,
            "consecutive_trigger_limit": self.consecutive_trigger_limit,
            "breaker_lock_exists": self.breaker_lock_file.exists(),
            "total_breaker_events": len(self.breaker_history)
        }
    
    def start_monitoring(self, pnl_callback=None):
        """Start continuous session monitoring"""
        if self.monitoring_active:
            logger.warning("Session monitoring already active")
            return
        
        self.monitoring_active = True
        logger.info("Starting continuous session monitoring")
        
        def monitoring_loop():
            while self.monitoring_active:
                try:
                    # Get current P&L from callback if provided
                    current_pnl = 0.0
                    if pnl_callback and callable(pnl_callback):
                        current_pnl = pnl_callback()
                    
                    # Check breaker status
                    if not self.check_breaker(current_pnl):
                        logger.critical("Session breaker triggered - stopping monitoring")
                        break
                    
                    # Sleep until next check
                    time.sleep(self.monitoring_interval)
                    
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")
                    time.sleep(self.monitoring_interval)
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        self.monitoring_thread.start()
    
    def stop_monitoring(self):
        """Stop continuous session monitoring"""
        if self.monitoring_active:
            logger.info("Stopping session monitoring")
            self.monitoring_active = False

# Convenience functions for easy integration
def create_session_breaker(**kwargs) -> SessionBreakerEngine:
    """Create session breaker with default settings"""
    return SessionBreakerEngine(**kwargs)

def check_session_breaker(pnl: float, account_balance: Optional[float] = None, 
                         trade_stats: Optional[Dict] = None, **breaker_kwargs) -> bool:
    """Quick session breaker check"""
    breaker = create_session_breaker(**breaker_kwargs)
    return breaker.check_breaker(pnl, account_balance, trade_stats)

if __name__ == "__main__":
    # Demo mode - test session breaker functionality
    print("🚨 RBOTzilla UNI - Session Breaker Engine Demo")
    print("PIN: 841921 | Phase 25 | Final Risk Circuit Breaker")
    print()
    
    # Create session breaker
    breaker = create_session_breaker(
        pnl_threshold_pct=-0.03,  # -3% for demo
        consecutive_trigger_limit=2,
        monitoring_interval=5
    )
    
    print("📊 Testing session breaker scenarios...")
    
    # Test scenarios
    scenarios = [
        (100.0, 10000.0, "Normal trading - should continue"),
        (-200.0, 10000.0, "Small loss - should continue"),
        (-350.0, 10000.0, "Threshold breach - should trigger breaker"),
        (-100.0, 10000.0, "After breaker - should remain halted")
    ]
    
    for i, (pnl, balance, description) in enumerate(scenarios, 1):
        print(f"\n🔍 Scenario {i}: {description}")
        print(f"   P&L: {pnl:+.2f} | Balance: {balance:.2f} | P&L%: {(pnl/balance):.1%}")
        
        # Mock trade stats
        trade_stats = {
            'total_trades': 10 + i,
            'winning_trades': 5 + i//2,
            'losing_trades': 5 - i//2,
            'max_drawdown': 0.02,
            'current_drawdown': abs(min(0, pnl)) / balance
        }
        
        result = breaker.check_breaker(pnl, balance, trade_stats)
        
        status = "✅ CONTINUE" if result else "🚨 HALT"
        print(f"   Result: {status}")
        
        if not result:
            print(f"   🔒 Breaker active - trading halted!")
            break
    
    print(f"\n📈 Session Status: {breaker.get_session_status()}")
    print("\n🎉 Session Breaker Demo Complete!")