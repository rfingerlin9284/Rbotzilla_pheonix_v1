#!/usr/bin/env python3
"""
Ghost Trading Engine - TEST VERSION (2min validation)
Tests narration/P&L logging with real connector integration
"""

import sys
import time
import random
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from brokers.oanda_connector import OandaConnector
from util.narration_logger import log_narration, log_pnl, get_session_summary
from util.mode_manager import switch_mode, get_mode_info

class GhostTradingTest:
    """2-minute ghost trading test"""
    
    def __init__(self, test_duration_seconds=120):
        self.duration = test_duration_seconds
        self.start_time = datetime.now(timezone.utc)
        self.end_time = self.start_time + timedelta(seconds=self.duration)
        
        # Switch to GHOST mode
        print(f"\n🔄 Switching to GHOST mode...")
        switch_mode("GHOST")
        
        mode_info = get_mode_info()
        print(f"✅ Mode: {mode_info['mode']} - {mode_info['description']}")
        
        # Initialize connector with auto-detection
        print(f"📡 Initializing OANDA connector (auto-detect from .upgrade_toggle)...")
        self.connector = OandaConnector()
        print(f"✅ Environment: {self.connector.environment}\n")
        
        # Tracking
        self.trades = []
        self.starting_capital = 2000.0
        self.current_capital = self.starting_capital
        
    def simulate_trade(self):
        """Simulate a single ghost trade with real logging"""
        
        # Random symbol
        symbols = ["EUR_USD", "GBP_USD", "USD_JPY"]
        instrument = random.choice(symbols)
        
        # Random entry (simulate current price)
        entry_price = round(random.uniform(1.10, 1.30), 5)
        
        # Calculate OCO levels (3.2 RR minimum)
        pips = 0.0010
        sl_distance = 10 * pips
        tp_distance = sl_distance * 3.2  # Charter minimum RR
        
        side = random.choice(["buy", "sell"])
        
        if side == "buy":
            stop_loss = entry_price - sl_distance
            take_profit = entry_price + tp_distance
            units = 10000
        else:
            stop_loss = entry_price + sl_distance
            take_profit = entry_price - tp_distance
            units = -10000
        
        print(f"\n📊 Placing {side.upper()} OCO: {instrument}")
        print(f"   Entry: {entry_price:.5f}")
        print(f"   SL: {stop_loss:.5f}")
        print(f"   TP: {take_profit:.5f}")
        print(f"   Units: {units}")
        
        # Place OCO via connector (logs to narration.jsonl automatically)
        result = self.connector.place_oco_order(
            instrument=instrument,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            units=units,
            ttl_hours=6.0
        )
        
        if result["success"]:
            print(f"   ✅ OCO placed: {result['order_id'][:30]}... (latency: {result['latency_ms']:.1f}ms)")
            
            # Simulate trade outcome (70% win rate for ghost validation)
            outcome = "win" if random.random() < 0.70 else "loss"
            
            # Simulate trade duration
            duration_seconds = random.randint(300, 1800)  # 5-30 minutes
            
            # Calculate P&L
            if outcome == "win":
                exit_price = take_profit
                pnl_pips = abs(take_profit - entry_price)
            else:
                exit_price = stop_loss
                pnl_pips = -abs(entry_price - stop_loss)
            
            # Convert to USD (rough calculation)
            gross_pnl = pnl_pips * abs(units) * 100  # Simplified
            fees = abs(units) * 0.00002  # Rough commission estimate
            net_pnl = gross_pnl - fees
            
            self.current_capital += net_pnl
            
            print(f"   {outcome.upper()}: Exit @ {exit_price:.5f} | P&L: ${net_pnl:.2f}")
            
            # Log to P&L file
            log_pnl(
                symbol=instrument,
                venue="oanda",
                entry_price=entry_price,
                exit_price=exit_price,
                units=abs(units),
                gross_pnl=gross_pnl,
                fees=fees,
                net_pnl=net_pnl,
                outcome=outcome,
                duration_seconds=duration_seconds,
                details={
                    "side": side,
                    "ghost_mode": True,
                    "simulated": True
                }
            )
            
            self.trades.append({
                "instrument": instrument,
                "outcome": outcome,
                "net_pnl": net_pnl,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
        else:
            print(f"   ❌ OCO failed: {result.get('error', 'Unknown error')}")
    
    def run(self):
        """Run ghost trading test"""
        
        print("\n" + "=" * 70)
        print("🔥 GHOST TRADING TEST SESSION")
        print("=" * 70)
        print(f"Duration: {self.duration} seconds")
        print(f"Starting Capital: ${self.starting_capital:.2f}")
        print(f"Start: {self.start_time.strftime('%H:%M:%S')}")
        print(f"End: {self.end_time.strftime('%H:%M:%S')}")
        print("=" * 70)
        
        # Log session start
        log_narration(
            event_type="GHOST_SESSION_START",
            details={
                "duration_seconds": self.duration,
                "starting_capital": self.starting_capital,
                "start_time": self.start_time.isoformat()
            },
            symbol=None,
            venue="oanda"
        )
        
        trade_interval = self.duration / 5  # 5 trades over duration
        
        try:
            for i in range(5):
                if datetime.now(timezone.utc) >= self.end_time:
                    break
                
                print(f"\n🎯 Trade {i+1}/5")
                self.simulate_trade()
                
                # Wait between trades
                if i < 4:  # Don't wait after last trade
                    wait_time = min(trade_interval, 10)  # Max 10 sec wait for test
                    print(f"   ⏳ Waiting {wait_time:.0f}s before next trade...")
                    time.sleep(wait_time)
            
            # Session complete
            self.finalize_session()
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Session interrupted by user")
            self.finalize_session()
    
    def finalize_session(self):
        """Finalize ghost session and log results"""
        
        print("\n" + "=" * 70)
        print("📊 GHOST SESSION COMPLETE")
        print("=" * 70)
        
        wins = sum(1 for t in self.trades if t["outcome"] == "win")
        losses = len(self.trades) - wins
        win_rate = (wins / len(self.trades) * 100) if self.trades else 0
        total_pnl = self.current_capital - self.starting_capital
        
        print(f"Total Trades: {len(self.trades)}")
        print(f"Wins: {wins} | Losses: {losses}")
        print(f"Win Rate: {win_rate:.1f}%")
        print(f"Starting Capital: ${self.starting_capital:.2f}")
        print(f"Ending Capital: ${self.current_capital:.2f}")
        print(f"Net P&L: ${total_pnl:+.2f}")
        print("=" * 70)
        
        # Log session end
        log_narration(
            event_type="GHOST_SESSION_END",
            details={
                "total_trades": len(self.trades),
                "wins": wins,
                "losses": losses,
                "win_rate": win_rate,
                "starting_capital": self.starting_capital,
                "ending_capital": self.current_capital,
                "net_pnl": total_pnl,
                "duration_seconds": (datetime.now(timezone.utc) - self.start_time).total_seconds()
            },
            symbol=None,
            venue="oanda"
        )
        
        # Show P&L summary from logs
        print("\n📈 P&L Summary from logs:")
        summary = get_session_summary()
        print(f"   Total trades logged: {summary['total_trades']}")
        print(f"   Win rate: {summary['win_rate']:.1f}%")
        print(f"   Gross P&L: ${summary['gross_pnl']:.2f}")
        print(f"   Total fees: ${summary['total_fees']:.2f}")
        print(f"   Net P&L: ${summary['net_pnl']:.2f}")
        
        # Switch back to OFF
        print(f"\n🔄 Switching back to OFF mode...")
        switch_mode("OFF")
        print(f"✅ Mode restored to OFF")


if __name__ == "__main__":
    # Run 2-minute test session
    test = GhostTradingTest(test_duration_seconds=120)
    test.run()
