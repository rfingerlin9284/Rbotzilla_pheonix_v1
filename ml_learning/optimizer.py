#!/usr/bin/env python3
"""
RBOTzilla UNI - Trading Optimizer Engine  
Sharpe-driven parameter optimization and performance tuning suggestions.
PIN: 841921 | Phase 13
"""

import json
import os
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, asdict
import threading
from collections import defaultdict
import math

@dataclass
class OptimizationResult:
    """
    ENGINEER (30%): Optimization result data structure
    """
    parameter: str
    current_value: Any
    suggested_value: Any
    expected_improvement: float  # Expected Sharpe ratio improvement
    confidence: float  # Confidence in suggestion (0-1)
    reasoning: str
    data_points: int  # Number of trades used for analysis

class TradingOptimizer:
    """
    PROF_QUANT (40%): Advanced Sharpe ratio analysis and parameter optimization
    ENGINEER (30%): Performance tracking and suggestion algorithms
    TRADER_PSYCH (20%): Behavioral optimization and risk psychology
    MENTOR_BK (10%): Update scheduling and fallback mechanisms
    
    Optimization engine that:
    - Analyzes trading performance using Sharpe ratios
    - Suggests parameter adjustments for strategies
    - Tracks performance improvements over time
    - Provides regime-specific optimizations
    """
    
    def __init__(self, pin: int = 841921, optimization_file: str = "optimizations.json"):
        """Initialize Trading Optimizer with PIN authentication"""
        if pin != 841921:
            raise ValueError("Invalid PIN for Trading Optimizer")
        
        self.pin_verified = True
        self.optimization_file = optimization_file
        self.min_trades_for_optimization = 20  # Minimum trades needed for suggestions
        self.lookback_days = 30  # Days to look back for performance analysis
        self.risk_free_rate = 0.02  # 2% annual risk-free rate
        
        # Performance tracking
        self.performance_history: List[Dict[str, Any]] = []
        self.optimization_history: List[OptimizationResult] = []
        self.lock = threading.Lock()
        
        # Parameter ranges for optimization
        self.parameter_ranges = {
            'confidence_threshold': (0.55, 0.85, 0.05),  # (min, max, step)
            'rsi_period': (10, 20, 2),
            'bb_period': (15, 25, 2),
            'bb_std': (1.5, 2.5, 0.1),
            'macd_fast': (8, 16, 2),
            'macd_slow': (20, 30, 2),
            'atr_period': (10, 20, 2),
            'volume_ma_period': (15, 25, 2)
        }
        
        self.logger = logging.getLogger(f"TradingOptimizer_{pin}")
        self.logger.info("Trading Optimizer initialized")
        
        # Load existing optimization history
        self._load_optimizations()
    
    def _load_optimizations(self):
        """
        ENGINEER: Load optimization history from persistent storage
        """
        if os.path.exists(self.optimization_file):
            try:
                with open(self.optimization_file, 'r') as f:
                    opt_data = json.load(f)
                
                self.performance_history = opt_data.get('performance_history', [])
                
                opt_results = []
                for opt_dict in opt_data.get('optimization_history', []):
                    try:
                        result = OptimizationResult(**opt_dict)
                        opt_results.append(result)
                    except Exception as e:
                        self.logger.warning(f"Failed to load optimization result: {e}")
                
                self.optimization_history = opt_results
                self.logger.info(f"Loaded {len(self.optimization_history)} optimization results")
                
            except Exception as e:
                self.logger.error(f"Failed to load optimizations: {e}")
                self.performance_history = []
                self.optimization_history = []
        else:
            self.logger.info("No existing optimization file found - starting fresh")
    
    def _save_optimizations(self):
        """
        ENGINEER: Save optimization history to persistent storage
        """
        try:
            opt_data = {
                'performance_history': self.performance_history[-1000:],  # Keep last 1000 records
                'optimization_history': [asdict(opt) for opt in self.optimization_history[-100:]],  # Keep last 100 optimizations
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
            
            # Write to temporary file first, then rename for atomic operation
            temp_file = f"{self.optimization_file}.tmp"
            with open(temp_file, 'w') as f:
                json.dump(opt_data, f, indent=2)
            
            os.rename(temp_file, self.optimization_file)
            self.logger.info("Saved optimization data")
            
        except Exception as e:
            self.logger.error(f"Failed to save optimizations: {e}")
    
    def record_trade_performance(self, trade_data: Dict[str, Any]):
        """
        ENGINEER: Record individual trade performance for optimization analysis
        """
        try:
            with self.lock:
                performance_record = {
                    'timestamp': trade_data.get('timestamp', datetime.now(timezone.utc).isoformat()),
                    'regime': trade_data.get('regime', 'UNKNOWN'),
                    'strategy': trade_data.get('strategy', 'UNKNOWN'),
                    'direction': trade_data.get('direction', 'HOLD'),
                    'confidence': trade_data.get('confidence', 0.0),
                    'entry_price': trade_data.get('entry_price'),
                    'exit_price': trade_data.get('exit_price'),
                    'pnl': trade_data.get('pnl', 0.0),
                    'pnl_pct': trade_data.get('pnl_pct', 0.0),
                    'duration_minutes': trade_data.get('duration_minutes', 0),
                    'outcome': trade_data.get('outcome', 'UNKNOWN'),
                    'parameters': trade_data.get('parameters', {})  # Strategy parameters used
                }
                
                self.performance_history.append(performance_record)
                self.logger.debug(f"Recorded trade performance: {performance_record['outcome']} PnL: {performance_record['pnl']:.4f}")
                
        except Exception as e:
            self.logger.error(f"Failed to record trade performance: {e}")
    
    def calculate_sharpe_ratio(self, returns: List[float], risk_free_rate: Optional[float] = None) -> float:
        """
        PROF_QUANT: Calculate Sharpe ratio for a series of returns
        """
        if not returns or len(returns) < 2:
            return 0.0
        
        if risk_free_rate is None:
            risk_free_rate = self.risk_free_rate
        
        # Convert to numpy array for calculations
        returns_array = np.array(returns)
        
        # Calculate mean return and standard deviation
        mean_return = np.mean(returns_array)
        std_return = np.std(returns_array, ddof=1) if len(returns_array) > 1 else 0.0
        
        # Avoid division by zero
        if std_return == 0:
            return 0.0
        
        # Calculate annualized Sharpe ratio (assuming daily returns)
        # Adjust risk-free rate to match return frequency
        daily_rf_rate = risk_free_rate / 365
        excess_return = mean_return - daily_rf_rate
        
        sharpe = (excess_return / std_return) * np.sqrt(252)  # Annualized with 252 trading days
        
        return sharpe
    
    def calculate_performance_metrics(self, trades: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        PROF_QUANT: Calculate comprehensive performance metrics
        """
        if not trades:
            return {
                'total_trades': 0,
                'win_rate': 0.0,
                'avg_return': 0.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'profit_factor': 0.0,
                'avg_trade_duration': 0.0
            }
        
        # Extract performance data
        returns = [t.get('pnl_pct', 0.0) for t in trades if t.get('pnl_pct') is not None]
        outcomes = [t.get('outcome') for t in trades]
        durations = [t.get('duration_minutes', 0) for t in trades]
        
        # Basic metrics
        total_trades = len(trades)
        wins = sum(1 for outcome in outcomes if outcome == 'WIN')
        win_rate = wins / total_trades if total_trades > 0 else 0.0
        
        # Return metrics
        avg_return = np.mean(returns) if returns else 0.0
        sharpe_ratio = self.calculate_sharpe_ratio(returns)
        
        # Drawdown calculation
        cumulative_returns = np.cumsum(returns) if returns else [0]
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdown = running_max - cumulative_returns
        max_drawdown = np.max(drawdown) if len(drawdown) > 0 else 0.0
        
        # Profit factor (gross profit / gross loss)
        winning_trades = [r for r in returns if r > 0]
        losing_trades = [r for r in returns if r < 0]
        gross_profit = sum(winning_trades) if winning_trades else 0.0
        gross_loss = abs(sum(losing_trades)) if losing_trades else 0.0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf') if gross_profit > 0 else 0.0
        
        # Average trade duration
        avg_duration = np.mean(durations) if durations else 0.0
        
        return {
            'total_trades': total_trades,
            'win_rate': win_rate,
            'avg_return': avg_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'profit_factor': profit_factor,
            'avg_trade_duration': avg_duration
        }
    
    def analyze_parameter_impact(self, parameter: str, trades: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        PROF_QUANT: Analyze how different parameter values affect performance
        """
        try:
            # Group trades by parameter value
            parameter_groups = defaultdict(list)
            
            for trade in trades:
                param_value = trade.get('parameters', {}).get(parameter)
                if param_value is not None:
                    parameter_groups[param_value].append(trade)
            
            if len(parameter_groups) < 2:
                return {'insufficient_data': True}
            
            # Calculate performance for each parameter value
            performance_by_param = {}
            for param_value, param_trades in parameter_groups.items():
                if len(param_trades) >= 5:  # Minimum trades for meaningful analysis
                    metrics = self.calculate_performance_metrics(param_trades)
                    performance_by_param[param_value] = metrics
            
            if len(performance_by_param) < 2:
                return {'insufficient_data': True}
            
            # Find optimal parameter value based on Sharpe ratio
            best_param = max(performance_by_param.keys(), 
                           key=lambda k: performance_by_param[k]['sharpe_ratio'])
            best_performance = performance_by_param[best_param]
            
            return {
                'parameter': parameter,
                'performance_by_value': performance_by_param,
                'optimal_value': best_param,
                'optimal_performance': best_performance,
                'improvement_potential': best_performance['sharpe_ratio'] - 
                                       np.mean([p['sharpe_ratio'] for p in performance_by_param.values()])
            }
            
        except Exception as e:
            self.logger.error(f"Parameter impact analysis failed for {parameter}: {e}")
            return {'error': str(e)}
    
    def generate_optimization_suggestions(self, regime: Optional[str] = None) -> List[OptimizationResult]:
        """
        MENTOR_BK: Generate optimization suggestions based on performance analysis
        TRADER_PSYCH: Apply behavioral insights to suggestions
        """
        try:
            suggestions = []
            
            # Filter recent trades
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.lookback_days)
            recent_trades = [
                trade for trade in self.performance_history
                if datetime.fromisoformat(trade['timestamp'].replace('Z', '+00:00')) >= cutoff_date
            ]
            
            # Filter by regime if specified
            if regime:
                recent_trades = [t for t in recent_trades if t.get('regime') == regime]
            
            if len(recent_trades) < self.min_trades_for_optimization:
                self.logger.info(f"Insufficient trades for optimization: {len(recent_trades)} < {self.min_trades_for_optimization}")
                return suggestions
            
            # Analyze each optimizable parameter
            for parameter, (min_val, max_val, step) in self.parameter_ranges.items():
                analysis = self.analyze_parameter_impact(parameter, recent_trades)
                
                if 'insufficient_data' in analysis or 'error' in analysis:
                    continue
                
                # Generate suggestion if improvement potential exists
                improvement_potential = analysis.get('improvement_potential', 0)
                if improvement_potential > 0.1:  # Minimum 0.1 Sharpe improvement
                    
                    # Get current parameter value (assume from most recent trade)
                    current_value = None
                    for trade in reversed(recent_trades):
                        if parameter in trade.get('parameters', {}):
                            current_value = trade['parameters'][parameter]
                            break
                    
                    optimal_value = analysis['optimal_value']
                    
                    # Calculate confidence based on data quality
                    total_data_points = sum(p['total_trades'] for p in analysis['performance_by_value'].values())
                    confidence = min(total_data_points / 50.0, 1.0)  # Max confidence at 50+ trades
                    
                    # Generate reasoning
                    optimal_performance = analysis['optimal_performance']
                    reasoning = f"Optimal {parameter}={optimal_value} shows Sharpe ratio of {optimal_performance['sharpe_ratio']:.3f} " \
                              f"with {optimal_performance['win_rate']:.1%} win rate over {optimal_performance['total_trades']} trades"
                    
                    suggestion = OptimizationResult(
                        parameter=parameter,
                        current_value=current_value,
                        suggested_value=optimal_value,
                        expected_improvement=improvement_potential,
                        confidence=confidence,
                        reasoning=reasoning,
                        data_points=total_data_points
                    )
                    
                    suggestions.append(suggestion)
            
            # Sort by expected improvement
            suggestions.sort(key=lambda x: x.expected_improvement, reverse=True)
            
            # Store suggestions in history
            with self.lock:
                self.optimization_history.extend(suggestions)
                if len(suggestions) > 0:
                    self._save_optimizations()
            
            self.logger.info(f"Generated {len(suggestions)} optimization suggestions")
            return suggestions
            
        except Exception as e:
            self.logger.error(f"Failed to generate optimization suggestions: {e}")
            return []
    
    def get_regime_performance_summary(self) -> Dict[str, Dict[str, Any]]:
        """
        PROF_QUANT: Get performance summary by trading regime
        """
        try:
            regime_trades = defaultdict(list)
            
            for trade in self.performance_history:
                regime = trade.get('regime', 'UNKNOWN')
                regime_trades[regime].append(trade)
            
            summary = {}
            for regime, trades in regime_trades.items():
                summary[regime] = self.calculate_performance_metrics(trades)
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to get regime performance summary: {e}")
            return {}
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive optimization report
        """
        try:
            recent_trades = self.performance_history[-100:]  # Last 100 trades
            overall_performance = self.calculate_performance_metrics(recent_trades)
            regime_performance = self.get_regime_performance_summary()
            
            # Recent optimization suggestions
            recent_suggestions = self.optimization_history[-10:]
            
            # Calculate optimization effectiveness (how many suggestions were beneficial)
            implemented_count = 0
            beneficial_count = 0
            
            # This would need integration with strategy parameter tracking
            # For now, provide placeholder data
            
            return {
                'overall_performance': overall_performance,
                'regime_performance': regime_performance,
                'recent_suggestions': [asdict(s) for s in recent_suggestions],
                'optimization_effectiveness': {
                    'total_suggestions': len(self.optimization_history),
                    'implemented_suggestions': implemented_count,
                    'beneficial_implementations': beneficial_count,
                    'success_rate': beneficial_count / implemented_count if implemented_count > 0 else 0.0
                },
                'data_quality': {
                    'total_trades_analyzed': len(self.performance_history),
                    'recent_trades': len(recent_trades),
                    'lookback_days': self.lookback_days,
                    'min_trades_for_optimization': self.min_trades_for_optimization
                },
                'generated_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate optimization report: {e}")
            return {'error': str(e)}
    
    def save_now(self):
        """Force save optimization data to disk"""
        with self.lock:
            self._save_optimizations()

def get_trading_optimizer(pin: int = 841921) -> TradingOptimizer:
    """Convenience function to get Trading Optimizer instance"""
    return TradingOptimizer(pin=pin)

# Example usage
if __name__ == "__main__":
    # Test Trading Optimizer
    optimizer = TradingOptimizer(pin=841921)
    
    print("📊 TRADING OPTIMIZER TEST RESULTS 📊")
    print("=" * 50)
    
    # Sample trade data
    sample_trades = [
        {
            'timestamp': (datetime.now(timezone.utc) - timedelta(days=i)).isoformat(),
            'regime': 'BULLISH',
            'strategy': 'BullishWolf',
            'direction': 'BUY',
            'confidence': 0.70 + (i % 3) * 0.05,
            'entry_price': 1.1000 + i * 0.001,
            'exit_price': 1.1000 + i * 0.001 + (0.002 if i % 2 == 0 else -0.001),
            'pnl': 0.002 if i % 2 == 0 else -0.001,
            'pnl_pct': 0.18 if i % 2 == 0 else -0.09,
            'duration_minutes': 30 + i * 5,
            'outcome': 'WIN' if i % 2 == 0 else 'LOSS',
            'parameters': {
                'confidence_threshold': 0.65,
                'rsi_period': 14,
                'bb_period': 20
            }
        }
        for i in range(25)  # Generate 25 sample trades
    ]
    
    # Record sample trades
    for trade in sample_trades:
        optimizer.record_trade_performance(trade)
    
    print(f"Recorded {len(sample_trades)} sample trades")
    
    # Generate optimization suggestions
    suggestions = optimizer.generate_optimization_suggestions()
    print(f"Generated {len(suggestions)} optimization suggestions")
    
    for suggestion in suggestions:
        print(f"  {suggestion.parameter}: {suggestion.current_value} → {suggestion.suggested_value}")
        print(f"    Expected improvement: {suggestion.expected_improvement:.3f}")
        print(f"    Confidence: {suggestion.confidence:.3f}")
    
    # Get optimization report
    report = optimizer.get_optimization_report()
    print(f"Overall Sharpe Ratio: {report['overall_performance']['sharpe_ratio']:.3f}")
    print(f"Win Rate: {report['overall_performance']['win_rate']:.1%}")
    
    print("✅ Trading Optimizer operational")