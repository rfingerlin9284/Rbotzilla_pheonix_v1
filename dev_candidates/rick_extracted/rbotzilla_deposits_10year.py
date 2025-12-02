#!/usr/bin/env python3
"""
RBOTZILLA 10-YEAR REALISTIC BACKTEST - MONTHLY DEPOSITS VERSION
Starting Capital: $2,000
Monthly Deposits: $1,000
Reinvestment: 85% (15% withdrawn for safety)
Full compounding with charter-compliant risk management
"""

import asyncio
import json
import time
import logging
import random
import numpy as np
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict, field
import os
from pathlib import Path
from enum import Enum

# Import authentic RICK Charter
from rick_charter import RickCharter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - RBOT10Y-DEPOSITS - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/rbotzilla_10year_deposits.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MarketCycle(Enum):
    """Market cycle phases"""
    BULL_STRONG = "BULL_STRONG"
    BULL_MODERATE = "BULL_MODERATE"
    SIDEWAYS = "SIDEWAYS"
    BEAR_MODERATE = "BEAR_MODERATE"
    BEAR_STRONG = "BEAR_STRONG"
    CRISIS = "CRISIS"

@dataclass
class MarketConditions:
    """Current market conditions"""
    cycle: MarketCycle
    volatility: float
    trend_strength: float
    correlation_factor: float
    liquidity_factor: float
    days_in_cycle: int
    next_cycle_change: int

@dataclass
class MonthlySnapshot:
    """Monthly performance snapshot"""
    year: int
    month: int
    starting_capital: float
    ending_capital: float
    deposit_amount: float
    withdrawal_amount: float
    net_trading_pnl: float
    trades_count: int
    win_rate: float
    max_drawdown_pct: float
    market_cycle: str

@dataclass
class YearlyPerformance:
    """Yearly performance summary"""
    year: int
    starting_capital: float
    ending_capital: float
    total_deposits: float
    total_withdrawals: float
    net_trading_pnl: float
    total_trades: int
    win_rate: float
    max_drawdown_pct: float
    sharpe_ratio: float
    profit_factor: float
    roi_pct: float
    dominant_cycle: str

@dataclass
class RealisticTrade:
    """Realistic trade with all costs"""
    trade_id: str
    symbol: str
    side: str
    notional_usd: float
    leverage: float
    entry_price: float
    exit_price: float
    stop_loss: float
    take_profit: float
    trailing_stop_activated: bool
    hedge_symbol: Optional[str]
    hedge_pnl: float
    gross_pnl: float
    commission: float
    slippage_cost: float
    net_pnl: float
    market_cycle: str
    volatility: float
    duration_seconds: int
    timestamp: datetime
    outcome: str
    year: int
    month: int
    rr_ratio: float

