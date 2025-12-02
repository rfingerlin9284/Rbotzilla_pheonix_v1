#!/usr/bin/env python3
"""
RICK Safe Trading Launcher
Demonstrates the complete progression system:
PAPER → VALIDATION → LIVE_READY → LIVE_AUTHORIZED

Commands:
1. Start paper trading session
2. Check progression status  
3. Request live authorization (when ready)
4. Authorize live trading (PIN required)
5. Start live trading session (when authorized)
"""

import sys
import os
sys.path.append('/home/ing/RICK/RICK_LIVE_CLEAN')

from safe_trading_engine import SafeTradingEngine
from safe_mode_manager import SafeModeManager
import json

def main_menu():
    """Display main menu and handle user input"""
    
    engine = SafeTradingEngine()
    manager = SafeModeManager()
    
    while True:
        print("\n" + "="*60)
        print("🤖 RICK SAFE TRADING SYSTEM")
        print("="*60)
        
        # Get current status
        status = engine.get_status_dashboard()
        
        print(f"Current Mode: {status['current_mode']}")
        print(f"Description: {status['mode_description']}")
        print(f"Ready for Live: {'✅ YES' if status['ready_for_live'] else '❌ NO'}")
        print(f"Live Authorized: {'🔴 YES' if status['live_authorized'] else '⚫ NO'}")
        
        print("\nPerformance Summary:")
        perf = status['performance_summary']
        print(f"  Trades: {perf['total_trades']} | Win Rate: {perf['win_rate_percent']}% | "
              f"Profit: ${perf['total_profit_usd']:.2f} | Days: {perf['trading_period_days']}")
        
        print("\nOptions:")
        print("1. 🧪 Start Paper Trading Session (Demo)")
        print("2. 📊 Check Detailed Progress Status")  
        print("3. 🎯 Request Live Authorization Review")
        print("4. 🔑 Authorize Live Trading (PIN Required)")
        print("5. 🔴 Start Live Trading Session")
        print("6. 💰 Check Account Balances")
        print("7. ❌ Exit")
        
        try:
            choice = input("\nSelect option (1-7): ").strip()
            
            if choice == '1':
                start_demo_session(engine)
            elif choice == '2':
                show_detailed_status(engine)
            elif choice == '3':
                request_authorization(engine)
            elif choice == '4':
                authorize_live_trading(engine)
            elif choice == '5':
                start_live_session(engine)
            elif choice == '6':
                check_balances(engine)
            elif choice == '7':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid option. Please try again.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def start_demo_session(engine):
    """Start a demo paper trading session"""
    print("\n🧪 Starting Demo Paper Trading Session...")
    print("This will simulate trades to build performance history.")
    
    duration = input("Duration in minutes (default 5): ").strip()
    if not duration:
        duration = 5
    else:
        duration = int(duration)
    
    print(f"\n🚀 Running demo session for {duration} minutes...")
    print("(Simulating random trades for demonstration)")
    
    # Start session
    result = engine.start_safe_trading_session(duration)
    
    print("\n📈 Session Complete!")
    print(f"Trades: {result['trades_executed']}")
    print(f"P&L: ${result['total_pnl']:.2f}")
    print(f"Mode: {result['current_mode']}")
    
    if result.get('ready_for_live'):
        print("\n🎯 READY FOR LIVE AUTHORIZATION!")
        
    print("\nNext Steps:")
    for step in result['next_steps']:
        print(f"  • {step}")

def show_detailed_status(engine):
    """Show detailed progression status"""
    print("\n📊 Detailed Progress Status")
    print("="*40)
    
    status = engine.get_status_dashboard()
    
    print(f"\nCurrent Mode: {status['current_mode']}")
    print(f"Description: {status['mode_description']}")
    
    print(f"\nThreshold Progress:")
    for metric, data in status['threshold_status'].items():
        status_icon = "✅" if data['met'] else "❌"
        print(f"  {status_icon} {metric.replace('_', ' ').title()}: {data['current']} (need: {data['threshold']})")
    
    print(f"\nNext Steps:")
    for step in status['next_steps']:
        print(f"  • {step}")

