#!/usr/bin/env python3
"""
Enhanced RICK Stochastic Engine - Full Charter Compliance
Implements: $15K minimum notional, dynamic leverage, ATR-based stops, OCO orders, trailing stops
Extracted from: WSL Ubuntu /home/ing/RICK/RICK_LIVE_CLEAN (READ ONLY)
"""

import asyncio
import json
import time
import logging
import random
import numpy as np
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import os
from pathlib import Path

# Import authentic RICK Charter
from rick_charter import RickCharter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/enhanced_rick_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ATRData:
    """ATR calculation for dynamic stops"""
    period_14: float
    current_volatility: float
    spread_multiplier: float

@dataclass
class OCOOrder:
    """One-Cancels-Other order structure"""
    entry_price: float
    stop_loss: float
    take_profit: float
    trailing_stop: bool
    placement_latency_ms: float
    order_id: str

@dataclass
class EnhancedTradeResult:
    """Enhanced trade result with full charter compliance"""
    trade_id: str
    symbol: str
    side: str
    notional_usd: float
    leverage: float
    entry_price: float
    exit_price: float
    stop_loss: float
    take_profit: float
    atr_multiplier: float
    spread_cost: float
    pnl: float
    duration_seconds: int
    timestamp: datetime
    outcome: str
    confidence: float
    oco_latency_ms: float
    trailing_activated: bool

class ATRCalculator:
    """Authentic ATR calculation for dynamic stops (NO TALIB)"""

    def __init__(self):
        self.price_history = []
        self.atr_period = 14

    def add_price_data(self, high: float, low: float, close: float):
        """Add price data for ATR calculation"""
        self.price_history.append({'high': high, 'low': low, 'close': close})

        # Keep only last 20 periods for calculation
        if len(self.price_history) > 20:
            self.price_history = self.price_history[-20:]

    def calculate_atr(self) -> float:
        """Calculate ATR without TALIB - pure stochastic approach"""
        if len(self.price_history) < 2:
            return 0.001  # Default small ATR

        true_ranges = []
        for i in range(1, len(self.price_history)):
            current = self.price_history[i]
            previous = self.price_history[i-1]

            tr1 = current['high'] - current['low']
            tr2 = abs(current['high'] - previous['close'])
            tr3 = abs(current['low'] - previous['close'])

            true_ranges.append(max(tr1, tr2, tr3))

        # Simple average (stochastic approach vs exponential)
        periods_to_use = min(self.atr_period, len(true_ranges))
        if periods_to_use == 0:
            return 0.001

        return sum(true_ranges[-periods_to_use:]) / periods_to_use

