#!/usr/bin/env python3
"""
CONSOLIDATED RISK MANAGEMENT - RICK Phoenix System
===================================================
Combines risk modules from:
- DynamicSizing (Kelly Criterion)
- CorrelationMonitor (Portfolio tracking)
- SessionBreaker (-5% halt)
- QuantHedgeRules (Multi-condition analysis)

PIN: 841921 | Charter Compliant
"""

import numpy as np
import threading
import logging
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timezone, timedelta
from enum import Enum
import json
import os

logger = logging.getLogger(__name__)

# =============================================================================
# ENUMS AND DATA CLASSES
# =============================================================================

class RiskLevel(Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    EXTREME = "EXTREME"
    CRITICAL = "CRITICAL"

class HedgeAction(Enum):
    """Recommended hedge actions based on market conditions"""
    FULL_LONG = "full_long"
    MODERATE_LONG = "moderate_long"
    REDUCE_EXPOSURE = "reduce_exposure"
    CLOSE_ALL = "close_all"
    HEDGE_SHORT = "hedge_short"
    PAUSE_TRADING = "pause_trading"
    WAIT_FOR_CLARITY = "wait_for_clarity"

@dataclass
class PositionSizeResult:
    """Position sizing result from Kelly calculation"""
    symbol: str
    base_kelly_fraction: float
    adjusted_kelly_fraction: float
    volatility_adjustment: float
    final_position_size: float
    max_position_limit: float
    recommended_units: int
    risk_level: str
    reasoning: str
    confidence: float
    sharpe_adjustment: float

@dataclass
class HedgeCondition:
    """Individual condition evaluation for hedge decision"""
    condition_name: str
    current_value: float
    threshold: float
    severity: str  # green, yellow, red
    recommendation: str
    details: Dict = None

@dataclass
class QuantHedgeAnalysis:
    """Complete multi-condition hedge analysis"""
    timestamp: datetime
    regime: str
    volatility_level: str
    volatility_value: float
    conditions: List[HedgeCondition]
    severity_score: float
    primary_action: str
    secondary_actions: List[str]
    position_size_multiplier: float
    risk_level: str
    confidence: float
    summary: str
    detailed_analysis: Dict

# =============================================================================
# KELLY CRITERION POSITION SIZING (from risk/dynamic_sizing.py)
# =============================================================================

class DynamicSizing:
    """
    Advanced Kelly Criterion position sizing with volatility adjustment
    
    Features:
    - Kelly optimal fraction calculation
    - Volatility-based position adjustment
    - Sharpe ratio scaling
    - Maximum position limits (10% capital)
    - Conservative quarter-Kelly by default
    """
    
    def __init__(self, pin: int = 841921, account_balance: float = 100000.0):
        if pin != 841921:
            raise ValueError("Invalid PIN for Dynamic Sizing")
        
        self.pin_verified = True
        self.account_balance = account_balance
        self.max_position_pct = 0.10  # 10% maximum
        self.min_position_pct = 0.001  # 0.1% minimum
        self.kelly_multiplier = 0.25  # Quarter Kelly (conservative)
        self.volatility_lookback = 20
        
        # Risk parameters
        self.risk_free_rate = 0.02  # 2% annual
        self.max_leverage = 1.0
        self.emergency_stop_drawdown = 0.15  # 15% max drawdown
        
        # Performance tracking
        self.performance_history: Dict[str, List[Dict]] = {}
        self.position_history: List[Dict] = []
        self.lock = threading.Lock()
        
        # Volatility adjustment
        self.volatility_target = 0.02  # 2% daily vol target
        self.volatility_adjustment_factor = 0.5
        
        self.logger = logging.getLogger(f"DynamicSizing_{pin}")
    
    def update_account_balance(self, new_balance: float):
        """Update account balance for position calculations"""
        with self.lock:
            self.account_balance = new_balance
    
    def record_trade_result(self, symbol: str, trade_data: Dict[str, Any]):
        """Record trade results for Kelly calculation"""
        try:
            with self.lock:
                if symbol not in self.performance_history:
                    self.performance_history[symbol] = []
                
                trade_record = {
                    'timestamp': trade_data.get('timestamp', datetime.now(timezone.utc).isoformat()),
                    'outcome': trade_data.get('outcome', 'UNKNOWN'),
                    'pnl': trade_data.get('pnl', 0.0),
                    'pnl_pct': trade_data.get('pnl_pct', 0.0),
                    'position_size': trade_data.get('position_size', 0.0),
                    'duration_minutes': trade_data.get('duration_minutes', 0),
                }
                
                self.performance_history[symbol].append(trade_record)
                
                # Keep last 100 trades
                if len(self.performance_history[symbol]) > 100:
                    self.performance_history[symbol] = self.performance_history[symbol][-100:]
                
        except Exception as e:
            self.logger.error(f"Failed to record trade: {e}")
    
    def calculate_kelly_fraction(self, symbol: str, min_trades: int = 10) -> Tuple[float, Dict]:
        """
        Calculate Kelly optimal fraction
        
        Formula: f = (bp - q) / b
        where:
        - f = fraction to wager
        - b = odds ratio (avg_win / avg_loss)
        - p = win probability
        - q = loss probability (1-p)
        """
        try:
            if symbol not in self.performance_history:
                return 0.0, {'error': 'No history for symbol'}
            
            trades = self.performance_history[symbol]
            if len(trades) < min_trades:
                return 0.0, {'error': f'Insufficient trades: {len(trades)} < {min_trades}'}
            
            wins = [t for t in trades if t['outcome'] == 'WIN']
            losses = [t for t in trades if t['outcome'] == 'LOSS']
            
            if not wins or not losses:
                return 0.0, {'error': 'Need both wins and losses'}
            
            win_rate = len(wins) / len(trades)
            loss_rate = 1 - win_rate
            
            avg_win = np.mean([t['pnl_pct'] for t in wins])
            avg_loss = abs(np.mean([t['pnl_pct'] for t in losses]))
            
            if avg_loss == 0:
                return 0.0, {'error': 'Average loss is zero'}
            
            odds_ratio = avg_win / avg_loss
            kelly_fraction = (odds_ratio * win_rate - loss_rate) / odds_ratio
            kelly_fraction = max(0.0, kelly_fraction)
            
            # Apply conservative multiplier
            conservative_kelly = kelly_fraction * self.kelly_multiplier
            
            return conservative_kelly, {
                'trades_analyzed': len(trades),
                'win_rate': win_rate,
                'avg_win_pct': avg_win,
                'avg_loss_pct': avg_loss,
                'odds_ratio': odds_ratio,
                'raw_kelly': kelly_fraction,
                'conservative_kelly': conservative_kelly
            }
            
        except Exception as e:
            return 0.0, {'error': str(e)}
    
    def calculate_volatility_adjustment(self, symbol: str, price_data: Optional[List[float]] = None) -> float:
        """Calculate volatility adjustment factor"""
        try:
            if price_data and len(price_data) >= self.volatility_lookback:
                returns = np.diff(np.log(price_data))
                realized_vol = np.std(returns) * np.sqrt(252)
            elif symbol in self.performance_history and len(self.performance_history[symbol]) >= 5:
                returns = [t['pnl_pct'] / 100 for t in self.performance_history[symbol][-self.volatility_lookback:]]
                realized_vol = np.std(returns) * np.sqrt(252)
            else:
                return 1.0
            
            vol_adjustment = min(self.volatility_target / max(realized_vol, 0.001), 2.0)
            vol_adjustment = max(vol_adjustment, 0.1)
            
            return vol_adjustment
        except Exception:
            return 1.0
    
    def calculate_sharpe_adjustment(self, symbol: str) -> float:
        """Adjust position size based on Sharpe ratio"""
        try:
            if symbol not in self.performance_history or len(self.performance_history[symbol]) < 10:
                return 1.0
            
            trades = self.performance_history[symbol][-30:]
            returns = [t['pnl_pct'] / 100 for t in trades]
            
            if len(returns) < 5:
                return 1.0
            
            mean_return = np.mean(returns)
            std_return = np.std(returns)
            
            if std_return == 0:
                return 1.0
            
            daily_rf_rate = self.risk_free_rate / 252
            sharpe_ratio = (mean_return - daily_rf_rate) / std_return
            
            # Convert Sharpe to adjustment
            if sharpe_ratio > 2.0:
                return 1.5
            elif sharpe_ratio > 1.0:
                return 1.0 + (sharpe_ratio - 1.0) * 0.5
            elif sharpe_ratio > 0:
                return 0.7 + sharpe_ratio * 0.3
            else:
                return 0.5
                
        except Exception:
            return 1.0
    
    def calculate_position_size(self, symbol: str, current_price: float,
                                confidence: float = 1.0,
                                price_data: Optional[List[float]] = None,
                                regime: Optional[str] = None) -> PositionSizeResult:
        """Main position sizing calculation combining all factors"""
        try:
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
                    reasoning=kelly_data.get('error', 'No Kelly calculation'),
                    confidence=0.0,
                    sharpe_adjustment=1.0
                )
            
            vol_adj = self.calculate_volatility_adjustment(symbol, price_data)
            sharpe_adj = self.calculate_sharpe_adjustment(symbol)
            
            # Regime adjustment
            regime_adj = 1.0
            if regime == 'SIDEWAYS':
                regime_adj = 0.6
            elif regime == 'CRISIS':
                regime_adj = 0.2
            elif regime in ['BULL_STRONG', 'BEAR_STRONG']:
                regime_adj = 1.2
            
            # Final position size
            adjusted_kelly = kelly_fraction * vol_adj * sharpe_adj * confidence * regime_adj
            final_size = min(adjusted_kelly, self.max_position_pct)
            final_size = max(final_size, self.min_position_pct)
            
            # Calculate units
            position_value = self.account_balance * final_size
            units = int(position_value / current_price) if current_price > 0 else 0
            
            # Assess risk level
            combined_risk = kelly_fraction * vol_adj * sharpe_adj
            if combined_risk >= 0.08:
                risk_level = "EXTREME"
            elif combined_risk >= 0.06:
                risk_level = "HIGH"
            elif combined_risk >= 0.03:
                risk_level = "MODERATE"
            else:
                risk_level = "LOW"
            
            return PositionSizeResult(
                symbol=symbol,
                base_kelly_fraction=kelly_fraction,
                adjusted_kelly_fraction=adjusted_kelly,
                volatility_adjustment=vol_adj,
                final_position_size=final_size,
                max_position_limit=self.max_position_pct,
                recommended_units=units,
                risk_level=risk_level,
                reasoning=f"Kelly={kelly_fraction:.3f}, Vol={vol_adj:.2f}, Sharpe={sharpe_adj:.2f}",
                confidence=confidence,
                sharpe_adjustment=sharpe_adj
            )
            
        except Exception as e:
            self.logger.error(f"Position size calculation failed: {e}")
            return PositionSizeResult(
                symbol=symbol, base_kelly_fraction=0.0, adjusted_kelly_fraction=0.0,
                volatility_adjustment=1.0, final_position_size=0.0,
                max_position_limit=self.max_position_pct, recommended_units=0,
                risk_level="ERROR", reasoning=str(e), confidence=0.0, sharpe_adjustment=1.0
            )

