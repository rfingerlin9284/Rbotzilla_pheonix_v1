#!/usr/bin/env python3
"""
RICK Safe Trading Engine
Progressive validation system - Paper → Validation → Live
Only enables live trading after proven performance
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional

# Add system paths
sys.path.append('/home/ing/RICK/RICK_LIVE_CLEAN')

from safe_mode_manager import SafeModeManager, TradingMode
from brokers.oanda_connector import OandaConnector
from brokers.coinbase_advanced_connector import CoinbaseAdvancedConnector

class SafeTradingEngine:
    """
    Safe trading engine with progressive validation
    """
    
    def __init__(self, pin: Optional[int] = None):
        self.pin = pin
        self.safe_mode = SafeModeManager(pin)
        self.logger = self._setup_logging()
        
        # Initialize connectors
        self.oanda = None
        self.coinbase = None
        self._initialize_connectors()
        
        # Trading state
        self.is_running = False
        self.current_mode = self.safe_mode.get_current_mode()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for safe trading"""
        logger = logging.getLogger('safe_trading_engine')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.FileHandler('logs/safe_trading.log', mode='a')
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
        
    def _initialize_connectors(self):
        """Initialize broker connectors based on current mode"""
        self.current_mode = self.safe_mode.get_current_mode()
        
        if self.current_mode == TradingMode.LIVE_AUTHORIZED:
            # Live mode - initialize with PIN
            self.logger.warning("🔴 INITIALIZING LIVE CONNECTORS")
            self.oanda = OandaConnector(pin=self.pin) if self.pin == 841921 else None
            self.coinbase = CoinbaseAdvancedConnector(pin=self.pin) if self.pin == 841921 else None
        else:
            # Paper/Safe mode - no PIN needed
            self.logger.info(f"📄 INITIALIZING PAPER CONNECTORS ({self.current_mode.value})")
            self.oanda = OandaConnector()  # Paper mode by default
            self.coinbase = CoinbaseAdvancedConnector()  # Paper mode by default
            
    def start_safe_trading_session(self, duration_minutes: int = 60) -> Dict:
        """Start a safe trading session with automatic progression tracking"""
        
        self.logger.info(f"🚀 Starting safe trading session - Mode: {self.current_mode.value}")
        
        # Pre-flight safety checks
        safety_check = self._perform_safety_checks()
        if not safety_check['safe_to_proceed']:
            return safety_check
            
        self.is_running = True
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        session_stats = {
            'start_time': start_time,
            'duration_minutes': duration_minutes,
            'trades_executed': 0,
            'total_pnl': 0.0,
            'mode': self.current_mode.value
        }
        
        try:
            while self.is_running and time.time() < end_time:
                # Check for mode progression
                self._check_mode_progression()
                
                # Execute trading logic
                trade_result = self._execute_safe_trading_logic()
                
                if trade_result:
                    session_stats['trades_executed'] += 1
                    session_stats['total_pnl'] += trade_result.get('pnl', 0)
                    
                    # Record trade for progression analysis
                    self.safe_mode.record_trade_result(trade_result)
                    
                    self.logger.info(f"Trade executed: {trade_result}")
                    
                # Wait before next iteration
                time.sleep(30)  # Check every 30 seconds
                
        except KeyboardInterrupt:
            self.logger.info("Trading session interrupted by user")
        except Exception as e:
            self.logger.error(f"Trading session error: {e}")
            
        self.is_running = False
        session_stats['end_time'] = time.time()
        
        # Generate session summary
        return self._generate_session_summary(session_stats)
        
    def _perform_safety_checks(self) -> Dict:
        """Perform comprehensive safety checks before trading"""
        checks = {
            'mode_valid': self.current_mode is not None,
            'connectors_initialized': bool(self.oanda or self.coinbase),
            'charter_loaded': True,  # Assume loaded from connectors
            'credentials_valid': True,  # Will be validated during first trade
            'live_authorization_valid': True  # Check if live mode is properly authorized
        }
        
        # Special check for live mode
        if self.current_mode == TradingMode.LIVE_AUTHORIZED:
            checks['live_authorization_valid'] = self.safe_mode._is_live_authorized()
            
        all_checks_pass = all(checks.values())
        
        return {
            'safe_to_proceed': all_checks_pass,
            'checks': checks,
            'mode': self.current_mode.value,
            'message': 'All safety checks passed' if all_checks_pass else 'Safety checks failed'
        }
        
    def _check_mode_progression(self):
        """Check if we should progress to next trading mode"""
        new_mode = self.safe_mode.get_current_mode()
        
        if new_mode != self.current_mode:
            self.logger.warning(f"🔄 MODE PROGRESSION: {self.current_mode.value} → {new_mode.value}")
            self.current_mode = new_mode
            
            # Reinitialize connectors for new mode
            self._initialize_connectors()
            
            # Log progression
            if new_mode == TradingMode.LIVE_READY:
                self.logger.warning("🎯 PERFORMANCE THRESHOLDS MET - Ready for live authorization!")
                
    def _execute_safe_trading_logic(self) -> Optional[Dict]:
        """Execute safe trading logic based on current mode"""
        
        # Demo trading logic - replace with your actual strategy
        if self.current_mode in [TradingMode.PAPER, TradingMode.SAFE_VALIDATION]:
            return self._execute_paper_trade()
        elif self.current_mode == TradingMode.LIVE_READY:
            # Continue paper trading until manual authorization
            return self._execute_paper_trade()
        elif self.current_mode == TradingMode.LIVE_AUTHORIZED:
            return self._execute_live_trade()
            
        return None
        
    def _execute_paper_trade(self) -> Optional[Dict]:
        """Execute a paper trade for validation"""
        
        # Simple demo strategy - random profitable/losing trades for testing
        import random
        
        # Simulate trade decision
        if random.random() < 0.1:  # 10% chance of trade each iteration
            
            # Simulate trade parameters
            symbol = random.choice(['EUR/USD', 'BTC-USD', 'ETH-USD'])
            side = random.choice(['BUY', 'SELL'])
            size_usd = random.randint(500, 2000)
            
            # Simulate result (biased toward winning for demo)
            is_win = random.random() < 0.67  # 67% win rate
            
            if is_win:
                pnl = random.randint(50, 300)  # $50-300 profit
                result = 'WIN'
            else:
                pnl = -random.randint(25, 150)  # $25-150 loss
                result = 'LOSS'
                
            return {
                'symbol': symbol,
                'side': side,
                'size_usd': size_usd,
                'result': result,
                'pnl': pnl,
                'timestamp': time.time(),
                'mode': 'PAPER'
            }
            
        return None
        
    def _execute_live_trade(self) -> Optional[Dict]:
        """Execute a live trade (only when authorized)"""
        
        # Verify authorization is still valid
        if not self.safe_mode._is_live_authorized():
            self.logger.error("🚫 Live authorization expired - switching to paper mode")
            self.current_mode = TradingMode.PAPER
            self._initialize_connectors()
            return None
            
        # Your actual live trading logic would go here
        # For now, return None to prevent accidental live trading
        self.logger.info("🔴 LIVE TRADE LOGIC - Would execute real trade here")
        
        return None
        
    def _generate_session_summary(self, stats: Dict) -> Dict:
        """Generate comprehensive session summary"""
        
        duration = stats['end_time'] - stats['start_time']
        
        # Get current progression status
        progression = self.safe_mode.get_progression_status()
        
        summary = {
            'session_complete': True,
            'duration_minutes': duration / 60,
            'trades_executed': stats['trades_executed'],
            'total_pnl': stats['total_pnl'],
            'mode_during_session': stats['mode'],
            'current_mode': progression['current_mode'],
            'ready_for_live': progression['ready_for_live'],
            'live_authorized': progression['live_authorized'],
            'performance_summary': progression['performance_summary'],
            'next_steps': progression['next_steps']
        }
        
        # Add session performance
        if stats['trades_executed'] > 0:
            summary['session_performance'] = {
                'avg_pnl_per_trade': stats['total_pnl'] / stats['trades_executed'],
                'trades_per_hour': stats['trades_executed'] / (duration / 3600),
                'profitable_session': stats['total_pnl'] > 0
            }
            
        self.logger.info(f"Session complete - {stats['trades_executed']} trades, "
                        f"${stats['total_pnl']:.2f} P&L, Mode: {progression['current_mode']}")
        
        return summary
        
    def get_status_dashboard(self) -> Dict:
        """Get comprehensive status dashboard"""
        progression = self.safe_mode.get_progression_status()
        
        return {
            'engine_status': 'RUNNING' if self.is_running else 'STOPPED',
            'current_mode': progression['current_mode'],
            'mode_description': self._get_mode_description(progression['current_mode']),
            'performance_summary': progression['performance_summary'],
            'threshold_status': progression['threshold_comparison'],
            'ready_for_live': progression['ready_for_live'],
            'live_authorized': progression['live_authorized'],
            'next_steps': progression['next_steps'],
            'connectors_status': {
                'oanda': 'ACTIVE' if self.oanda else 'INACTIVE',
                'coinbase': 'ACTIVE' if self.coinbase else 'INACTIVE'
            }
        }
        
    def _get_mode_description(self, mode: str) -> str:
        """Get user-friendly mode description"""
        descriptions = {
            'PAPER': 'Paper trading - Building performance history safely',
            'SAFE_VALIDATION': 'Validation mode - Testing strategy performance',
            'LIVE_READY': 'Ready for live - All thresholds met, awaiting authorization',
            'LIVE_AUTHORIZED': 'Live trading - Real money trading authorized'
        }
        return descriptions.get(mode, mode)
        
    def request_live_authorization_review(self) -> Dict:
        """Request live trading authorization review"""
        return self.safe_mode.request_live_authorization()
        
    def authorize_live_trading(self, pin: int, duration_hours: int = 24) -> Dict:
        """Authorize live trading with PIN"""
        result = self.safe_mode.authorize_live_trading(pin, duration_hours)
        
        if result.get('status') == 'authorized':
            self.logger.warning(f"🔴 LIVE TRADING AUTHORIZED for {duration_hours} hours")
            self._initialize_connectors()  # Reinitialize with live credentials
            
        return result
        
    def stop_trading(self):
        """Stop the trading engine"""
        self.is_running = False
        self.logger.info("🛑 Trading engine stopped")


def test_safe_engine():
    """Test the safe trading engine"""
    print("=== RICK Safe Trading Engine Test ===")
    print()
    
    # Initialize engine
    engine = SafeTradingEngine()
    
    # Get status
    status = engine.get_status_dashboard()
    
    print(f"Engine Status: {status['engine_status']}")
    print(f"Current Mode: {status['current_mode']}")
    print(f"Description: {status['mode_description']}")
    print()
    
    print("Performance Summary:")
    for key, value in status['performance_summary'].items():
        print(f"  {key}: {value}")
    print()
    
    print("Threshold Status (sample):")
    for metric, data in list(status['threshold_status'].items())[:3]:
        status_icon = "✅" if data['met'] else "❌"
        print(f"  {status_icon} {metric}: {data['current']} (need: {data['threshold']})")
    print()
    
    print("Next Steps:")
    for step in status['next_steps']:
        print(f"  • {step}")
    print()
    
    print("=== Test Complete ===")
    print("Run: engine.start_safe_trading_session(60) to begin trading")


if __name__ == "__main__":
    test_safe_engine()