class EnhancedStochasticEngine:
    """
    Enhanced RICK Engine with Full Charter Compliance
    - $15K minimum notional
    - Dynamic leverage based on volatility
    - ATR-based stop losses
    - OCO order simulation
    - Trailing stops
    - Spread/slippage gates
    """

    def __init__(self, pin: int):
        # PIN validation
        if not RickCharter.validate_pin(pin):
            raise PermissionError("Invalid PIN for enhanced RICK engine")

        self.PIN = pin
        self.start_time = datetime.now(timezone.utc)

        # Charter-compliant capital requirements
        self.starting_capital = 25000.0  # Above $15K minimum
        self.current_capital = self.starting_capital
        self.min_notional = RickCharter.MIN_NOTIONAL_USD  # $15,000

        # ATR calculator
        self.atr_calculator = ATRCalculator()
        self._initialize_price_history()

        # Performance tracking
        self.trades: List[EnhancedTradeResult] = []
        self.total_pnl = 0.0
        self.wins = 0
        self.losses = 0

        # Charter compliance tracking
        self.daily_trades = 0
        self.concurrent_positions = 0
        self.daily_pnl_pct = 0.0

        logger.info(f"Enhanced RICK Engine initialized - Charter compliant")
        logger.info(f"Starting capital: ${self.starting_capital:,.2f}")
        logger.info(f"Min notional: ${self.min_notional:,.2f}")

    def _initialize_price_history(self):
        """Initialize with stochastic price history for ATR calculation"""
        base_price = 1.1000
        for i in range(20):
            # Generate stochastic OHLC data
            volatility = random.uniform(0.0020, 0.0080)  # 20-80 pips volatility

            high = base_price + random.uniform(0, volatility)
            low = base_price - random.uniform(0, volatility)
            close = base_price + random.uniform(-volatility/2, volatility/2)

            self.atr_calculator.add_price_data(high, low, close)
            base_price = close  # Walk the price

    def _calculate_dynamic_leverage(self, atr: float, account_balance: float) -> float:
        """Calculate dynamic leverage based on volatility and account size"""
        # Higher volatility = lower leverage (risk management)
        base_leverage = 10.0

        # ATR-based adjustment
        if atr > 0.0060:  # High volatility (60+ pips)
            leverage_multiplier = 0.5
        elif atr > 0.0040:  # Medium volatility (40-60 pips)
            leverage_multiplier = 0.75
        else:  # Low volatility (<40 pips)
            leverage_multiplier = 1.0

        # Account size adjustment (larger accounts can use higher leverage)
        if account_balance > 50000:
            size_multiplier = 1.2
        elif account_balance > 25000:
            size_multiplier = 1.0
        else:
            size_multiplier = 0.8

        final_leverage = base_leverage * leverage_multiplier * size_multiplier
        return min(final_leverage, 20.0)  # Cap at 20:1

    def _calculate_position_size(self, leverage: float, notional_target: float) -> float:
        """Calculate position size based on leverage and notional target"""
        return notional_target / leverage

    def _generate_oco_order(self, symbol: str, side: str) -> Optional[OCOOrder]:
        """Generate OCO order with charter-compliant parameters"""

        # Current ATR calculation
        current_atr = self.atr_calculator.calculate_atr()

        # Generate entry price with spread consideration
        base_price = 1.1000 + random.uniform(-0.0100, 0.0100)

        # Spread gate validation (Charter: FX 0.15x ATR14)
        max_spread = current_atr * RickCharter.FX_MAX_SPREAD_ATR_MULTIPLIER
        actual_spread = random.uniform(0.0001, max_spread * 1.5)  # Some fail spread test

        if actual_spread > max_spread:
            logger.warning(f"Spread gate failed: {actual_spread:.5f} > {max_spread:.5f}")
            return None

        # ATR-based stop loss (Charter: FX 1.2x ATR)
        stop_distance = current_atr * RickCharter.FX_STOP_LOSS_ATR_MULTIPLIER

        if side == 'BUY':
            entry_price = base_price + (actual_spread / 2)  # Ask price
            stop_loss = entry_price - stop_distance
            take_profit = entry_price + (stop_distance * RickCharter.MIN_RISK_REWARD_RATIO)
        else:  # SELL
            entry_price = base_price - (actual_spread / 2)  # Bid price
            stop_loss = entry_price + stop_distance
            take_profit = entry_price - (stop_distance * RickCharter.MIN_RISK_REWARD_RATIO)

        # OCO placement latency simulation
        placement_latency_ms = random.uniform(50, 400)  # 50-400ms

        if placement_latency_ms > RickCharter.MAX_PLACEMENT_LATENCY_MS:
            logger.warning(f"OCO latency exceeded: {placement_latency_ms:.1f}ms > {RickCharter.MAX_PLACEMENT_LATENCY_MS}ms")
            return None

        return OCOOrder(
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            trailing_stop=random.choice([True, False]),  # 50% get trailing
            placement_latency_ms=placement_latency_ms,
            order_id=f"OCO_{int(time.time() * 1000)}"
        )

    async def execute_enhanced_trade(self):
        """Execute charter-compliant trade with full RICK requirements"""

        # Daily limits check
        if self.daily_trades >= RickCharter.MAX_DAILY_TRADES:
            logger.warning("Daily trade limit reached")
            return

        if self.concurrent_positions >= RickCharter.MAX_CONCURRENT_POSITIONS:
            logger.warning("Concurrent position limit reached")
            return

        # Daily loss breaker check
        if self.daily_pnl_pct <= RickCharter.DAILY_LOSS_BREAKER_PCT:
            logger.error(f"Daily loss breaker hit: {self.daily_pnl_pct:.2f}%")
            return

        # Generate signal
        regime = random.choice(['bullish', 'bearish', 'sideways'])
        if regime == 'bullish':
            signal = 'BUY' if random.random() < 0.7 else 'HOLD'
        elif regime == 'bearish':
            signal = 'SELL' if random.random() < 0.7 else 'HOLD'
        else:
            signal = 'HOLD' if random.random() < 0.6 else random.choice(['BUY', 'SELL'])

        if signal == 'HOLD':
            logger.info(f"Signal: HOLD - Regime: {regime}")
            return

        # Generate OCO order
        oco_order = self._generate_oco_order("EUR/USD", signal)
        if not oco_order:
            logger.warning("OCO order generation failed - skipping trade")
            return

        # Calculate current ATR and dynamic leverage
        current_atr = self.atr_calculator.calculate_atr()
        dynamic_leverage = self._calculate_dynamic_leverage(current_atr, self.current_capital)

        # Position sizing with minimum notional
        notional_target = max(self.min_notional, self.current_capital * 0.1)  # 10% of capital or min $15K
        position_size = self._calculate_position_size(dynamic_leverage, notional_target)

        # Risk validation
        risk = abs(oco_order.entry_price - oco_order.stop_loss) * position_size
        reward = abs(oco_order.take_profit - oco_order.entry_price) * position_size
        rr_ratio = reward / risk if risk > 0 else 0

        if not RickCharter.validate_risk_reward(rr_ratio):
            logger.warning(f"RR ratio {rr_ratio:.2f} below charter minimum {RickCharter.MIN_RISK_REWARD_RATIO}")
            return

        # Execute trade simulation
        self.concurrent_positions += 1
        trade_id = f"ENHANCED_{len(self.trades)+1:04d}"

        # Simulate execution time
        execution_time = random.randint(30, 180)  # 30 seconds to 3 minutes
        await asyncio.sleep(min(execution_time / 20, 9))  # Accelerated for testing

        # Determine outcome with trailing stop simulation
        confidence = random.uniform(0.4, 0.9)
        base_win_prob = confidence * 0.8

        # Trailing stop enhancement
        if oco_order.trailing_stop:
            base_win_prob += 0.1  # Trailing stops improve win rate

        is_winner = random.random() < base_win_prob

        # Calculate exit and PnL
        extra_profit = 0
        if is_winner:
            # Winner - could be TP or trailing stop profit
            if oco_order.trailing_stop and random.random() < 0.3:
                # Trailing stop captured more profit
                extra_profit = random.uniform(0.1, 0.5) * abs(oco_order.take_profit - oco_order.entry_price)
                if signal == 'BUY':
                    exit_price = oco_order.take_profit + extra_profit
                else:
                    exit_price = oco_order.take_profit - extra_profit
                trailing_activated = True
            else:
                exit_price = oco_order.take_profit
                trailing_activated = False

            pnl = reward + (extra_profit * position_size)
            outcome = 'win'
            self.wins += 1
        else:
            # Loss - hit stop loss
            exit_price = oco_order.stop_loss
            pnl = -risk
            outcome = 'loss'
            trailing_activated = False
            self.losses += 1

        # Spread cost
        spread_cost = (current_atr * RickCharter.FX_MAX_SPREAD_ATR_MULTIPLIER) * position_size
        pnl -= spread_cost  # Deduct spread cost

        # Update capital and daily tracking
        self.current_capital += pnl
        self.total_pnl += pnl
        self.daily_trades += 1
        self.daily_pnl_pct = ((self.current_capital - self.starting_capital) / self.starting_capital) * 100
        self.concurrent_positions -= 1

        # Create enhanced trade result
        trade_result = EnhancedTradeResult(
            trade_id=trade_id,
            symbol="EUR/USD",
            side=signal,
            notional_usd=notional_target,
            leverage=dynamic_leverage,
            entry_price=oco_order.entry_price,
            exit_price=exit_price,
            stop_loss=oco_order.stop_loss,
            take_profit=oco_order.take_profit,
            atr_multiplier=RickCharter.FX_STOP_LOSS_ATR_MULTIPLIER,
            spread_cost=spread_cost,
            pnl=pnl,
            duration_seconds=execution_time,
            timestamp=datetime.now(timezone.utc),
            outcome=outcome,
            confidence=confidence,
            oco_latency_ms=oco_order.placement_latency_ms,
            trailing_activated=trailing_activated
        )

        self.trades.append(trade_result)

        logger.info(f"Enhanced Trade {trade_id}: {signal} @ {oco_order.entry_price:.4f}")
        logger.info(f"  Notional: ${notional_target:,.0f} | Leverage: {dynamic_leverage:.1f}x | ATR: {current_atr:.5f}")
        logger.info(f"  Exit: {exit_price:.4f} | PnL: ${pnl:,.2f} | Outcome: {outcome.upper()}")
        logger.info(f"  OCO Latency: {oco_order.placement_latency_ms:.1f}ms | Trailing: {trailing_activated}")

        # Update price history for next ATR calculation
        high = max(oco_order.entry_price, exit_price) + random.uniform(0, 0.0020)
        low = min(oco_order.entry_price, exit_price) - random.uniform(0, 0.0020)
        self.atr_calculator.add_price_data(high, low, exit_price)

    async def run_enhanced_test(self, duration_minutes: int = 10):
        """Run enhanced RICK test with full charter compliance"""
        end_time = self.start_time + timedelta(minutes=duration_minutes)

        logger.info("🚀 ENHANCED RICK ENGINE - FULL CHARTER COMPLIANCE")
        logger.info(f"Duration: {duration_minutes} minutes")
        logger.info(f"Capital: ${self.starting_capital:,.2f}")
        logger.info(f"Min Notional: ${self.min_notional:,.2f}")
        logger.info("Features: Dynamic leverage, ATR stops, OCO orders, trailing stops")

        try:
            while datetime.now(timezone.utc) < end_time:
                await self.execute_enhanced_trade()

                # Variable interval between trades
                await asyncio.sleep(random.uniform(2, 8))

        except Exception as e:
            logger.error(f"Enhanced test error: {e}")
        finally:
            await self.generate_enhanced_report()

    async def generate_enhanced_report(self):
        """Generate comprehensive enhanced test report"""
        total_trades = len(self.trades)
        win_rate = (self.wins / total_trades * 100) if total_trades > 0 else 0

        # Calculate average metrics
        avg_notional = sum(t.notional_usd for t in self.trades) / total_trades if total_trades > 0 else 0
        avg_leverage = sum(t.leverage for t in self.trades) / total_trades if total_trades > 0 else 0
        avg_oco_latency = sum(t.oco_latency_ms for t in self.trades) / total_trades if total_trades > 0 else 0
        trailing_count = sum(1 for t in self.trades if t.trailing_activated)

        # Charter compliance metrics
        charter_compliance = {
            'min_notional_met': all(t.notional_usd >= self.min_notional for t in self.trades) if self.trades else True,
            'rr_compliance': all(abs(t.take_profit - t.entry_price) / abs(t.stop_loss - t.entry_price) >= RickCharter.MIN_RISK_REWARD_RATIO for t in self.trades) if self.trades else True,
            'daily_trade_limit': self.daily_trades <= RickCharter.MAX_DAILY_TRADES,
            'daily_loss_breaker': self.daily_pnl_pct > RickCharter.DAILY_LOSS_BREAKER_PCT,
            'oco_latency_compliance': all(t.oco_latency_ms <= RickCharter.MAX_PLACEMENT_LATENCY_MS for t in self.trades) if self.trades else True
        }

        report = {
            'enhanced_test_summary': {
                'total_trades': total_trades,
                'wins': self.wins,
                'losses': self.losses,
                'win_rate': win_rate,
                'total_pnl': self.total_pnl,
                'final_capital': self.current_capital,
                'daily_pnl_pct': self.daily_pnl_pct,
                'avg_notional_usd': avg_notional,
                'avg_leverage': avg_leverage,
                'avg_oco_latency_ms': avg_oco_latency,
                'trailing_stops_activated': trailing_count
            },
            'charter_compliance': charter_compliance,
            'all_charter_compliant': all(charter_compliance.values()),
            'enhanced_features': {
                'dynamic_leverage': True,
                'atr_based_stops': True,
                'oco_orders': True,
                'trailing_stops': True,
                'spread_gates': True,
                'minimum_notional': True,
                'no_talib': True
            },
            'trades': [asdict(trade) for trade in self.trades],
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

        # Save report
        os.makedirs('logs', exist_ok=True)
        with open('logs/enhanced_rick_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)

        # Log summary
        logger.info("🏆 ENHANCED RICK TEST COMPLETE")
        logger.info(f"Trades: {total_trades} | Win Rate: {win_rate:.1f}%")
        logger.info(f"Total PnL: ${self.total_pnl:,.2f} | Final Capital: ${self.current_capital:,.2f}")
        logger.info(f"Daily PnL: {self.daily_pnl_pct:.2f}% | Avg Notional: ${avg_notional:,.0f}")
        logger.info(f"Avg Leverage: {avg_leverage:.1f}x | OCO Latency: {avg_oco_latency:.1f}ms")
        logger.info(f"Trailing Activated: {trailing_count}/{total_trades}")
        logger.info(f"Charter Compliant: {'✅ YES' if report['all_charter_compliant'] else '❌ NO'}")

        return report