# =============================================================================
# CORRELATION MONITOR (from PhoenixV2/gate/correlation_monitor.py)
# =============================================================================

class CorrelationMonitor:
    """
    Portfolio correlation tracking to prevent USD concentration risk
    
    Features:
    - Tracks all open positions by direction
    - Calculates USD exposure
    - Warns when correlation exceeds 70%
    """
    
    # Correlation matrix for common FX pairs
    CORRELATION_MATRIX = {
        'EUR_USD': {'USD': -1.0, 'EUR': 1.0},
        'GBP_USD': {'USD': -1.0, 'GBP': 1.0},
        'USD_JPY': {'USD': 1.0, 'JPY': -1.0},
        'USD_CHF': {'USD': 1.0, 'CHF': -1.0},
        'AUD_USD': {'USD': -1.0, 'AUD': 1.0},
        'USD_CAD': {'USD': 1.0, 'CAD': -1.0},
        'NZD_USD': {'USD': -1.0, 'NZD': 1.0},
        'EUR_GBP': {'EUR': 1.0, 'GBP': -1.0},
        'EUR_JPY': {'EUR': 1.0, 'JPY': -1.0},
        'GBP_JPY': {'GBP': 1.0, 'JPY': -1.0},
    }
    
    def __init__(self, pin: int = 841921, max_correlation: float = 0.70):
        if pin != 841921:
            raise PermissionError("Invalid PIN")
        self.max_correlation = max_correlation
        self.positions: List[Dict] = []
        self.logger = logging.getLogger("CorrelationMonitor")
    
    def add_position(self, symbol: str, direction: str, size: float):
        """Add a position to track"""
        self.positions.append({
            'symbol': symbol,
            'direction': direction.upper(),  # Normalize to BUY/SELL
            'size': size
        })
    
    def remove_position(self, symbol: str):
        """Remove a position"""
        self.positions = [p for p in self.positions if p['symbol'] != symbol]
    
    def clear_positions(self):
        """Clear all tracked positions"""
        self.positions = []
    
    def calculate_currency_exposure(self) -> Dict[str, float]:
        """Calculate net exposure to each currency"""
        exposure = {}
        
        for pos in self.positions:
            symbol = pos['symbol']
            direction = pos['direction']
            size = pos['size']
            
            # Get currency weights
            weights = self.CORRELATION_MATRIX.get(symbol, {})
            
            for currency, weight in weights.items():
                # BUY = positive exposure to base, negative to quote
                # SELL = reverse
                multiplier = 1.0 if direction == 'BUY' else -1.0
                exposure[currency] = exposure.get(currency, 0) + (weight * multiplier * size)
        
        return exposure
    
    def calculate_usd_correlation(self) -> float:
        """Calculate USD concentration as percentage"""
        exposure = self.calculate_currency_exposure()
        
        if not exposure:
            return 0.0
        
        total_exposure = sum(abs(v) for v in exposure.values())
        usd_exposure = abs(exposure.get('USD', 0))
        
        if total_exposure == 0:
            return 0.0
        
        return usd_exposure / total_exposure
    
    def check_new_position(self, symbol: str, direction: str, size: float) -> Tuple[bool, str]:
        """
        Check if adding a new position would exceed correlation limits
        
        Returns:
            (allowed: bool, reason: str)
        """
        # Temporarily add position
        temp_positions = self.positions.copy()
        self.positions.append({
            'symbol': symbol,
            'direction': direction.upper(),
            'size': size
        })
        
        usd_corr = self.calculate_usd_correlation()
        
        # Restore original positions
        self.positions = temp_positions
        
        if usd_corr > self.max_correlation:
            return False, f"USD correlation {usd_corr:.1%} would exceed max {self.max_correlation:.1%}"
        
        return True, f"Correlation OK: {usd_corr:.1%}"

