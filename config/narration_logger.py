"""
RICK NARRATION LOGGER
=====================
Real-time event logging with automatic terminal tail
Provides plain English narration of all system events
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
import json
from enum import Enum


class EventType(Enum):
    """Event types for narration"""
    SYSTEM_START = "SYSTEM_START"
    SYSTEM_STOP = "SYSTEM_STOP"
    STATUS_CHECK = "STATUS_CHECK"
    TRADE_SIGNAL = "TRADE_SIGNAL"
    TRADE_EXECUTED = "TRADE_EXECUTED"
    TRADE_MODIFIED = "TRADE_MODIFIED"
    TRADE_CLOSED = "TRADE_CLOSED"
    HIVE_CONSENSUS = "HIVE_CONSENSUS"
    GUARDIAN_GATE = "GUARDIAN_GATE"
    LEARNING_UPDATE = "LEARNING_UPDATE"
    MANUAL_TRADE = "MANUAL_TRADE"
    POSITION_REASSESS = "POSITION_REASSESS"
    ERROR = "ERROR"


class NarrationLogger:
    """Handles all system narration and logging in plain English"""
    
    def __init__(self, log_dir: str = "logs", log_file: str = "narration.log"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.log_file = self.log_dir / log_file
        
        # Configure logging
        self.logger = logging.getLogger("RICK_NARRATION")
        self.logger.setLevel(logging.DEBUG)
        
        # File handler
        fh = logging.FileHandler(self.log_file)
        fh.setLevel(logging.DEBUG)
        
        # Console handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
    
    # ============ PLAIN ENGLISH NARRATION ============
    
    def narrate_system_start(self, mode: str, brokers: list):
        """Narrate system startup"""
        msg = f"🟢 RICK SYSTEM STARTING in {mode.upper()} mode with {', '.join(brokers).upper()} brokers active."
        self.logger.info(msg)
        return msg
    
    def narrate_system_stop(self):
        """Narrate system shutdown"""
        msg = "🔴 RICK SYSTEM STOPPING. All trading halted. Monitoring positions until close."
        self.logger.info(msg)
        return msg
    
    def narrate_status_check(self, status_dict: dict):
        """Narrate status check in plain English"""
        mode = status_dict.get('trading_mode', 'unknown').upper()
        sys_status = status_dict.get('system_status', 'unknown').upper()
        brokers = status_dict.get('active_brokers', [])
        
        msg = f"📊 STATUS CHECK: Trading mode is {mode}, system is {sys_status}, active brokers are {', '.join(brokers).upper()}."
        self.logger.info(msg)
        return msg
    
    def narrate_hive_consensus(self, symbol: str, decision: str, confidence: float, votes: dict):
        """Narrate hive consensus decision"""
        vote_summary = " | ".join([f"{k}: {v:.0%}" for k, v in votes.items()])
        msg = f"🧠 HIVE CONSENSUS on {symbol}: {decision.upper()} with {confidence:.0%} confidence. Votes: {vote_summary}"
        self.logger.info(msg)
        return msg
    
    def narrate_guardian_gate(self, symbol: str, passed: bool, checks: dict):
        """Narrate guardian gate validation"""
        status = "✅ PASSED" if passed else "❌ REJECTED"
        checks_summary = " | ".join([f"{k}: {v}" for k, v in checks.items()])
        msg = f"🛡️ GUARDIAN GATE for {symbol}: {status}. Checks: {checks_summary}"
        self.logger.info(msg)
        return msg
    
    def narrate_trade_executed(self, symbol: str, direction: str, quantity: float, entry_price: float, broker: str):
        """Narrate trade execution"""
        msg = f"✅ TRADE EXECUTED: {direction.upper()} {quantity} {symbol} at {entry_price} via {broker.upper()}. Position now active."
        self.logger.info(msg)
        return msg
    
    def narrate_trade_modified(self, symbol: str, action: str, detail: str):
        """Narrate trade modification"""
        msg = f"🔄 POSITION MODIFIED on {symbol}: {action.upper()}. {detail}"
        self.logger.info(msg)
        return msg
    
    def narrate_position_reassess(self, symbol: str, current_pnl: float, action: str, reason: str):
        """Narrate position reassessment"""
        pnl_str = f"+${current_pnl}" if current_pnl > 0 else f"-${abs(current_pnl)}"
        msg = f"📈 POSITION REASSESS on {symbol}: Current P&L is {pnl_str}. Action: {action.upper()}. Reason: {reason}"
        self.logger.info(msg)
        return msg
    
    def narrate_trade_closed(self, symbol: str, pnl: float, reason: str):
        """Narrate trade closure"""
        pnl_str = f"+${pnl}" if pnl > 0 else f"-${abs(pnl)}"
        msg = f"📊 TRADE CLOSED on {symbol}: Final P&L: {pnl_str}. Reason: {reason}. Learning updated."
        self.logger.info(msg)
        return msg
    
    def narrate_learning_update(self, trades_analyzed: int, accuracy: float, improvement: float):
        """Narrate learning update"""
        msg = f"🧠 LEARNING UPDATE: Analyzed {trades_analyzed} trades. Current accuracy: {accuracy:.1%}. Improvement: +{improvement:.1%} from last update."
        self.logger.info(msg)
        return msg
    
    def narrate_manual_trade(self, symbol: str, parameters: dict):
        """Narrate manual trade input"""
        msg = f"👤 MANUAL TRADE REQUESTED: {symbol} with parameters: {json.dumps(parameters, indent=2)}"
        self.logger.info(msg)
        return msg
    
    def narrate_error(self, error_type: str, message: str):
        """Narrate error"""
        msg = f"⚠️ ERROR [{error_type}]: {message}"
        self.logger.error(msg)
        return msg
    
    # ============ UTILITY METHODS ============
    
    def get_tail(self, lines: int = 20) -> list:
        """Get last N lines of narration log"""
        try:
            with open(self.log_file, 'r') as f:
                all_lines = f.readlines()
                return all_lines[-lines:]
        except FileNotFoundError:
            return ["No narration log yet."]
    
    def print_tail(self, lines: int = 20):
        """Print tail of narration log to console"""
        print("\n" + "="*80)
        print("📜 NARRATION LOG (Latest Events)")
        print("="*80)
        for line in self.get_tail(lines):
            print(line.rstrip())
        print("="*80 + "\n")
    
    def stream_tail(self, lines: int = 20):
        """Continuously stream narration log (like 'tail -f')"""
        import time
        last_position = 0
        
        try:
            while True:
                try:
                    with open(self.log_file, 'r') as f:
                        f.seek(last_position)
                        new_lines = f.readlines()
                        last_position = f.tell()
                        
                        for line in new_lines:
                            print(line.rstrip())
                
                except FileNotFoundError:
                    pass
                
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\n\n[Stopped streaming narration log]")


# Global narration logger instance
_narration_logger: Optional[NarrationLogger] = None


def get_narration_logger() -> NarrationLogger:
    """Get or create global narration logger"""
    global _narration_logger
    if _narration_logger is None:
        _narration_logger = NarrationLogger()
    return _narration_logger


if __name__ == "__main__":
    # Example usage
    logger = get_narration_logger()
    
    logger.narrate_system_start("paper", ["oanda", "ibkr"])
    logger.narrate_hive_consensus(
        "EURUSD",
        "buy",
        0.87,
        {"ML_Model_1": 0.85, "Pattern_Match": 0.91, "Regime": 0.85}
    )
    logger.narrate_guardian_gate(
        "EURUSD",
        True,
        {"risk_check": "pass", "capital_check": "pass", "position_check": "pass"}
    )
    logger.narrate_trade_executed("EURUSD", "buy", 10000, 1.1050, "oanda")
    logger.narrate_status_check({
        "trading_mode": "paper_practice",
        "system_status": "online_autonomous",
        "active_brokers": ["oanda", "ibkr"]
    })
    
    logger.print_tail(10)
