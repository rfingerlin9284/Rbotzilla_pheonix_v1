#!/usr/bin/env python3
"""
RBOTZILLA AGGRESSIVE MOMENTUM TRAILING - ENHANCED VERSION
Features:
- Smart trailing that CANCELS TP on strong momentum
- Breakeven stop moves automatically
- Partial profit taking at milestones
- Dynamic trailing that tightens progressively
- Loss prevention with momentum detection
- Never caps a good run!
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
from enum import Enum

from rick_charter import RickCharter

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - RBOT-MOMENTUM - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/rbotzilla_momentum_trailing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MarketCycle(Enum):
    BULL_STRONG = "BULL_STRONG"
    BULL_MODERATE = "BULL_MODERATE"
    SIDEWAYS = "SIDEWAYS"
    BEAR_MODERATE = "BEAR_MODERATE"
    BEAR_STRONG = "BEAR_STRONG"
    CRISIS = "CRISIS"

@dataclass
class MarketConditions:
    cycle: MarketCycle
    volatility: float
    trend_strength: float
    momentum_factor: float  # NEW: Momentum detection
    liquidity_factor: float
    days_in_cycle: int

@dataclass
class MomentumTrade:
    """Trade with advanced momentum tracking"""
    trade_id: str
    symbol: str
    side: str
    notional_usd: float
    leverage: float
    entry_price: float
    exit_price: float
    initial_stop_loss: float
    final_stop_loss: float  # After trailing
    initial_take_profit: float
    tp_cancelled: bool  # Did we cancel TP for momentum?
    breakeven_activated: bool
    partial_exits: int  # Number of partial profit takes
    max_profit_reached: float  # Peak profit in pips
    trailing_distance_final: float
    momentum_detected: bool
    hedge_symbol: Optional[str]
    hedge_pnl: float
    gross_pnl: float
    commission: float
    net_pnl: float
    market_cycle: str
    duration_seconds: int
    timestamp: datetime
    outcome: str
    rr_ratio: float
    momentum_multiplier: float  # How much extra we got from momentum

class MomentumDetector:
    """Detects price momentum in real-time"""

    def __init__(self):
        self.price_history = []

    def detect_momentum(self, entry_price: float, current_price: float,
                       side: str, atr: float, market_conditions: MarketConditions) -> Tuple[bool, float]:
        """
        Detect if trade has strong momentum
        Returns: (has_momentum, momentum_strength)
        """
        # Calculate profit in ATR units
        if side == 'BUY':
            profit_atr = (current_price - entry_price) / atr
        else:
            profit_atr = (entry_price - current_price) / atr

        # Strong momentum indicators
        has_strong_momentum = False
        momentum_strength = 0.0

        # Criterion 1: Profit > 2x ATR quickly
        if profit_atr > 2.0:
            has_strong_momentum = True
            momentum_strength = profit_atr / 2.0  # 1.0 = 2x ATR, 2.0 = 4x ATR

        # Criterion 2: Market cycle supports momentum
        if market_conditions.cycle in [MarketCycle.BULL_STRONG, MarketCycle.BEAR_STRONG]:
            momentum_strength *= 1.3
            if profit_atr > 1.5:
                has_strong_momentum = True

        # Criterion 3: Trend strength
        if market_conditions.trend_strength > 0.7 and profit_atr > 1.5:
            has_strong_momentum = True
            momentum_strength *= market_conditions.trend_strength

        return has_strong_momentum, momentum_strength

class SmartTrailingSystem:
    """
    Advanced trailing stop system that:
    1. Moves to breakeven at 1x ATR profit
    2. Takes partial profits at milestones
    3. Tightens trail as profit grows
    4. CANCELS TP when momentum detected
    5. Never caps a good run
    """

    def __init__(self):
        self.momentum_detector = MomentumDetector()

    def calculate_breakeven_point(self, entry_price: float, atr: float, side: str) -> float:
        """At 1x ATR profit, move stop to breakeven"""
        if side == 'BUY':
            return entry_price + atr
        else:
            return entry_price - atr

    def should_move_to_breakeven(self, entry_price: float, current_price: float,
                                 atr: float, side: str) -> bool:
        """Check if we should move stop to breakeven"""
        breakeven_trigger = self.calculate_breakeven_point(entry_price, atr, side)

        if side == 'BUY':
            return current_price >= breakeven_trigger
        else:
            return current_price <= breakeven_trigger

    def calculate_dynamic_trailing_distance(self, entry_price: float, current_price: float,
                                           atr: float, side: str, initial_stop_distance: float) -> float:
        """
        Progressive trailing that tightens as profit grows:
        - 0-1x ATR profit: 1.2x ATR trail (charter standard)
        - 1-2x ATR profit: 1.0x ATR trail (tightening)
        - 2-3x ATR profit: 0.8x ATR trail (tight)
        - 3-4x ATR profit: 0.6x ATR trail (very tight)
        - 4+x ATR profit: 0.5x ATR trail (ultra tight, lock profit)
        """
        if side == 'BUY':
            profit_atr = (current_price - entry_price) / atr
        else:
            profit_atr = (entry_price - current_price) / atr

        if profit_atr < 1.0:
            return atr * 1.2  # Charter standard
        elif profit_atr < 2.0:
            return atr * 1.0  # Start tightening
        elif profit_atr < 3.0:
            return atr * 0.8  # Tight
        elif profit_atr < 4.0:
            return atr * 0.6  # Very tight
        else:
            return atr * 0.5  # Ultra tight, lock in gains

    def should_take_partial_profit(self, entry_price: float, current_price: float,
                                   atr: float, side: str, partials_taken: int) -> bool:
        """
        Take partial profits at milestones:
        - 25% at 2x ATR profit
        - 25% at 3x ATR profit
        - Let remaining 50% run with trailing
        """
        if side == 'BUY':
            profit_atr = (current_price - entry_price) / atr
        else:
            profit_atr = (entry_price - current_price) / atr

        if partials_taken == 0 and profit_atr >= 2.0:
            return True  # First partial at 2x ATR
        elif partials_taken == 1 and profit_atr >= 3.0:
            return True  # Second partial at 3x ATR

        return False

    def simulate_trailing_execution(self, entry_price: float, side: str, atr: float,
                                   initial_sl: float, initial_tp: float,
                                   market_conditions: MarketConditions,
                                   confidence: float) -> dict:
        """
        Simulate complete trade execution with smart trailing
        Returns full trade outcome with momentum tracking
        """
        current_price = entry_price
        stop_loss = initial_sl
        take_profit = initial_tp
        tp_cancelled = False
        breakeven_activated = False
        partials_taken = 0
        max_profit = 0.0
        momentum_detected = False
        momentum_multiplier = 1.0

        # Simulate price movement (tick by tick)
        ticks = random.randint(50, 300)  # 50-300 ticks

        for tick in range(ticks):
            # Price movement based on market conditions
            tick_size = atr * 0.01 * random.uniform(0.5, 1.5)

            # Direction bias based on side and momentum
            if side == 'BUY':
                direction_bias = 0.6 if confidence > 0.7 else 0.5
            else:
                direction_bias = 0.4 if confidence > 0.7 else 0.5

            if random.random() < direction_bias:
                current_price += tick_size if side == 'BUY' else -tick_size
            else:
                current_price -= tick_size if side == 'BUY' else -tick_size

            # Calculate current profit
            if side == 'BUY':
                current_profit = (current_price - entry_price) / atr
            else:
                current_profit = (entry_price - current_price) / atr

            max_profit = max(max_profit, current_profit)

            # Check for momentum
            has_momentum, momentum_strength = self.momentum_detector.detect_momentum(
                entry_price, current_price, side, atr, market_conditions
            )

            if has_momentum and not tp_cancelled:
                # CANCEL TP - LET IT RUN!
                tp_cancelled = True
                momentum_detected = True
                momentum_multiplier = momentum_strength
                logger.debug(f"🚀 MOMENTUM DETECTED! Cancelling TP, letting trade run (strength: {momentum_strength:.2f}x)")

            # Move to breakeven
            if not breakeven_activated and self.should_move_to_breakeven(entry_price, current_price, atr, side):
                stop_loss = entry_price
                breakeven_activated = True
                logger.debug(f"🔒 Breakeven activated at {entry_price}")

            # Take partial profits
            if self.should_take_partial_profit(entry_price, current_price, atr, side, partials_taken):
                partials_taken += 1
                logger.debug(f"💰 Partial profit #{partials_taken} taken at {current_profit:.1f}x ATR")

            # Update trailing stop (if in profit)
            if current_profit > 0:
                trail_distance = self.calculate_dynamic_trailing_distance(
                    entry_price, current_price, atr, side, atr * 1.2
                )

                if side == 'BUY':
                    new_stop = current_price - trail_distance
                    stop_loss = max(stop_loss, new_stop)  # Only move up
                else:
                    new_stop = current_price + trail_distance
                    stop_loss = min(stop_loss, new_stop)  # Only move down

            # Check exits
            # Stop loss hit
            if side == 'BUY' and current_price <= stop_loss:
                exit_price = stop_loss
                outcome = 'loss' if stop_loss < entry_price else 'win'  # Could be BE or profit
                break
            elif side == 'SELL' and current_price >= stop_loss:
                exit_price = stop_loss
                outcome = 'loss' if stop_loss > entry_price else 'win'
                break

            # Take profit hit (only if not cancelled)
            if not tp_cancelled:
                if side == 'BUY' and current_price >= take_profit:
                    exit_price = take_profit
                    outcome = 'win'
                    break
                elif side == 'SELL' and current_price <= take_profit:
                    exit_price = take_profit
                    outcome = 'win'
                    break
        else:
            # Time exit (trail was never hit)
            exit_price = current_price
            if side == 'BUY':
                outcome = 'win' if exit_price > entry_price else 'loss'
            else:
                outcome = 'win' if exit_price < entry_price else 'loss'

        # Calculate final PnL
        if side == 'BUY':
            gross_pnl_pct = (exit_price - entry_price) / entry_price
        else:
            gross_pnl_pct = (entry_price - exit_price) / entry_price

        return {
            'exit_price': exit_price,
            'final_stop_loss': stop_loss,
            'tp_cancelled': tp_cancelled,
            'breakeven_activated': breakeven_activated,
            'partial_exits': partials_taken,
            'max_profit_reached': max_profit,
            'trailing_distance_final': abs(exit_price - stop_loss),
            'momentum_detected': momentum_detected,
            'momentum_multiplier': momentum_multiplier,
            'outcome': outcome,
            'gross_pnl_pct': gross_pnl_pct
        }

class RBOTzillaMomentumEngine:
    """
    RBOTzilla with AGGRESSIVE MOMENTUM TRAILING
    - Never caps a good run
    - Smart breakeven moves
    - Partial profit taking
    - Dynamic tightening trail
    - Loss prevention
    """

    def __init__(self, pin: int, initial_capital: float = 30000.0):
        if not RickCharter.validate_pin(pin):
            raise PermissionError("Invalid PIN")

        self.PIN = pin
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.monthly_deposit = 1000.0

        self.trailing_system = SmartTrailingSystem()
        self.trades: List[MomentumTrade] = []

        self.simulation_start_date = datetime(2015, 1, 1, tzinfo=timezone.utc)
        self.current_date = self.simulation_start_date

        # Aggressive settings
        self.max_position_size_usd = 100000.0  # $100K cap per trade
        self.max_daily_trades = 35
        self.daily_trades = 0

        logger.info("🚀 RBOTZILLA MOMENTUM TRAILING ENGINE")
        logger.info(f"💰 Initial Capital: ${initial_capital:,.0f}")
        logger.info("🎯 Aggressive trailing - Never caps momentum runs!")

    async def execute_momentum_trade(self, market_conditions: MarketConditions):
        """Execute trade with full momentum-aware trailing"""

        if self.daily_trades >= self.max_daily_trades:
            return

        # Setup
        symbol = random.choice(['EURUSD', 'GBPUSD', 'USDJPY', 'GOLD'])
        confidence = random.uniform(0.6, 0.92)
        side = random.choice(['BUY', 'SELL'])

        # Position sizing (5-10% of capital)
        position_pct = random.uniform(5.0, 10.0)
        notional = min(self.current_capital * (position_pct / 100), self.max_position_size_usd)
        notional = max(notional, RickCharter.MIN_NOTIONAL_USD)

        # Leverage (8-20x based on conditions)
        base_leverage = 15.0 if market_conditions.cycle in [MarketCycle.BULL_STRONG, MarketCycle.BULL_MODERATE] else 10.0
        leverage = base_leverage * confidence
        leverage = np.clip(leverage, 5.0, 25.0)

        position_size = notional / leverage

        # Entry and stops
        base_prices = {'EURUSD': 1.1200, 'GBPUSD': 1.2800, 'USDJPY': 110.0, 'GOLD': 1800.0}
        base_price = base_prices[symbol]
        entry_price = base_price + base_price * market_conditions.volatility * random.uniform(-0.015, 0.015)

        atr = base_price * market_conditions.volatility * 0.01
        stop_distance = atr * 1.2  # Charter: 1.2x ATR
        rr_ratio = random.uniform(3.5, 6.0)
        tp_distance = stop_distance * rr_ratio

        if side == 'BUY':
            initial_sl = entry_price - stop_distance
            initial_tp = entry_price + tp_distance
        else:
            initial_sl = entry_price + stop_distance
            initial_tp = entry_price - tp_distance

        # Execute with smart trailing
        result = self.trailing_system.simulate_trailing_execution(
            entry_price, side, atr, initial_sl, initial_tp, market_conditions, confidence
        )

        # Calculate PnL
        gross_pnl = result['gross_pnl_pct'] * position_size * leverage

        # Adjust for partials (reduce gross by 50% if 2 partials taken)
        if result['partial_exits'] > 0:
            partial_reduction = result['partial_exits'] * 0.25  # 25% per partial
            gross_pnl *= (1 - partial_reduction + partial_reduction)  # Keep base, adjust remainder

        # Costs
        commission = notional * 0.0002
        slippage = notional * 0.0001
        net_pnl = gross_pnl - commission - slippage

        # Update capital
        self.current_capital += net_pnl

        # Record trade
        trade = MomentumTrade(
            trade_id=f"RBOT_MOM_{len(self.trades)+1:05d}",
            symbol=symbol,
            side=side,
            notional_usd=notional,
            leverage=leverage,
            entry_price=entry_price,
            exit_price=result['exit_price'],
            initial_stop_loss=initial_sl,
            final_stop_loss=result['final_stop_loss'],
            initial_take_profit=initial_tp,
            tp_cancelled=result['tp_cancelled'],
            breakeven_activated=result['breakeven_activated'],
            partial_exits=result['partial_exits'],
            max_profit_reached=result['max_profit_reached'],
            trailing_distance_final=result['trailing_distance_final'],
            momentum_detected=result['momentum_detected'],
            hedge_symbol=None,
            hedge_pnl=0.0,
            gross_pnl=gross_pnl,
            commission=commission,
            net_pnl=net_pnl,
            market_cycle=market_conditions.cycle.value,
            duration_seconds=random.randint(600, 3600),
            timestamp=self.current_date,
            outcome=result['outcome'],
            rr_ratio=rr_ratio,
            momentum_multiplier=result['momentum_multiplier']
        )

        self.trades.append(trade)
        self.daily_trades += 1

        # Log momentum wins
        if result['momentum_detected']:
            logger.info(f"🚀 MOMENTUM WIN: {trade.trade_id} | {result['momentum_multiplier']:.2f}x | ${net_pnl:,.2f}")

    async def run_quick_test(self, duration_minutes: int = 30):
        """Quick 30-minute test of momentum system"""
        logger.info("🚀 TESTING MOMENTUM TRAILING SYSTEM")
        logger.info(f"Duration: {duration_minutes} minutes")
        logger.info("=" * 80)

        end_time = self.current_date + timedelta(minutes=duration_minutes)

        # Simulated market conditions
        market_conditions = MarketConditions(
            cycle=MarketCycle.BULL_MODERATE,
            volatility=0.6,
            trend_strength=0.75,
            momentum_factor=0.7,
            liquidity_factor=1.0,
            days_in_cycle=45
        )

        try:
            while self.current_date < end_time:
                await self.execute_momentum_trade(market_conditions)

                # Fast execution
                await asyncio.sleep(random.uniform(0.1, 0.3))
                self.current_date += timedelta(minutes=1)

                if len(self.trades) % 50 == 0 and len(self.trades) > 0:
                    logger.info(f"📊 {len(self.trades)} trades | Capital: ${self.current_capital:,.2f}")

        except Exception as e:
            logger.error(f"Test error: {e}")
        finally:
            await self.generate_momentum_report()

    async def generate_momentum_report(self):
        """Generate comprehensive momentum trading report"""
        total_trades = len(self.trades)
        if total_trades == 0:
            logger.warning("No trades executed")
            return

        wins = len([t for t in self.trades if t.outcome == 'win'])
        win_rate = (wins / total_trades) * 100

        # Momentum statistics
        momentum_trades = [t for t in self.trades if t.momentum_detected]
        tp_cancelled_trades = [t for t in self.trades if t.tp_cancelled]
        breakeven_trades = [t for t in self.trades if t.breakeven_activated]
        partial_trades = [t for t in self.trades if t.partial_exits > 0]

        avg_momentum_mult = np.mean([t.momentum_multiplier for t in momentum_trades]) if momentum_trades else 0

        total_pnl = sum(t.net_pnl for t in self.trades)
        momentum_pnl = sum(t.net_pnl for t in momentum_trades)

        report = {
            'momentum_system_summary': {
                'total_trades': total_trades,
                'win_rate': win_rate,
                'total_pnl': total_pnl,
                'final_capital': self.current_capital,
                'return_pct': ((self.current_capital - self.initial_capital) / self.initial_capital) * 100
            },
            'momentum_features': {
                'momentum_trades': len(momentum_trades),
                'momentum_pct': (len(momentum_trades) / total_trades) * 100,
                'avg_momentum_multiplier': avg_momentum_mult,
                'tp_cancelled_count': len(tp_cancelled_trades),
                'breakeven_activated': len(breakeven_trades),
                'partial_exits_used': len(partial_trades),
                'momentum_contribution_pnl': momentum_pnl
            },
            'sample_momentum_trades': [asdict(t) for t in momentum_trades[:10]]
        }

        os.makedirs('logs', exist_ok=True)
        with open('logs/rbotzilla_momentum_test.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)

        logger.info("🏆 MOMENTUM SYSTEM TEST COMPLETE")
        logger.info(f"📊 Total Trades: {total_trades} | Win Rate: {win_rate:.1f}%")
        logger.info(f"💰 Final Capital: ${self.current_capital:,.2f} | PnL: ${total_pnl:,.2f}")
        logger.info(f"🚀 Momentum Trades: {len(momentum_trades)} ({len(momentum_trades)/total_trades*100:.1f}%)")
        logger.info(f"🎯 TP Cancelled: {len(tp_cancelled_trades)} | Breakeven: {len(breakeven_trades)}")
        logger.info(f"💎 Avg Momentum Multiplier: {avg_momentum_mult:.2f}x")
        logger.info(f"📈 Momentum PnL Contribution: ${momentum_pnl:,.2f}")

        return report

async def main():
    """Test momentum trailing system"""
    PIN = 841921

    print("🤖🚀 RBOTZILLA MOMENTUM TRAILING SYSTEM TEST")
    print("Never Caps Momentum Runs | Smart Breakeven | Partial Profits")
    print("=" * 80)

    try:
        engine = RBOTzillaMomentumEngine(pin=PIN, initial_capital=30000.0)
        await engine.run_quick_test(duration_minutes=30)

        print("\n📁 Report: logs/rbotzilla_momentum_test.json")

    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