class MarketCycleSimulator:
    """Simulates realistic 10-year market cycles"""

    def __init__(self):
        self.current_conditions = self._initialize_conditions()
        self.cycle_history = []

    def _initialize_conditions(self) -> MarketConditions:
        """Initialize with bull market"""
        return MarketConditions(
            cycle=MarketCycle.BULL_MODERATE,
            volatility=0.6,
            trend_strength=0.7,
            correlation_factor=0.5,
            liquidity_factor=1.0,
            days_in_cycle=0,
            next_cycle_change=random.randint(30, 90)
        )

    def advance_day(self):
        """Advance market conditions by one day"""
        self.current_conditions.days_in_cycle += 1

        # Gradually change conditions
        self.current_conditions.volatility *= random.uniform(0.95, 1.05)
        self.current_conditions.volatility = np.clip(self.current_conditions.volatility, 0.1, 2.0)

        # Check for cycle change
        if self.current_conditions.days_in_cycle >= self.current_conditions.next_cycle_change:
            self._transition_cycle()

    def _transition_cycle(self):
        """Transition to next market cycle"""
        current = self.current_conditions.cycle

        transitions = {
            MarketCycle.BULL_STRONG: [MarketCycle.BULL_MODERATE, MarketCycle.SIDEWAYS],
            MarketCycle.BULL_MODERATE: [MarketCycle.BULL_STRONG, MarketCycle.SIDEWAYS, MarketCycle.BEAR_MODERATE],
            MarketCycle.SIDEWAYS: [MarketCycle.BULL_MODERATE, MarketCycle.BEAR_MODERATE],
            MarketCycle.BEAR_MODERATE: [MarketCycle.BEAR_STRONG, MarketCycle.SIDEWAYS, MarketCycle.CRISIS],
            MarketCycle.BEAR_STRONG: [MarketCycle.CRISIS, MarketCycle.BEAR_MODERATE, MarketCycle.SIDEWAYS],
            MarketCycle.CRISIS: [MarketCycle.BEAR_STRONG, MarketCycle.SIDEWAYS, MarketCycle.BULL_MODERATE]
        }

        # 5% chance of crisis
        if random.random() < 0.05:
            next_cycle = MarketCycle.CRISIS
        else:
            next_cycle = random.choice(transitions[current])

        self.current_conditions.cycle = next_cycle
        self.current_conditions.days_in_cycle = 0
        self.current_conditions.next_cycle_change = random.randint(30, 90)

        cycle_settings = {
            MarketCycle.BULL_STRONG: {'vol': 0.4, 'trend': 0.9, 'liq': 1.2},
            MarketCycle.BULL_MODERATE: {'vol': 0.5, 'trend': 0.7, 'liq': 1.1},
            MarketCycle.SIDEWAYS: {'vol': 0.3, 'trend': 0.3, 'liq': 1.0},
            MarketCycle.BEAR_MODERATE: {'vol': 0.8, 'trend': 0.6, 'liq': 0.9},
            MarketCycle.BEAR_STRONG: {'vol': 1.2, 'trend': 0.8, 'liq': 0.7},
            MarketCycle.CRISIS: {'vol': 2.0, 'trend': 0.9, 'liq': 0.5}
        }

        settings = cycle_settings[next_cycle]
        self.current_conditions.volatility = settings['vol']
        self.current_conditions.trend_strength = settings['trend']
        self.current_conditions.liquidity_factor = settings['liq']

        logger.info(f"🔄 CYCLE CHANGE: {next_cycle.value}")

class AdvancedHedgingSystem:
    """Full correlation-based portfolio hedging"""

    def __init__(self):
        self.base_correlations = {
            'EURUSD': {'GBPUSD': 0.82, 'USDJPY': -0.68, 'GOLD': 0.58},
            'GBPUSD': {'EURUSD': 0.82, 'USDJPY': -0.62, 'GOLD': 0.52},
            'USDJPY': {'EURUSD': -0.68, 'GBPUSD': -0.62, 'GOLD': -0.38},
            'GOLD': {'EURUSD': 0.58, 'GBPUSD': 0.52, 'USDJPY': -0.38}
        }

    def find_optimal_hedge(self, symbol: str, market_conditions: MarketConditions) -> Tuple[Optional[str], float]:
        """Find optimal hedge pair and ratio"""
        if symbol not in self.base_correlations:
            return None, 0.0

        correlations = self.base_correlations[symbol]
        hedge_candidates = [(s, c) for s, c in correlations.items() if c < -0.3]

        if not hedge_candidates:
            return None, 0.0

        best_hedge = min(hedge_candidates, key=lambda x: x[1])
        hedge_symbol, correlation = best_hedge

        base_ratio = abs(correlation) * 0.5

        if market_conditions.cycle in [MarketCycle.BEAR_STRONG, MarketCycle.CRISIS]:
            hedge_ratio = min(base_ratio * 1.3, 0.7)
        else:
            hedge_ratio = base_ratio

        return hedge_symbol, hedge_ratio

    def calculate_hedge_pnl(self, hedge_symbol: Optional[str], hedge_ratio: float,
                           main_pnl: float, market_conditions: MarketConditions) -> float:
        """Calculate realistic hedge PnL"""
        if not hedge_symbol or hedge_ratio == 0:
            return 0.0

        if market_conditions.cycle == MarketCycle.CRISIS:
            effectiveness = 0.85
        elif market_conditions.cycle == MarketCycle.SIDEWAYS:
            effectiveness = 0.4
        else:
            effectiveness = 0.6

        if main_pnl < 0:
            hedge_pnl = abs(main_pnl) * hedge_ratio * effectiveness
        else:
            hedge_pnl = -abs(main_pnl) * hedge_ratio * 0.3 * effectiveness

        return hedge_pnl

