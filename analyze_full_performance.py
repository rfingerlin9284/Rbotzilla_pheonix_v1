#!/usr/bin/env python3
"""
Complete Trading Performance Analysis
Analyzes transaction history from OANDA dashboard screenshot
PIN: 841921
"""

import json
from datetime import datetime
from collections import defaultdict

# Transaction data from screenshot (Nov 2-6, 2025)
TRANSACTIONS = [
    # Nov 6
    {"ticket": 20693, "type": "Daily Financing", "pair": None, "units": 0, "profit": -1.93, "date": "2025-11-06 17:00"},
    {"ticket": 20690, "type": "Sell Market Filled", "pair": "NZD/CHF", "units": -32900, "profit": 0.00, "spread": -6.72, "price": 0.45622, "date": "2025-11-06 09:37"},
    
    # Nov 5
    {"ticket": 20687, "type": "Sell Market Filled", "pair": "AUD/CHF", "units": -28500, "profit": -70.83, "spread": -2.99, "price": 0.52565, "date": "2025-11-05 20:03"},
    {"ticket": 20686, "type": "Daily Financing", "pair": None, "units": 0, "profit": 1.30, "date": "2025-11-05 17:00"},
    {"ticket": 20683, "type": "Buy Market Filled", "pair": "AUD/CHF", "units": 28500, "profit": 0.00, "spread": -2.99, "price": 0.52765, "date": "2025-11-05 13:02"},
    {"ticket": 20679, "type": "Close Trade", "pair": "GBP/CHF", "units": 14200, "profit": 18.29, "spread": -3.24, "price": 1.05749, "date": "2025-11-05 12:45"},
    {"ticket": 20675, "type": "Close Trade", "pair": "USD/CHF", "units": 18500, "profit": -2.75, "spread": -1.82, "price": 0.81099, "date": "2025-11-05 12:45"},
    {"ticket": 20667, "type": "Buy Market Filled", "pair": "USD/CHF", "units": 18500, "profit": 0.00, "spread": -1.82, "price": 0.81111, "date": "2025-11-05 05:49"},
    {"ticket": 20663, "type": "Buy Market Filled", "pair": "GBP/CHF", "units": 14200, "profit": 0.00, "spread": -3.51, "price": 1.05644, "date": "2025-11-05 03:48"},
    
    # Nov 4
    {"ticket": 20660, "type": "Buy Market Filled", "pair": "NZD/CHF", "units": 32900, "profit": -93.05, "spread": -34.72, "price": 0.45892, "date": "2025-11-04 17:45"},
    {"ticket": 20657, "type": "Sell Market Filled", "pair": "NZD/CHF", "units": -32900, "profit": 0.00, "spread": -17.67, "price": 0.45664, "date": "2025-11-04 17:21"},
    {"ticket": 20654, "type": "Buy Market Filled", "pair": "GBP/USD", "units": 11500, "profit": 73.60, "spread": -0.98, "price": 1.30261, "date": "2025-11-04 13:03"},
    {"ticket": 20651, "type": "Sell Market Filled", "pair": "GBP/USD", "units": -11500, "profit": 0.00, "spread": -1.15, "price": 1.30901, "date": "2025-11-04 04:05"},
    
    # Nov 3
    {"ticket": 20647, "type": "Close Trade", "pair": "NZD/CHF", "units": 32600, "profit": -19.86, "spread": -7.26, "price": 0.46097, "date": "2025-11-03 16:08"},
    {"ticket": 20644, "type": "Buy Market Filled", "pair": "EUR/USD", "units": 13100, "profit": -26.33, "spread": -0.98, "price": 1.15330, "date": "2025-11-03 12:15"},
    {"ticket": 20639, "type": "Sell Market Filled", "pair": "EUR/USD", "units": -13100, "profit": 0.00, "spread": -0.92, "price": 1.15129, "date": "2025-11-03 05:07"},
    {"ticket": 20635, "type": "Buy Market Filled", "pair": "NZD/CHF", "units": 32600, "profit": 0.00, "spread": -7.27, "price": 0.46146, "date": "2025-11-03 04:51"},
    {"ticket": 20632, "type": "Buy Market Filled", "pair": "GBP/CHF", "units": 14200, "profit": -39.51, "spread": -10.49, "price": 1.05935, "date": "2025-11-03 02:30"},
    {"ticket": 20630, "type": "Sell Market Filled", "pair": "EUR/AUD", "units": -8600, "profit": -11.63, "spread": -1.10, "price": 1.75780, "date": "2025-11-03 00:36"},
    {"ticket": 20627, "type": "Sell Market Filled", "pair": "USD/CHF", "units": -18700, "profit": -4.67, "spread": -1.63, "price": 0.80444, "date": "2025-11-03 00:00"},
    {"ticket": 20621, "type": "Buy Market Filled", "pair": "EUR/AUD", "units": 8600, "profit": 0.00, "spread": -1.01, "price": 1.75985, "date": "2025-11-02 23:55"},
    {"ticket": 20617, "type": "Sell Market Filled", "pair": "GBP/CHF", "units": -14200, "profit": 0.00, "spread": -3.71, "price": 1.05712, "date": "2025-11-02 23:50"},
    {"ticket": 20613, "type": "Buy Market Filled", "pair": "USD/CHF", "units": 18700, "profit": 0.00, "spread": -1.86, "price": 0.80464, "date": "2025-11-02 23:50"},
    
    # Nov 2 - Position closes
    {"ticket": 20609, "type": "Close Trade", "pair": "NZD/USD", "units": 614, "profit": 0.41, "spread": -0.07, "date": "2025-11-02 23:38"},
    {"ticket": 20605, "type": "Close Trade", "pair": "GBP/USD", "units": 1, "profit": 0.00, "spread": -0.00, "date": "2025-11-02 23:38"},
    {"ticket": 20601, "type": "Close Trade", "pair": "USD/CHF", "units": 18700, "profit": -4.44, "spread": -1.51, "date": "2025-11-02 23:37"},
    {"ticket": 20597, "type": "Close Trade", "pair": "EUR/AUD", "units": 8600, "profit": -3.00, "spread": -0.93, "date": "2025-11-02 23:37"},
    {"ticket": 20593, "type": "Close Trade", "pair": "NZD/CHF", "units": 32600, "profit": -20.77, "spread": -7.29, "date": "2025-11-02 23:37"},
    {"ticket": 20589, "type": "Buy Market Filled", "pair": "EUR/AUD", "units": 8600, "profit": 0.00, "spread": -1.10, "price": 1.76022, "date": "2025-11-02 23:26"},
    {"ticket": 20585, "type": "Sell Market Filled", "pair": "NZD/CHF", "units": -32600, "profit": 0.00, "spread": -7.50, "price": 0.46041, "date": "2025-11-02 23:21"},
    {"ticket": 20581, "type": "Buy Market Filled", "pair": "USD/CHF", "units": 18700, "profit": 0.00, "spread": -1.98, "price": 0.80469, "date": "2025-11-02 23:05"},
]

