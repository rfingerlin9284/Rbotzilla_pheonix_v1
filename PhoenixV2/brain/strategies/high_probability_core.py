"""
High Probability Core Strategies
Implementations of the top-priority, high-probability strategies called for in the spec:
- Liquidity Sweep / Stop Hunt Reversal
- Institutional Supply & Demand (Fresh Zone)
- Multi-Timeframe Confluence

Each strategy provides a `vote(market_data)` method that returns 'BUY'|'SELL'|'HOLD'
and defines a `name` attribute to be used by the learning subsystem.
"""
from typing import Dict, Any
import logging
import os
import json
import pandas as pd


class BaseWolf:
    def __init__(self, overrides=None):
        self.params = self.load_params(overrides)

    def load_params(self, overrides):
        # Default
        defaults = {'sl_mult': 1.5, 'rr': 2.0, 'lookback': 20}
        # Load Golden Params from file if exists and apply nested 'params' field when present
        path = "PhoenixV2/config/golden_params.json"
        logger = logging.getLogger('Strategy')
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    saved = json.load(f)
                    cls_name = self.__class__.__name__
                    if cls_name in saved:
                        # If the saved entry contains a nested 'params' field, prefer that
                        entry = saved.get(cls_name, {})
                        params = entry.get('params') if isinstance(entry, dict) else None
                        if params and isinstance(params, dict):
                            defaults.update(params)
                            logger.info(f"Loaded golden params for {cls_name} from {path}: {params}")
                        else:
                            # Backwards compatibility: direct mapping
                            try:
                                defaults.update(entry)
                                logger.info(f"Loaded golden params (legacy) for {cls_name} from {path}")
                            except Exception:
                                logger.debug(f"No valid params for {cls_name} inside {path}")
            except Exception:
                logger.exception(f"Failed to read golden params from {path}")
        # Apply Overrides (from Backtester)
        if overrides:
            try:
                defaults.update(overrides)
            except Exception:
                pass
        return defaults


class LiquiditySweepWolf(BaseWolf):
    """Detects false breakout / liquidity sweep setups.
    Heuristic:
    - Price creates a wick beyond a swing high/low then closes back into the range
    - Candle wick size is larger than recent average (1.5x)
    - A subsequent reversal candle forms (close back inside range)
    """
    name = 'liquidity_sweep'

    def __init__(self, wick_multiplier: float = 1.0, overrides=None):
        super().__init__(overrides)
        self.wick_multiplier = wick_multiplier

    def set_params(self, wick_multiplier: float = 1.5):
        self.wick_multiplier = wick_multiplier

    def vote(self, market_data: Dict[str, Any]) -> str:
        price = market_data.get('price', 0)
        close = market_data.get('close', price)
        high = market_data.get('high', price)
        low = market_data.get('low', price)
        prev_high = market_data.get('prev_high', high)
        prev_low = market_data.get('prev_low', low)
        avg_wick = market_data.get('avg_wick', 0)

        # avoid edge cases
        if not price or not avg_wick:
            return 'HOLD'

        upper_wick = high - max(close, market_data.get('open', close))
        lower_wick = min(close, market_data.get('open', close)) - low

        # Bullish False Breakout (liquidity grab above previous high then fail)
        if high > prev_high and upper_wick > avg_wick * self.wick_multiplier and close < prev_high:
            return 'SELL'  # Institutions swept stops then reversed down

        # Bearish False Breakout (liquidity grab below previous low then fail)
        if low < prev_low and lower_wick > avg_wick * self.wick_multiplier and close > prev_low:
            return 'BUY'  # Institutions swept stops below then reversed up

        return 'HOLD'

    def generate_signal_from_row(self, row, prev_row):
        # Construct mini market_data for live style vote
        market_data = {
            'open': float(row.get('open', 0)),
            'high': float(row.get('high', 0)),
            'low': float(row.get('low', 0)),
            'close': float(row.get('close', 0)),
            'price': float(row.get('close', 0)),
            'prev_high': float(prev_row.get('high', float(row.get('high', 0)))) if prev_row is not None else float(row.get('high', 0)),
            'prev_low': float(prev_row.get('low', float(row.get('low', 0)))) if prev_row is not None else float(row.get('low', 0)),
            'avg_wick': float(((float(row.get('high', 0)) - float(row.get('low', 0))) * 0.25))
        }
        v = self.vote(market_data)
        if v in ['BUY', 'SELL']:
            return {'direction': v, 'confidence': 0.8}
        return None


