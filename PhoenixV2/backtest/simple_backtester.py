import pandas as pd
import numpy as np

class SimpleBacktester:
    def __init__(self, strategy_class, data, initial_capital=10000):
        self.strategy_class = strategy_class
        self.data = data
        self.capital = initial_capital
        self.trades = []

    def run(self, **kwargs):
        """
        Runs the strategy with specific parameters (kwargs) on the data.
        """
        # Instantiate strategy with overrides - prefer direct kwargs when possible
        try:
            strategy = self.strategy_class(**kwargs)
        except Exception:
            try:
                strategy = self.strategy_class(overrides=kwargs)
            except Exception:
                strategy = self.strategy_class()
        
        position = None # None, 'BUY', 'SELL'
        entry_price = 0
        sl = 0
        tp = 0
        
        for i in range(50, len(self.data)): # Skip warmup
            row = self.data.iloc[i]
            prev_row = self.data.iloc[i-1]
            
            # Check Exit
            if position:
                pnl = 0
                if position == 'BUY':
                    if row['low'] <= sl: pnl = sl - entry_price # Stop Hit
                    elif row['high'] >= tp: pnl = tp - entry_price # Target Hit
                elif position == 'SELL':
                    if row['high'] >= sl: pnl = entry_price - sl # Stop Hit
                    elif row['low'] <= tp: pnl = entry_price - tp # Target Hit
                
                if pnl != 0:
                    self.capital += (pnl * 1000) # Assume 1000 units
                    self.trades.append(pnl)
                    position = None
                    continue

            # Check Entry (if flat)
            if position is None:
                # Pass slice of data to strategy (simulating live)
                # Note: In real optimized backtest we'd vectorise, but this mimics the live engine logic
                signal = None
                if hasattr(strategy, 'generate_signal_from_row'):
                    try:
                        signal = strategy.generate_signal_from_row(row, prev_row)
                    except Exception:
                        signal = None
                else:
                    # Fall back to `vote` API if available
                    try:
                        # Build minimal df slice for strategies expecting a df
                        signal = None
                        if hasattr(strategy, 'vote'):
                            market_data = {'df': self.data.iloc[max(0, i-50):i+1]}
                            v = strategy.vote(market_data)
                            if v in ['BUY', 'SELL']:
                                signal = {'direction': v, 'confidence': 0.7}
                    except Exception:
                        signal = None
                
                if signal:
                    position = signal['direction']
                    entry_price = row['close']
                    # Simple ATR-based SL/TP for testing if strategy doesn't provide absolute levels
                    atr = (row['high'] - row['low'])
                    if position == 'BUY':
                        sl = entry_price - (atr * kwargs.get('sl_mult', 1.5))
                        tp = entry_price + (atr * kwargs.get('sl_mult', 1.5) * kwargs.get('rr', 2.0))
                    else:
                        sl = entry_price + (atr * kwargs.get('sl_mult', 1.5))
                        tp = entry_price - (atr * kwargs.get('sl_mult', 1.5) * kwargs.get('rr', 2.0))

        return self.get_stats()

    def get_stats(self):
        wins = [t for t in self.trades if t > 0]
        losses = [t for t in self.trades if t <= 0]
        win_rate = len(wins) / len(self.trades) if self.trades else 0
        total_pnl = sum(self.trades)
        return {"win_rate": win_rate, "pnl": total_pnl, "trades": len(self.trades)}
"""
Simple Backtester for PhoenixV2 strategies.
"""