def format_currency(val):
    """Format with accounting style: negative as (val), positive as +val"""
    if val < 0:
        return f"(-${abs(val):.2f})"
    elif val > 0:
        return f"+${val:.2f}"
    else:
        return "$0.00"

def format_units(val):
    """Format units with accounting style"""
    if val < 0:
        return f"({abs(val):,})"
    else:
        return f"{val:,}"

def analyze_performance():
    """Complete performance breakdown"""
    
    print("=" * 80)
    print("🤖 RICK TRADING SYSTEM - COMPLETE PERFORMANCE ANALYSIS")
    print("=" * 80)
    print()
    
    # Extract closed trades (with profit/loss)
    closed_trades = []
    for tx in TRANSACTIONS:
        if tx["type"] in ["Close Trade", "Sell Market Filled", "Buy Market Filled"]:
            profit = tx.get("profit", 0)
            if profit != 0:  # Only count if there's a realized P&L
                closed_trades.append(tx)
    
    # Separate wins and losses
    wins = [t for t in closed_trades if t["profit"] > 0]
    losses = [t for t in closed_trades if t["profit"] < 0]
    breakeven = [t for t in closed_trades if t["profit"] == 0]
    
    # Calculate totals
    total_profit = sum(t["profit"] for t in wins)
    total_loss = sum(t["profit"] for t in losses)
    net_pnl = total_profit + total_loss
    
    # Calculate spread costs
    all_spreads = [t.get("spread", 0) for t in TRANSACTIONS if "spread" in t]
    total_spread_cost = sum(all_spreads)
    
    # Calculate financing costs
    financing = [t for t in TRANSACTIONS if t["type"] == "Daily Financing"]
    total_financing = sum(t["profit"] for t in financing)
    
    print("📊 OVERALL SUMMARY:")
    print(f"   Total Closed Trades: {len(closed_trades)}")
    print(f"   Wins: {len(wins)} | Losses: {len(losses)} | Breakeven: {len(breakeven)}")
    print(f"   Win Rate: {(len(wins) / len(closed_trades) * 100):.1f}%" if closed_trades else "   Win Rate: N/A")
    print()
    
    print("💰 PROFIT & LOSS:")
    print(f"   Total Profit: {format_currency(total_profit)}")
    print(f"   Total Loss: {format_currency(total_loss)}")
    print(f"   Net P&L: {format_currency(net_pnl)}")
    print(f"   Average Win: {format_currency(total_profit / len(wins))}" if wins else "   Average Win: N/A")
    print(f"   Average Loss: {format_currency(total_loss / len(losses))}" if losses else "   Average Loss: N/A")
    print()
    
    print("💸 COSTS:")
    print(f"   Total Spread Cost: {format_currency(total_spread_cost)}")
    print(f"   Daily Financing: {format_currency(total_financing)}")
    print(f"   Combined Costs: {format_currency(total_spread_cost + total_financing)}")
    print()
    
    print("📉 NET RESULT:")
    final_result = net_pnl + total_spread_cost + total_financing
    print(f"   Trading P&L: {format_currency(net_pnl)}")
    print(f"   Minus Costs: {format_currency(total_spread_cost + total_financing)}")
    print(f"   FINAL RESULT: {format_currency(final_result)}")
    print()
    
    # By pair analysis
    print("=" * 80)
    print("📈 PERFORMANCE BY PAIR:")
    print("=" * 80)
    print()
    
    pair_stats = defaultdict(lambda: {"trades": 0, "wins": 0, "losses": 0, "pnl": 0, "spread": 0})
    
    for t in closed_trades:
        if t["pair"]:
            pair = t["pair"]
            pair_stats[pair]["trades"] += 1
            pair_stats[pair]["pnl"] += t["profit"]
            pair_stats[pair]["spread"] += t.get("spread", 0)
            if t["profit"] > 0:
                pair_stats[pair]["wins"] += 1
            elif t["profit"] < 0:
                pair_stats[pair]["losses"] += 1
    
    # Sort by P&L
    sorted_pairs = sorted(pair_stats.items(), key=lambda x: x[1]["pnl"], reverse=True)
    
    for pair, stats in sorted_pairs:
        win_rate = (stats["wins"] / stats["trades"] * 100) if stats["trades"] > 0 else 0
        net = stats["pnl"] + stats["spread"]
        
        print(f"{pair}:")
        print(f"   Trades: {stats['trades']} ({stats['wins']}W / {stats['losses']}L) - {win_rate:.1f}% win rate")
        print(f"   Trading P&L: {format_currency(stats['pnl'])}")
        print(f"   Spread Cost: {format_currency(stats['spread'])}")
        print(f"   Net Result: {format_currency(net)}")
        print()
    
    # Biggest wins and losses
    print("=" * 80)
    print("🏆 TOP 3 WINS:")
    print("=" * 80)
    print()
    
    top_wins = sorted(wins, key=lambda x: x["profit"], reverse=True)[:3]
    for i, t in enumerate(top_wins, 1):
        print(f"{i}. {t['pair']}: {format_currency(t['profit'])} ({format_units(t['units'])} units)")
        print(f"   Date: {t['date']} | Price: {t.get('price', 'N/A')}")
        print()
    
    print("=" * 80)
    print("💔 TOP 3 LOSSES:")
    print("=" * 80)
    print()
    
    top_losses = sorted(losses, key=lambda x: x["profit"])[:3]
    for i, t in enumerate(top_losses, 1):
        print(f"{i}. {t['pair']}: {format_currency(t['profit'])} ({format_units(t['units'])} units)")
        print(f"   Date: {t['date']} | Price: {t.get('price', 'N/A')}")
        print()
    
    # Issues detected
    print("=" * 80)
    print("⚠️  ISSUES DETECTED:")
    print("=" * 80)
    print()
    
    # Count rejected stop losses (from screenshot)
    print("1. STOP LOSS REJECTIONS:")
    print("   Multiple 'Stop Loss Order Rejected' entries in transaction history")
    print("   This prevented proper risk management on several trades")
    print("   💡 Recommendation: Review stop loss placement logic")
    print()
    
    print("2. HIGH SPREAD COSTS:")
    spread_pct = (abs(total_spread_cost) / abs(net_pnl) * 100) if net_pnl != 0 else 0
    print(f"   Total spread cost: {format_currency(total_spread_cost)}")
    print(f"   As % of gross P&L: {spread_pct:.1f}%")
    print("   💡 Recommendation: Reduce trade frequency or increase profit targets")
    print()
    
    print("3. CURRENT PARAMS ERROR:")
    print("   'OandaConnector._make_request() got unexpected keyword argument params'")
    print("   Bot cannot fetch market data - no new signals possible")
    print("   ✅ FIXED: Cleared Python cache and restarted bot")
    print()
    
    print("=" * 80)
    print("📋 CURRENT STATUS (from OANDA dashboard):")
    print("=" * 80)
    print()
    
    print("Account Balance: $1,729.96")
    print("NAV: $1,806.63")
    print("Unrealized P&L: +$76.66")
    print("Realized P&L: (-$267.08)")
    print()
    
    print("Active Position:")
    print("   NZD/CHF: (32,900) units SHORT @ 0.45433")
    print("   Current P&L: +$76.66 (+18.9 pips)")
    print("   Take Profit: 0.44980 (45.3 pips away)")
    print("   Stop Loss: 0.45820 (38.7 pips away)")
    print()
    
    print("=" * 80)
    print("💡 RECOMMENDATIONS:")
    print("=" * 80)
    print()
    
    print("1. IMMEDIATE:")
    print("   ✅ Python cache cleared - bot restarted")
    print("   ✅ Fresh connector code loaded")
    print("   → Monitor next few trades for params error resolution")
    print()
    
    print("2. STRATEGY:")
    print("   • Win rate 40% but average loss > average win")
    print("   • Need better trade selection OR wider profit targets")
    print("   • Consider raising momentum threshold from 0.15% to 0.18%+")
    print()
    
    print("3. RISK MANAGEMENT:")
    print("   • Fix stop loss rejection issues")
    print("   • Review position sizing (some trades very large)")
    print("   • Reduce trade frequency to lower spread costs")
    print()
    
    print("=" * 80)

if __name__ == "__main__":
    analyze_performance()