class SupplyDemandWolf(BaseWolf):
    """Detects supply/demand zones and fresh zones that favor reversal.
    Heuristic:
    - Fresh zone: Price hasn't revisited zone for N bars
    - Price enters zone and forms a directional rejection candle
    - Volume at zone is supportive (lower volume on tests for bullish demand)
    """
    name = 'supply_demand'

    def vote(self, market_data: Dict[str, Any]) -> str:
        price = market_data.get('price', 0)
        zone_low = market_data.get('zone_low', 0)
        zone_high = market_data.get('zone_high', 0)
        last_test_bars = market_data.get('zone_last_test_bars', 0)
        rejection_body = market_data.get('rejection_body', 0)
        volume = market_data.get('volume', 0)
        avg_volume = market_data.get('avg_volume', 1)

        if not price or not zone_low or not zone_high:
            return 'HOLD'

        # if zone is fresh (has not been tested recently) and price enters it
        if zone_low <= price <= zone_high and last_test_bars > 10:
            # If rejection_body is strong and volume does not rise -> probable reversal
            if rejection_body and rejection_body >= 0.25 * (zone_high - zone_low):
                if volume <= avg_volume:
                    # If price enters low part of zone -> buy (use midline for simplicity)
                    midline = zone_low + (zone_high - zone_low) * 0.5
                    if price <= midline:
                        return 'BUY'
                    # If price enters top part -> sell
                    if price > midline:
                        return 'SELL'

        return 'HOLD'

    def generate_signal_from_row(self, row, prev_row):
        market_data = {
            'price': float(row.get('close', 0)),
            'zone_low': float(row.get('zone_low', 0)),
            'zone_high': float(row.get('zone_high', 0)),
            'zone_last_test_bars': int(row.get('zone_last_test_bars', 0)),
            'rejection_body': float(row.get('rejection_body', 0)),
            'volume': float(row.get('volume', 0)),
            'avg_volume': float(row.get('avg_volume', 0)) or 1.0
        }
        v = self.vote(market_data)
        if v in ['BUY', 'SELL']:
            return {'direction': v, 'confidence': 0.7}
        return None


class MultiTFConfluenceWolf(BaseWolf):
    """Checks for alignment across time frames: weekly/daily/higher timeframe trend aligned with local timeframe.
    Heuristic:
    - If HTF trend (e.g., weekly/daily) is bullish and local timeframe shows pullback in demand zone, signal BUY.
    - Vice versa for bearish setups.
    """
    name = 'multi_tf_confluence'

    def vote(self, market_data: Dict[str, Any]) -> str:
        htf_trend = market_data.get('htf_trend', 'NEUTRAL').lower()
        ltf_trend = market_data.get('ltf_trend', 'NEUTRAL').lower()
        pullback = market_data.get('pullback', 0)  # % pullback in LTF
        if htf_trend == 'bull' and ltf_trend in ['pullback', 'weak'] and pullback > 0.01:
            return 'BUY'
        if htf_trend == 'bear' and ltf_trend in ['pullback', 'weak'] and pullback > 0.01:
            return 'SELL'
        return 'HOLD'

    def generate_signal_from_row(self, row, prev_row):
        market_data = {
            'htf_trend': row.get('htf_trend', 'NEUTRAL'),
            'ltf_trend': row.get('ltf_trend', 'NEUTRAL'),
            'pullback': float(row.get('pullback', 0))
        }
        v = self.vote(market_data)
        if v in ['BUY', 'SELL']:
            return {'direction': v, 'confidence': 0.6}
        return None


__all__ = ['LiquiditySweepWolf', 'SupplyDemandWolf', 'MultiTFConfluenceWolf']


