#!/usr/bin/env python3
"""
RBOTzilla UNI - Dynamic Position Sizing Engine
Kelly Criterion-based position sizing with volatility adjustment and risk limits.
PIN: 841921 | Phase 14
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
import math

@dataclass
class PositionSizeResult:
    """
    ENGINEER (35%): Position sizing result data structure
    """
    symbol: str
    base_kelly_fraction: float
    adjusted_kelly_fraction: float
    volatility_adjustment: float
    final_position_size: float
    max_position_limit: float
    recommended_units: int
    risk_level: str  # LOW, MODERATE, HIGH, EXTREME
    reasoning: str
    confidence: float
    sharpe_adjustment: float

class DynamicSizing:
    """
    PROF_QUANT (40%): Advanced Kelly Criterion mathematics and risk modeling
    ENGINEER (35%): Position control systems and trading limits
    TRADER_PSYCH (20%): Portfolio exposure psychology and behavioral risk management
    MENTOR_BK (5%): Risk parity adaptation and system reliability
    
    Dynamic position sizing system that:
    - Calculates Kelly optimal fraction based on win rate and payoff ratios
    - Adjusts for volatility and market regime
    - Enforces maximum position limits (10% capital)
    - Integrates with ML performance data for adaptive sizing
    - Provides psychological risk controls
    """
    
    def __init__(self, pin: int = 841921, account_balance: float = 100000.0):
        """Initialize Dynamic Sizing with PIN authentication"""
        if pin != 841921:
            raise ValueError("Invalid PIN for Dynamic Sizing")
        
        self.pin_verified = True
        self.account_balance = account_balance
        self.max_position_pct = 0.10  # 10% maximum position size
        self.min_position_pct = 0.001  # 0.1% minimum position size
        self.kelly_multiplier = 0.25  # Conservative Kelly scaling (quarter Kelly)
        self.volatility_lookback = 20  # Days for volatility calculation
        
        # Risk management parameters
        self.risk_free_rate = 0.02  # 2% annual risk-free rate
        self.max_leverage = 1.0  # No leverage by default
        self.emergency_stop_drawdown = 0.15  # 15% maximum drawdown
        
        # Performance tracking for Kelly calculation
        self.performance_history: Dict[str, List[Dict[str, Any]]] = {}
        self.position_history: List[Dict[str, Any]] = []
        self.lock = threading.Lock()
        
        # Volatility adjustment parameters
        self.volatility_target = 0.02  # 2% daily volatility target
        self.volatility_adjustment_factor = 0.5  # How much to adjust for volatility
        
        self.logger = logging.getLogger(f"DynamicSizing_{pin}")
        self.logger.info(f"Dynamic Sizing initialized with ${account_balance:,.2f} account balance")
    
    def update_account_balance(self, new_balance: float):
        """
        ENGINEER: Update account balance for position calculations
        """
        with self.lock:
            old_balance = self.account_balance
            self.account_balance = new_balance
            self.logger.info(f"Account balance updated: ${old_balance:,.2f} → ${new_balance:,.2f}")
    
    def record_trade_result(self, symbol: str, trade_data: Dict[str, Any]):
        """
        ENGINEER: Record trade results for Kelly calculation
        """
        try:
            with self.lock:
                if symbol not in self.performance_history:
                    self.performance_history[symbol] = []
                
                trade_record = {
                    'timestamp': trade_data.get('timestamp', datetime.now(timezone.utc).isoformat()),
                    'outcome': trade_data.get('outcome', 'UNKNOWN'),  # WIN, LOSS, BREAKEVEN
                    'pnl': trade_data.get('pnl', 0.0),
                    'pnl_pct': trade_data.get('pnl_pct', 0.0),
                    'position_size': trade_data.get('position_size', 0.0),
                    'duration_minutes': trade_data.get('duration_minutes', 0),
                    'entry_price': trade_data.get('entry_price'),
                    'exit_price': trade_data.get('exit_price')
                }
                
                self.performance_history[symbol].append(trade_record)
                
                # Keep only recent trades (last 100 per symbol)
                if len(self.performance_history[symbol]) > 100:
                    self.performance_history[symbol] = self.performance_history[symbol][-100:]
                
                self.logger.debug(f"Recorded trade result for {symbol}: {trade_record['outcome']} PnL: {trade_record['pnl']:.4f}")
                
        except Exception as e:
            self.logger.error(f"Failed to record trade result for {symbol}: {e}")
    
    def calculate_kelly_fraction(self, symbol: str, min_trades: int = 10) -> Tuple[float, Dict[str, Any]]:
        """
        PROF_QUANT: Calculate Kelly optimal fraction using historical performance
        
        Kelly formula: f = (bp - q) / b
        Where:
        - f = fraction of capital to wager
        - b = odds received on the wager (average win / average loss)
        - p = probability of winning
        - q = probability of losing (1-p)
        """
        try:
            if symbol not in self.performance_history:
                return 0.0, {'error': 'No performance history for symbol'}
            
            trades = self.performance_history[symbol]
            
            if len(trades) < min_trades:
                return 0.0, {'error': f'Insufficient trades: {len(trades)} < {min_trades}'}
            
            # Calculate win rate
            wins = [t for t in trades if t['outcome'] == 'WIN']
            losses = [t for t in trades if t['outcome'] == 'LOSS']
            
            if not wins or not losses:
                return 0.0, {'error': 'Need both wins and losses for Kelly calculation'}
            
            win_rate = len(wins) / len(trades)
            loss_rate = 1 - win_rate
            
            # Calculate average win and loss amounts
            avg_win = np.mean([t['pnl_pct'] for t in wins])
            avg_loss = abs(np.mean([t['pnl_pct'] for t in losses]))  # Make positive
            
            if avg_loss == 0:
                return 0.0, {'error': 'Average loss is zero'}
            
            # Kelly fraction calculation
            odds_ratio = avg_win / avg_loss  # This is 'b' in Kelly formula
            kelly_fraction = (odds_ratio * win_rate - loss_rate) / odds_ratio
            
            # Ensure non-negative
            kelly_fraction = max(0.0, kelly_fraction)
            
            # Apply conservative multiplier
            conservative_kelly = kelly_fraction * self.kelly_multiplier
            
            calculation_data = {
                'trades_analyzed': len(trades),
                'win_rate': win_rate,
                'avg_win_pct': avg_win,
                'avg_loss_pct': avg_loss,
                'odds_ratio': odds_ratio,
                'raw_kelly': kelly_fraction,
                'conservative_kelly': conservative_kelly
            }
            
            return conservative_kelly, calculation_data
            
        except Exception as e:
            self.logger.error(f"Kelly fraction calculation failed for {symbol}: {e}")
            return 0.0, {'error': str(e)}
    
    def calculate_volatility_adjustment(self, symbol: str, price_data: Optional[List[float]] = None) -> float:
        """
        PROF_QUANT: Calculate volatility adjustment factor
        """
        try:
            if price_data and len(price_data) >= self.volatility_lookback:
                # Calculate realized volatility from price data
                returns = np.diff(np.log(price_data))
                realized_vol = np.std(returns) * np.sqrt(252)  # Annualized
            else:
                # Use symbol-specific performance history
                if symbol not in self.performance_history or len(self.performance_history[symbol]) < 5:
                    return 1.0  # No adjustment if insufficient data
                
                returns = [t['pnl_pct'] / 100 for t in self.performance_history[symbol][-self.volatility_lookback:]]
                realized_vol = np.std(returns) * np.sqrt(252)  # Annualized
            
            # Adjust position size based on volatility
            vol_adjustment = min(self.volatility_target / max(realized_vol, 0.001), 2.0)  # Cap at 2x
            vol_adjustment = max(vol_adjustment, 0.1)  # Floor at 0.1x
            
            return vol_adjustment
            
        except Exception as e:
            self.logger.warning(f"Volatility adjustment calculation failed for {symbol}: {e}")
            return 1.0
    
    def calculate_sharpe_adjustment(self, symbol: str) -> float:
        """
        PROF_QUANT: Adjust position size based on Sharpe ratio performance
        """
        try:
            if symbol not in self.performance_history or len(self.performance_history[symbol]) < 10:
                return 1.0  # No adjustment
            
            trades = self.performance_history[symbol][-30:]  # Last 30 trades
            returns = [t['pnl_pct'] / 100 for t in trades]
            
            if not returns or len(returns) < 5:
                return 1.0
            
            # Calculate Sharpe ratio
            mean_return = np.mean(returns)
            std_return = np.std(returns)
            
            if std_return == 0:
                return 1.0
            
            daily_rf_rate = self.risk_free_rate / 252
            sharpe_ratio = (mean_return - daily_rf_rate) / std_return
            
            # Convert Sharpe to adjustment factor
            # Higher Sharpe = larger positions (up to 1.5x), Lower Sharpe = smaller positions (down to 0.5x)
            if sharpe_ratio > 2.0:
                adjustment = 1.5
            elif sharpe_ratio > 1.0:
                adjustment = 1.0 + (sharpe_ratio - 1.0) * 0.5
            elif sharpe_ratio > 0:
                adjustment = 0.7 + sharpe_ratio * 0.3
            else:
                adjustment = 0.5  # Poor performance = smaller positions
            
            return adjustment
            
        except Exception as e:
            self.logger.warning(f"Sharpe adjustment calculation failed for {symbol}: {e}")
            return 1.0
    
    def assess_risk_level(self, kelly_fraction: float, volatility_adj: float, sharpe_adj: float) -> str:
        """
        TRADER_PSYCH: Assess psychological risk level for position
        """
        # Combine factors to assess overall risk
        combined_risk = kelly_fraction * volatility_adj * sharpe_adj
        
        if combined_risk >= 0.08:
            return "EXTREME"
        elif combined_risk >= 0.06:
            return "HIGH"
        elif combined_risk >= 0.03:
            return "MODERATE"
        else:
            return "LOW"
    
    def calculate_position_size(self, symbol: str, current_price: float, 
                              confidence: float = 1.0, 
                              price_data: Optional[List[float]] = None,
                              regime: Optional[str] = None) -> PositionSizeResult:
        """
        MENTOR_BK: Main position sizing logic combining all factors
        TRADER_PSYCH: Apply psychological risk controls
        """
        try:
            # Calculate Kelly fraction
            kelly_fraction, kelly_data = self.calculate_kelly_fraction(symbol)
            
            if kelly_fraction == 0.0:
                return PositionSizeResult(
                    symbol=symbol,
                    base_kelly_fraction=0.0,
                    adjusted_kelly_fraction=0.0,
                    volatility_adjustment=1.0,
                    final_position_size=0.0,
                    max_position_limit=self.max_position_pct,
                    recommended_units=0,
                    risk_level="NONE",
                    reasoning=kelly_data.get('error', 'No Kelly calculation possible'),
                    confidence=0.0,
                    sharpe_adjustment=1.0
                )
            
            # Calculate adjustments
            volatility_adjustment = self.calculate_volatility_adjustment(symbol, price_data)
            sharpe_adjustment = self.calculate_sharpe_adjustment(symbol)
            
            # Apply regime adjustment
            regime_adjustment = 1.0
            if regime == 'SIDEWAYS':
                regime_adjustment = 0.7  # Smaller positions in ranging markets
            elif regime == 'BEARISH':
                regime_adjustment = 0.8  # Smaller positions in bear markets
            # BULLISH keeps 1.0 (no adjustment)
            
            # Combine all adjustments
            adjusted_kelly = kelly_fraction * volatility_adjustment * sharpe_adjustment * regime_adjustment * confidence
            
            # Apply position limits
            final_position_size = min(adjusted_kelly, self.max_position_pct)
            final_position_size = max(final_position_size, 0.0)
            
            # Calculate recommended units
            position_value = self.account_balance * final_position_size
            recommended_units = int(position_value / current_price) if current_price > 0 else 0
            
            # Assess risk level
            risk_level = self.assess_risk_level(kelly_fraction, volatility_adjustment, sharpe_adjustment)
            
            # Generate reasoning
            reasoning_parts = []
            reasoning_parts.append(f"Kelly: {kelly_fraction:.3f}")
            reasoning_parts.append(f"Vol adj: {volatility_adjustment:.2f}")
            reasoning_parts.append(f"Sharpe adj: {sharpe_adjustment:.2f}")
            reasoning_parts.append(f"Regime adj: {regime_adjustment:.2f}")
            if confidence != 1.0:
                reasoning_parts.append(f"Confidence: {confidence:.2f}")
            
            reasoning = " | ".join(reasoning_parts)
            
            if 'trades_analyzed' in kelly_data:
                reasoning += f" | {kelly_data['trades_analyzed']} trades analyzed"
            
            return PositionSizeResult(
                symbol=symbol,
                base_kelly_fraction=kelly_fraction,
                adjusted_kelly_fraction=adjusted_kelly,
                volatility_adjustment=volatility_adjustment,
                final_position_size=final_position_size,
                max_position_limit=self.max_position_pct,
                recommended_units=recommended_units,
                risk_level=risk_level,
                reasoning=reasoning,
                confidence=confidence,
                sharpe_adjustment=sharpe_adjustment
            )
            
        except Exception as e:
            self.logger.error(f"Position size calculation failed for {symbol}: {e}")
            return PositionSizeResult(
                symbol=symbol,
                base_kelly_fraction=0.0,
                adjusted_kelly_fraction=0.0,
                volatility_adjustment=1.0,
                final_position_size=0.0,
                max_position_limit=self.max_position_pct,
                recommended_units=0,
                risk_level="ERROR",
                reasoning=f"Calculation error: {str(e)}",
                confidence=0.0,
                sharpe_adjustment=1.0
            )
    
    def get_portfolio_risk_summary(self) -> Dict[str, Any]:
        """
        TRADER_PSYCH: Get portfolio-level risk assessment
        """
        try:
            with self.lock:
                total_symbols = len(self.performance_history)
                active_symbols = len([s for s, trades in self.performance_history.items() if trades])
                
                # Calculate overall statistics
                all_trades = []
                for symbol_trades in self.performance_history.values():
                    all_trades.extend(symbol_trades)
                
                if not all_trades:
                    return {
                        'total_symbols': total_symbols,
                        'active_symbols': active_symbols,
                        'overall_win_rate': 0.0,
                        'total_trades': 0,
                        'account_balance': self.account_balance,
                        'max_position_limit': self.max_position_pct
                    }
                
                wins = sum(1 for t in all_trades if t['outcome'] == 'WIN')
                overall_win_rate = wins / len(all_trades)
                
                # Recent performance (last 30 days)
                recent_cutoff = datetime.now(timezone.utc) - timedelta(days=30)
                recent_trades = [
                    t for t in all_trades 
                    if datetime.fromisoformat(t['timestamp'].replace('Z', '+00:00')) >= recent_cutoff
                ]
                
                recent_pnl = sum(t['pnl'] for t in recent_trades)
                
                return {
                    'total_symbols': total_symbols,
                    'active_symbols': active_symbols,
                    'overall_win_rate': overall_win_rate,
                    'total_trades': len(all_trades),
                    'recent_trades_30d': len(recent_trades),
                    'recent_pnl_30d': recent_pnl,
                    'account_balance': self.account_balance,
                    'max_position_limit': self.max_position_pct,
                    'kelly_multiplier': self.kelly_multiplier,
                    'volatility_target': self.volatility_target
                }
                
        except Exception as e:
            self.logger.error(f"Portfolio risk summary failed: {e}")
            return {'error': str(e)}
    
    def adjust_risk_parameters(self, drawdown_pct: float):
        """
        MENTOR_BK: Dynamically adjust risk parameters based on portfolio performance
        """
        try:
            with self.lock:
                if drawdown_pct > 0.10:  # 10%+ drawdown
                    # Reduce Kelly multiplier and position limits
                    self.kelly_multiplier = max(0.1, self.kelly_multiplier * 0.8)
                    self.max_position_pct = max(0.05, self.max_position_pct * 0.9)
                    self.logger.warning(f"High drawdown {drawdown_pct:.1%} - reducing risk parameters")
                elif drawdown_pct < 0.02:  # Low drawdown, good performance
                    # Gradually increase risk parameters (but stay conservative)
                    self.kelly_multiplier = min(0.5, self.kelly_multiplier * 1.05)
                    self.max_position_pct = min(0.15, self.max_position_pct * 1.02)
                    self.logger.info(f"Good performance - slightly increasing risk parameters")
                
        except Exception as e:
            self.logger.error(f"Risk parameter adjustment failed: {e}")

def get_dynamic_sizing(pin: int = 841921, account_balance: float = 100000.0) -> DynamicSizing:
    """Convenience function to get Dynamic Sizing instance"""
    return DynamicSizing(pin=pin, account_balance=account_balance)

# Example usage
if __name__ == "__main__":
    # Test Dynamic Sizing
    sizer = DynamicSizing(pin=841921, account_balance=50000.0)
    
    print("💰 DYNAMIC SIZING TEST RESULTS 💰")
    print("=" * 50)
    
    # Simulate some trade history
    test_symbol = "EUR_USD"
    
    # Add sample trade results
    sample_trades = [
        {'outcome': 'WIN', 'pnl': 150.0, 'pnl_pct': 0.30, 'position_size': 0.05},
        {'outcome': 'LOSS', 'pnl': -80.0, 'pnl_pct': -0.16, 'position_size': 0.05},
        {'outcome': 'WIN', 'pnl': 120.0, 'pnl_pct': 0.24, 'position_size': 0.05},
        {'outcome': 'WIN', 'pnl': 200.0, 'pnl_pct': 0.40, 'position_size': 0.05},
        {'outcome': 'LOSS', 'pnl': -75.0, 'pnl_pct': -0.15, 'position_size': 0.05},
        {'outcome': 'WIN', 'pnl': 180.0, 'pnl_pct': 0.36, 'position_size': 0.05},
        {'outcome': 'LOSS', 'pnl': -90.0, 'pnl_pct': -0.18, 'position_size': 0.05},
        {'outcome': 'WIN', 'pnl': 160.0, 'pnl_pct': 0.32, 'position_size': 0.05},
        {'outcome': 'WIN', 'pnl': 140.0, 'pnl_pct': 0.28, 'position_size': 0.05},
        {'outcome': 'WIN', 'pnl': 110.0, 'pnl_pct': 0.22, 'position_size': 0.05},
        {'outcome': 'LOSS', 'pnl': -85.0, 'pnl_pct': -0.17, 'position_size': 0.05},
        {'outcome': 'WIN', 'pnl': 170.0, 'pnl_pct': 0.34, 'position_size': 0.05}
    ]
    
    for trade in sample_trades:
        sizer.record_trade_result(test_symbol, trade)
    
    print(f"Recorded {len(sample_trades)} sample trades for {test_symbol}")
    
    # Test position sizing
    current_price = 1.1000
    position_result = sizer.calculate_position_size(
        symbol=test_symbol,
        current_price=current_price,
        confidence=0.75,
        regime='BULLISH'
    )
    
    print(f"\nPosition Sizing Results for {test_symbol}:")
    print(f"Kelly Fraction: {position_result.base_kelly_fraction:.4f}")
    print(f"Adjusted Fraction: {position_result.adjusted_kelly_fraction:.4f}")
    print(f"Final Position Size: {position_result.final_position_size:.2%}")
    print(f"Recommended Units: {position_result.recommended_units:,}")
    print(f"Risk Level: {position_result.risk_level}")
    print(f"Reasoning: {position_result.reasoning}")
    
    # Test portfolio summary
    portfolio_summary = sizer.get_portfolio_risk_summary()
    print(f"\nPortfolio Summary:")
    print(f"Win Rate: {portfolio_summary['overall_win_rate']:.1%}")
    print(f"Total Trades: {portfolio_summary['total_trades']}")
    print(f"Account Balance: ${portfolio_summary['account_balance']:,.2f}")
    
    print("\n✅ Dynamic Sizing operational")

def get_kelly_sizer(pin: int = 841921) -> DynamicSizing:
    """Convenience function to get Kelly Sizer instance"""
    return DynamicSizing(pin=pin)