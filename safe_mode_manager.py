#!/usr/bin/env python3
"""
RICK Safe Mode Progression System
Validates paper trading performance before allowing live trading
PIN: 841921 required for live authorization after meeting thresholds
"""

import os
import sys
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Add foundation path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

class TradingMode(Enum):
    PAPER = "PAPER"
    SAFE_VALIDATION = "SAFE_VALIDATION"  
    LIVE_READY = "LIVE_READY"
    LIVE_AUTHORIZED = "LIVE_AUTHORIZED"

@dataclass
class SafetyThresholds:
    """Safety thresholds that must be met before live trading"""
    
    # Minimum performance requirements
    MIN_WIN_RATE = 0.65  # 65% win rate
    MIN_PROFIT_FACTOR = 1.8  # Profit factor > 1.8
    MIN_SHARPE_RATIO = 1.5  # Sharpe ratio > 1.5
    MIN_TRADES_REQUIRED = 50  # Minimum 50 trades for statistical significance
    MIN_CONSECUTIVE_DAYS = 7  # Must be profitable for 7 consecutive days
    MAX_DRAWDOWN = 0.15  # Maximum 15% drawdown allowed
    
    # Capital requirements
    MIN_PAPER_CAPITAL = 10000.0  # Must manage at least $10K in paper
    MIN_DAILY_PROFIT_TARGET = 200.0  # Average $200+ daily profit
    
    # Risk management validation
    MAX_SINGLE_TRADE_RISK = 0.02  # No single trade > 2% of capital
    MIN_RISK_REWARD_RATIO = 2.0  # Risk/reward ratio > 2:1
    
    # Time requirements
    MIN_PAPER_TRADING_DAYS = 14  # Minimum 2 weeks paper trading
    MIN_LIVE_SIMULATION_HOURS = 168  # 7 days of continuous simulation