# =============================================================================
# SESSION BREAKER (from risk/session_breaker.py)
# =============================================================================

class SessionBreaker:
    """
    Daily loss limit enforcement (-5% session halt)
    
    Features:
    - Tracks daily P&L
    - Halts all trading if daily loss exceeds threshold
    - Automatic reset at session start
    """
    
    def __init__(self, pin: int = 841921, max_daily_loss_pct: float = 0.05, account_balance: float = 100000.0):
        if pin != 841921:
            raise PermissionError("Invalid PIN")
        
        self.max_daily_loss_pct = max_daily_loss_pct
        self.account_balance = account_balance
        self.session_start_balance = account_balance
        self.daily_pnl = 0.0
        self.is_halted = False
        self.halt_reason = ""
        self.session_date = datetime.now(timezone.utc).date()
        self.trades_today = 0
        self.logger = logging.getLogger("SessionBreaker")
    
    def start_new_session(self, starting_balance: float):
        """Start a new trading session"""
        self.session_start_balance = starting_balance
        self.account_balance = starting_balance
        self.daily_pnl = 0.0
        self.is_halted = False
        self.halt_reason = ""
        self.session_date = datetime.now(timezone.utc).date()
        self.trades_today = 0
        self.logger.info(f"New session started with balance ${starting_balance:,.2f}")
    
    def check_session_date(self):
        """Auto-reset if new day"""
        today = datetime.now(timezone.utc).date()
        if today != self.session_date:
            self.start_new_session(self.account_balance)
    
    def record_pnl(self, pnl: float):
        """Record a trade's P&L"""
        self.check_session_date()
        
        self.daily_pnl += pnl
        self.account_balance += pnl
        self.trades_today += 1
        
        # Check for breach
        loss_pct = -self.daily_pnl / self.session_start_balance if self.session_start_balance > 0 else 0
        
        if loss_pct >= self.max_daily_loss_pct:
            self.is_halted = True
            self.halt_reason = f"Daily loss {loss_pct:.1%} >= {self.max_daily_loss_pct:.1%} limit"
            self.logger.warning(f"SESSION HALTED: {self.halt_reason}")
    
    def can_trade(self) -> Tuple[bool, str]:
        """Check if trading is allowed"""
        self.check_session_date()
        
        if self.is_halted:
            return False, self.halt_reason
        
        return True, f"Trading allowed. Daily P&L: ${self.daily_pnl:,.2f}"
    
    def get_remaining_risk(self) -> float:
        """Get remaining risk budget for the day"""
        max_loss = self.session_start_balance * self.max_daily_loss_pct
        remaining = max_loss + self.daily_pnl  # daily_pnl is negative for losses
        return max(0, remaining)
    
    def get_status(self) -> Dict:
        """Get current session status"""
        self.check_session_date()
        
        return {
            'session_date': str(self.session_date),
            'session_start_balance': self.session_start_balance,
            'current_balance': self.account_balance,
            'daily_pnl': self.daily_pnl,
            'daily_pnl_pct': self.daily_pnl / self.session_start_balance if self.session_start_balance > 0 else 0,
            'is_halted': self.is_halted,
            'halt_reason': self.halt_reason,
            'trades_today': self.trades_today,
            'remaining_risk': self.get_remaining_risk()
        }

