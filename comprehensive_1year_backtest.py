#!/usr/bin/env python3
"""
RICK PHOENIX V2 - Comprehensive 1-Year Backtest
Tests all strategies with HiveMind integration across all platforms
Historical Data: /mnt/c/Users/RFing/Downloads/historical_csv/
"""
import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import json
from typing import Dict, List, Any

# Add project root to path
sys.path.insert(0, '/home/ing/RICK/RICK_PHOENIX')

from PhoenixV2.config.charter import Charter
from PhoenixV2.brain.hive_mind import HiveMindBridge
from PhoenixV2.brain.wolf_pack import WolfPack

print("=" * 80)
print("🔥 RICK PHOENIX V2 - 1-YEAR COMPREHENSIVE BACKTEST")
print("=" * 80)
print(f"Start Time: {datetime.now().isoformat()}")
print(f"Initial Capital: $5,000")
print(f"Monthly Addition: $1,000")
print(f"Charter: {Charter.MAX_CONCURRENT_POSITIONS} positions, {Charter.MAX_MARGIN_UTILIZATION*100}% margin")
print("=" * 80)

# Configuration
HISTORICAL_DATA_PATH = Path("/mnt/c/Users/RFing/Downloads/historical_csv")
INITIAL_CAPITAL = 5000.0
MONTHLY_DEPOSIT = 1000.0
BACKTEST_PERIOD_DAYS = 365
# Minimum WolfPack confidence required to enter a trade during the backtest.
# Lower this to 0.05 for exploratory testing; raise for more conservative tests.
BACKTEST_WOLF_CONSENSUS_THRESHOLD = float(os.getenv('BACKTEST_WOLF_CONSENSUS_THRESHOLD', '0.15'))
# By default the live brain uses any WolfPack direction (non-HOLD) and does not validate confidence except for crypto.
# To mirror live behavior, set BACKTEST_USE_CONFIDENCE_FILTER=false. If True, use BACKTEST_WOLF_CONSENSUS_THRESHOLD.
BACKTEST_USE_CONFIDENCE_FILTER = os.getenv('BACKTEST_USE_CONFIDENCE_FILTER', 'false').lower() in ['true', '1', 'yes']
# Debug toggles for backtesting
BACKTEST_DEBUG = os.getenv('BACKTEST_DEBUG', 'true').lower() in ['true', '1', 'yes']
BACKTEST_SINGLE_SYMBOL = os.getenv('BACKTEST_SINGLE_SYMBOL', '')  # empty for all
# Allow running the backtest in HiveMind-only mode (no WolfPack)
BACKTEST_USE_WOLF_PACK = os.getenv('BACKTEST_USE_WOLF_PACK', str(Charter.USE_WOLF_PACK)).lower() in ['true', '1', 'yes']
TRADING_FEE_PCT = 0.0008  # 0.08% per trade (OANDA typical)
print(f"Mode: {'WolfPack Allowed' if BACKTEST_USE_WOLF_PACK else 'HiveMind-only'}")