class SafeModeManager:
    """
    Manages progression from paper trading to live trading
    with strict safety validation
    """
    
    def __init__(self, pin: Optional[int] = None):
        self.pin = pin
        self.thresholds = SafetyThresholds()
        self.logger = self._setup_logging()
        self.performance_file = 'logs/safe_mode_performance.json'
        self.authorization_file = 'logs/live_trading_authorization.json'
        
        # Create logs directory
        os.makedirs('logs', exist_ok=True)
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for safe mode operations"""
        logger = logging.getLogger('safe_mode_manager')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.FileHandler('logs/safe_mode_progression.log', mode='a')
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
        
    def get_current_mode(self) -> TradingMode:
        """Get current trading mode based on performance"""
        if not os.path.exists(self.performance_file):
            return TradingMode.PAPER
            
        performance = self._load_performance_data()
        
        if self._is_live_authorized():
            return TradingMode.LIVE_AUTHORIZED
        elif self._meets_all_thresholds(performance):
            return TradingMode.LIVE_READY
        elif self._has_sufficient_data(performance):
            return TradingMode.SAFE_VALIDATION
        else:
            return TradingMode.PAPER
            
    def record_trade_result(self, trade_data: Dict):
        """Record a trade result for threshold validation"""
        performance = self._load_performance_data()
        
        # Add timestamp
        trade_data['timestamp'] = time.time()
        trade_data['date'] = datetime.now().strftime('%Y-%m-%d')
        
        # Add trade to history
        if 'trades' not in performance:
            performance['trades'] = []
        performance['trades'].append(trade_data)
        
        # Update daily statistics
        self._update_daily_stats(performance, trade_data)
        
        # Recalculate metrics
        self._calculate_performance_metrics(performance)
        
        # Save updated performance
        self._save_performance_data(performance)
        
        # Log the update
        self.logger.info(f"Trade recorded: {trade_data['result']} | "
                        f"P&L: ${trade_data.get('pnl', 0):.2f} | "
                        f"Total trades: {len(performance['trades'])}")
        
        # Check if ready for next level
        self._check_progression(performance)
        
    def _update_daily_stats(self, performance: Dict, trade_data: Dict):
        """Update daily performance statistics"""
        date = trade_data['date']
        
        if 'daily_stats' not in performance:
            performance['daily_stats'] = {}
            
        if date not in performance['daily_stats']:
            performance['daily_stats'][date] = {
                'total_trades': 0,
                'winning_trades': 0,
                'total_pnl': 0.0,
                'max_single_loss': 0.0,
                'max_single_win': 0.0
            }
            
        daily = performance['daily_stats'][date]
        daily['total_trades'] += 1
        
        pnl = trade_data.get('pnl', 0.0)
        daily['total_pnl'] += pnl
        
        if trade_data.get('result') == 'WIN':
            daily['winning_trades'] += 1
            daily['max_single_win'] = max(daily['max_single_win'], pnl)
        else:
            daily['max_single_loss'] = min(daily['max_single_loss'], pnl)
            
    def _calculate_performance_metrics(self, performance: Dict):
        """Calculate comprehensive performance metrics"""
        trades = performance.get('trades', [])
        
        if not trades:
            return
            
        # Basic metrics
        total_trades = len(trades)
        winning_trades = sum(1 for t in trades if t.get('result') == 'WIN')
        win_rate = winning_trades / total_trades
        
        # P&L metrics
        total_pnl = sum(t.get('pnl', 0) for t in trades)
        winning_pnl = sum(t.get('pnl', 0) for t in trades if t.get('result') == 'WIN')
        losing_pnl = abs(sum(t.get('pnl', 0) for t in trades if t.get('result') == 'LOSS'))
        
        profit_factor = winning_pnl / losing_pnl if losing_pnl > 0 else float('inf')
        
        # Daily metrics
        daily_stats = performance.get('daily_stats', {})
        daily_pnls = [day['total_pnl'] for day in daily_stats.values()]
        
        if daily_pnls:
            avg_daily_pnl = sum(daily_pnls) / len(daily_pnls)
            daily_std = (sum((x - avg_daily_pnl) ** 2 for x in daily_pnls) / len(daily_pnls)) ** 0.5
            sharpe_ratio = avg_daily_pnl / daily_std if daily_std > 0 else 0
        else:
            avg_daily_pnl = 0
            sharpe_ratio = 0
            
        # Drawdown calculation
        running_pnl = 0
        peak = 0
        max_drawdown = 0
        
        for trade in trades:
            running_pnl += trade.get('pnl', 0)
            peak = max(peak, running_pnl)
            drawdown = (peak - running_pnl) / peak if peak > 0 else 0
            max_drawdown = max(max_drawdown, drawdown)
            
        # Consecutive profitable days
        consecutive_days = self._calculate_consecutive_profitable_days(daily_stats)
        
        # Store metrics
        performance['metrics'] = {
            'total_trades': total_trades,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe_ratio,
            'total_pnl': total_pnl,
            'avg_daily_pnl': avg_daily_pnl,
            'max_drawdown': max_drawdown,
            'consecutive_profitable_days': consecutive_days,
            'trading_days': len(daily_stats),
            'updated': datetime.now().isoformat()
        }
        
    def _calculate_consecutive_profitable_days(self, daily_stats: Dict) -> int:
        """Calculate consecutive profitable trading days"""
        if not daily_stats:
            return 0
            
        sorted_dates = sorted(daily_stats.keys(), reverse=True)
        consecutive = 0
        
        for date in sorted_dates:
            if daily_stats[date]['total_pnl'] > 0:
                consecutive += 1
            else:
                break
                
        return consecutive
        
    def _has_sufficient_data(self, performance: Dict) -> bool:
        """Check if we have enough data for validation"""
        metrics = performance.get('metrics', {})
        
        return (
            metrics.get('total_trades', 0) >= 10 and  # At least 10 trades
            metrics.get('trading_days', 0) >= 3       # At least 3 days
        )
        
    def _meets_all_thresholds(self, performance: Dict) -> bool:
        """Check if performance meets all safety thresholds"""
        metrics = performance.get('metrics', {})
        
        if not metrics:
            return False
            
        # Check each threshold
        checks = [
            metrics.get('total_trades', 0) >= self.thresholds.MIN_TRADES_REQUIRED,
            metrics.get('win_rate', 0) >= self.thresholds.MIN_WIN_RATE,
            metrics.get('profit_factor', 0) >= self.thresholds.MIN_PROFIT_FACTOR,
            metrics.get('sharpe_ratio', 0) >= self.thresholds.MIN_SHARPE_RATIO,
            metrics.get('consecutive_profitable_days', 0) >= self.thresholds.MIN_CONSECUTIVE_DAYS,
            metrics.get('max_drawdown', 1) <= self.thresholds.MAX_DRAWDOWN,
            metrics.get('avg_daily_pnl', 0) >= self.thresholds.MIN_DAILY_PROFIT_TARGET,
            metrics.get('trading_days', 0) >= self.thresholds.MIN_PAPER_TRADING_DAYS
        ]
        
        return all(checks)
        
    def _is_live_authorized(self) -> bool:
        """Check if live trading has been manually authorized"""
        if not os.path.exists(self.authorization_file):
            return False
            
        try:
            with open(self.authorization_file, 'r') as f:
                auth_data = json.load(f)
                
            return (
                auth_data.get('authorized', False) and
                auth_data.get('pin') == 841921 and
                auth_data.get('expires', 0) > time.time()
            )
        except:
            return False
            
    def request_live_authorization(self) -> Dict:
        """Request live trading authorization after meeting thresholds"""
        performance = self._load_performance_data()
        
        if not self._meets_all_thresholds(performance):
            return {
                "status": "not_ready",
                "message": "Performance thresholds not yet met",
                "current_metrics": performance.get('metrics', {}),
                "required_thresholds": self._get_threshold_comparison(performance)
            }
            
        # Generate authorization request
        auth_request = {
            "status": "ready_for_authorization",
            "timestamp": time.time(),
            "performance_summary": self._generate_performance_summary(performance),
            "risk_analysis": self._generate_risk_analysis(performance),
            "authorization_required": True,
            "message": "🎯 PERFORMANCE THRESHOLDS MET - Ready for live trading authorization"
        }
        
        # Save authorization request
        with open('logs/live_authorization_request.json', 'w') as f:
            json.dump(auth_request, f, indent=2)
            
        self.logger.warning("🎯 LIVE AUTHORIZATION REQUESTED - Manual approval required")
        
        return auth_request
        
    def authorize_live_trading(self, pin: int, duration_hours: int = 24) -> Dict:
        """Authorize live trading with PIN verification"""
        if pin != 841921:
            return {"status": "unauthorized", "message": "Invalid PIN"}
            
        performance = self._load_performance_data()
        
        if not self._meets_all_thresholds(performance):
            return {"status": "not_ready", "message": "Thresholds not met"}
            
        # Create authorization
        auth_data = {
            "authorized": True,
            "pin": pin,
            "authorized_at": time.time(),
            "expires": time.time() + (duration_hours * 3600),
            "duration_hours": duration_hours,
            "performance_validated": True,
            "metrics_snapshot": performance.get('metrics', {})
        }
        
        # Save authorization
        with open(self.authorization_file, 'w') as f:
            json.dump(auth_data, f, indent=2)
            
        self.logger.warning(f"🔴 LIVE TRADING AUTHORIZED for {duration_hours} hours")
        
        return {"status": "authorized", "expires_in_hours": duration_hours}
        
    def _generate_performance_summary(self, performance: Dict) -> Dict:
        """Generate performance summary for authorization review"""
        metrics = performance.get('metrics', {})
        
        return {
            "trading_period_days": metrics.get('trading_days', 0),
            "total_trades": metrics.get('total_trades', 0),
            "win_rate_percent": round(metrics.get('win_rate', 0) * 100, 1),
            "profit_factor": round(metrics.get('profit_factor', 0), 2),
            "sharpe_ratio": round(metrics.get('sharpe_ratio', 0), 2),
            "total_profit_usd": round(metrics.get('total_pnl', 0), 2),
            "avg_daily_profit_usd": round(metrics.get('avg_daily_pnl', 0), 2),
            "max_drawdown_percent": round(metrics.get('max_drawdown', 0) * 100, 1),
            "consecutive_profitable_days": metrics.get('consecutive_profitable_days', 0)
        }
        
    def _generate_risk_analysis(self, performance: Dict) -> Dict:
        """Generate risk analysis for authorization review"""
        trades = performance.get('trades', [])
        
        if not trades:
            return {}
            
        # Calculate risk metrics
        trade_sizes = [abs(t.get('pnl', 0)) for t in trades]
        avg_trade_size = sum(trade_sizes) / len(trade_sizes)
        max_trade_size = max(trade_sizes)
        
        return {
            "avg_trade_size_usd": round(avg_trade_size, 2),
            "max_single_trade_size_usd": round(max_trade_size, 2),
            "risk_per_trade_percent": round((max_trade_size / 10000) * 100, 2),  # Assume $10K capital
            "risk_management_score": self._calculate_risk_score(trades),
            "consistency_score": self._calculate_consistency_score(performance)
        }
        
    def _calculate_risk_score(self, trades: List[Dict]) -> str:
        """Calculate risk management score"""
        if not trades:
            return "INSUFFICIENT_DATA"
            
        # Analyze position sizing consistency
        trade_sizes = [abs(t.get('pnl', 0)) for t in trades]
        avg_size = sum(trade_sizes) / len(trade_sizes)
        size_variance = sum((size - avg_size) ** 2 for size in trade_sizes) / len(trade_sizes)
        
        if size_variance < avg_size * 0.1:
            return "EXCELLENT"
        elif size_variance < avg_size * 0.3:
            return "GOOD"
        else:
            return "NEEDS_IMPROVEMENT"
            
    def _calculate_consistency_score(self, performance: Dict) -> str:
        """Calculate trading consistency score"""
        daily_stats = performance.get('daily_stats', {})
        
        if len(daily_stats) < 5:
            return "INSUFFICIENT_DATA"
            
        profitable_days = sum(1 for day in daily_stats.values() if day['total_pnl'] > 0)
        consistency_rate = profitable_days / len(daily_stats)
        
        if consistency_rate >= 0.8:
            return "EXCELLENT"
        elif consistency_rate >= 0.6:
            return "GOOD"
        else:
            return "NEEDS_IMPROVEMENT"
            
    def _get_threshold_comparison(self, performance: Dict) -> Dict:
        """Get comparison of current performance vs thresholds"""
        metrics = performance.get('metrics', {})
        
        return {
            "trades_required": {
                "threshold": self.thresholds.MIN_TRADES_REQUIRED,
                "current": metrics.get('total_trades', 0),
                "met": metrics.get('total_trades', 0) >= self.thresholds.MIN_TRADES_REQUIRED
            },
            "win_rate": {
                "threshold": f"{self.thresholds.MIN_WIN_RATE*100:.1f}%",
                "current": f"{metrics.get('win_rate', 0)*100:.1f}%",
                "met": metrics.get('win_rate', 0) >= self.thresholds.MIN_WIN_RATE
            },
            "profit_factor": {
                "threshold": self.thresholds.MIN_PROFIT_FACTOR,
                "current": round(metrics.get('profit_factor', 0), 2),
                "met": metrics.get('profit_factor', 0) >= self.thresholds.MIN_PROFIT_FACTOR
            },
            "sharpe_ratio": {
                "threshold": self.thresholds.MIN_SHARPE_RATIO,
                "current": round(metrics.get('sharpe_ratio', 0), 2),
                "met": metrics.get('sharpe_ratio', 0) >= self.thresholds.MIN_SHARPE_RATIO
            },
            "consecutive_profitable_days": {
                "threshold": self.thresholds.MIN_CONSECUTIVE_DAYS,
                "current": metrics.get('consecutive_profitable_days', 0),
                "met": metrics.get('consecutive_profitable_days', 0) >= self.thresholds.MIN_CONSECUTIVE_DAYS
            },
            "max_drawdown": {
                "threshold": f"{self.thresholds.MAX_DRAWDOWN*100:.1f}%",
                "current": f"{metrics.get('max_drawdown', 1)*100:.1f}%",
                "met": metrics.get('max_drawdown', 1) <= self.thresholds.MAX_DRAWDOWN
            },
            "daily_profit": {
                "threshold": f"${self.thresholds.MIN_DAILY_PROFIT_TARGET:.0f}",
                "current": f"${metrics.get('avg_daily_pnl', 0):.0f}",
                "met": metrics.get('avg_daily_pnl', 0) >= self.thresholds.MIN_DAILY_PROFIT_TARGET
            },
            "trading_days": {
                "threshold": self.thresholds.MIN_PAPER_TRADING_DAYS,
                "current": metrics.get('trading_days', 0),
                "met": metrics.get('trading_days', 0) >= self.thresholds.MIN_PAPER_TRADING_DAYS
            }
        }
        
    def get_progression_status(self) -> Dict:
        """Get current progression status and next steps"""
        performance = self._load_performance_data()
        current_mode = self.get_current_mode()
        
        return {
            "current_mode": current_mode.value,
            "performance_summary": self._generate_performance_summary(performance),
            "threshold_comparison": self._get_threshold_comparison(performance),
            "ready_for_live": self._meets_all_thresholds(performance),
            "live_authorized": self._is_live_authorized(),
            "next_steps": self._get_next_steps(current_mode, performance)
        }
        
    def _get_next_steps(self, mode: TradingMode, performance: Dict) -> List[str]:
        """Get next steps based on current mode"""
        if mode == TradingMode.PAPER:
            return [
                "Continue paper trading to build performance history",
                f"Need {self.thresholds.MIN_TRADES_REQUIRED} trades (current: {performance.get('metrics', {}).get('total_trades', 0)})",
                f"Need {self.thresholds.MIN_PAPER_TRADING_DAYS} trading days (current: {performance.get('metrics', {}).get('trading_days', 0)})"
            ]
        elif mode == TradingMode.SAFE_VALIDATION:
            comparison = self._get_threshold_comparison(performance)
            unmet = [key for key, data in comparison.items() if not data['met']]
            return [f"Improve {metric.replace('_', ' ')}: {comparison[metric]['current']} → {comparison[metric]['threshold']}" for metric in unmet]
        elif mode == TradingMode.LIVE_READY:
            return [
                "🎯 All thresholds met! Ready for live trading authorization",
                "Run: manager.request_live_authorization() to review results",
                "Manual authorization with PIN 841921 required for live trading"
            ]
        elif mode == TradingMode.LIVE_AUTHORIZED:
            return [
                "🔴 LIVE TRADING AUTHORIZED",
                "Monitor performance closely",
                "Authorization expires automatically for safety"
            ]
            
        return []
        
    def _load_performance_data(self) -> Dict:
        """Load performance data from file"""
        if not os.path.exists(self.performance_file):
            return {}
            
        try:
            with open(self.performance_file, 'r') as f:
                return json.load(f)
        except:
            return {}
            
    def _save_performance_data(self, performance: Dict):
        """Save performance data to file"""
        with open(self.performance_file, 'w') as f:
            json.dump(performance, f, indent=2)
            
    def _check_progression(self, performance: Dict):
        """Check if ready to progress to next level"""
        current_mode = self.get_current_mode()
        
        if current_mode == TradingMode.SAFE_VALIDATION and self._meets_all_thresholds(performance):
            self.logger.warning("🎯 THRESHOLDS MET - Ready for live authorization request!")
            
        metrics = performance.get('metrics', {})
        self.logger.info(f"Progress: {metrics.get('total_trades', 0)} trades | "
                        f"Win rate: {metrics.get('win_rate', 0)*100:.1f}% | "
                        f"Profit factor: {metrics.get('profit_factor', 0):.2f} | "
                        f"Mode: {current_mode.value}")


def test_safe_mode():
    """Test safe mode progression system"""
    print("=== RICK Safe Mode Progression System ===")
    print()
    
    manager = SafeModeManager()
    
    # Check current status
    status = manager.get_progression_status()
    
    print(f"Current Mode: {status['current_mode']}")
    print(f"Ready for Live: {status['ready_for_live']}")
    print(f"Live Authorized: {status['live_authorized']}")
    print()
    
    print("Performance Summary:")
    for key, value in status['performance_summary'].items():
        print(f"  {key}: {value}")
    print()
    
    print("Threshold Status:")
    for metric, data in status['threshold_comparison'].items():
        status_icon = "✅" if data['met'] else "❌"
        print(f"  {status_icon} {metric}: {data['current']} (need: {data['threshold']})")
    print()
    
    print("Next Steps:")
    for step in status['next_steps']:
        print(f"  • {step}")
    print()
    
    print("=== Test Complete ===")


if __name__ == "__main__":
    test_safe_mode()