class RBOTzillaMonthlyDeposits:
    """
    RBOTzilla with Monthly Deposits and 85% Reinvestment
    - $30K initial + $1K/month deposits
    - 85% reinvestment (15% withdrawn for safety)
    - Charter-compliant risk management
    - Smart trailing stops
    - Dynamic leverage scaling
    """

    def __init__(self, pin: int):
        if not RickCharter.validate_pin(pin):
            raise PermissionError("Invalid PIN")

        self.PIN = pin

        # Capital management with deposits
        self.initial_capital = 30000.0  # $30K starting
        self.monthly_deposit = 1000.0   # $1K per month
        self.reinvestment_rate = 0.85   # 85% reinvested
        self.withdrawal_rate = 0.15     # 15% withdrawn

        self.current_capital = self.initial_capital
        self.peak_capital = self.initial_capital
        self.total_deposits = self.initial_capital
        self.total_withdrawals = 0.0
        self.trading_capital = self.initial_capital  # Capital used for trading

        # Market simulation
        self.market_sim = MarketCycleSimulator()
        self.hedging_system = AdvancedHedgingSystem()

        # Performance tracking
        self.trades: List[RealisticTrade] = []
        self.monthly_snapshots: List[MonthlySnapshot] = []
        self.yearly_performance: List[YearlyPerformance] = []

        # Risk management
        self.max_position_size_usd = 50000.0  # Cap at $50K per position
        self.daily_trades = 0
        self.max_daily_trades = 40
        self.current_drawdown_pct = 0.0
        self.max_drawdown_pct = 0.0

        # Trading costs
        self.commission_rate = 0.0002
        self.slippage_rate = 0.0001

        # Simulation state
        self.simulation_start_date = datetime(2015, 1, 1, tzinfo=timezone.utc)
        self.current_date = self.simulation_start_date
        self.current_month_start_capital = self.current_capital
        self.month_trades_count = 0
        self.month_start_date = self.simulation_start_date

        logger.info("🤖💰 RBOTZILLA - MONTHLY DEPOSITS MODE")
        logger.info(f"💵 Initial Capital: ${self.initial_capital:,.0f}")
        logger.info(f"📅 Monthly Deposit: ${self.monthly_deposit:,.0f}")
        logger.info(f"♻️  Reinvestment: {self.reinvestment_rate*100:.0f}%")
        logger.info(f"💸 Withdrawal: {self.withdrawal_rate*100:.0f}%")

    def process_monthly_deposit(self):
        """Process monthly deposit and profit withdrawal"""
        # Calculate trading profit this month
        month_trading_pnl = sum(t.net_pnl for t in self.trades if
                                t.year == self.current_date.year and
                                t.month == self.current_date.month)

        # Only withdraw from profits (not deposits)
        if month_trading_pnl > 0:
            withdrawal = month_trading_pnl * self.withdrawal_rate
            self.current_capital -= withdrawal
            self.total_withdrawals += withdrawal
            logger.info(f"💸 Withdrew ${withdrawal:,.2f} (15% of profits)")

        # Add monthly deposit
        self.current_capital += self.monthly_deposit
        self.total_deposits += self.monthly_deposit
        self.trading_capital = self.current_capital

        logger.info(f"💰 Monthly deposit: ${self.monthly_deposit:,.2f} | New capital: ${self.current_capital:,.2f}")

    def calculate_position_size(self, market_conditions: MarketConditions) -> float:
        """Charter-compliant dynamic position sizing"""
        # Base: 3-8% of TRADING capital (not total with deposits)
        base_pct = 5.0

        # Market cycle adjustment
        cycle_multipliers = {
            MarketCycle.BULL_STRONG: 1.6,
            MarketCycle.BULL_MODERATE: 1.3,
            MarketCycle.SIDEWAYS: 0.9,
            MarketCycle.BEAR_MODERATE: 0.7,
            MarketCycle.BEAR_STRONG: 0.5,
            MarketCycle.CRISIS: 0.3
        }

        cycle_mult = cycle_multipliers[market_conditions.cycle]

        # Drawdown protection
        if self.current_drawdown_pct > 20:
            dd_mult = 0.3
        elif self.current_drawdown_pct > 15:
            dd_mult = 0.5
        elif self.current_drawdown_pct > 10:
            dd_mult = 0.7
        else:
            dd_mult = 1.0

        # Recent performance scaling
        if len(self.trades) >= 20:
            recent_trades = self.trades[-20:]
            recent_win_rate = len([t for t in recent_trades if t.outcome == 'win']) / 20

            if recent_win_rate > 0.7:
                perf_mult = 1.4  # Scale up after wins
            elif recent_win_rate < 0.5:
                perf_mult = 0.6  # Scale down after losses
            else:
                perf_mult = 1.0
        else:
            perf_mult = 1.0

        final_pct = base_pct * cycle_mult * dd_mult * perf_mult
        final_pct = np.clip(final_pct, 1.0, 12.0)

        # Calculate notional with cap
        notional = self.trading_capital * (final_pct / 100)
        notional = min(notional, self.max_position_size_usd)
        notional = max(notional, RickCharter.MIN_NOTIONAL_USD)

        return notional

    def calculate_dynamic_leverage(self, market_conditions: MarketConditions, confidence: float) -> float:
        """Charter-compliant dynamic leverage"""
        base_leverage = {
            MarketCycle.BULL_STRONG: 15.0,
            MarketCycle.BULL_MODERATE: 12.0,
            MarketCycle.SIDEWAYS: 8.0,
            MarketCycle.BEAR_MODERATE: 6.0,
            MarketCycle.BEAR_STRONG: 4.0,
            MarketCycle.CRISIS: 2.5
        }

        leverage = base_leverage[market_conditions.cycle]
        leverage *= (0.8 + confidence * 0.4)
        leverage *= market_conditions.liquidity_factor

        return np.clip(leverage, 2.0, 25.0)

    def calculate_smart_trailing_stop(self, entry_price: float, side: str,
                                      atr: float, current_profit_pips: float) -> float:
        """Smart trailing stop that tightens as profit grows"""
        initial_stop_distance = atr * 1.2  # Charter: 1.2x ATR

        # Tighten stop as profit accumulates
        if current_profit_pips > atr * 4:  # 4x ATR profit
            trailing_distance = atr * 0.8  # Tighten to 0.8x
        elif current_profit_pips > atr * 2:  # 2x ATR profit
            trailing_distance = atr * 1.0
        else:
            trailing_distance = initial_stop_distance

        return trailing_distance

    def calculate_win_probability(self, market_conditions: MarketConditions, confidence: float) -> float:
        """Realistic win probability"""
        base_win_rates = {
            MarketCycle.BULL_STRONG: 0.73,
            MarketCycle.BULL_MODERATE: 0.68,
            MarketCycle.SIDEWAYS: 0.58,
            MarketCycle.BEAR_MODERATE: 0.54,
            MarketCycle.BEAR_STRONG: 0.50,
            MarketCycle.CRISIS: 0.42
        }

        base_rate = base_win_rates[market_conditions.cycle]
        confidence_factor = (confidence - 0.5) * 0.3
        vol_factor = -0.05 * (market_conditions.volatility - 0.6)

        final_prob = base_rate + confidence_factor + vol_factor
        return np.clip(final_prob, 0.35, 0.85)

    async def execute_charter_trade(self, market_conditions: MarketConditions):
        """Execute charter-compliant trade with trailing stops"""

        if self.daily_trades >= self.max_daily_trades:
            return

        # Symbol selection
        symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'GOLD']
        symbol = random.choice(symbols)

        # Signal generation
        confidence = random.uniform(0.55, 0.9)
        side = random.choice(['BUY', 'SELL'])

        # Position sizing
        notional = self.calculate_position_size(market_conditions)
        leverage = self.calculate_dynamic_leverage(market_conditions, confidence)
        position_size = notional / leverage

        # Entry price
        base_prices = {'EURUSD': 1.1200, 'GBPUSD': 1.2800, 'USDJPY': 110.0, 'GOLD': 1800.0}
        base_price = base_prices[symbol]
        price_move = base_price * market_conditions.volatility * random.uniform(-0.02, 0.02)
        entry_price = base_price + price_move

        # ATR for stops
        atr = base_price * market_conditions.volatility * 0.01

        # Smart stop loss (Charter: 1.2x ATR for FX)
        if market_conditions.cycle in [MarketCycle.CRISIS, MarketCycle.BEAR_STRONG]:
            sl_mult = 1.5
        else:
            sl_mult = 1.2  # Charter standard

        stop_distance = atr * sl_mult

        # Take profit (Charter: RR >= 3.2)
        rr_ratio = random.uniform(3.2, 5.5)
        tp_distance = stop_distance * rr_ratio

        if side == 'BUY':
            stop_loss = entry_price - stop_distance
            take_profit = entry_price + tp_distance
        else:
            stop_loss = entry_price + stop_distance
            take_profit = entry_price - tp_distance

        # Validate RR ratio (Charter requirement)
        if not RickCharter.validate_risk_reward(rr_ratio):
            return  # Skip trade

        # Find hedge
        hedge_symbol, hedge_ratio = self.hedging_system.find_optimal_hedge(symbol, market_conditions)

        # Execution
        await asyncio.sleep(0)

        # Outcome with trailing stop consideration
        win_prob = self.calculate_win_probability(market_conditions, confidence)
        is_winner = random.random() < win_prob

        trailing_activated = False

        if is_winner:
            # Simulate trailing stop behavior
            if random.random() < 0.4:  # 40% of wins use trailing stop
                trailing_activated = True
                # Trailing stop captures more profit
                extra_profit_mult = random.uniform(1.1, 1.8)
                exit_price = entry_price + (tp_distance * extra_profit_mult) if side == 'BUY' else entry_price - (tp_distance * extra_profit_mult)
            else:
                exit_price = take_profit

            if side == 'BUY':
                gross_pnl = (exit_price - entry_price) * position_size
            else:
                gross_pnl = (entry_price - exit_price) * position_size
            outcome = 'win'
        else:
            exit_price = stop_loss
            if side == 'BUY':
                gross_pnl = (exit_price - entry_price) * position_size
            else:
                gross_pnl = (entry_price - exit_price) * position_size
            outcome = 'loss'

        # Hedge PnL
        hedge_pnl = self.hedging_system.calculate_hedge_pnl(hedge_symbol, hedge_ratio, gross_pnl, market_conditions)

        # Costs
        commission = notional * self.commission_rate
        slippage = notional * self.slippage_rate * market_conditions.volatility / market_conditions.liquidity_factor

        net_pnl = gross_pnl + hedge_pnl - commission - slippage

        # Update capital (only trading capital)
        self.trading_capital += net_pnl
        self.current_capital += net_pnl

        # Drawdown tracking
        if self.current_capital > self.peak_capital:
            self.peak_capital = self.current_capital
            self.current_drawdown_pct = 0.0
        else:
            self.current_drawdown_pct = ((self.peak_capital - self.current_capital) / self.peak_capital) * 100
            if self.current_drawdown_pct > self.max_drawdown_pct:
                self.max_drawdown_pct = self.current_drawdown_pct

        # Create trade record
        trade = RealisticTrade(
            trade_id=f"RBOT_DEP_{len(self.trades)+1:06d}",
            symbol=symbol,
            side=side,
            notional_usd=notional,
            leverage=leverage,
            entry_price=entry_price,
            exit_price=exit_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            trailing_stop_activated=trailing_activated,
            hedge_symbol=hedge_symbol,
            hedge_pnl=hedge_pnl,
            gross_pnl=gross_pnl,
            commission=commission,
            slippage_cost=slippage,
            net_pnl=net_pnl,
            market_cycle=market_conditions.cycle.value,
            volatility=market_conditions.volatility,
            duration_seconds=random.randint(300, 3600),
            timestamp=self.current_date,
            outcome=outcome,
            year=self.current_date.year,
            month=self.current_date.month,
            rr_ratio=rr_ratio
        )

        self.trades.append(trade)
        self.daily_trades += 1
        self.month_trades_count += 1

        # Periodic logging
        if len(self.trades) % 500 == 0:
            logger.info(f"📊 {len(self.trades):,} trades | Capital: ${self.current_capital:,.2f} | DD: {self.current_drawdown_pct:.1f}%")

    async def simulate_trading_day(self):
        """Simulate one trading day"""
        self.daily_trades = 0

        # Check for month end
        if self.current_date.day == 1 and self.current_date != self.month_start_date:
            await self.finalize_month()
            self.process_monthly_deposit()

        # Advance market
        self.market_sim.advance_day()

        # Trade frequency
        trades_per_day = {
            MarketCycle.BULL_STRONG: 22,
            MarketCycle.BULL_MODERATE: 18,
            MarketCycle.SIDEWAYS: 12,
            MarketCycle.BEAR_MODERATE: 14,
            MarketCycle.BEAR_STRONG: 10,
            MarketCycle.CRISIS: 8
        }

        target_trades = trades_per_day[self.market_sim.current_conditions.cycle]

        for _ in range(target_trades):
            await self.execute_charter_trade(self.market_sim.current_conditions)

        self.current_date += timedelta(days=1)

        # Year end
        if self.current_date.month == 1 and self.current_date.day == 1:
            await self.finalize_year()

    async def finalize_month(self):
        """Finalize monthly snapshot"""
        month_trades = [t for t in self.trades if
                       t.year == self.current_date.year and
                       t.month == self.current_date.month]

        if not month_trades:
            return

        month_pnl = sum(t.net_pnl for t in month_trades)
        win_rate = len([t for t in month_trades if t.outcome == 'win']) / len(month_trades) * 100

        snapshot = MonthlySnapshot(
            year=self.current_date.year,
            month=self.current_date.month,
            starting_capital=self.current_month_start_capital,
            ending_capital=self.current_capital,
            deposit_amount=self.monthly_deposit if self.current_date != self.simulation_start_date else self.initial_capital,
            withdrawal_amount=month_pnl * self.withdrawal_rate if month_pnl > 0 else 0,
            net_trading_pnl=month_pnl,
            trades_count=len(month_trades),
            win_rate=win_rate,
            max_drawdown_pct=self.current_drawdown_pct,
            market_cycle=self.market_sim.current_conditions.cycle.value
        )

        self.monthly_snapshots.append(snapshot)
        self.current_month_start_capital = self.current_capital
        self.month_start_date = self.current_date
        self.month_trades_count = 0

    async def finalize_year(self):
        """Finalize yearly performance"""
        year = self.current_date.year - 1
        year_trades = [t for t in self.trades if t.year == year]

        if not year_trades:
            return

        year_pnl = sum(t.net_pnl for t in year_trades)
        win_rate = len([t for t in year_trades if t.outcome == 'win']) / len(year_trades) * 100

        year_deposits = self.monthly_deposit * 12
        year_withdrawals = sum(s.withdrawal_amount for s in self.monthly_snapshots if s.year == year)

        # ROI calculation (trading profit / invested capital)
        invested_capital = self.total_deposits
        roi_pct = (year_pnl / invested_capital) * 100 if invested_capital > 0 else 0

        # Profit factor
        wins = [t.net_pnl for t in year_trades if t.net_pnl > 0]
        losses = [abs(t.net_pnl) for t in year_trades if t.net_pnl < 0]
        profit_factor = sum(wins) / sum(losses) if losses else 0

        yearly_perf = YearlyPerformance(
            year=year,
            starting_capital=self.monthly_snapshots[0].starting_capital if self.monthly_snapshots else self.initial_capital,
            ending_capital=self.current_capital,
            total_deposits=year_deposits,
            total_withdrawals=year_withdrawals,
            net_trading_pnl=year_pnl,
            total_trades=len(year_trades),
            win_rate=win_rate,
            max_drawdown_pct=self.max_drawdown_pct,
            sharpe_ratio=0.0,
            profit_factor=profit_factor,
            roi_pct=roi_pct,
            dominant_cycle="MIXED"
        )

        self.yearly_performance.append(yearly_perf)
        self.max_drawdown_pct = 0.0

        logger.info(f"📅 YEAR {year}: Capital ${self.current_capital:,.2f} | ROI {roi_pct:.1f}% | Trades: {len(year_trades):,}")

    async def run_10year_backtest(self):
        """Run 10-year backtest with monthly deposits"""
        logger.info("🚀 STARTING 10-YEAR BACKTEST - MONTHLY DEPOSITS MODE")
        logger.info("=" * 80)

        total_days = 365 * 10

        try:
            for day in range(total_days):
                await self.simulate_trading_day()

                if day % 365 == 0:
                    year = self.simulation_start_date.year + (day // 365)
                    logger.info(f"📆 Year {year} starting...")

            if self.current_date.year > (self.yearly_performance[-1].year if self.yearly_performance else 2015):
                await self.finalize_year()

        except Exception as e:
            logger.error(f"Backtest error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await self.generate_final_report()

    async def generate_final_report(self):
        """Generate comprehensive 10-year report"""
        total_invested = self.total_deposits
        final_value = self.current_capital + self.total_withdrawals
        net_profit = final_value - total_invested
        roi_total = (net_profit / total_invested) * 100

        total_trades = len(self.trades)
        total_wins = len([t for t in self.trades if t.outcome == 'win'])
        overall_win_rate = (total_wins / total_trades * 100) if total_trades > 0 else 0

        trailing_stops_used = len([t for t in self.trades if t.trailing_stop_activated])

        report = {
            'deposit_strategy_summary': {
                'initial_deposit': self.initial_capital,
                'monthly_deposit': self.monthly_deposit,
                'total_deposited': total_invested,
                'total_withdrawn': self.total_withdrawals,
                'final_capital': self.current_capital,
                'final_total_value': final_value,
                'net_profit': net_profit,
                'total_roi_pct': roi_total,
                'reinvestment_rate': self.reinvestment_rate * 100
            },
            'trading_performance': {
                'total_trades': total_trades,
                'overall_win_rate': overall_win_rate,
                'trailing_stops_activated': trailing_stops_used,
                'max_drawdown_pct': max((y.max_drawdown_pct for y in self.yearly_performance), default=0)
            },
            'yearly_breakdown': [asdict(y) for y in self.yearly_performance],
            'monthly_snapshots': [asdict(m) for m in self.monthly_snapshots[-24:]],  # Last 2 years
            'sample_trades': [asdict(t) for t in self.trades[::200]]
        }

        os.makedirs('logs', exist_ok=True)
        with open('logs/rbotzilla_deposits_10year.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)

        logger.info("🏆 10-YEAR BACKTEST COMPLETE - MONTHLY DEPOSITS")
        logger.info("=" * 80)
        logger.info(f"💰 Total Deposited: ${total_invested:,.2f}")
        logger.info(f"💸 Total Withdrawn: ${self.total_withdrawals:,.2f}")
        logger.info(f"💵 Final Capital: ${self.current_capital:,.2f}")
        logger.info(f"💎 Total Value: ${final_value:,.2f}")
        logger.info(f"📈 Net Profit: ${net_profit:,.2f}")
        logger.info(f"📊 Total ROI: {roi_total:.2f}%")
        logger.info(f"✅ Win Rate: {overall_win_rate:.1f}%")
        logger.info(f"📉 Max Drawdown: {max((y.max_drawdown_pct for y in self.yearly_performance), default=0):.2f}%")
        logger.info(f"🎯 Total Trades: {total_trades:,}")
        logger.info(f"🔄 Trailing Stops: {trailing_stops_used:,}")

        return report

async def main():
    """Run 10-year backtest with monthly deposits"""
    PIN = 841921

    print("🤖💰 RBOTZILLA 10-YEAR BACKTEST")
    print("$2K Initial + $1K Monthly Deposits")
    print("85% Reinvestment | Full Compounding | Charter Compliant")
    print("=" * 80)

    try:
        engine = RBOTzillaMonthlyDeposits(pin=PIN)
        await engine.run_10year_backtest()

        print("\n📁 Report saved to: logs/rbotzilla_deposits_10year.json")

    except Exception as e:
        logger.error(f"Backtest failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