# =============================================================================
# QUANT HEDGE RULES (from hive/quant_hedge_rules.py)
# =============================================================================

class QuantHedgeRules:
    """
    Multi-condition analysis engine for hedge decisions
    
    5 Weighted Conditions:
    1. Volatility (30%)
    2. Trend Strength (25%)
    3. Correlation Risk (20%)
    4. Volume Confirmation (15%)
    5. Margin Utilization (10%)
    
    7 Hedge Actions:
    - FULL_LONG, MODERATE_LONG, REDUCE_EXPOSURE
    - CLOSE_ALL, HEDGE_SHORT, PAUSE_TRADING, WAIT_FOR_CLARITY
    """
    
    def __init__(self, pin: int = 841921):
        if pin != 841921:
            raise PermissionError("Invalid PIN")
        
        self.logger = logging.getLogger("QuantHedgeRules")
        
        # Volatility thresholds
        self.volatility_thresholds = {
            'low': 0.015,      # <1.5%
            'moderate': 0.030, # 1.5-3.0%
            'high': 0.050,     # 3.0-5.0%
            'extreme': 0.075   # >5%
        }
        
        # Condition weights (sum = 1.0)
        self.condition_weights = {
            'volatility': 0.30,
            'trend_strength': 0.25,
            'correlation': 0.20,
            'volume': 0.15,
            'margin_utilization': 0.10
        }
    
    def get_hedge_params(self, regime: str, volatility: float) -> Dict:
        """Get hedge parameters for current market state"""
        params = {
            "size_multiplier": 1.0,
            "hedge_ratio": 0.0,
            "stop_tightener": 1.0,
            "mode": "STANDARD"
        }
        
        if regime == "BULL_STRONG":
            params["size_multiplier"] = 1.2
            params["stop_tightener"] = 1.2
            params["mode"] = "ATTACK_BULL"
        elif regime == "BEAR_STRONG":
            params["size_multiplier"] = 1.2
            params["stop_tightener"] = 1.0
            params["mode"] = "ATTACK_BEAR"
        elif regime == "SIDEWAYS":
            params["size_multiplier"] = 0.6
            params["stop_tightener"] = 0.5
            params["mode"] = "DEFENSE_CHOP"
        elif regime == "CRISIS" or volatility > 0.02:
            params["size_multiplier"] = 0.2
            params["stop_tightener"] = 0.25
            params["mode"] = "BUNKER_PROTOCOL"
        
        return params
    
    def classify_volatility(self, volatility: float) -> str:
        """Classify volatility level"""
        if volatility < self.volatility_thresholds['low']:
            return 'LOW'
        elif volatility < self.volatility_thresholds['moderate']:
            return 'MODERATE'
        elif volatility < self.volatility_thresholds['high']:
            return 'HIGH'
        else:
            return 'EXTREME'
    
    def analyze_conditions(self, volatility: float, trend_strength: float,
                           correlation: float, volume_ratio: float,
                           margin_utilization: float) -> List[HedgeCondition]:
        """Analyze all 5 conditions and return severity assessments"""
        conditions = []
        
        # 1. Volatility assessment
        vol_level = self.classify_volatility(volatility)
        vol_severity = 'green' if vol_level == 'LOW' else 'yellow' if vol_level in ['MODERATE', 'HIGH'] else 'red'
        conditions.append(HedgeCondition(
            condition_name='volatility',
            current_value=volatility,
            threshold=self.volatility_thresholds['moderate'],
            severity=vol_severity,
            recommendation='REDUCE_SIZE' if vol_severity == 'red' else 'NORMAL'
        ))
        
        # 2. Trend strength assessment (ADX-like)
        trend_severity = 'green' if trend_strength > 40 else 'yellow' if trend_strength > 20 else 'red'
        conditions.append(HedgeCondition(
            condition_name='trend_strength',
            current_value=trend_strength,
            threshold=20.0,
            severity=trend_severity,
            recommendation='FOLLOW_TREND' if trend_severity == 'green' else 'WAIT'
        ))
        
        # 3. Correlation assessment
        corr_severity = 'green' if correlation < 0.4 else 'yellow' if correlation < 0.7 else 'red'
        conditions.append(HedgeCondition(
            condition_name='correlation',
            current_value=correlation,
            threshold=0.7,
            severity=corr_severity,
            recommendation='HEDGE' if corr_severity == 'red' else 'NORMAL'
        ))
        
        # 4. Volume confirmation
        vol_severity = 'green' if volume_ratio > 1.2 else 'yellow' if volume_ratio > 0.8 else 'red'
        conditions.append(HedgeCondition(
            condition_name='volume',
            current_value=volume_ratio,
            threshold=1.0,
            severity=vol_severity,
            recommendation='CONFIRM' if vol_severity == 'green' else 'WAIT'
        ))
        
        # 5. Margin utilization
        margin_severity = 'green' if margin_utilization < 0.2 else 'yellow' if margin_utilization < 0.35 else 'red'
        conditions.append(HedgeCondition(
            condition_name='margin_utilization',
            current_value=margin_utilization,
            threshold=0.35,
            severity=margin_severity,
            recommendation='REDUCE_EXPOSURE' if margin_severity == 'red' else 'NORMAL'
        ))
        
        return conditions
    
    def determine_action(self, conditions: List[HedgeCondition], regime: str) -> Tuple[str, List[str]]:
        """Determine primary and secondary hedge actions"""
        red_count = sum(1 for c in conditions if c.severity == 'red')
        yellow_count = sum(1 for c in conditions if c.severity == 'yellow')
        
        # Critical conditions
        vol_cond = next((c for c in conditions if c.condition_name == 'volatility'), None)
        corr_cond = next((c for c in conditions if c.condition_name == 'correlation'), None)
        margin_cond = next((c for c in conditions if c.condition_name == 'margin_utilization'), None)
        
        secondary = []
        
        # CLOSE_ALL: Multiple red conditions
        if red_count >= 3 or (vol_cond and vol_cond.severity == 'red' and corr_cond and corr_cond.severity == 'red'):
            return HedgeAction.CLOSE_ALL.value, ['REDUCE_EXPOSURE']
        
        # REDUCE_EXPOSURE: Margin too high
        if margin_cond and margin_cond.severity == 'red':
            secondary.append('HEDGE_SHORT')
            return HedgeAction.REDUCE_EXPOSURE.value, secondary
        
        # PAUSE_TRADING: Too much uncertainty
        if red_count >= 2 or (yellow_count >= 3 and red_count >= 1):
            return HedgeAction.PAUSE_TRADING.value, ['WAIT_FOR_CLARITY']
        
        # HEDGE_SHORT: High correlation
        if corr_cond and corr_cond.severity == 'red':
            return HedgeAction.HEDGE_SHORT.value, ['REDUCE_EXPOSURE']
        
        # WAIT_FOR_CLARITY: Mixed signals
        if yellow_count >= 3:
            return HedgeAction.WAIT_FOR_CLARITY.value, []
        
        # FULL_LONG or MODERATE_LONG based on regime
        if regime in ['BULL', 'BULL_STRONG'] and red_count == 0:
            if yellow_count == 0:
                return HedgeAction.FULL_LONG.value, []
            else:
                return HedgeAction.MODERATE_LONG.value, ['WATCH_VOLATILITY']
        
        return HedgeAction.MODERATE_LONG.value, []
    
    def analyze(self, volatility: float, trend_strength: float, correlation: float,
                volume_ratio: float, margin_utilization: float, regime: str) -> QuantHedgeAnalysis:
        """Full multi-condition analysis"""
        conditions = self.analyze_conditions(
            volatility, trend_strength, correlation, volume_ratio, margin_utilization
        )
        
        # Calculate severity score (0-100)
        severity_weights = {'green': 0, 'yellow': 1, 'red': 2}
        total_severity = sum(severity_weights.get(c.severity, 0) * self.condition_weights.get(c.condition_name, 0.1)
                            for c in conditions)
        severity_score = total_severity * 50  # Scale to 0-100
        
        # Determine action
        primary_action, secondary_actions = self.determine_action(conditions, regime)
        
        # Position size multiplier
        if primary_action == HedgeAction.CLOSE_ALL.value:
            size_mult = 0.0
        elif primary_action == HedgeAction.REDUCE_EXPOSURE.value:
            size_mult = 0.5
        elif primary_action == HedgeAction.PAUSE_TRADING.value:
            size_mult = 0.0
        elif primary_action == HedgeAction.FULL_LONG.value:
            size_mult = 1.0
        else:
            size_mult = 0.75
        
        # Risk level
        if severity_score > 75:
            risk_level = "CRITICAL"
        elif severity_score > 50:
            risk_level = "ELEVATED"
        elif severity_score > 25:
            risk_level = "MODERATE"
        else:
            risk_level = "SAFE"
        
        # Confidence in recommendation
        confidence = max(0.5, 1.0 - severity_score / 100)
        
        return QuantHedgeAnalysis(
            timestamp=datetime.now(timezone.utc),
            regime=regime,
            volatility_level=self.classify_volatility(volatility),
            volatility_value=volatility,
            conditions=conditions,
            severity_score=severity_score,
            primary_action=primary_action,
            secondary_actions=secondary_actions,
            position_size_multiplier=size_mult,
            risk_level=risk_level,
            confidence=confidence,
            summary=f"{primary_action} recommended ({risk_level} risk, {severity_score:.0f}/100 severity)",
            detailed_analysis={'regime': regime, 'conditions_count': len(conditions)}
        )

