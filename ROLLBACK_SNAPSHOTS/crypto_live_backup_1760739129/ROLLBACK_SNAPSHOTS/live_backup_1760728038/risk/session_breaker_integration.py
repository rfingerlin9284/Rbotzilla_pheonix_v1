#!/usr/bin/env python3
"""
RBOTzilla UNI - Session Breaker Integration Example
Phase 25 - Trading Engine Integration with Session Circuit Breaker
PIN: 841921

This example demonstrates how to integrate the Session Breaker Engine with the main trading engine.
Shows integration with Phase 22 alerting and Phase 24 OCO validator for comprehensive risk management.
"""

import os
import sys
import time
import threading
from datetime import datetime
from typing import Dict, Optional

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from risk.session_breaker import SessionBreakerEngine, check_session_breaker

class TradingEngineWithSessionBreaker:
    """
    Example trading engine with integrated session breaker
    
    This demonstrates complete integration of the session breaker system
    with the main trading engine for ultimate risk protection.
    """
    
    def __init__(self, broker, initial_balance=10000.0):
        self.broker = broker
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.total_pnl = 0.0
        self.trade_history = []
        
        # Initialize session breaker
        self.session_breaker = SessionBreakerEngine(
            pnl_threshold_pct=-0.05,      # -5% daily loss limit
            consecutive_trigger_limit=3,   # 3 consecutive breaker triggers
            session_reset_hours=24,        # 24-hour session reset
            monitoring_interval=30         # 30-second monitoring
        )
        
        self.running = False
        self.trades_today = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.max_drawdown = 0.0
        self.current_drawdown = 0.0
        
        print("🚨 Trading Engine with Session Breaker initialized")
        print(f"   Initial balance: ${self.initial_balance:,.2f}")
        print(f"   P&L threshold: -5.0% (${self.initial_balance * -0.05:,.2f})")
        print(f"   Consecutive trigger limit: 3")
    
    def start_trading(self):
        """Start trading with session breaker protection"""
        print("\n🚀 Starting trading engine with session breaker protection...")
        
        # Check if breaker is already active from previous session
        if self.session_breaker.is_breaker_active:
            print("🚨 WARNING: Session breaker is already active from previous session!")
            print("   Use session_breaker.reset_session() to manually reset if needed")
            return False
        
        self.running = True
        
        try:
            self._main_trading_loop()
        except KeyboardInterrupt:
            print("\n⏹️  Stopping trading engine...")
            self.running = False
            return True
    
    def _main_trading_loop(self):
        """Main trading loop with session breaker integration"""
        loop_count = 0
        
        while self.running:
            loop_count += 1
            current_time = datetime.now().strftime('%H:%M:%S')
            
            print(f"\n📊 Trading Loop #{loop_count} - {current_time}")
            
            try:
                # 1. Execute trading strategies (mock)
                trade_result = self._execute_mock_trade()
                
                # 2. Update P&L and statistics
                if trade_result:
                    self._update_trade_statistics(trade_result)
                
                # 3. **CRITICAL**: Check session breaker before continuing
                if not self._check_session_breaker():
                    print("🚨 Session breaker triggered - HALTING TRADING ENGINE")
                    self._handle_emergency_shutdown()
                    break
                
                # 4. Additional risk checks (OCO, position monitoring, etc.)
                self._perform_additional_risk_checks()
                
                # 5. Log status
                self._log_trading_status()
                
                # Sleep before next loop
                time.sleep(10)
                
            except Exception as e:
                print(f"❌ Error in trading loop: {e}")
                
                # Check breaker on error too
                if not self._check_session_breaker():
                    print("🚨 Session breaker triggered after error")
                    break
                
                time.sleep(5)
    
    def _execute_mock_trade(self) -> Optional[Dict]:
        """Mock trading execution for demonstration"""
        import random
        
        # Simulate trade opportunity (30% chance)
        if random.random() < 0.3:
            # Simulate trade outcome (60% win rate normally, but decreasing with losses)
            win_rate = max(0.3, 0.6 - (self.losing_trades * 0.05))
            is_winner = random.random() < win_rate
            
            # Simulate trade size and outcome
            trade_size = random.uniform(100, 500)
            
            if is_winner:
                pnl = trade_size * random.uniform(0.01, 0.03)  # 1-3% gain
                print(f"   💰 Trade executed: +${pnl:.2f} (Winner)")
            else:
                pnl = -trade_size * random.uniform(0.01, 0.02)  # 1-2% loss
                print(f"   📉 Trade executed: ${pnl:.2f} (Loser)")
            
            trade_result = {
                'pnl': pnl,
                'size': trade_size,
                'is_winner': is_winner,
                'timestamp': datetime.now().isoformat()
            }
            
            return trade_result
        else:
            print("   📊 No trade opportunities found")
            return None
    
    def _update_trade_statistics(self, trade_result: Dict):
        """Update trading statistics"""
        pnl = trade_result['pnl']
        
        # Update totals
        self.total_pnl += pnl
        self.current_balance = self.initial_balance + self.total_pnl
        self.trades_today += 1
        
        # Update win/loss counts
        if trade_result['is_winner']:
            self.winning_trades += 1
        else:
            self.losing_trades += 1
        
        # Update drawdown
        if self.total_pnl < 0:
            self.current_drawdown = abs(self.total_pnl) / self.initial_balance
            self.max_drawdown = max(self.max_drawdown, self.current_drawdown)
        else:
            self.current_drawdown = 0.0
        
        # Store trade history
        self.trade_history.append(trade_result)
        
        print(f"   📈 Updated P&L: ${self.total_pnl:+.2f} | Balance: ${self.current_balance:,.2f}")
        print(f"   📊 Trades: {self.trades_today} | Win Rate: {(self.winning_trades/max(1, self.trades_today)*100):.1f}%")
    
    def _check_session_breaker(self) -> bool:
        """Check session breaker - returns False if trading should halt"""
        
        # Prepare trade statistics for breaker
        trade_stats = {
            'total_trades': self.trades_today,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'max_drawdown': self.max_drawdown,
            'current_drawdown': self.current_drawdown
        }
        
        # Check session breaker
        can_continue = self.session_breaker.check_breaker(
            current_pnl=self.total_pnl,
            account_balance=self.initial_balance,
            trade_stats=trade_stats
        )
        
        if not can_continue:
            print("   🚨 SESSION BREAKER: Trading halted due to risk limits")
            return False
        
        # Calculate risk level for display
        pnl_pct = (self.total_pnl / self.initial_balance) * 100
        risk_level = "LOW" if pnl_pct > -2 else "MEDIUM" if pnl_pct > -4 else "HIGH"
        
        print(f"   ✅ SESSION BREAKER: OK (P&L: {pnl_pct:+.1f}% | Risk: {risk_level})")
        return True
    
    def _perform_additional_risk_checks(self):
        """Additional risk management checks"""
        # This would integrate with other risk systems
        print("   🔍 Additional risk checks: OCO validation, position limits, correlation...")
        
        # Mock additional checks
        if self.trades_today > 20:
            print("   ⚠️  High trade frequency - monitoring for overtrading")
        
        if self.current_drawdown > 0.03:
            print(f"   ⚠️  Significant drawdown: {self.current_drawdown:.1%}")
    
    def _log_trading_status(self):
        """Log current trading status"""
        pnl_pct = (self.total_pnl / self.initial_balance) * 100
        win_rate = (self.winning_trades / max(1, self.trades_today)) * 100
        
        print(f"   📋 Status: P&L {pnl_pct:+.1f}% | Trades {self.trades_today} | WR {win_rate:.1f}% | DD {self.current_drawdown:.1%}")
    
    def _handle_emergency_shutdown(self):
        """Handle emergency shutdown when session breaker triggers"""
        print("\n" + "="*60)
        print("🚨 EMERGENCY SHUTDOWN INITIATED")
        print("="*60)
        
        print("📊 Final Trading Statistics:")
        print(f"   Total Trades: {self.trades_today}")
        print(f"   Winning Trades: {self.winning_trades}")
        print(f"   Losing Trades: {self.losing_trades}")
        print(f"   Win Rate: {(self.winning_trades/max(1, self.trades_today)*100):.1f}%")
        print(f"   Total P&L: ${self.total_pnl:+.2f}")
        print(f"   P&L Percentage: {(self.total_pnl/self.initial_balance)*100:+.2f}%")
        print(f"   Final Balance: ${self.current_balance:,.2f}")
        print(f"   Max Drawdown: {self.max_drawdown:.2%}")
        
        print(f"\n🔒 Session Breaker Status:")
        status = self.session_breaker.get_session_status()
        print(f"   Breaker Active: {status['is_breaker_active']}")
        print(f"   Consecutive Triggers: {status['consecutive_triggers']}")
        print(f"   Session Duration: {status['session_duration_hours']:.2f} hours")
        
        print(f"\n💾 Session breaker lock file created: .session_breaker.lock")
        print(f"   Trading engine will remain halted until manual reset")
        print(f"   Use session_breaker.reset_session() to reset after review")
        
        print("\n🚨 EMERGENCY SHUTDOWN COMPLETE")
        print("="*60)
        
        # Stop the engine
        self.running = False
    
    def get_current_status(self) -> Dict:
        """Get current engine status"""
        return {
            'running': self.running,
            'total_pnl': self.total_pnl,
            'current_balance': self.current_balance,
            'trades_today': self.trades_today,
            'win_rate': (self.winning_trades / max(1, self.trades_today)) * 100,
            'current_drawdown': self.current_drawdown,
            'max_drawdown': self.max_drawdown,
            'session_breaker_status': self.session_breaker.get_session_status()
        }

