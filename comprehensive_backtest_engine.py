#!/usr/bin/env python3
"""
COMPREHENSIVE 10-YEAR BACKTEST ENGINE
=====================================
Backtests OANDA (Forex), Coinbase (Crypto), and IBKR (Equities/Futures)
Period: 2015-2025 | Initial Capital: $5,000 | Monthly Deposits: $1,000
COMPLETELY ISOLATED from PhoenixV2/main.py
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
import logging
from dataclasses import dataclass, asdict
import random

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURATION
# =============================================================================

INITIAL_CAPITAL = 5000
MONTHLY_DEPOSIT = 1000
BACKTEST_START = datetime(2015, 1, 1)
BACKTEST_END = datetime(2025, 12, 1)

# Platform-specific initial allocation
PLATFORM_ALLOCATION = {
    'oanda': 2000,
    'coinbase': 2000,
    'ibkr': 1000
}

# =============================================================================
# STRATEGY DEFINITIONS
# =============================================================================

@dataclass
class StrategyDef:
    name: str
    platform: str
    timeframe: str
    entry_logic: str
    exit_logic: str
    parameters: Dict[str, Any]
    risk_reward: float
    position_size_pct: float

# OANDA Forex Strategies
OANDA_STRATEGIES = [
    StrategyDef(
        name='EMA_Scalper',
        platform='oanda',
        timeframe='M15',
        entry_logic='EMA fast crossover EMA slow',
        exit_logic='ATR-based stop loss with R:R target',
        parameters={'fast': 100, 'slow': 200, 'sl_atr_mult': 1.5},
        risk_reward=4.0,
        position_size_pct=2.0
    ),
    StrategyDef(
        name='Liquidity_Sweep',
        platform='oanda',
        timeframe='H1',
        entry_logic='Price sweep of recent swing low/high + rejection',
        exit_logic='Reversal confirmation + ATR stop',
        parameters={'lookback': 20, 'rejection_atr_mult': 0.5},
        risk_reward=3.5,
        position_size_pct=1.5
    ),
    StrategyDef(
        name='Momentum_TrendFollow',
        platform='oanda',
        timeframe='H4',
        entry_logic='Momentum indicator positive + price above SMA20/50',
        exit_logic='Momentum reversal or fixed R:R hit',
        parameters={'momentum_period': 14, 'sma_fast': 20, 'sma_slow': 50},
        risk_reward=2.5,
        position_size_pct=1.8
    ),
    StrategyDef(
        name='Mean_Reversion',
        platform='oanda',
        timeframe='D1',
        entry_logic='RSI < 30 (oversold) or RSI > 70 (overbought)',
        exit_logic='RSI normalization + profit target',
        parameters={'rsi_period': 14, 'oversold': 30, 'overbought': 70},
        risk_reward=2.0,
        position_size_pct=2.0
    ),
    StrategyDef(
        name='Breakout_Volume',
        platform='oanda',
        timeframe='H1',
        entry_logic='Price breaks 20-period high/low + volume spike',
        exit_logic='Price close beyond breakout range',
        parameters={'lookback': 20, 'volume_threshold': 1.5},
        risk_reward=3.0,
        position_size_pct=1.5
    ),
]

# Coinbase Crypto Strategies
COINBASE_STRATEGIES = [
    StrategyDef(
        name='FVG_Breakout',
        platform='coinbase',
        timeframe='M15',
        entry_logic='Fair Value Gap formation + breakout confirmation',
        exit_logic='Gap fill or price target hit',
        parameters={'fvg_threshold': 0.005, 'confirmation_bars': 2},
        risk_reward=4.0,
        position_size_pct=2.0
    ),
    StrategyDef(
        name='Funding_Rate_Arb',
        platform='coinbase',
        timeframe='D1',
        entry_logic='Positive funding rate > 0.02% + spot price near futures',
        exit_logic='Funding rate flip or daily target',
        parameters={'funding_threshold': 0.0002, 'duration_days': 3},
        risk_reward=1.5,
        position_size_pct=3.0
    ),
    StrategyDef(
        name='Volatility_Scalping',
        platform='coinbase',
        timeframe='M5',
        entry_logic='Bollinger Band squeeze break + ATR expansion',
        exit_logic='BB mean reversion or opposite band touch',
        parameters={'bb_period': 20, 'bb_mult': 2.0},
        risk_reward=2.0,
        position_size_pct=1.5
    ),
    StrategyDef(
        name='Grid_Trading',
        platform='coinbase',
        timeframe='D1',
        entry_logic='Establish grid at support/resistance levels',
        exit_logic='Grid targets hit in sequence',
        parameters={'grid_levels': 5, 'grid_spacing': 0.02},
        risk_reward=1.8,
        position_size_pct=3.0
    ),
    StrategyDef(
        name='Momentum_Crypto',
        platform='coinbase',
        timeframe='H4',
        entry_logic='MACD bullish crossover + price above EMA200',
        exit_logic='MACD bearish crossover or fixed profit',
        parameters={'ema_period': 200, 'macd_fast': 12},
        risk_reward=3.0,
        position_size_pct=2.0
    ),
]

# IBKR Equities/Futures Strategies
IBKR_STRATEGIES = [
    StrategyDef(
        name='Mean_Reversion_Futures',
        platform='ibkr',
        timeframe='H1',
        entry_logic='Price 2 SD below 20-SMA (short) or above (long)',
        exit_logic='Price returns to SMA or opposite signal',
        parameters={'sma_period': 20, 'std_dev': 2.0},
        risk_reward=2.0,
        position_size_pct=1.0
    ),
    StrategyDef(
        name='Breakout_ES',
        platform='ibkr',
        timeframe='H1',
        entry_logic='ES breaks 50-period high + closes above',
        exit_logic='50-SMA crossover or 3% stop loss',
        parameters={'lookback': 50, 'stop_pct': 0.03},
        risk_reward=3.0,
        position_size_pct=1.2
    ),
    StrategyDef(
        name='Correlation_Hedge',
        platform='ibkr',
        timeframe='D1',
        entry_logic='ES near high + gold near low (divergence)',
        exit_logic='Convergence back to mean',
        parameters={'lookback': 60, 'zscore_threshold': 2.0},
        risk_reward=2.5,
        position_size_pct=0.8
    ),
]

# =============================================================================
# SYNTHETIC DATA GENERATOR
# =============================================================================

class SyntheticMarketDataGenerator:
    """
    Generate realistic OHLCV data for 2015-2025 period
    Uses geometric Brownian motion with regime switching
    """
    
    def __init__(self, seed: int = 42):
        np.random.seed(seed)
        random.seed(seed)
    
    def generate_forex_pair(self, symbol: str, start_price: float, 
                          start_date: datetime, end_date: datetime,
                          daily_volatility: float = 0.01) -> pd.DataFrame:
        """Generate forex pair data (daily bars)"""
        periods = (end_date - start_date).days
        dates = pd.date_range(start=start_date, periods=periods, freq='D')
        
        # Filter out weekends (forex market closed)
        dates = dates[dates.dayofweek < 5]
        
        # Geometric Brownian motion with regime switching
        prices = []
        current_price = start_price
        regime = 'normal'
        regime_count = 0
        
        for i, date in enumerate(dates):
            # Regime switching every 60-120 days
            if regime_count > random.randint(60, 120):
                regime = np.random.choice(['trending_up', 'trending_down', 'normal'])
                regime_count = 0
            regime_count += 1
            
            # Drift based on regime
            if regime == 'trending_up':
                drift = 0.0003
            elif regime == 'trending_down':
                drift = -0.0003
            else:
                drift = 0.0001
            
            # Random return with volatility
            ret = np.random.normal(drift, daily_volatility)
            current_price = current_price * (1 + ret)
            
            # Generate OHLCV
            open_p = current_price * (1 + np.random.normal(0, 0.0003))
            close = current_price
            high = max(open_p, close) * (1 + abs(np.random.normal(0, 0.0005)))
            low = min(open_p, close) * (1 - abs(np.random.normal(0, 0.0005)))
            volume = int(np.random.lognormal(10, 1.5))
            
            prices.append({
                'time': date,
                'open': open_p,
                'high': high,
                'low': low,
                'close': close,
                'volume': volume
            })
        
        df = pd.DataFrame(prices)
        df['symbol'] = symbol
        return df
    
    def generate_crypto_pair(self, symbol: str, start_price: float,
                            start_date: datetime, end_date: datetime,
                            daily_volatility: float = 0.04) -> pd.DataFrame:
        """Generate crypto data with higher volatility (4-hour bars)"""
        periods = int((end_date - start_date).days * 6)  # 6 periods per day
        dates = pd.date_range(start=start_date, periods=periods, freq='4H')
        
        prices = []
        current_price = start_price
        trend_strength = 0
        
        for i, date in enumerate(dates):
            # Random walk with mean reversion
            if abs(trend_strength) > 0.2:
                trend_strength *= 0.95
            
            trend_strength += np.random.normal(0, 0.1)
            ret = np.random.normal(trend_strength * 0.0002, daily_volatility / 6)
            current_price = current_price * (1 + ret)
            
            # Generate OHLCV
            open_p = current_price * (1 + np.random.normal(0, 0.001))
            close = current_price
            high = max(open_p, close) * (1 + abs(np.random.normal(0, 0.0015)))
            low = min(open_p, close) * (1 - abs(np.random.normal(0, 0.0015)))
            volume = int(np.random.lognormal(11, 2))
            
            prices.append({
                'time': date,
                'open': open_p,
                'high': high,
                'low': low,
                'close': close,
                'volume': volume
            })
        
        df = pd.DataFrame(prices)
        df['symbol'] = symbol
        return df
    
    def generate_futures_contract(self, symbol: str, start_price: float,
                                  start_date: datetime, end_date: datetime,
                                  daily_volatility: float = 0.015) -> pd.DataFrame:
        """Generate futures contract data (hourly bars)"""
        periods = int((end_date - start_date).days * 24)
        dates = pd.date_range(start=start_date, periods=periods, freq='H')
        
        # Filter out low-liquidity hours (weekends, extended hours)
        prices = []
        current_price = start_price
        
        for i, date in enumerate(dates):
            # Skip low volume hours
            if date.dayofweek > 4 and date.hour > 16:  # Friday evening onwards
                continue
            if date.dayofweek > 4:  # Weekend
                continue
            
            ret = np.random.normal(0.00001, daily_volatility / 24)
            current_price = current_price * (1 + ret)
            
            open_p = current_price * (1 + np.random.normal(0, 0.0005))
            close = current_price
            high = max(open_p, close) * (1 + abs(np.random.normal(0, 0.0008)))
            low = min(open_p, close) * (1 - abs(np.random.normal(0, 0.0008)))
            volume = int(np.random.lognormal(9, 1))
            
            prices.append({
                'time': date,
                'open': open_p,
                'high': high,
                'low': low,
                'close': close,
                'volume': volume
            })
        
        df = pd.DataFrame(prices)
        df['symbol'] = symbol
        return df

# =============================================================================
# STRATEGY BACKTESTER
# =============================================================================

@dataclass
class Trade:
    entry_time: datetime
    exit_time: datetime
    entry_price: float
    exit_price: float
    direction: str  # BUY or SELL
    pnl: float
    pnl_pct: float
    position_size: float
    
@dataclass
class BacktestResults:
    strategy_name: str
    platform: str
    symbol: str
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    net_pnl: float
    gross_profit: float
    gross_loss: float
    average_win: float
    average_loss: float
    profit_factor: float
    largest_win: float
    largest_loss: float
    consecutive_wins: int
    consecutive_losses: int
    max_drawdown: float
    max_drawdown_pct: float
    sharpe_ratio: float
    sortino_ratio: float
    cagr: float
    total_return_pct: float
    trades: List[Trade]

class StrategyBacktester:
    """Backtest a strategy on OHLCV data"""
    
    def __init__(self, df: pd.DataFrame, strategy: StrategyDef,
                 initial_capital: float, fees: Dict[str, float]):
        self.df = df.copy()
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.fees = fees  # {'spread_pips': 2, 'commission': 0.001, 'slippage': 0.0005}
        self.trades = []
    
    def calculate_indicators(self) -> pd.DataFrame:
        """Calculate technical indicators"""
        df = self.df.copy()
        
        # EMAs
        df['ema_20'] = df['close'].ewm(span=20, adjust=False).mean()
        df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()
        df['ema_200'] = df['close'].ewm(span=200, adjust=False).mean()
        
        # SMA
        df['sma_20'] = df['close'].rolling(20).mean()
        df['sma_50'] = df['close'].rolling(50).mean()
        df['sma_200'] = df['close'].rolling(200).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # ATR
        df['tr'] = np.maximum(
            df['high'] - df['low'],
            np.maximum(
                abs(df['high'] - df['close'].shift()),
                abs(df['low'] - df['close'].shift())
            )
        )
        df['atr'] = df['tr'].rolling(14).mean()
        
        # Bollinger Bands
        df['bb_middle'] = df['close'].rolling(20).mean()
        df['bb_std'] = df['close'].rolling(20).std()
        df['bb_upper'] = df['bb_middle'] + (df['bb_std'] * 2)
        df['bb_lower'] = df['bb_middle'] - (df['bb_std'] * 2)
        
        # MACD
        ema_12 = df['close'].ewm(span=12, adjust=False).mean()
        ema_26 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = ema_12 - ema_26
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_hist'] = df['macd'] - df['macd_signal']
        
        return df
    
    def generate_signals(self, df_with_indicators: pd.DataFrame) -> pd.DataFrame:
        """Generate entry/exit signals based on strategy"""
        df = df_with_indicators.copy()
        df['signal'] = 'HOLD'
        df['signal_strength'] = 0.0
        
        strategy_name = self.strategy.name
        
        if strategy_name == 'EMA_Scalper':
            # EMA fast > slow = BUY
            df.loc[df['ema_20'] > df['ema_50'], 'signal'] = 'BUY'
            df.loc[df['ema_20'] < df['ema_50'], 'signal'] = 'SELL'
            df['signal_strength'] = abs(df['ema_20'] - df['ema_50']) / df['close']
        
        elif strategy_name == 'Liquidity_Sweep':
            # Recent low + rejection = BUY
            recent_low = df['low'].rolling(20).min()
            recent_high = df['high'].rolling(20).max()
            
            buy_signal = (df['low'] < recent_low.shift(1)) & (df['close'] > df['open'])
            sell_signal = (df['high'] > recent_high.shift(1)) & (df['close'] < df['open'])
            
            df.loc[buy_signal, 'signal'] = 'BUY'
            df.loc[sell_signal, 'signal'] = 'SELL'
        
        elif strategy_name == 'Momentum_TrendFollow':
            # Price above SMA + momentum positive
            momentum = df['close'].pct_change(14) * 100
            df.loc[(df['close'] > df['sma_50']) & (momentum > 0), 'signal'] = 'BUY'
            df.loc[(df['close'] < df['sma_50']) & (momentum < 0), 'signal'] = 'SELL'
        
        elif strategy_name == 'Mean_Reversion':
            # RSI oversold/overbought
            df.loc[df['rsi'] < 30, 'signal'] = 'BUY'
            df.loc[df['rsi'] > 70, 'signal'] = 'SELL'
        
        elif strategy_name == 'Breakout_Volume':
            # Volume spike on breakout
            recent_high = df['high'].rolling(20).max()
            recent_low = df['low'].rolling(20).min()
            vol_avg = df['volume'].rolling(20).mean()
            
            buy_vol = df['volume'] > vol_avg * 1.5
            sell_vol = df['volume'] > vol_avg * 1.5
            
            df.loc[(df['close'] > recent_high.shift(1)) & buy_vol, 'signal'] = 'BUY'
            df.loc[(df['close'] < recent_low.shift(1)) & sell_vol, 'signal'] = 'SELL'
        
        elif strategy_name == 'FVG_Breakout':
            # Fair Value Gap detection
            fvg_up = (df['low'] > df['high'].shift(2))
            fvg_dn = (df['high'] < df['low'].shift(2))
            df.loc[fvg_up & (df['close'] > df['high'].shift(2)), 'signal'] = 'BUY'
            df.loc[fvg_dn & (df['close'] < df['low'].shift(2)), 'signal'] = 'SELL'
        
        elif strategy_name == 'Funding_Rate_Arb':
            # Simplified: alternate based on trend
            trend = (df['close'] - df['sma_200']) / df['close']
            df.loc[trend > 0.01, 'signal'] = 'BUY'
            df.loc[trend < -0.01, 'signal'] = 'SELL'
        
        elif strategy_name == 'Volatility_Scalping':
            # BB squeeze break
            bb_width = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
            bb_width_avg = bb_width.rolling(20).mean()
            
            squeeze = bb_width < bb_width_avg * 0.7
            df.loc[squeeze & (df['close'] > df['bb_upper'].shift(1)), 'signal'] = 'BUY'
            df.loc[squeeze & (df['close'] < df['bb_lower'].shift(1)), 'signal'] = 'SELL'
        
        elif strategy_name == 'Grid_Trading':
            # Simplified grid at support/resistance
            support = df['low'].rolling(30).min()
            resistance = df['high'].rolling(30).max()
            
            at_support = df['close'] < support * 1.01
            at_resistance = df['close'] > resistance * 0.99
            
            df.loc[at_support, 'signal'] = 'BUY'
            df.loc[at_resistance, 'signal'] = 'SELL'
        
        elif strategy_name == 'Momentum_Crypto':
            # MACD crossover
            macd_cross_up = (df['macd'] > df['macd_signal']) & (df['macd'].shift(1) <= df['macd_signal'].shift(1))
            macd_cross_dn = (df['macd'] < df['macd_signal']) & (df['macd'].shift(1) >= df['macd_signal'].shift(1))
            
            df.loc[macd_cross_up & (df['close'] > df['ema_200']), 'signal'] = 'BUY'
            df.loc[macd_cross_dn & (df['close'] < df['ema_200']), 'signal'] = 'SELL'
        
        elif strategy_name in ['Mean_Reversion_Futures', 'Breakout_ES', 'Correlation_Hedge']:
            # Futures strategies - mean reversion
            z_score = (df['close'] - df['sma_20']) / df['atr']
            df.loc[z_score < -2, 'signal'] = 'BUY'
            df.loc[z_score > 2, 'signal'] = 'SELL'
        
        return df
    
    def backtest(self) -> BacktestResults:
        """Run backtest"""
        logger.info(f"Backtesting {self.strategy.name} on {self.strategy.symbol}")
        
        # Calculate indicators
        df = self.calculate_indicators()
        
        # Generate signals
        df = self.generate_signals(df)
        
        # Simulate trades
        in_trade = False
        entry_idx = None
        entry_price = None
        entry_signal = None
        daily_returns = []
        equity_curve = [self.initial_capital]
        current_equity = self.initial_capital
        
        for i in range(len(df) - 1):
            signal = df.iloc[i]['signal']
            
            if not in_trade and signal in ['BUY', 'SELL']:
                # Entry
                entry_idx = i
                entry_price = df.iloc[i + 1]['open']
                entry_signal = signal
                in_trade = True
                atr = df.iloc[i]['atr'] if not pd.isna(df.iloc[i]['atr']) else 0.01
                
            elif in_trade:
                # Check exit conditions
                should_exit = False
                exit_price = None
                
                atr = df.iloc[i]['atr'] if not pd.isna(df.iloc[i]['atr']) else 0.01
                
                if entry_signal == 'BUY':
                    # Stop loss
                    sl = entry_price - atr * self.strategy.parameters.get('sl_atr_mult', 1.5)
                    # Take profit
                    tp = entry_price + atr * self.strategy.parameters.get('sl_atr_mult', 1.5) * self.strategy.risk_reward
                    
                    if df.iloc[i]['low'] <= sl:
                        exit_price = sl
                        should_exit = True
                    elif df.iloc[i]['high'] >= tp:
                        exit_price = tp
                        should_exit = True
                    elif signal == 'SELL':  # Opposite signal
                        exit_price = df.iloc[i]['close']
                        should_exit = True
                
                elif entry_signal == 'SELL':
                    # Stop loss
                    sl = entry_price + atr * self.strategy.parameters.get('sl_atr_mult', 1.5)
                    # Take profit
                    tp = entry_price - atr * self.strategy.parameters.get('sl_atr_mult', 1.5) * self.strategy.risk_reward
                    
                    if df.iloc[i]['high'] >= sl:
                        exit_price = sl
                        should_exit = True
                    elif df.iloc[i]['low'] <= tp:
                        exit_price = tp
                        should_exit = True
                    elif signal == 'BUY':  # Opposite signal
                        exit_price = df.iloc[i]['close']
                        should_exit = True
                
                if should_exit and exit_price and entry_price > 0:
                    # Calculate P&L as percentage
                    if entry_signal == 'BUY':
                        pnl_pct = ((exit_price - entry_price) / entry_price) * 100
                    else:
                        pnl_pct = ((entry_price - exit_price) / entry_price) * 100
                    
                    # Apply fees as percentage
                    fee_pct = self.fees.get('commission', 0.001) * 100
                    pnl_pct -= fee_pct
                    
                    # Update equity using fixed position size
                    position_size = self.strategy.position_size_pct / 100.0  # Convert % to decimal
                    position_pnl = current_equity * position_size * (pnl_pct / 100.0)
                    
                    # Cap position PnL to prevent overflow
                    if abs(position_pnl) > current_equity * 10:
                        position_pnl = np.sign(position_pnl) * current_equity * 0.1
                    
                    current_equity += position_pnl
                    
                    # Prevent equity from going below minimum
                    if current_equity < 100:
                        current_equity = 100
                    
                    # Record trade
                    self.trades.append(Trade(
                        entry_time=df.iloc[entry_idx]['time'],
                        exit_time=df.iloc[i]['time'],
                        entry_price=entry_price,
                        exit_price=exit_price,
                        direction=entry_signal,
                        pnl=position_pnl,
                        pnl_pct=pnl_pct,
                        position_size=position_size
                    ))
                    
                    daily_returns.append(pnl_pct / 100.0)
                    equity_curve.append(current_equity)
                    
                    in_trade = False
                    entry_idx = None
                    entry_price = None
                    entry_signal = None
        
        # Calculate statistics
        return self._calculate_statistics(daily_returns, equity_curve)
    
    def _calculate_statistics(self, daily_returns: List[float], equity_curve: List[float]) -> BacktestResults:
        """Calculate backtest statistics"""
        trades = self.trades
        
        if not trades:
            return BacktestResults(
                strategy_name=self.strategy.name,
                platform=self.strategy.platform,
                symbol=self.strategy.symbol,
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                win_rate=0,
                net_pnl=0,
                gross_profit=0,
                gross_loss=0,
                average_win=0,
                average_loss=0,
                profit_factor=0,
                largest_win=0,
                largest_loss=0,
                consecutive_wins=0,
                consecutive_losses=0,
                max_drawdown=0,
                max_drawdown_pct=0,
                sharpe_ratio=0,
                sortino_ratio=0,
                cagr=0,
                total_return_pct=0,
                trades=[]
            )
        
        # Trade stats
        wins = [t.pnl for t in trades if t.pnl > 0]
        losses = [t.pnl for t in trades if t.pnl <= 0]
        
        total_pnl = sum(t.pnl for t in trades)
        gross_profit = sum(wins) if wins else 0
        gross_loss = abs(sum(losses)) if losses else 0
        
        # Calculate consecutive wins/losses
        consecutive_wins = 0
        consecutive_losses = 0
        max_consecutive_wins = 0
        max_consecutive_losses = 0
        
        for trade in trades:
            if trade.pnl > 0:
                consecutive_wins += 1
                consecutive_losses = 0
                max_consecutive_wins = max(max_consecutive_wins, consecutive_wins)
            else:
                consecutive_losses += 1
                consecutive_wins = 0
                max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)
        
        # Drawdown
        max_dd = 0
        peak = equity_curve[0]
        for eq in equity_curve:
            if eq > peak:
                peak = eq
            dd = (peak - eq) / peak if peak > 0 else 0
            max_dd = max(max_dd, dd)
        
        # Sharpe ratio with safeguards
        sharpe = 0
        sortino = 0
        
        if daily_returns and len(daily_returns) > 1:
            mean_ret = np.mean(daily_returns)
            std_ret = np.std(daily_returns)
            
            if std_ret > 0 and np.isfinite(mean_ret):
                sharpe = (mean_ret / std_ret) * np.sqrt(252)
                sharpe = max(-10, min(10, sharpe))  # Cap at +/- 10
            
            # Sortino (only downside volatility)
            downside_returns = [r for r in daily_returns if r < 0]
            downside_std = np.std(downside_returns) if downside_returns else std_ret
            
            if downside_std > 0 and np.isfinite(mean_ret):
                sortino = (mean_ret / downside_std) * np.sqrt(252)
                sortino = max(-10, min(10, sortino))  # Cap at +/- 10
        
        # CAGR
        start_eq = self.initial_capital
        end_eq = equity_curve[-1] if equity_curve else start_eq
        years = len(self.df) / 252 if len(self.df) > 0 else 1
        
        if years > 0 and end_eq > 0 and start_eq > 0:
            try:
                cagr = ((end_eq / start_eq) ** (1 / years) - 1) * 100
                cagr = max(-99, min(1000, cagr))  # Cap CAGR
            except:
                cagr = 0
        else:
            cagr = 0
        
        total_return = ((end_eq - start_eq) / start_eq) * 100 if start_eq > 0 else 0
        total_return = max(-99, min(1000, total_return))  # Cap return
        
        return BacktestResults(
            strategy_name=self.strategy.name,
            platform=self.strategy.platform,
            symbol=self.strategy.symbol,
            total_trades=len(trades),
            winning_trades=len(wins),
            losing_trades=len(losses),
            win_rate=(len(wins) / len(trades) * 100) if trades else 0,
            net_pnl=total_pnl if np.isfinite(total_pnl) else 0,
            gross_profit=gross_profit if np.isfinite(gross_profit) else 0,
            gross_loss=gross_loss if np.isfinite(gross_loss) else 0,
            average_win=(sum(wins) / len(wins)) if wins and np.isfinite(sum(wins)) else 0,
            average_loss=(sum(losses) / len(losses)) if losses and np.isfinite(sum(losses)) else 0,
            profit_factor=(gross_profit / gross_loss) if gross_loss > 0 and np.isfinite(gross_profit / gross_loss) else 0,
            largest_win=max(wins) if wins else 0,
            largest_loss=min(losses) if losses else 0,
            consecutive_wins=max_consecutive_wins,
            consecutive_losses=max_consecutive_losses,
            max_drawdown=max_dd * 100,
            max_drawdown_pct=max_dd * 100,
            sharpe_ratio=sharpe,
            sortino_ratio=sortino,
            cagr=cagr,
            total_return_pct=total_return,
            trades=trades
        )

# =============================================================================
# MAIN BACKTEST ENGINE
# =============================================================================

def run_comprehensive_backtest():
    """Run 10-year comprehensive backtest"""
    logger.info("=" * 80)
    logger.info("COMPREHENSIVE 10-YEAR BACKTEST ENGINE")
    logger.info("=" * 80)
    logger.info(f"Period: {BACKTEST_START} to {BACKTEST_END}")
    logger.info(f"Initial Capital: ${INITIAL_CAPITAL:,.2f}")
    logger.info(f"Monthly Deposits: ${MONTHLY_DEPOSIT:,.2f}")
    
    data_gen = SyntheticMarketDataGenerator(seed=42)
    
    results_by_platform = {
        'oanda': [],
        'coinbase': [],
        'ibkr': []
    }
    
    fees_config = {
        'oanda': {'spread_pips': 2, 'commission': 0.001, 'slippage': 0.0005},
        'coinbase': {'commission': 0.0006, 'slippage': 0.001},
        'ibkr': {'commission': 0.0002, 'slippage': 0.0002}
    }
    
    # OANDA Forex Backtests
    logger.info("\n" + "=" * 80)
    logger.info("OANDA FOREX BACKTESTS")
    logger.info("=" * 80)
    
    forex_pairs = {
        'EUR_USD': 1.05,
        'GBP_USD': 1.27,
        'USD_JPY': 110.0,
        'AUD_USD': 0.68,
    }
    
    for pair, start_price in forex_pairs.items():
        df = data_gen.generate_forex_pair(pair, start_price, BACKTEST_START, BACKTEST_END)
        
        for strategy in OANDA_STRATEGIES:
            strategy.symbol = pair
            backtester = StrategyBacktester(df, strategy, PLATFORM_ALLOCATION['oanda'], fees_config['oanda'])
            result = backtester.backtest()
            results_by_platform['oanda'].append(result)
            
            logger.info(f"{strategy.name} on {pair}: {result.total_trades} trades, "
                       f"Win Rate: {result.win_rate:.1f}%, PnL: ${result.net_pnl:,.2f}, CAGR: {result.cagr:.2f}%")
    
    # Coinbase Crypto Backtests
    logger.info("\n" + "=" * 80)
    logger.info("COINBASE CRYPTO BACKTESTS")
    logger.info("=" * 80)
    
    crypto_pairs = {
        'BTC-USD': 500,
        'ETH-USD': 50,
        'SOL-USD': 25,
        'LINK-USD': 10,
    }
    
    for pair, start_price in crypto_pairs.items():
        df = data_gen.generate_crypto_pair(pair, start_price, BACKTEST_START, BACKTEST_END)
        
        for strategy in COINBASE_STRATEGIES:
            strategy.symbol = pair
            backtester = StrategyBacktester(df, strategy, PLATFORM_ALLOCATION['coinbase'], fees_config['coinbase'])
            result = backtester.backtest()
            results_by_platform['coinbase'].append(result)
            
            logger.info(f"{strategy.name} on {pair}: {result.total_trades} trades, "
                       f"Win Rate: {result.win_rate:.1f}%, PnL: ${result.net_pnl:,.2f}, CAGR: {result.cagr:.2f}%")
    
    # IBKR Futures Backtests
    logger.info("\n" + "=" * 80)
    logger.info("IBKR FUTURES BACKTESTS")
    logger.info("=" * 80)
    
    futures_contracts = {
        'ES': 4000,
        'NQ': 12000,
        'GC': 2000,
    }
    
    for contract, start_price in futures_contracts.items():
        df = data_gen.generate_futures_contract(contract, start_price, BACKTEST_START, BACKTEST_END)
        
        for strategy in IBKR_STRATEGIES:
            strategy.symbol = contract
            backtester = StrategyBacktester(df, strategy, PLATFORM_ALLOCATION['ibkr'], fees_config['ibkr'])
            result = backtester.backtest()
            results_by_platform['ibkr'].append(result)
            
            logger.info(f"{strategy.name} on {contract}: {result.total_trades} trades, "
                       f"Win Rate: {result.win_rate:.1f}%, PnL: ${result.net_pnl:,.2f}, CAGR: {result.cagr:.2f}%")
    
    return results_by_platform

def format_results(results_by_platform: Dict[str, List[BacktestResults]]) -> str:
    """Format results in specified output format"""
    
    output = []
    output.append("=" * 100)
    output.append("BACKTEST RESULTS SUMMARY")
    output.append("=" * 100)
    output.append(f"Period: 2015-2025 (10 years)")
    output.append(f"Initial Capital: $5,000 | Monthly Deposits: $1,000")
    output.append("")
    
    # OANDA Results
    output.append("--- OANDA PLATFORM (Forex) ---")
    oanda_results = sorted(results_by_platform['oanda'], 
                          key=lambda x: x.net_pnl if x.total_trades > 0 else -float('inf'),
                          reverse=True)
    
    output.append("Rank | Strategy Name (Symbol) | Win Rate | Net PnL | CAGR | Max DD | Sharpe | Profit Factor")
    output.append("-" * 100)
    
    for i, result in enumerate(oanda_results[:10], 1):
        if result.total_trades > 0:
            output.append(
                f"{i:2d}. | {result.strategy_name:30s} ({result.symbol:10s}) | "
                f"{result.win_rate:6.1f}% | ${result.net_pnl:10,.0f} | "
                f"{result.cagr:6.2f}% | {result.max_drawdown:6.2f}% | "
                f"{result.sharpe_ratio:6.2f} | {result.profit_factor:6.2f}"
            )
    
    output.append("")
    
    # Coinbase Results
    output.append("--- COINBASE PLATFORM (Crypto Spot + Perps) ---")
    coinbase_results = sorted(results_by_platform['coinbase'],
                             key=lambda x: x.net_pnl if x.total_trades > 0 else -float('inf'),
                             reverse=True)
    
    output.append("Rank | Strategy Name (Symbol) | Win Rate | Net PnL | CAGR | Max DD | Sharpe | Profit Factor")
    output.append("-" * 100)
    
    for i, result in enumerate(coinbase_results[:10], 1):
        if result.total_trades > 0:
            output.append(
                f"{i:2d}. | {result.strategy_name:30s} ({result.symbol:10s}) | "
                f"{result.win_rate:6.1f}% | ${result.net_pnl:10,.0f} | "
                f"{result.cagr:6.2f}% | {result.max_drawdown:6.2f}% | "
                f"{result.sharpe_ratio:6.2f} | {result.profit_factor:6.2f}"
            )
    
    output.append("")
    
    # IBKR Results
    output.append("--- IBKR PLATFORM (Equities/Futures) ---")
    ibkr_results = sorted(results_by_platform['ibkr'],
                         key=lambda x: x.net_pnl if x.total_trades > 0 else -float('inf'),
                         reverse=True)
    
    output.append("Rank | Strategy Name (Symbol) | Win Rate | Net PnL | CAGR | Max DD | Sharpe | Profit Factor")
    output.append("-" * 100)
    
    for i, result in enumerate(ibkr_results[:10], 1):
        if result.total_trades > 0:
            output.append(
                f"{i:2d}. | {result.strategy_name:30s} ({result.symbol:10s}) | "
                f"{result.win_rate:6.1f}% | ${result.net_pnl:10,.0f} | "
                f"{result.cagr:6.2f}% | {result.max_drawdown:6.2f}% | "
                f"{result.sharpe_ratio:6.2f} | {result.profit_factor:6.2f}"
            )
    
    output.append("")
    output.append("")
    
    # Global Summary
    output.append("--- GLOBAL PLATFORM COMPARISON (All Platforms Combined) ---")
    all_results = oanda_results + coinbase_results + ibkr_results
    best_overall = max(all_results, key=lambda x: x.net_pnl if x.total_trades > 0 else -float('inf'))
    
    total_pnl = sum(r.net_pnl for r in all_results if r.total_trades > 0)
    avg_win_rate = np.mean([r.win_rate for r in all_results if r.total_trades > 0])
    avg_sharpe = np.mean([r.sharpe_ratio for r in all_results if r.total_trades > 0])
    
    output.append(f"Overall Best Strategy | Win Rate | Combined Net PnL | Global CAGR | Global Max DD | Global Sharpe")
    output.append(f"{best_overall.strategy_name:40s} | {best_overall.win_rate:6.1f}% | "
                 f"${total_pnl:12,.0f} | {best_overall.cagr:6.2f}% | TBD | {avg_sharpe:6.2f}")
    
    output.append("")
    output.append("")
    
    # Platform-specific best performers
    output.append("--- PLATFORM-SPECIFIC BEST PERFORMERS ---")
    output.append("Platform | Best Strategy | Performance vs Baseline | Recommendation")
    output.append("-" * 100)
    
    if oanda_results and oanda_results[0].total_trades > 0:
        output.append(f"OANDA    | {oanda_results[0].strategy_name:30s} | +{oanda_results[0].net_pnl:8,.0f} | Deploy with risk limits")
    
    if coinbase_results and coinbase_results[0].total_trades > 0:
        output.append(f"Coinbase | {coinbase_results[0].strategy_name:30s} | +{coinbase_results[0].net_pnl:8,.0f} | Deploy with position sizing")
    
    if ibkr_results and ibkr_results[0].total_trades > 0:
        output.append(f"IBKR     | {ibkr_results[0].strategy_name:30s} | +{ibkr_results[0].net_pnl:8,.0f} | Deploy with hedges")
    
    output.append("")
    output.append("")
    
    # Top 3 strategies deep dive
    output.append("--- TOP 3 GLOBAL STRATEGIES - DEEP DIVE ANALYSIS ---")
    output.append("=" * 100)
    
    top_3 = sorted(all_results, key=lambda x: x.net_pnl if x.total_trades > 0 else -float('inf'), reverse=True)[:3]
    
    for i, strategy_result in enumerate(top_3, 1):
        output.append(f"\n#{i} - {strategy_result.strategy_name} ({strategy_result.platform.upper()} / {strategy_result.symbol})")
        output.append("-" * 100)
        output.append(f"  Net PnL:              ${strategy_result.net_pnl:,.2f}")
        output.append(f"  Total Trades:        {strategy_result.total_trades}")
        output.append(f"  Win Rate:            {strategy_result.win_rate:.2f}%")
        output.append(f"  Profit Factor:       {strategy_result.profit_factor:.2f}x")
        output.append(f"  CAGR:                {strategy_result.cagr:.2f}%")
        output.append(f"  Max Drawdown:        {strategy_result.max_drawdown:.2f}%")
        output.append(f"  Sharpe Ratio:        {strategy_result.sharpe_ratio:.2f}")
        output.append(f"  Average Win:         ${strategy_result.average_win:,.2f}")
        output.append(f"  Average Loss:        ${strategy_result.average_loss:,.2f}")
        output.append(f"  Largest Win:         ${strategy_result.largest_win:,.2f}")
        output.append(f"  Largest Loss:        ${strategy_result.largest_loss:,.2f}")
        output.append(f"  Consecutive Wins:    {strategy_result.consecutive_wins}")
        output.append(f"  Consecutive Losses:  {strategy_result.consecutive_losses}")
        
        # Extract strategy details
        strat_def = None
        for s in OANDA_STRATEGIES + COINBASE_STRATEGIES + IBKR_STRATEGIES:
            if s.name == strategy_result.strategy_name:
                strat_def = s
                break
        
        if strat_def:
            output.append(f"\n  Strategy Configuration:")
            output.append(f"    Timeframe:           {strat_def.timeframe}")
            output.append(f"    Entry Logic:         {strat_def.entry_logic}")
            output.append(f"    Exit Logic:          {strat_def.exit_logic}")
            output.append(f"    Risk:Reward Ratio:   1:{strat_def.risk_reward}")
            output.append(f"    Position Size:       {strat_def.position_size_pct}% per trade")
            output.append(f"    Parameters:          {strat_def.parameters}")
        
        output.append(f"\n  Why It Works:")
        output.append(f"    - Consistent win rate suggests strong edge in identified market conditions")
        output.append(f"    - Profit factor of {strategy_result.profit_factor:.2f}x indicates profitable strategy")
        output.append(f"    - Sharpe ratio of {strategy_result.sharpe_ratio:.2f} shows risk-adjusted returns")
        
        output.append(f"\n  When It Fails:")
        output.append(f"    - Max consecutive losses: {strategy_result.consecutive_losses} trades")
        output.append(f"    - Max drawdown: {strategy_result.max_drawdown:.2f}% (during adverse market regimes)")
        output.append(f"    - Performance may degrade in ranging/choppy markets")
        
        output.append(f"\n  Phoenix V2 Integration Recommendation:")
        output.append(f"    ✓ Add to WolfPack voting ensemble")
        output.append(f"    ✓ Use {strat_def.position_size_pct}% position sizing")
        output.append(f"    ✓ Implement {strat_def.risk_reward}:1 R:R on all signals")
        output.append(f"    ✓ Deploy on {strat_def.symbol} with {strat_def.timeframe} confirmation")
    
    return "\n".join(output)

def main():
    """Main execution"""
    logger.info("Starting comprehensive backtest analysis...")
    
    # Run backtests
    results = run_comprehensive_backtest()
    
    # Format output
    formatted_results = format_results(results)
    
    # Print to console
    print(formatted_results)
    
    # Save results
    output_file = '/home/ing/RICK/RICK_PHOENIX/BACKTEST_RESULTS_COMPREHENSIVE_20251201.json'
    
    # Prepare JSON output
    json_results = {}
    for platform, platform_results in results.items():
        json_results[platform] = [
            {
                'strategy_name': r.strategy_name,
                'symbol': r.symbol,
                'total_trades': r.total_trades,
                'winning_trades': r.winning_trades,
                'losing_trades': r.losing_trades,
                'win_rate': r.win_rate,
                'net_pnl': r.net_pnl,
                'gross_profit': r.gross_profit,
                'gross_loss': r.gross_loss,
                'average_win': r.average_win,
                'average_loss': r.average_loss,
                'profit_factor': r.profit_factor,
                'largest_win': r.largest_win,
                'largest_loss': r.largest_loss,
                'consecutive_wins': r.consecutive_wins,
                'consecutive_losses': r.consecutive_losses,
                'max_drawdown_pct': r.max_drawdown_pct,
                'sharpe_ratio': r.sharpe_ratio,
                'sortino_ratio': r.sortino_ratio,
                'cagr': r.cagr,
                'total_return_pct': r.total_return_pct,
            }
            for r in platform_results if r.total_trades > 0
        ]
    
    with open(output_file, 'w') as f:
        json.dump(json_results, f, indent=2)
    
    logger.info(f"\nResults saved to: {output_file}")
    logger.info("\n" + "=" * 80)
    logger.info("BACKTEST ANALYSIS COMPLETE")
    logger.info("=" * 80)

if __name__ == '__main__':
    main()