class BacktestEngine:
    def __init__(self):
        self.capital = INITIAL_CAPITAL
        self.equity_curve = [INITIAL_CAPITAL]
        self.trades = []
        self.positions = []
        self.hive_mind = HiveMindBridge()
        self.wolf_pack = None  # Will initialize if needed
        
    def load_historical_data(self, category: str) -> Dict[str, pd.DataFrame]:
        """Load all CSV files from a category (forex/crypto_spot/crypto_futures)"""
        category_path = HISTORICAL_DATA_PATH / category
        data = {}
        
        if not category_path.exists():
            print(f"⚠️  Path not found: {category_path}")
            return data
            
        for csv_file in category_path.glob("*.csv"):
            try:
                df = pd.read_csv(csv_file)
                # Ensure required columns exist
                required_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
                if all(col in df.columns for col in required_cols):
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    df = df.sort_values('timestamp')
                    # Filter to last 1 year
                    cutoff = df['timestamp'].max() - timedelta(days=BACKTEST_PERIOD_DAYS)
                    df = df[df['timestamp'] >= cutoff]
                    
                    symbol = csv_file.stem  # e.g., EUR_USD
                    data[symbol] = df
                    print(f"  ✅ Loaded {symbol}: {len(df)} candles")
                else:
                    print(f"  ⚠️  {csv_file.name}: Missing required columns")
            except Exception as e:
                print(f"  ❌ Error loading {csv_file.name}: {e}")
                
        return data
    
    def calculate_position_size(self, entry: float, sl: float, risk_pct: float = 0.02) -> float:
        """Calculate position size based on risk per trade"""
        risk_amount = self.capital * risk_pct
        stop_distance = abs(entry - sl)
        
        if stop_distance == 0:
            return 0
            
        position_size = risk_amount / stop_distance
        return position_size
    
    def simulate_trade(self, symbol: str, direction: str, entry: float, sl: float, 
                      tp: float, df: pd.DataFrame, entry_idx: int) -> Dict[str, Any]:
        """Simulate a single trade execution"""
        # Calculate position size
        position_size = self.calculate_position_size(entry, sl, Charter.MAX_RISK_PER_TRADE)
        
        if position_size == 0:
            if BACKTEST_DEBUG:
                print(f"   ⓘ simulate_trade: position_size=0 (entry={entry} sl={sl} risk_pct={Charter.MAX_RISK_PER_TRADE})")
            return None
            
        # Validate position fits within capital
        notional = position_size * entry
        if notional > self.capital * 0.5:  # Max 50% per position
            notional = self.capital * 0.5
            position_size = notional / entry
            
        # Apply trading fees
        entry_fee = notional * TRADING_FEE_PCT
        
        # Simulate trade execution through remaining candles
        exit_price = None
        exit_reason = None
        exit_idx = entry_idx
        
        for i in range(entry_idx + 1, len(df)):
            candle = df.iloc[i]
            
            # Check stop loss hit
            if direction == "BUY":
                if candle['low'] <= sl:
                    exit_price = sl
                    exit_reason = "STOP_LOSS"
                    exit_idx = i
                    break
                elif candle['high'] >= tp:
                    exit_price = tp
                    exit_reason = "TAKE_PROFIT"
                    exit_idx = i
                    break
            else:  # SELL
                if candle['high'] >= sl:
                    exit_price = sl
                    exit_reason = "STOP_LOSS"
                    exit_idx = i
                    break
                elif candle['low'] <= tp:
                    exit_price = tp
                    exit_reason = "TAKE_PROFIT"
                    exit_idx = i
                    break
                    
            # Max hold time: 7 days (168 hours)
            if i - entry_idx > 168:
                exit_price = candle['close']
                exit_reason = "TIMEOUT"
                exit_idx = i
                break
        
        # If no exit triggered, close at last candle
        if exit_price is None:
            exit_price = df.iloc[-1]['close']
            exit_reason = "EOD"
            exit_idx = len(df) - 1
            
        # Calculate P&L
        if direction == "BUY":
            pnl = (exit_price - entry) * position_size
        else:
            pnl = (entry - exit_price) * position_size
            
        exit_fee = position_size * exit_price * TRADING_FEE_PCT
        net_pnl = pnl - entry_fee - exit_fee
        
        return {
            "symbol": symbol,
            "direction": direction,
            "entry_price": entry,
            "exit_price": exit_price,
            "entry_time": df.iloc[entry_idx]['timestamp'],
            "exit_time": df.iloc[exit_idx]['timestamp'],
            "position_size": position_size,
            "notional": notional,
            "pnl": net_pnl,
            "pnl_pct": (net_pnl / notional) * 100,
            "exit_reason": exit_reason,
            "fees": entry_fee + exit_fee
        }
    
    def run_strategy_backtest(self, symbol: str, df: pd.DataFrame, 
                              strategy_name: str = "HiveMind") -> List[Dict]:
        """Run backtest for a single symbol with specified strategy"""
        trades = []
        
        # Initialize WolfPack for this run (when allowed)
        if BACKTEST_USE_WOLF_PACK and self.wolf_pack is None:
            self.wolf_pack = WolfPack()

        # Ensure minimum data points
        if len(df) < 100:
            return trades
            
        # Run through historical data
        # We step forward, simulating real-time data arrival
        # Optimization: Don't run every single candle if it's too slow, but for accuracy we should.
        # Let's run every candle but ensure we pass the correct history.
        
        for i in range(100, len(df) - 10):  # Leave buffer at end
            candle = df.iloc[i]
            
            # Check if we can take new position (respect Charter limits)
            active_positions = len([t for t in trades if t.get('exit_reason') is None])
            if active_positions >= Charter.MAX_CONCURRENT_POSITIONS:
                continue
                
            # Prepare Market Data for WolfPack
            # We must pass the history up to this point (i+1 to include current candle as 'latest closed')
            # In a real backtest, we'd assume 'i' is the just-closed candle.
            history_df = df.iloc[:i+1]
            
            market_data = {
                "symbol": symbol,
                "price": float(candle['close']),
                "high": float(candle['high']),
                "low": float(candle['low']),
                "volume": float(candle['volume']),
                "df": history_df # Pass full history for indicators
            }
            
            # Get Consensus from the REAL WolfPack (if enabled)
            if not BACKTEST_USE_WOLF_PACK:
                # HiveMind-only mode (no WolfPack) - no signals tested for WolfPack backtest harness
                continue
            consensus = self.wolf_pack.get_consensus(market_data)
            # Log the consensus details for debugging; per-symbol vote and confidence
            if consensus:
                if 'votes' in consensus:
                    # We only log every 500 candles to avoid huge output
                    if i % 500 == 0:
                        print(f"   ⓘ {symbol} @ idx={i} - Consensus: {consensus['direction']} confidence={consensus.get('confidence', 0.0):.3f} votes={consensus.get('votes')}")
            
            signal = None
            # Use a configurable, lower threshold for backtest so the WolfPack can be evaluated
            if not BACKTEST_USE_CONFIDENCE_FILTER:
                # Mirror live brain: take non-HOLD consensus as entry
                if consensus['direction'] == 'BUY':
                    signal = "BUY"
                elif consensus['direction'] == 'SELL':
                    signal = "SELL"
                else:
                    continue
            else:
                # Use the configured threshold
                if consensus['direction'] == 'BUY' and consensus.get('confidence', 0.0) >= BACKTEST_WOLF_CONSENSUS_THRESHOLD:
                    signal = "BUY"
                elif consensus['direction'] == 'SELL' and consensus.get('confidence', 0.0) >= BACKTEST_WOLF_CONSENSUS_THRESHOLD:
                    signal = "SELL"
                else:
                    continue
                
            # Set stop loss and take profit (3:1 RR minimum per Charter)
            # Use ATR for dynamic stops if WolfPack didn't provide them (it usually doesn't, it just votes direction)
            atr = df['high'].iloc[i-20:i].subtract(df['low'].iloc[i-20:i]).mean()
            entry = float(candle['close'])
            
            if signal == "BUY":
                sl = entry - (atr * 1.5)
                tp = entry + (atr * 4.5)  # 3:1 RR
            else:
                sl = entry + (atr * 1.5)
                tp = entry - (atr * 4.5)
                
            # Execute trade simulation
            if BACKTEST_DEBUG:
                print(f"   ⓘ Attempting trade: {symbol} {signal} idx={i} entry={entry:.6f} sl={sl:.6f} tp={tp:.6f} atr={atr:.6f} conf={consensus.get('confidence', 0.0):.3f}")
            trade = self.simulate_trade(symbol, signal, entry, sl, tp, df, i)
            if BACKTEST_DEBUG and trade is None:
                try:
                    pos_size_debug = self.calculate_position_size(entry, sl, Charter.MAX_RISK_PER_TRADE)
                except Exception as e:
                    pos_size_debug = f"error: {e}"
                print(f"   ⓘ simulate_trade returned None for {symbol} idx={i}. calc_pos_size={pos_size_debug}")
            if trade:
                trades.append(trade)
                # Update capital
                self.capital += trade['pnl']
                self.equity_curve.append(self.capital)
                
        return trades
    
    def generate_report(self, all_trades: List[Dict], category: str) -> Dict[str, Any]:
        """Generate performance report"""
        if not all_trades:
            return {
                "category": category,
                "total_trades": 0,
                "win_rate": 0,
                "total_pnl": 0,
                "avg_win": 0,
                "avg_loss": 0,
                "max_drawdown": 0,
                "sharpe_ratio": 0,
                "profit_factor": 0,
                "final_capital": self.capital
            }
            
        df_trades = pd.DataFrame(all_trades)
        
        winners = df_trades[df_trades['pnl'] > 0]
        losers = df_trades[df_trades['pnl'] < 0]
        
        return {
            "category": category,
            "total_trades": len(all_trades),
            "win_rate": (len(winners) / len(all_trades)) * 100 if len(all_trades) > 0 else 0,
            "total_pnl": df_trades['pnl'].sum(),
            "avg_win": winners['pnl'].mean() if len(winners) > 0 else 0,
            "avg_loss": losers['pnl'].mean() if len(losers) > 0 else 0,
            "max_drawdown": self.calculate_max_drawdown(),
            "sharpe_ratio": self.calculate_sharpe_ratio(df_trades),
            "profit_factor": abs(winners['pnl'].sum() / losers['pnl'].sum()) if len(losers) > 0 and losers['pnl'].sum() != 0 else 0,
            "final_capital": self.capital
        }
    
    def calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown"""
        if len(self.equity_curve) < 2:
            return 0
            
        peak = self.equity_curve[0]
        max_dd = 0
        
        for value in self.equity_curve:
            if value > peak:
                peak = value
            dd = ((peak - value) / peak) * 100
            if dd > max_dd:
                max_dd = dd
                
        return max_dd
    
    def calculate_sharpe_ratio(self, df_trades: pd.DataFrame) -> float:
        """Calculate Sharpe ratio"""
        if len(df_trades) < 2:
            return 0
            
        returns = df_trades['pnl_pct'].values
        if len(returns) == 0 or np.std(returns) == 0:
            return 0
            
        return (np.mean(returns) / np.std(returns)) * np.sqrt(252)  # Annualized

# Run backtest
engine = BacktestEngine()

print("\n" + "=" * 80)
print("📊 LOADING HISTORICAL DATA")
print("=" * 80)

# Load all categories
categories = {
    "OANDA_Forex": "forex",
    "Coinbase_Crypto_Spot": "crypto_spot",
    "Crypto_Futures": "crypto_futures"
}

all_results = {}
all_trades_combined = []

for platform, category in categories.items():
    print(f"\n🔍 {platform} ({category})")
    print("-" * 80)
    
    data = engine.load_historical_data(category)
    
    if not data:
        print(f"  ⚠️  No data found for {platform}")
        continue
        
    platform_trades = []
    
    for symbol, df in data.items():
        if BACKTEST_SINGLE_SYMBOL and symbol != BACKTEST_SINGLE_SYMBOL:
            continue
        print(f"\n  📈 Backtesting {symbol}...")
        trades = engine.run_strategy_backtest(symbol, df, "HiveMind+WolfPack")
        platform_trades.extend(trades)
        print(f"     Trades: {len(trades)}, Capital: ${engine.capital:,.2f}")
        
    all_trades_combined.extend(platform_trades)
    
    # Generate report for this platform
    report = engine.generate_report(platform_trades, platform)
    all_results[platform] = report
    
    print(f"\n  📊 {platform} Results:")
    print(f"     Total Trades: {report['total_trades']}")
    print(f"     Win Rate: {report['win_rate']:.1f}%")
    print(f"     Total P&L: ${report['total_pnl']:,.2f}")
    print(f"     Sharpe Ratio: {report['sharpe_ratio']:.2f}")
    print(f"     Max Drawdown: {report['max_drawdown']:.1f}%")

# Add monthly deposits
months_elapsed = BACKTEST_PERIOD_DAYS / 30
total_deposits = MONTHLY_DEPOSIT * months_elapsed
engine.capital += total_deposits

print("\n" + "=" * 80)
print("🎯 FINAL RESULTS - 1 YEAR BACKTEST")
print("=" * 80)
print(f"Initial Capital: ${INITIAL_CAPITAL:,.2f}")
print(f"Monthly Deposits: ${MONTHLY_DEPOSIT:,.2f} x {months_elapsed:.1f} = ${total_deposits:,.2f}")
print(f"Total Invested: ${INITIAL_CAPITAL + total_deposits:,.2f}")
print(f"Final Capital: ${engine.capital:,.2f}")
print(f"Net Profit: ${engine.capital - INITIAL_CAPITAL - total_deposits:,.2f}")
print(f"ROI: {((engine.capital - INITIAL_CAPITAL - total_deposits) / (INITIAL_CAPITAL + total_deposits)) * 100:.1f}%")

# Generate global report
global_report = engine.generate_report(all_trades_combined, "GLOBAL")
print(f"\nTotal Trades: {global_report['total_trades']}")
print(f"Win Rate: {global_report['win_rate']:.1f}%")
print(f"Sharpe Ratio: {global_report['sharpe_ratio']:.2f}")
print(f"Max Drawdown: {global_report['max_drawdown']:.1f}%")
print(f"Profit Factor: {global_report['profit_factor']:.2f}")

# Save results
output_file = Path("backtest_results") / f"1year_backtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
output_file.parent.mkdir(exist_ok=True)

results_data = {
    "backtest_config": {
        "initial_capital": INITIAL_CAPITAL,
        "monthly_deposit": MONTHLY_DEPOSIT,
        "period_days": BACKTEST_PERIOD_DAYS,
        "charter_max_positions": Charter.MAX_CONCURRENT_POSITIONS,
        "charter_max_margin": Charter.MAX_MARGIN_UTILIZATION,
        "trading_fee_pct": TRADING_FEE_PCT
    },
    "platform_results": all_results,
    "global_results": global_report,
    "final_capital": engine.capital,
    "total_invested": INITIAL_CAPITAL + total_deposits,
    "net_profit": engine.capital - INITIAL_CAPITAL - total_deposits,
    "roi_pct": ((engine.capital - INITIAL_CAPITAL - total_deposits) / (INITIAL_CAPITAL + total_deposits)) * 100,
    "hivemind_integrated": True,
    "wolfpack_integrated": BACKTEST_USE_WOLF_PACK
}

with open(output_file, 'w') as f:
    json.dump(results_data, f, indent=2)

print(f"\n✅ Results saved to: {output_file}")
print("=" * 80)