class MockBroker:
    """Mock broker for demonstration"""
    
    def __init__(self):
        self.name = "mock_session_broker"
        self.balance = 10000.0
    
    def get_account_balance(self):
        return self.balance

def run_session_breaker_demo():
    """Run comprehensive session breaker integration demonstration"""
    print("🚨 RBOTzilla UNI - Session Breaker Integration Demo")
    print("=" * 70)
    print("PIN: 841921 | Phase 25 | Final Risk Circuit Breaker Integration")
    print()
    
    # Create mock broker
    broker = MockBroker()
    
    print("🎯 Demo Options:")
    print("   1. Run trading engine with session breaker (automatic)")
    print("   2. Test manual session breaker trigger")
    print("   3. Show session breaker status")
    print("   4. Reset session breaker")
    print("   5. Exit demo")
    
    while True:
        try:
            choice = input("\nSelect option (1-5): ").strip()
            
            if choice == "1":
                print("\n🚀 Starting trading engine with session breaker...")
                print("   (The demo will simulate trades and trigger breaker on losses)")
                print("   (Press Ctrl+C to stop manually)")
                
                engine = TradingEngineWithSessionBreaker(broker, initial_balance=5000.0)  # Lower balance for faster demo
                engine.start_trading()
                
            elif choice == "2":
                print("\n🔴 Testing manual session breaker trigger...")
                breaker = SessionBreakerEngine()
                result = breaker.manual_stop("Manual demo trigger")
                print(f"   Manual trigger result: {'HALTED' if not result else 'FAILED'}")
                
            elif choice == "3":
                print("\n📊 Current Session Breaker Status:")
                breaker = SessionBreakerEngine()
                status = breaker.get_session_status()
                
                for key, value in status.items():
                    print(f"   {key}: {value}")
                
            elif choice == "4":
                print("\n🔄 Resetting session breaker...")
                breaker = SessionBreakerEngine()
                breaker.reset_session()
                print("   ✅ Session breaker reset complete")
                
            elif choice == "5":
                print("Demo complete - thanks for testing session breaker!")
                break
                
            else:
                print("Invalid option - please select 1-5")
                
        except KeyboardInterrupt:
            print("\nDemo interrupted by user")
            break
        except Exception as e:
            print(f"Demo error: {e}")
    
    print("\n🎉 Session Breaker Integration Demo Complete!")

if __name__ == "__main__":
    run_session_breaker_demo()