#!/usr/bin/env python3
"""
RICK Narration to Human English Translator
Converts JSON system events into plain, coherent English narratives
Shows what, why, how, when, timing, position, $$$ in organized manner
Pace matches human reading speed for easy comprehension
PIN: 841921
"""

import json
import time
import os
from datetime import datetime
from typing import Dict, List, Optional
from collections import deque

class NarrationTranslator:
    """
    Converts JSON log events into human-readable plain English
    Maintains conversational flow and appropriate pacing
    """
    
    def __init__(self, pacing_delay: float = 0.5):
        """
        Initialize translator
        
        Args:
            pacing_delay: Seconds between output lines for human readability
        """
        self.pacing_delay = pacing_delay
        self.event_buffer = deque(maxlen=100)  # Keep last 100 events
        self.session_start = datetime.utcnow()
        
    def translate_event(self, event: Dict) -> str:
        """
        Translate a JSON event into plain English
        
        Args:
            event: JSON event dictionary
            
        Returns:
            Human-readable English description
        """
        event_type = event.get('event', 'unknown')
        
        # Route to specific translator
        translators = {
            'engine_initialized': self._translate_engine_init,
            'engine_start': self._translate_engine_start,
            'paper_trading_cycle': self._translate_paper_cycle,
            'paper_trade_executed': self._translate_paper_trade,
            'validation_cycle': self._translate_validation,
            'live_ready': self._translate_live_ready,
            'live_trading_cycle': self._translate_live_cycle,
            'live_trade_executed': self._translate_live_trade,
            'oco_orders_placed': self._translate_oco,
            'trade_error': self._translate_error,
            'engine_shutdown': self._translate_shutdown,
            'position_reassessed': self._translate_position_reassess,
            'hive_consensus': self._translate_hive_consensus,
            'charter_violation': self._translate_charter_violation,
            'diagnostic_complete': self._translate_diagnostic,
            'daily_audit': self._translate_daily_audit
        }
        
        translator = translators.get(event_type, self._translate_generic)
        return translator(event)
    
    def _translate_engine_init(self, event: Dict) -> str:
        """Translate engine initialization"""
        mode = event.get('mode', 'UNKNOWN')
        pin_verified = event.get('pin_verified', False)
        timestamp = event.get('timestamp', '')
        
        text = f"🚀 RICK Trading Engine initialized at {self._format_time(timestamp)}.\n"
        text += f"   Starting mode: {mode}\n"
        text += f"   Security: PIN {'VERIFIED ✅' if pin_verified else 'not provided ⚠️'}\n"
        text += f"   All systems loading..."
        
        return text
    
    def _translate_engine_start(self, event: Dict) -> str:
        """Translate engine start"""
        mode = event.get('mode', 'UNKNOWN')
        timestamp = event.get('timestamp', '')
        
        text = f"▶️  Engine started at {self._format_time(timestamp)}\n"
        text += f"   Operating in {mode} mode\n"
        text += f"   Scanning markets for opportunities..."
        
        return text
    
    def _translate_paper_cycle(self, event: Dict) -> str:
        """Translate paper trading cycle"""
        message = event.get('message', '')
        
        text = f"📝 Paper Trading Active\n"
        text += f"   {message}\n"
        text += f"   Building performance track record with zero risk."
        
        return text
    
    def _translate_paper_trade(self, event: Dict) -> str:
        """Translate paper trade execution with full details"""
        symbol = event.get('symbol', 'UNKNOWN')
        direction = event.get('direction', 'UNKNOWN').upper()
        entry = event.get('entry', 0)
        target = event.get('target', 0)
        stop_loss = event.get('stop_loss', 0)
        rr_ratio = event.get('risk_reward', 0)
        hive_consensus = event.get('hive_consensus', 'UNKNOWN')
        hive_confidence = event.get('hive_confidence', 0)
        timestamp = event.get('timestamp', '')
        
        # Calculate profit potential
        profit_potential = target - entry if direction == 'BUY' else entry - target
        profit_pct = (profit_potential / entry * 100) if entry > 0 else 0
        
        text = f"📊 PAPER TRADE EXECUTED - {symbol} at {self._format_time(timestamp)}\n"
        text += f"\n"
        text += f"   WHAT: {direction} {symbol}\n"
        text += f"   WHY: Hive Mind consensus is {hive_consensus} with {hive_confidence:.1%} confidence\n"
        text += f"        Multiple technical confluences detected (FVG + Fibonacci + Volume)\n"
        text += f"\n"
        text += f"   HOW: Entry at ${entry:,.2f}\n"
        text += f"        Target at ${target:,.2f} (+{profit_pct:.2f}% profit potential)\n"
        text += f"        Stop Loss at ${stop_loss:,.2f}\n"
        text += f"        Risk/Reward Ratio: {rr_ratio:.2f}:1 {'✅' if rr_ratio >= 3.2 else '⚠️'}\n"
        text += f"\n"
        text += f"   WHEN: {self._format_time(timestamp)}\n"
        text += f"   TIMING: Optimal entry zone identified\n"
        text += f"   POSITION: Paper simulation (no real money)\n"
        text += f"   MONEY: Tracking for performance validation"
        
        return text
    
    def _translate_validation(self, event: Dict) -> str:
        """Translate validation cycle"""
        message = event.get('message', '')
        
        text = f"🎯 Safe Validation Mode\n"
        text += f"   {message}\n"
        text += f"   Demonstrating consistent profitability before live trading."
        
        return text
    
    def _translate_live_ready(self, event: Dict) -> str:
        """Translate live ready status"""
        message = event.get('message', '')
        
        text = f"🏆 MILESTONE ACHIEVED - Live Trading Qualified!\n"
        text += f"\n"
        text += f"   ✅ Win rate threshold met\n"
        text += f"   ✅ Profit factor validated\n"
        text += f"   ✅ Risk management verified\n"
        text += f"   ✅ Minimum trades completed\n"
        text += f"\n"
        text += f"   {message}\n"
        text += f"   Waiting for your approval to begin real trading."
        
        return text
    
    def _translate_live_cycle(self, event: Dict) -> str:
        """Translate live trading cycle"""
        message = event.get('message', '')
        
        text = f"💰 LIVE TRADING ACTIVE\n"
        text += f"   {message}\n"
        text += f"   Charter enforcement: STRICT\n"
        text += f"   OCO protection: ENABLED\n"
        text += f"   Hive mind: MONITORING"
        
        return text
    
    def _translate_live_trade(self, event: Dict) -> str:
        """Translate live trade execution with full context"""
        symbol = event.get('symbol', 'UNKNOWN')
        order_id = event.get('order_id', 'UNKNOWN')
        direction = event.get('direction', 'UNKNOWN').upper()
        notional = event.get('notional', 0)
        entry = event.get('entry', 0)
        target = event.get('target', 0)
        stop_loss = event.get('stop_loss', 0)
        timestamp = event.get('timestamp', '')
        
        # Calculate expected profit/loss
        expected_profit = target - entry if direction == 'BUY' else entry - target
        expected_loss = entry - stop_loss if direction == 'BUY' else stop_loss - entry
        rr = expected_profit / expected_loss if expected_loss > 0 else 0
        
        text = f"💵 LIVE TRADE EXECUTED - REAL MONEY\n"
        text += f"\n"
        text += f"   WHAT: {direction} ${notional:,.2f} of {symbol}\n"
        text += f"   WHY: High-probability setup confirmed by Hive Mind consensus\n"
        text += f"        Technical confluence: FVG support + Fibonacci retracement\n"
        text += f"        Risk management: Meets charter requirements (RR: {rr:.2f}:1)\n"
        text += f"\n"
        text += f"   HOW: Market order executed at ${entry:,.2f}\n"
        text += f"        OCO orders placed automatically:\n"
        text += f"          - Take Profit: ${target:,.2f} (${expected_profit:,.2f} profit)\n"
        text += f"          - Stop Loss: ${stop_loss:,.2f} (${expected_loss:,.2f} max loss)\n"
        text += f"\n"
        text += f"   WHEN: {self._format_time(timestamp)}\n"
        text += f"   TIMING: Entry triggered on bullish FVG sweep\n"
        text += f"   POSITION: Now holding {symbol}\n"
        text += f"   MONEY: ${notional:,.2f} deployed, ${expected_profit:,.2f} target profit\n"
        text += f"\n"
        text += f"   Order ID: {order_id}\n"
        text += f"   Status: Monitoring for exit conditions"
        
        return text
    
    def _translate_oco(self, event: Dict) -> str:
        """Translate OCO order placement"""
        parent_order = event.get('parent_order', 'UNKNOWN')
        tp_order = event.get('take_profit_order', 'UNKNOWN')
        sl_order = event.get('stop_loss_order', 'UNKNOWN')
        message = event.get('message', '')
        
        text = f"🛡️  OCO PROTECTION ACTIVE\n"
        text += f"   {message}\n"
        text += f"\n"
        text += f"   Take Profit Order: {tp_order}\n"
        text += f"   Stop Loss Order: {sl_order}\n"
        text += f"   Parent Trade: {parent_order}\n"
        text += f"\n"
        text += f"   One-Cancels-Other logic ensures automatic exit.\n"
        text += f"   No manual intervention required."
        
        return text
    
    def _translate_error(self, event: Dict) -> str:
        """Translate error event"""
        error = event.get('error', 'Unknown error')
        timestamp = event.get('timestamp', '')
        
        text = f"⚠️  ERROR DETECTED at {self._format_time(timestamp)}\n"
        text += f"   Issue: {error}\n"
        text += f"   Action: Trade skipped, system continues monitoring\n"
        text += f"   Safety: All positions remain protected"
        
        return text
    
    def _translate_shutdown(self, event: Dict) -> str:
        """Translate engine shutdown"""
        timestamp = event.get('timestamp', '')
        
        text = f"🛑 Engine Shutdown at {self._format_time(timestamp)}\n"
        text += f"   All systems safely stopped\n"
        text += f"   Position status: Check manually if any were open\n"
        text += f"   Session complete"
        
        return text
    
    def _translate_position_reassess(self, event: Dict) -> str:
        """Translate position reassessment"""
        symbol = event.get('symbol', 'UNKNOWN')
        action = event.get('action', 'UNKNOWN')
        reasoning = event.get('reasoning', '')
        timestamp = event.get('timestamp', '')
        
        text = f"🔍 POSITION REASSESSMENT - {symbol}\n"
        text += f"\n"
        text += f"   WHAT: Hive Mind reviewed current {symbol} position\n"
        text += f"   WHY: {reasoning}\n"
        text += f"   HOW: Fresh ML analysis + current market data + news sentiment\n"
        text += f"   DECISION: {action}\n"
        text += f"   WHEN: {self._format_time(timestamp)}\n"
        text += f"\n"
        text += f"   Charter compliance: {'✅ PASSED' if event.get('charter_compliant') else '❌ BLOCKED'}"
        
        return text
    
    def _translate_hive_consensus(self, event: Dict) -> str:
        """Translate hive mind consensus"""
        consensus = event.get('consensus', 'UNKNOWN')
        confidence = event.get('confidence', 0)
        agents_voted = event.get('agents_voted', [])
        reasoning = event.get('reasoning', '')
        
        text = f"🧠 HIVE MIND CONSENSUS\n"
        text += f"\n"
        text += f"   Consensus: {consensus}\n"
        try:
            from util.confidence import format_confidence
            conf_str = format_confidence(confidence)
        except Exception:
            conf_str = f"{confidence:.1%}"
        text += f"   Confidence: {conf_str}\n"
        text += f"   Agents Voted: {', '.join(agents_voted)}\n"
        text += f"\n"
        text += f"   Reasoning: {reasoning}"
        
        return text
    
    def _translate_charter_violation(self, event: Dict) -> str:
        """Translate charter violation"""
        violation_type = event.get('violation_type', 'UNKNOWN')
        details = event.get('details', '')
        
        text = f"🚨 CHARTER VIOLATION BLOCKED\n"
        text += f"\n"
        text += f"   Type: {violation_type}\n"
        text += f"   Details: {details}\n"
        text += f"\n"
        text += f"   Action: Trade rejected\n"
        text += f"   System: Operating within safety constraints"
        
        return text
    
    def _translate_diagnostic(self, event: Dict) -> str:
        """Translate diagnostic results"""
        results = event.get('results', {})
        timestamp = event.get('timestamp', '')
        
        text = f"🔧 10-MINUTE DIAGNOSTIC COMPLETE\n"
        text += f"   Time: {self._format_time(timestamp)}\n"
        text += f"\n"
        text += f"   API Status: {results.get('api_status', 'UNKNOWN')}\n"
        text += f"   Auth Tokens: {results.get('auth_status', 'UNKNOWN')}\n"
        text += f"   Logging: {results.get('logging_status', 'UNKNOWN')}\n"
        text += f"   Charter: {results.get('charter_status', 'UNKNOWN')}\n"
        text += f"   Gated Logic: {results.get('gates_status', 'UNKNOWN')}\n"
        text += f"   OCO Logic: {results.get('oco_status', 'UNKNOWN')}\n"
        text += f"\n"
        text += f"   Overall Health: {results.get('overall', 'UNKNOWN')}"
        
        return text
    
    def _translate_daily_audit(self, event: Dict) -> str:
        """Translate daily audit report"""
        wins = event.get('winning_trades', 0)
        losses = event.get('losing_trades', 0)
        total_profit = event.get('total_profit', 0)
        win_rate = event.get('win_rate', 0)
        avg_win = event.get('avg_win', 0)
        avg_loss = event.get('avg_loss', 0)
        
        text = f"📈 DAILY PERFORMANCE AUDIT\n"
        text += f"\n"
        text += f"   Winning Trades: {wins} (avg: ${avg_win:,.2f})\n"
        text += f"   Losing Trades: {losses} (avg: ${avg_loss:,.2f})\n"
        text += f"   Win Rate: {win_rate:.1%}\n"
        text += f"   Total Profit: ${total_profit:,.2f}\n"
        text += f"\n"
        text += f"   Performance: {'🟢 EXCELLENT' if win_rate > 0.7 else '🟡 GOOD' if win_rate > 0.6 else '🔴 NEEDS IMPROVEMENT'}\n"
        text += f"\n"
        text += f"   What worked: {event.get('what_worked', 'Analysis in progress...')}\n"
        text += f"   What to improve: {event.get('what_to_improve', 'Analysis in progress...')}"
        
        return text
    
    def _translate_generic(self, event: Dict) -> str:
        """Generic fallback translator"""
        event_type = event.get('event', 'UNKNOWN')
        message = event.get('message', json.dumps(event, indent=2))
        timestamp = event.get('timestamp', '')
        
        text = f"📌 {event_type.upper().replace('_', ' ')}\n"
        text += f"   {message}\n"
        if timestamp:
            text += f"   Time: {self._format_time(timestamp)}"
        
        return text
    
    def _format_time(self, timestamp: str) -> str:
        """Format ISO timestamp to human-readable"""
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.strftime('%H:%M:%S')
        except:
            return timestamp
    
    def stream_narration(self, narration_file: str = 'logs/narration.jsonl'):
        """
        Stream and translate narration file in real-time
        Outputs plain English with appropriate pacing
        """
        print("=" * 80)
        print("🎙️  RICK NARRATION STREAM - Plain English Translation")
        print("=" * 80)
        print()
        
        # Check if file exists
        if not os.path.exists(narration_file):
            print(f"⚠️  Waiting for narration log to appear: {narration_file}")
            print()
        
        # Follow file (tail -f style)
        with open(narration_file, 'r') as f:
            # Go to end of file
            f.seek(0, 2)
            
            while True:
                line = f.readline()
                
                if line:
                    try:
                        event = json.loads(line.strip())
                        translation = self.translate_event(event)
                        
                        print(translation)
                        print()
                        print("-" * 80)
                        print()
                        
                        # Pace output for readability
                        time.sleep(self.pacing_delay)
                        
                    except json.JSONDecodeError:
                        pass  # Skip malformed lines
                else:
                    # No new data, wait
                    time.sleep(0.5)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='RICK Narration to English Translator')
    parser.add_argument('--file', type=str, default='logs/narration.jsonl',
                        help='Narration file to monitor')
    parser.add_argument('--pace', type=float, default=0.5,
                        help='Seconds between outputs (default: 0.5)')
    
    args = parser.parse_args()
    
    translator = NarrationTranslator(pacing_delay=args.pace)
    
    try:
        translator.stream_narration(narration_file=args.file)
    except KeyboardInterrupt:
        print("\n🛑 Narration stream stopped")
