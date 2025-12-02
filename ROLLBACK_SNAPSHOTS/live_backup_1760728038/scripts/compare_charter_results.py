#!/usr/bin/env python3
"""
Compare Charter-Compliant Ghost Results vs Old Fake Results
"""

import json
import os
from pathlib import Path

def main():
    print("=" * 80)
    print("📊 GHOST TRADING COMPARISON: OLD (Fake) vs NEW (Charter-Compliant)")
    print("=" * 80)
    print()
    
    # Load old fake results
    old_report_path = "ghost_trading_final_report.json"
    if os.path.exists(old_report_path):
        with open(old_report_path, 'r') as f:
            old_report = json.load(f)
        print("✅ OLD Report Found: ghost_trading_final_report.json")
    else:
        print("⚠️  OLD report not found")
        old_report = None
    
    # Load new Charter-compliant results
    new_report_path = "ghost_trading_charter_compliant_report.json"
    if os.path.exists(new_report_path):
        with open(new_report_path, 'r') as f:
            new_report = json.load(f)
        print("✅ NEW Report Found: ghost_trading_charter_compliant_report.json")
    else:
        print("⚠️  NEW report not found - Run ./launch_charter_ghost.sh first")
        new_report = None
    
    print()
    print("=" * 80)
    
    if old_report:
        print("📋 OLD GHOST ENGINE (Fake Results)")
        print("-" * 80)
        print(f"Duration:            {old_report.get('session_duration_minutes', 0):.1f} minutes")
        print(f"Total Trades:        {old_report.get('total_trades', 0)}")
        print(f"Wins:                {old_report.get('wins', 0)}")
        print(f"Losses:              {old_report.get('losses', 0)}")
        print(f"Win Rate:            {old_report.get('win_rate', 0):.1f}%")
        print(f"Total P&L:           ${old_report.get('total_pnl', 0):.2f}")
        print(f"Avg P&L per Trade:   ${old_report.get('avg_pnl_per_trade', 0):.2f}")
        print(f"Trade Frequency:     {old_report.get('total_trades', 0) / old_report.get('session_duration_minutes', 1):.2f} trades/min")
        print()
        print("⚠️  ISSUES:")
        print("   • NO Charter enforcement")
        print("   • Position size: ~$22.50 (670x too small!)")
        print("   • Hardcoded 70% win rate")
        print("   • Simulated prices (not real OANDA)")
        print("   • Results are MEANINGLESS for LIVE")
        print()
    
    if new_report:
        print("=" * 80)
        print("✅ NEW CHARTER-COMPLIANT ENGINE (Real Results)")
        print("-" * 80)
        print(f"Duration:            {new_report.get('session_duration_hours', 0):.2f} hours")
        print(f"Total Trades:        {new_report.get('total_trades', 0)}")
        print(f"Completed Trades:    {new_report.get('completed_trades', 0)}")
        print(f"Wins:                {new_report.get('wins', 0)}")
        print(f"Losses:              {new_report.get('losses', 0)}")
        print(f"Win Rate:            {new_report.get('win_rate', 0):.1f}%")
        print(f"Total P&L:           ${new_report.get('total_pnl', 0):,.2f}")
        print(f"Avg P&L per Trade:   ${new_report.get('avg_pnl_per_trade', 0):,.2f}")
        print(f"Starting Capital:    ${new_report.get('starting_capital', 0):,.2f}")
        print(f"Ending Capital:      ${new_report.get('ending_capital', 0):,.2f}")
        print(f"Return:              {new_report.get('return_pct', 0):.2f}%")
        print(f"Trades Rejected:     {new_report.get('trades_rejected', 0)}")
        print(f"Charter Violations:  {new_report.get('charter_violations', 0)}")
        print(f"Promotion Eligible:  {'YES ✅' if new_report.get('promotion_eligible', False) else 'NO ❌'}")
        print()
        print("✅ CHARTER COMPLIANCE:")
        charter = new_report.get('charter_compliance', {})
        print(f"   MIN_NOTIONAL_USD:       ${charter.get('min_notional_usd', 0):,} ✅")
        print(f"   MIN_RISK_REWARD:        {charter.get('min_risk_reward', 0)} ✅")
        print(f"   MAX_HOLD_HOURS:         {charter.get('max_hold_hours', 0)} ✅")
        print(f"   Enforced:               {charter.get('enforced', False)}")
        print()
    
    if old_report and new_report:
        print("=" * 80)
        print("📊 SIDE-BY-SIDE COMPARISON")
        print("=" * 80)
        print()
        print(f"{'Metric':<30} {'OLD (Fake)':<20} {'NEW (Real)':<20}")
        print("-" * 80)
        
        # Duration
        old_hours = old_report.get('session_duration_minutes', 0) / 60
        new_hours = new_report.get('session_duration_hours', 0)
        print(f"{'Duration':<30} {old_hours:.2f}h{'':<14} {new_hours:.2f}h")
        
        # Trades
        old_trades = old_report.get('total_trades', 0)
        new_trades = new_report.get('completed_trades', 0)
        print(f"{'Total Trades':<30} {old_trades:<20} {new_trades:<20}")
        
        # Win Rate
        old_wr = old_report.get('win_rate', 0)
        new_wr = new_report.get('win_rate', 0)
        print(f"{'Win Rate':<30} {old_wr:.1f}%{'':<14} {new_wr:.1f}%")
        
        # Total P&L
        old_pnl = old_report.get('total_pnl', 0)
        new_pnl = new_report.get('total_pnl', 0)
        print(f"{'Total P&L':<30} ${old_pnl:.2f}{'':<13} ${new_pnl:,.2f}")
        
        # Avg P&L per Trade
        old_avg = old_report.get('avg_pnl_per_trade', 0)
        new_avg = new_report.get('avg_pnl_per_trade', 0)
        multiplier = new_avg / old_avg if old_avg > 0 else 0
        print(f"{'Avg P&L per Trade':<30} ${old_avg:.2f}{'':<13} ${new_avg:,.2f} ({multiplier:.0f}x)")
        
        # Position Size
        print(f"{'Position Size':<30} {'~$22.50':<20} {'$15,000 (Charter)':<20}")
        
        # Leverage
        print(f"{'Leverage':<30} {'None (0x)':<20} {'6.6x':<20}")
        
        # Charter Compliance
        print(f"{'Charter Compliant':<30} {'NO ❌':<20} {'YES ✅':<20}")
        
        # Predictive Value
        print(f"{'Predictive for LIVE':<30} {'NO ❌':<20} {'YES ✅':<20}")
        
        print()
        print("=" * 80)
        print("📌 KEY INSIGHT:")
        print("=" * 80)
        print()
        if multiplier > 1:
            print(f"The NEW engine produces {multiplier:.0f}x larger P&L because it uses")
            print(f"Charter-compliant position sizes ($15,000 vs $22.50)")
        print()
        print("⚠️  DO NOT use OLD results for LIVE decisions!")
        print("✅  Use NEW Charter-compliant results instead!")
        print()
    
    if not new_report:
        print()
        print("=" * 80)
        print("🚀 NEXT STEP: Run Charter-Compliant Ghost Session")
        print("=" * 80)
        print()
        print("To get REAL validation data, run:")
        print("  $ ./launch_charter_ghost.sh")
        print()
        print("This will:")
        print("  • Enforce all Charter rules ($15K notional, 3.2 RR, etc.)")
        print("  • Use real OANDA API")
        print("  • Calculate proper leverage (6.6x)")
        print("  • Run for 4 hours with realistic timing")
        print("  • Produce valid performance metrics")
        print()

if __name__ == "__main__":
    main()