class SupplyDemandMultiTapWolf(BaseWolf):
    """Detects zones that have been tapped multiple times and signals on the next test.
    Heuristic:
    - Zone (low/high) observed and counted; if taps >=3, mark as multi-tap
    - On next test, if rejection candle forms, it signals reversal
    """
    name = 'supply_demand_multi_tap'

    def vote(self, market_data: Dict[str, Any]) -> str:
        price = market_data.get('price', 0)
        zone_low = market_data.get('zone_low', 0)
        zone_high = market_data.get('zone_high', 0)
        taps = market_data.get('zone_taps', 0)
        rejection = market_data.get('rejection_body', 0)
        if zone_low <= price <= zone_high and taps >= 3 and rejection and rejection > 0.2 * (zone_high - zone_low):
            # If in lower part of zone -> buy, upper part -> sell
            if price < (zone_low + (zone_high - zone_low) * 0.5):
                return 'BUY'
            return 'SELL'
        return 'HOLD'

    def generate_signal_from_row(self, row, prev_row):
        market_data = {'price': float(row.get('close', 0)), 'zone_low': float(row.get('zone_low', 0)), 'zone_high': float(row.get('zone_high', 0)), 'zone_taps': int(row.get('zone_taps', 0)), 'rejection_body': float(row.get('rejection_body', 0))}
        v = self.vote(market_data)
        if v in ['BUY', 'SELL']:
            return {'direction': v, 'confidence': 0.65}
        return None


class ChartPatternBreakWolf(BaseWolf):
    """Detects classical chart pattern breakouts (triangles, flags).
    Heuristic:
    - If consolidation flag identified and price breaks the pattern boundary with volume spike -> signal
    """
    name = 'chart_pattern_break'

    def vote(self, market_data: Dict[str, Any]) -> str:
        breakout_up = market_data.get('breakout_up', False)
        breakout_down = market_data.get('breakout_down', False)
        volume = market_data.get('volume', 0)
        avg_volume = market_data.get('avg_volume', 1)
        if breakout_up and volume > avg_volume * 1.5:
            return 'BUY'
        if breakout_down and volume > avg_volume * 1.5:
            return 'SELL'
        return 'HOLD'

    def generate_signal_from_row(self, row, prev_row):
        market_data = {'breakout_up': row.get('breakout_up', False), 'breakout_down': row.get('breakout_down', False), 'volume': float(row.get('volume', 0)), 'avg_volume': float(row.get('avg_volume', 0)) or 1}
        v = self.vote(market_data)
        if v in ['BUY', 'SELL']:
            return {'direction': v, 'confidence': 0.7}
        return None


class RangeMidlineBounceWolf(BaseWolf):
    """Range midline bounce logic: signal when price rejects at midline within a range.
    Heuristic:
    - Identify range support and resistance -> compute midline
    - If price approaches midline from advantage side and rejection candle, signal to the edge
    """
    name = 'range_midline_bounce'

    def vote(self, market_data: Dict[str, Any]) -> str:
        price = market_data.get('price', 0)
        support = market_data.get('support', 0)
        resistance = market_data.get('resistance', 0)
        midline = (support + resistance) / 2 if support and resistance else None
        rejection_body = market_data.get('rejection_body', 0)
        adx = market_data.get('adx', 20)
        # Only trade midline when ADX indicates non-trending (adx < 25)
        if not midline or adx > 25:
            return 'HOLD'
        # If close to midline and rejection observed
        if abs(price - midline) < (resistance - support) * 0.1 and rejection_body > (resistance - support) * 0.2:
            # If midline candle rejects downward -> SELL toward support
            if price < midline:
                return 'SELL'
            else:
                return 'BUY'
        return 'HOLD'

    def generate_signal_from_row(self, row, prev_row):
        market_data = {'price': float(row.get('close', 0)), 'support': float(row.get('support', 0)), 'resistance': float(row.get('resistance', 0)), 'rejection_body': float(row.get('rejection_body', 0)), 'adx': float(row.get('adx', 20))}
        v = self.vote(market_data)
        if v in ['BUY', 'SELL']:
            return {'direction': v, 'confidence': 0.65}
        return None

__all__.extend(['SupplyDemandMultiTapWolf', 'ChartPatternBreakWolf', 'RangeMidlineBounceWolf'])


class LongWickReversalWolf(BaseWolf):
    """Identifies long wick candles at key levels signaling reversals.
    Heuristic:
    - Candle wick (upper or lower) > 2x body and at key level
    - Close returns inside previous candle's range
    """
    name = 'long_wick_reversal'

    def vote(self, market_data: Dict[str, Any]) -> str:
        price = market_data.get('price', 0)
        close = market_data.get('close', price)
        open_p = market_data.get('open', close)
        high = market_data.get('high', close)
        low = market_data.get('low', close)
        prev_high = market_data.get('prev_high', high)
        prev_low = market_data.get('prev_low', low)

        body = abs(close - open_p)
        if body == 0:
            return 'HOLD'
        upper_wick = high - max(close, open_p)
        lower_wick = min(close, open_p) - low

        if upper_wick > body * 2 and close < prev_high:
            return 'SELL'
        if lower_wick > body * 2 and close > prev_low:
            return 'BUY'
        return 'HOLD'

    def generate_signal_from_row(self, row, prev_row):
        market_data = {'price': float(row.get('close', 0)), 'open': float(row.get('open', 0)), 'high': float(row.get('high', 0)), 'low': float(row.get('low', 0)), 'prev_high': float(prev_row.get('high', float(row.get('high', 0)))) if prev_row is not None else float(row.get('high', 0)), 'prev_low': float(prev_row.get('low', float(row.get('low', 0)))) if prev_row is not None else float(row.get('low', 0))}
        v = self.vote(market_data)
        if v in ['BUY', 'SELL']:
            return {'direction': v, 'confidence': 0.7}
        return None


