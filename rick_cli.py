"""
RICK INTERACTIVE CLI
====================
Command-line interface with dropdown menus and real-time narration
"""

import sys
from typing import Optional
from config.enhanced_task_config import (
    get_enhanced_task_config,
    SystemAction,
    TradeParameters
)
from config.narration_logger import get_narration_logger
import threading
import time


class RICKInteractiveCLI:
    """Interactive CLI for RICK system"""
    
    def __init__(self):
        self.config = get_enhanced_task_config()
        self.narration = get_narration_logger()
        self.running = True
    
    def display_banner(self):
        """Display system banner"""
        print("""
╔════════════════════════════════════════════════════════════════════════════════╗
║                                                                                ║
║                  🤖 RICK HIVE MIND COLLECTIVE TRADING 🤖                       ║
║                                                                                ║
║                        Approval 841921 - LIVE SYSTEM                          ║
║                                                                                ║
║   Autonomous AI Trading | Real-Time Position Management | Closed-Loop Learning║
║                                                                                ║
╚════════════════════════════════════════════════════════════════════════════════╝
""")
    
    def display_main_menu(self):
        """Display main action dropdown"""
        print("\n" + "="*80)
        print("📋 SELECT ACTION (Dropdown Menu #1)")
        print("="*80)
        print("1) ▶️  START - Initialize system and begin trading")
        print("2) ⏹️  STOP - Shutdown system gracefully")
        print("3) 📊 VERIFY STATUS - Check system health")
        print("4) 👤 MANUAL TRADE - Input custom trade parameters")
        print("5) 📈 REASSESS POSITIONS - Check all open trades")
        print("6) 📜 VIEW NARRATION LOG - Stream real-time events")
        print("7) 🔧 SETTINGS - Configure system parameters")
        print("8) ❌ EXIT - Quit RICK CLI")
        print("="*80)
        
        choice = input("\nEnter your choice (1-8): ").strip()
        return choice
    
    def handle_choice(self, choice: str):
        """Handle menu choice"""
        if choice == "1":
            self.action_start()
        elif choice == "2":
            self.action_stop()
        elif choice == "3":
            self.action_verify_status()
        elif choice == "4":
            self.action_manual_trade()
        elif choice == "5":
            self.action_reassess()
        elif choice == "6":
            self.action_view_narration()
        elif choice == "7":
            self.action_settings()
        elif choice == "8":
            self.action_exit()
        else:
            print("❌ Invalid choice. Please select 1-8.")
    
    def action_start(self):
        """START action"""
        print("\n" + "="*80)
        print("▶️  STARTING RICK SYSTEM")
        print("="*80)
        result = self.config.execute_action(SystemAction.START)
        print(result)
        print("\n✅ System is now ONLINE and AUTONOMOUS")
        print("📊 Dashboard: http://localhost:8501")
        print("📜 Narration: Check logs/ directory for real-time events")
    
    def action_stop(self):
        """STOP action"""
        print("\n" + "="*80)
        print("⏹️  STOPPING RICK SYSTEM")
        print("="*80)
        confirm = input("Are you sure? (yes/no): ").strip().lower()
        if confirm == "yes":
            result = self.config.execute_action(SystemAction.STOP)
            print(result)
            print("\n✅ System has been shutdown")
        else:
            print("❌ Stop cancelled")
    
    def action_verify_status(self):
        """VERIFY STATUS action"""
        print("\n" + "="*80)
        print("📊 SYSTEM STATUS")
        print("="*80)
        result = self.config.execute_action(SystemAction.VERIFY_STATUS)
        print(result)
        self.narration.print_tail(10)
    
    def action_manual_trade(self):
        """MANUAL TRADE action"""
        print("\n" + "="*80)
        print("👤 MANUAL TRADE INPUT")
        print("="*80)
        print("\nEnter trade parameters in plain English:")
        print("Examples:")
        print("  'Buy 10000 EURUSD at market with 2% risk'")
        print("  'Sell 5000 GBPUSD with 50 pip stop and 100 pip target'")
        print("  Or paste JSON: {\"direction\": \"buy\", \"symbol\": \"EURUSD\", ...}")
        print()
        
        trade_input = input("Enter trade parameters: ").strip()
        
        if not trade_input:
            print("❌ No input provided")
            return
        
        # Parse and submit
        try:
            parsed = self.config.manual_trade_input(trade_input)
            print("\n📊 Parsed parameters:")
            for key, value in parsed.items():
                print(f"  {key}: {value}")
            
            # Create trade parameters object
            trade_params = TradeParameters(
                symbol=parsed.get("symbol", "EURUSD"),
                direction=parsed.get("direction", "buy"),
                quantity=parsed.get("quantity", 10000),
                entry_price=parsed.get("entry_price"),
                stop_loss=parsed.get("stop_loss"),
                take_profit=parsed.get("take_profit"),
                risk_percent=parsed.get("risk_percent", 2.0),
                broker=parsed.get("broker", "oanda")
            )
            
            # Get hive analysis and plan
            plan = self.config.submit_manual_trade(trade_params)
            print(plan)
            
            # Ask for approval
            approve = input("\nApprove this trade? (yes/no): ").strip().lower()
            if approve == "yes":
                print("✅ Trade APPROVED and submitted to Hive")
                self.narration.narrate_trade_executed(
                    trade_params.symbol,
                    trade_params.direction,
                    trade_params.quantity,
                    trade_params.entry_price or 0,
                    trade_params.broker
                )
            else:
                print("❌ Trade rejected by user")
        
        except Exception as e:
            print(f"❌ Error parsing trade: {e}")
    
    def action_reassess(self):
        """REASSESS POSITIONS action"""
        print("\n" + "="*80)
        print("📈 REASSESSING ALL OPEN POSITIONS")
        print("="*80)
        print("Fetching real-time market data for all open positions...")
        print("(Updates every minute automatically)")
        print()
        
        result = self.config.execute_action(SystemAction.REASSESS_POSITIONS)
        print(result)
        
        # Stream reassessments
        print("\n✅ Position reassessment complete. Hive is managing trades in real-time.")
        print("   Next reassessment in 60 seconds...")
    
    def action_view_narration(self):
        """VIEW NARRATION LOG action"""
        print("\n" + "="*80)
        print("📜 NARRATION LOG - Real-time System Events")
        print("="*80)
        print("Streaming latest events (Press Ctrl+C to stop)...\n")
        
        try:
            self.narration.stream_tail(20)
        except KeyboardInterrupt:
            print("\n\n✅ Stopped streaming narration log")
    
    def action_settings(self):
        """SETTINGS action"""
        print("\n" + "="*80)
        print("🔧 SYSTEM SETTINGS")
        print("="*80)
        print("\n1) Trading Mode")
        print("   a) Paper Practice (simulated money)")
        print("   b) Paper Real-Time (real data, fake money)")
        print("   c) Live Real Money")
        print("\n2) Broker Selection")
        print("   a) Enable/disable Oanda")
        print("   b) Enable/disable IBKR")
        print("   c) Enable/disable Coinbase")
        print("\n3) Hive Settings")
        print("   a) Toggle Autonomy")
        print("   b) Toggle Learning")
        print("   c) Toggle Dialogue")
        print("\n4) Risk Management")
        print("   a) Set Max Drawdown")
        print("   b) Set Position Size")
        print("   c) Set Daily Loss Limit")
        
        setting = input("\nSelect setting to modify (1a, 2b, etc.): ").strip()
        print(f"✅ Setting '{setting}' selected (configuration UI would load here)")
    
    def action_exit(self):
        """EXIT action"""
        confirm = input("\nExit RICK CLI? (yes/no): ").strip().lower()
        if confirm == "yes":
            print("\n" + "="*80)
            print("👋 RICK System CLI Closing")
            print("="*80)
            print("✅ Thank you for using RICK Hive Mind Collective Trading")
            print("📊 All positions remain under autonomous hive management")
            self.running = False
            sys.exit(0)
        else:
            print("❌ Exit cancelled")
    
    def run(self):
        """Run the CLI"""
        self.display_banner()
        
        print("\n🟢 RICK CLI is ready!")
        print("📊 System Status: Ready for commands")
        print("📜 All events will be logged to: logs/narration.log")
        print("🎯 Narration will stream in real-time to terminal\n")
        
        while self.running:
            try:
                choice = self.display_main_menu()
                self.handle_choice(choice)
                
                # Brief pause between actions
                time.sleep(0.5)
            
            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupted by user. Use 'STOP' from menu to shutdown safely.")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                self.narration.narrate_error("CLI_ERROR", str(e))


def main():
    """Main entry point"""
    cli = RICKInteractiveCLI()
    cli.run()


if __name__ == "__main__":
    main()
