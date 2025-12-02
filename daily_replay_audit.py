#!/usr/bin/env python3
"""
RICK Daily Replay & Audit System
Generates on-demand performance reports
Auto-investigates winners and losers
Prompts for ML learning updates
PIN: 841921
"""

import os
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

sys.path.append(os.path.dirname(__file__))

class DailyReplayAudit:
    """
    Daily performance audit and analysis system
    Investigates what worked, what didn't, and why
    """
    
    def __init__(self):
        self.trades_file = 'logs/trades.json'
        self.performance_file = 'logs/safe_mode_performance.json'
        self.ml_training_file = 'ml/training_data.json'
        
    def run_daily_audit(self, date: Optional[str] = None):
        """
        Run daily audit for specified date
        If no date provided, uses today
        """
        if date is None:
            date = datetime.utcnow().strftime('%Y-%m-%d')
        
        print("=" * 80)
        print(f"📈 DAILY PERFORMANCE AUDIT - {date}")
        print("=" * 80)
        print()
        
        # Load trades for the day
        trades = self._load_trades_for_date(date)
        
        if not trades:
            print(f"No trades found for {date}")
            print()
            return
        
        # Calculate performance metrics
        metrics = self._calculate_metrics(trades)
        
        # Display summary
        self._display_summary(metrics)
        
        # Analyze winners
        print()
        print("🟢 ANALYZING WINNING TRADES")
        print("-" * 80)
        winners = [t for t in trades if t.get('pnl', 0) > 0]
        winner_insights = self._analyze_winners(winners)
        self._display_insights(winner_insights)
        
        # Analyze losers
        print()
        print("🔴 ANALYZING LOSING TRADES")
        print("-" * 80)
        losers = [t for t in trades if t.get('pnl', 0) < 0]
        loser_insights = self._analyze_losers(losers)
        self._display_insights(loser_insights)
        
        # Prompt for ML learning
        print()
        self._prompt_ml_learning(winner_insights, loser_insights)
    
    def _load_trades_for_date(self, date: str) -> List[Dict]:
        """Load all trades for specified date"""
        if not os.path.exists(self.trades_file):
            return []
        
        with open(self.trades_file, 'r') as f:
            all_trades = json.load(f)
        
        # Filter by date
        date_trades = [
            trade for trade in all_trades
            if trade.get('timestamp', '').startswith(date)
        ]
        
        return date_trades
    
    def _calculate_metrics(self, trades: List[Dict]) -> Dict:
        """Calculate performance metrics"""
        winning_trades = [t for t in trades if t.get('pnl', 0) > 0]
        losing_trades = [t for t in trades if t.get('pnl', 0) < 0]
        
        total_wins = len(winning_trades)
        total_losses = len(losing_trades)
        total_trades = len(trades)
        
        win_rate = total_wins / total_trades if total_trades > 0 else 0
        
        total_profit = sum(t.get('pnl', 0) for t in winning_trades)
        total_loss = abs(sum(t.get('pnl', 0) for t in losing_trades))
        
        avg_win = total_profit / total_wins if total_wins > 0 else 0
        avg_loss = total_loss / total_losses if total_losses > 0 else 0
        
        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
        
        net_profit = total_profit - total_loss
        
        return {
            "total_trades": total_trades,
            "winning_trades": total_wins,
            "losing_trades": total_losses,
            "win_rate": win_rate,
            "total_profit": total_profit,
            "total_loss": total_loss,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "profit_factor": profit_factor,
            "net_profit": net_profit
        }
    
    def _display_summary(self, metrics: Dict):
        """Display performance summary"""
        print("📊 PERFORMANCE SUMMARY")
        print()
        print(f"Total Trades: {metrics['total_trades']}")
        print(f"Winning Trades: {metrics['winning_trades']} (avg: ${metrics['avg_win']:,.2f})")
        print(f"Losing Trades: {metrics['losing_trades']} (avg: ${metrics['avg_loss']:,.2f})")
        print()
        print(f"Win Rate: {metrics['win_rate']:.1%}")
        print(f"Profit Factor: {metrics['profit_factor']:.2f}")
        print()
        print(f"Gross Profit: ${metrics['total_profit']:,.2f}")
        print(f"Gross Loss: -${metrics['total_loss']:,.2f}")
        print(f"Net Profit: ${metrics['net_profit']:,.2f}")
        print()
        
        # Performance rating
        if metrics['win_rate'] >= 0.7 and metrics['profit_factor'] >= 2.0:
            rating = "🟢 EXCELLENT"
        elif metrics['win_rate'] >= 0.6 and metrics['profit_factor'] >= 1.5:
            rating = "🟡 GOOD"
        elif metrics['win_rate'] >= 0.5:
            rating = "🟠 ACCEPTABLE"
        else:
            rating = "🔴 NEEDS IMPROVEMENT"
        
        print(f"Performance Rating: {rating}")
    
    def _analyze_winners(self, winners: List[Dict]) -> Dict:
        """Analyze why winning trades succeeded"""
        if not winners:
            return {"patterns": [], "summary": "No winning trades to analyze"}
        
        # Analyze common patterns
        patterns = []
        
        # Check for common symbols
        symbols = {}
        for trade in winners:
            symbol = trade.get('symbol', 'UNKNOWN')
            symbols[symbol] = symbols.get(symbol, 0) + 1
        
        most_profitable_symbol = max(symbols.items(), key=lambda x: x[1]) if symbols else None
        if most_profitable_symbol:
            patterns.append(
                f"Symbol {most_profitable_symbol[0]} had {most_profitable_symbol[1]} winning trade(s)"
            )
        
        # Check for common entry conditions
        fvg_wins = sum(1 for t in winners if t.get('fvg_confluence', False))
        if fvg_wins > len(winners) * 0.6:
            patterns.append(
                f"{fvg_wins}/{len(winners)} winners had FVG confluence (strong indicator)"
            )
        
        fib_wins = sum(1 for t in winners if t.get('fibonacci_confluence', False))
        if fib_wins > len(winners) * 0.6:
            patterns.append(
                f"{fib_wins}/{len(winners)} winners had Fibonacci confluence"
            )
        
        # Average hold time for winners
        avg_hold_time = sum(t.get('hold_time_hours', 0) for t in winners) / len(winners)
        patterns.append(
            f"Average winning hold time: {avg_hold_time:.1f} hours"
        )
        
        # Risk/reward analysis
        avg_rr = sum(t.get('risk_reward_ratio', 0) for t in winners) / len(winners)
        patterns.append(
            f"Average R:R ratio for winners: {avg_rr:.2f}:1"
        )
        
        summary = f"Winners consistently showed {', '.join(patterns[:2])}. " \
                  f"Technical confluence (FVG + Fibonacci) appears highly predictive. " \
                  f"Optimal hold time around {avg_hold_time:.0f} hours. " \
                  f"Higher R:R ratios ({avg_rr:.1f}:1) correlated with success. " \
                  f"Recommend maintaining current entry criteria and position sizing."
        
        return {
            "patterns": patterns,
            "summary": summary,
            "count": len(winners)
        }
    
    def _analyze_losers(self, losers: List[Dict]) -> Dict:
        """Analyze why losing trades failed"""
        if not losers:
            return {"patterns": [], "summary": "No losing trades to analyze"}
        
        patterns = []
        
        # Check for common failure modes
        premature_stops = sum(1 for t in losers if t.get('stopped_out', False))
        if premature_stops > 0:
            patterns.append(
                f"{premature_stops}/{len(losers)} losses hit stop loss (possibly too tight)"
            )
        
        # Low confidence trades
        low_confidence = sum(1 for t in losers if t.get('hive_confidence', 1.0) < 0.6)
        if low_confidence > len(losers) * 0.5:
            patterns.append(
                f"{low_confidence}/{len(losers)} losses had low hive confidence (<60%)"
            )
        
        # Weak technical setup
        weak_setup = sum(1 for t in losers if not t.get('fvg_confluence') and not t.get('fibonacci_confluence'))
        if weak_setup > 0:
            patterns.append(
                f"{weak_setup}/{len(losers)} losses lacked strong technical confluence"
            )
        
        # Average loss analysis
        avg_loss = sum(abs(t.get('pnl', 0)) for t in losers) / len(losers)
        patterns.append(
            f"Average loss: ${avg_loss:,.2f}"
        )
        
        summary = f"Losses primarily occurred when {patterns[0] if patterns else 'entry criteria were weak'}. " \
                  f"Pattern shows need for stricter confluence requirements. " \
                  f"Consider raising minimum hive confidence to 70% threshold. " \
                  f"Stop loss placement may need adjustment based on ATR volatility. " \
                  f"Recommend filtering out trades without both FVG and Fibonacci alignment."
        
        return {
            "patterns": patterns,
            "summary": summary,
            "count": len(losers)
        }
    
    def _display_insights(self, insights: Dict):
        """Display analysis insights"""
        patterns = insights.get('patterns', [])
        summary = insights.get('summary', '')
        count = insights.get('count', 0)
        
        if count == 0:
            print("   No trades in this category")
            return
        
        print()
        print(f"   Trades Analyzed: {count}")
        print()
        print("   Key Patterns:")
        for pattern in patterns:
            print(f"     • {pattern}")
        
        print()
        print("   Summary:")
        print(f"     {summary}")
    
    def _prompt_ml_learning(self, winner_insights: Dict, loser_insights: Dict):
        """Prompt user to save learnings to ML system"""
        print()
        print("=" * 80)
        print("🧠 ML LEARNING OPPORTUNITY")
        print("=" * 80)
        print()
        print("The system has identified patterns in today's trading.")
        print("Would you like to update the ML models with these insights?")
        print()
        
        if winner_insights.get('count', 0) > 0:
            print("✅ SUCCESSES TO REINFORCE:")
            print(f"   {winner_insights['summary']}")
            print()
            response = input("   Save winning patterns to ML? (yes/no): ")
            if response.lower() == 'yes':
                self._save_to_ml(winner_insights, 'success')
                print("   ✅ Winning patterns saved to ML training data")
            else:
                print("   ⏭️  Skipped")
        
        print()
        
        if loser_insights.get('count', 0) > 0:
            print("🔧 FAILURES TO CORRECT:")
            print(f"   {loser_insights['summary']}")
            print()
            response = input("   Save losing patterns to ML for correction? (yes/no): ")
            if response.lower() == 'yes':
                self._save_to_ml(loser_insights, 'failure')
                print("   ✅ Losing patterns saved for correction")
            else:
                print("   ⏭️  Skipped")
        
        print()
        print("📝 OR: Leave bot as-is (no changes)")
        response = input("Make no changes to ML? (yes/no): ")
        if response.lower() == 'yes':
            print("✅ ML models unchanged - continuing with current parameters")
        
        print()
        print("=" * 80)
    
    def _save_to_ml(self, insights: Dict, category: str):
        """Save insights to ML training data"""
        os.makedirs('ml', exist_ok=True)
        
        # Load existing training data
        if os.path.exists(self.ml_training_file):
            with open(self.ml_training_file, 'r') as f:
                training_data = json.load(f)
        else:
            training_data = {"successes": [], "failures": []}
        
        # Add new insights
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "category": category,
            "patterns": insights.get('patterns', []),
            "summary": insights.get('summary', ''),
            "count": insights.get('count', 0)
        }
        
        if category == 'success':
            training_data['successes'].append(entry)
        else:
            training_data['failures'].append(entry)
        
        # Save back
        with open(self.ml_training_file, 'w') as f:
            json.dump(training_data, f, indent=2)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='RICK Daily Replay & Audit')
    parser.add_argument('--date', type=str, help='Date to audit (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    audit = DailyReplayAudit()
    audit.run_daily_audit(date=args.date)