# =============================================================================
# UNIFIED RISK MANAGER
# =============================================================================

class UnifiedRiskManager:
    """
    Combined risk management interface
    Integrates all risk modules into single access point
    """
    
    def __init__(self, pin: int = 841921, account_balance: float = 100000.0):
        if pin != 841921:
            raise PermissionError("Invalid PIN")
        
        self.dynamic_sizing = DynamicSizing(pin, account_balance)
        self.correlation_monitor = CorrelationMonitor(pin)
        self.session_breaker = SessionBreaker(pin, account_balance=account_balance)
        self.quant_hedge = QuantHedgeRules(pin)
        
        self.logger = logging.getLogger("UnifiedRiskManager")
    
    def can_enter_trade(self, symbol: str, direction: str, size: float,
                        account: Dict, positions: List[Dict]) -> Tuple[bool, str]:
        """
        Check if a new trade is allowed
        
        Returns:
            (allowed: bool, reason: str)
        """
        # Check session breaker
        can_trade, reason = self.session_breaker.can_trade()
        if not can_trade:
            return False, f"Session halted: {reason}"
        
        # Check correlation
        allowed, corr_reason = self.correlation_monitor.check_new_position(symbol, direction, size)
        if not allowed:
            return False, f"Correlation limit: {corr_reason}"
        
        # Check margin utilization
        nav = float(account.get('nav', 0))
        margin_used = float(account.get('margin_used', 0))
        
        if nav > 0 and margin_used / nav > 0.35:
            return False, f"Margin utilization {margin_used/nav:.1%} exceeds 35%"
        
        # Check concurrent positions
        if len(positions) >= 3:
            return False, "Already at maximum concurrent positions (3)"
        
        return True, "All risk checks passed"
    
    def get_position_size(self, symbol: str, current_price: float,
                          confidence: float = 1.0,
                          price_data: Optional[List[float]] = None,
                          regime: str = "UNKNOWN") -> PositionSizeResult:
        """Get recommended position size"""
        return self.dynamic_sizing.calculate_position_size(
            symbol, current_price, confidence, price_data, regime
        )
    
    def get_hedge_recommendation(self, volatility: float, trend_strength: float,
                                  correlation: float, volume_ratio: float,
                                  margin_utilization: float, regime: str) -> QuantHedgeAnalysis:
        """Get hedge recommendation based on market conditions"""
        return self.quant_hedge.analyze(
            volatility, trend_strength, correlation, volume_ratio, margin_utilization, regime
        )
    
    def record_trade(self, symbol: str, trade_data: Dict):
        """Record a completed trade for analysis"""
        self.dynamic_sizing.record_trade_result(symbol, trade_data)
        if 'pnl' in trade_data:
            self.session_breaker.record_pnl(trade_data['pnl'])
    
    def update_positions(self, positions: List[Dict]):
        """Update correlation monitor with current positions"""
        self.correlation_monitor.clear_positions()
        for pos in positions:
            self.correlation_monitor.add_position(
                pos.get('symbol', 'UNKNOWN'),
                pos.get('direction', 'BUY'),
                pos.get('size', 1.0)
            )