def request_authorization(engine):
    """Request live trading authorization"""
    print("\n🎯 Requesting Live Authorization Review...")
    
    result = engine.request_live_authorization_review()
    
    if result['status'] == 'ready_for_authorization':
        print("\n✅ READY FOR LIVE AUTHORIZATION!")
        print("\nPerformance Summary:")
        perf = result['performance_summary']
        for key, value in perf.items():
            print(f"  {key}: {value}")
            
        print("\nRisk Analysis:")
        risk = result['risk_analysis']
        for key, value in risk.items():
            print(f"  {key}: {value}")
            
        print(f"\n{result['message']}")
        print("Use option 4 to authorize with PIN 841921")
        
    else:
        print(f"❌ {result['message']}")
        print("\nCurrent Metrics:")
        metrics = result.get('current_metrics', {})
        for key, value in metrics.items():
            print(f"  {key}: {value}")

def authorize_live_trading(engine):
    """Authorize live trading with PIN"""
    print("\n🔑 Live Trading Authorization")
    print("WARNING: This enables REAL MONEY trading!")
    
    try:
        pin = int(input("Enter PIN: ").strip())
        duration = input("Authorization duration in hours (default 24): ").strip()
        
        if not duration:
            duration = 24
        else:
            duration = int(duration)
            
        result = engine.authorize_live_trading(pin, duration)
        
        if result['status'] == 'authorized':
            print(f"\n🔴 LIVE TRADING AUTHORIZED for {duration} hours!")
            print("You can now use option 5 to start live trading.")
        elif result['status'] == 'unauthorized':
            print("❌ Invalid PIN. Authorization denied.")
        elif result['status'] == 'not_ready':
            print("❌ Performance thresholds not yet met.")
        else:
            print(f"❌ {result.get('message', 'Authorization failed')}")
            
    except ValueError:
        print("❌ Invalid input. Please enter numeric values.")

def start_live_session(engine):
    """Start a live trading session"""
    status = engine.get_status_dashboard()
    
    if not status['live_authorized']:
        print("❌ Live trading not authorized. Use option 4 first.")
        return
        
    print("\n🔴 STARTING LIVE TRADING SESSION")
    print("WARNING: This uses REAL MONEY!")
    
    confirm = input("Type 'CONFIRM' to proceed: ").strip()
    if confirm != 'CONFIRM':
        print("❌ Live trading cancelled.")
        return
        
    duration = input("Duration in minutes (default 30): ").strip()
    if not duration:
        duration = 30
    else:
        duration = int(duration)
        
    print(f"\n🔴 Starting live session for {duration} minutes...")
    
    # Start live session
    result = engine.start_safe_trading_session(duration)
    
    print("\n📈 Live Session Complete!")
    print(f"Trades: {result['trades_executed']}")
    print(f"P&L: ${result['total_pnl']:.2f}")
    print(f"Mode: {result['current_mode']}")

def check_balances(engine):
    """Check account balances"""
    print("\n💰 Account Balances")
    print("="*30)
    
    # Check OANDA
    if engine.oanda:
        print("OANDA Account:")
        try:
            oanda_info = engine.oanda.get_account_info()
            if 'error' not in oanda_info:
                print(f"  Balance: ${oanda_info.get('balance', 0):,.2f}")
                print(f"  Margin Available: ${oanda_info.get('margin_available', 0):,.2f}")
            else:
                print(f"  Error: {oanda_info['error']}")
        except Exception as e:
            print(f"  Error: {e}")
    
    # Check Coinbase
    if engine.coinbase:
        print("\nCoinbase Account:")
        try:
            cb_info = engine.coinbase.get_account_info()
            if 'error' not in cb_info:
                if cb_info.get('mode') == 'LIVE':
                    balances = cb_info.get('balances', {})
                    for currency, balance in balances.items():
                        print(f"  {currency}: ${balance.get('available', 0):,.2f}")
                else:
                    print(f"  Mode: {cb_info.get('mode')} - ${cb_info.get('balance_usd', 0):,.2f}")
            else:
                print(f"  Error: {cb_info['error']}")
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")