class MomentumShiftWolf(BaseWolf):
    """Detects sudden momentum shifts: series of small candles followed by large opposite candle.
    Heuristic:
    - Several consecutive small range candles (e.g., 5)
    - Followed by one candle with range > 2x average range and opposite close
    """
    name = 'momentum_shift'

    def vote(self, market_data: Dict[str, Any]) -> str:
        df = market_data.get('df')
        if df is None:
            return 'HOLD'
        try:
            # Calculate recent candle ranges
            ranges = (df['high'] - df['low']).tail(10)
            avg_range = float(ranges.mean()) if len(ranges) > 0 else 0
            last_range = float(ranges.iloc[-1]) if len(ranges) > 0 else 0
            second_last_range = float(ranges.iloc[-2]) if len(ranges) > 1 else 0
            # Check for a series (5) of small ranges before last
            small_series = (ranges.iloc[:-1] < avg_range * 0.6).sum() >= 5 if len(ranges) > 6 else False
            if small_series and last_range > avg_range * 2:
                # Determine direction of last candle
                last_close = float(df['close'].iloc[-1])
                last_open = float(df['open'].iloc[-1])
                if last_close > last_open:
                    return 'BUY'
                else:
                    return 'SELL'
        except Exception:
            return 'HOLD'
        return 'HOLD'

    def generate_signal_from_row(self, row, prev_row):
        # MomentumShift requires a dataframe; attempt a minimal df build
        try:
            df = pd.DataFrame([prev_row, row]) if prev_row is not None else pd.DataFrame([row])
        except Exception:
            df = None
        market_data = {'df': df}
        v = self.vote(market_data)
        if v in ['BUY', 'SELL']:
            return {'direction': v, 'confidence': 0.7}
        return None


class CCIDivergenceWolf(BaseWolf):
    """Detects CCI divergence where price makes lower low but CCI shows higher low etc.
    Heuristic: Price LL and CCI HL -> Buy; Price HH and CCI LH -> Sell
    """
    name = 'cci_divergence'

    def vote(self, market_data: Dict[str, Any]) -> str:
        df = market_data.get('df')
        if df is None or 'close' not in df.columns:
            return 'HOLD'
        try:
            # Simplified CCI: typical price minus SMA / mean deviation * constant
            tp = (df['high'] + df['low'] + df['close']) / 3.0
            sma = tp.rolling(window=14).mean()
            mean_dev = (tp - sma).abs().rolling(window=14).mean()
            cci = (tp - sma) / (0.015 * mean_dev)
            # Compare last two price lows and CCI lows
            p_low1 = df['low'].iloc[-1]
            p_low2 = df['low'].iloc[-2]
            c1 = cci.iloc[-1]
            c2 = cci.iloc[-2]
            # Price lower low & CCI higher low -> bullish divergence
            if p_low1 < p_low2 and c1 > c2:
                return 'BUY'
            # Price higher high & CCI lower high -> bearish divergence
            p_high1 = df['high'].iloc[-1]
            p_high2 = df['high'].iloc[-2]
            if p_high1 > p_high2 and c1 < c2:
                return 'SELL'
        except Exception:
            return 'HOLD'
        return 'HOLD'

    def generate_signal_from_row(self, row, prev_row):
        try:
            df = pd.DataFrame([prev_row, row]) if prev_row is not None else pd.DataFrame([row])
        except Exception:
            df = None
        market_data = {'df': df}
        v = self.vote(market_data)
        if v in ['BUY', 'SELL']:
            return {'direction': v, 'confidence': 0.7}
        return None

__all__.extend(['LongWickReversalWolf', 'MomentumShiftWolf', 'CCIDivergenceWolf'])