# =============================================================================
# SELF TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("CONSOLIDATED RISK MANAGEMENT - Self Test")
    print("=" * 60)
    
    # Test Dynamic Sizing
    print("\n--- Dynamic Sizing Test ---")
    sizing = DynamicSizing(841921, 100000)
    
    # Add some trade history
    for i in range(15):
        sizing.record_trade_result("EUR_USD", {
            'outcome': 'WIN' if i % 3 != 0 else 'LOSS',
            'pnl': 100 if i % 3 != 0 else -80,
            'pnl_pct': 1.0 if i % 3 != 0 else -0.8
        })
    
    result = sizing.calculate_position_size("EUR_USD", 1.1000, confidence=0.8)
    print(f"Position size: {result.final_position_size:.2%} ({result.recommended_units} units)")
    print(f"Risk level: {result.risk_level}, Kelly: {result.base_kelly_fraction:.3f}")
    
    # Test Correlation Monitor
    print("\n--- Correlation Monitor Test ---")
    corr_mon = CorrelationMonitor(841921)
    corr_mon.add_position("EUR_USD", "BUY", 10000)
    corr_mon.add_position("GBP_USD", "BUY", 10000)
    
    allowed, reason = corr_mon.check_new_position("AUD_USD", "BUY", 10000)
    print(f"Add AUD_USD long: {'Allowed' if allowed else 'Blocked'} - {reason}")
    print(f"USD correlation: {corr_mon.calculate_usd_correlation():.1%}")
    
    # Test Session Breaker
    print("\n--- Session Breaker Test ---")
    breaker = SessionBreaker(841921, account_balance=100000)
    breaker.record_pnl(-2000)
    print(f"After -$2000: Can trade = {breaker.can_trade()[0]}")
    breaker.record_pnl(-3500)
    print(f"After -$3500 more: Can trade = {breaker.can_trade()[0]} ({breaker.halt_reason})")
    
    # Test Quant Hedge Rules
    print("\n--- Quant Hedge Rules Test ---")
    hedge = QuantHedgeRules(841921)
    analysis = hedge.analyze(
        volatility=0.025,
        trend_strength=35.0,
        correlation=0.5,
        volume_ratio=1.1,
        margin_utilization=0.25,
        regime="BULL"
    )
    print(f"Action: {analysis.primary_action}")
    print(f"Risk level: {analysis.risk_level}, Size multiplier: {analysis.position_size_multiplier}")
    
    print("\n" + "=" * 60)
    print("All risk management tests passed!")
