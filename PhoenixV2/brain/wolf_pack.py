"""
PhoenixV2 Brain Module - Wolf Pack Strategies

The Wolf Pack is a collection of simple, independent strategies that vote
on trade direction. When 2+ strategies agree, the signal is stronger.
"""
import logging
import json
import importlib
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
from PhoenixV2.core.state_manager import StateManager
from .strategies.high_probability_core import (
    LiquiditySweepWolf,
    SupplyDemandWolf,
    MultiTFConfluenceWolf,
    SupplyDemandMultiTapWolf,
    ChartPatternBreakWolf,
    RangeMidlineBounceWolf,
    LongWickReversalWolf,
    MomentumShiftWolf,
    CCIDivergenceWolf,
)
from .strategies.correlation_wolf import CorrelationWolf
from .strategies.ema_scalper import EMAScalperWolf
from .strategies.fibonacci_wolf import FibonacciWolf
from .strategies.fvg_wolf import FVGWolf

logger = logging.getLogger("WolfPack")


class MomentumWolf:
    """
    Momentum-based strategy.
    Looks at price changes over recent periods.
    """
    
    def vote(self, market_data: Dict[str, Any]) -> str:
        # Extract momentum indicators
        price = market_data.get('price', 0)
        price_prev = market_data.get('price_prev', price)
        momentum = market_data.get('momentum', 0)  # % change
        
        # Calculate momentum if not provided
        if momentum == 0 and price > 0 and price_prev > 0:
            momentum = (price - price_prev) / price_prev
        
        # Strong momentum threshold: 0.2% move
        if momentum > 0.002:
            return "BUY"
        elif momentum < -0.002:
            return "SELL"
        return "HOLD"


class MeanReversionWolf:
    """
    Mean reversion strategy - fade extremes.
    When price is far from moving average, bet on return.
    """
    
    def vote(self, market_data: Dict[str, Any]) -> str:
        price = market_data.get('price', 0)
        sma_20 = market_data.get('sma_20', price)
        
        if price == 0 or sma_20 == 0:
            return "HOLD"
        
        # Calculate deviation from mean
        deviation = (price - sma_20) / sma_20
        
        # Extreme deviation threshold: 1.5%
        if deviation > 0.015:
            return "SELL"  # Price too high, sell for reversion
        elif deviation < -0.015:
            return "BUY"  # Price too low, buy for reversion
        return "HOLD"


class BreakoutWolf:
    """
    Breakout detection strategy.
    Looks for price breaking key levels with volume.
    """
    
    def vote(self, market_data: Dict[str, Any]) -> str:
        price = market_data.get('price', 0)
        high_20 = market_data.get('high_20', 0)
        low_20 = market_data.get('low_20', float('inf'))
        volume = market_data.get('volume', 0)
        avg_volume = market_data.get('avg_volume', 1)
        
        # Need volume confirmation (1.5x average)
        volume_confirmed = volume > avg_volume * 1.5 if avg_volume > 0 else False
        
        if price > high_20 and volume_confirmed:
            return "BUY"  # Bullish breakout
        elif price < low_20 and volume_confirmed:
            return "SELL"  # Bearish breakout
        return "HOLD"


class TrendFollowWolf:
    """
    Trend following strategy.
    Uses moving average crossovers.
    """
    
    def vote(self, market_data: Dict[str, Any]) -> str:
        sma_20 = market_data.get('sma_20', 0)
        sma_50 = market_data.get('sma_50', 0)
        price = market_data.get('price', 0)
        
        if sma_20 == 0 or sma_50 == 0:
            return "HOLD"
        
        # Golden cross / death cross with price confirmation
        if sma_20 > sma_50 * 1.005 and price > sma_20:
            return "BUY"  # Uptrend confirmed
        elif sma_20 < sma_50 * 0.995 and price < sma_20:
            return "SELL"  # Downtrend confirmed
        return "HOLD"


class RangeWolf:
    """
    Range-bound trading strategy.
    Buys at support, sells at resistance in ranging markets.
    """
    
    def vote(self, market_data: Dict[str, Any]) -> str:
        price = market_data.get('price', 0)
        support = market_data.get('support', 0)
        resistance = market_data.get('resistance', float('inf'))
        adx = market_data.get('adx', 50)  # ADX measures trend strength
        
        # Only trade ranges when ADX < 25 (no strong trend)
        if adx > 25:
            return "HOLD"
        
        if support > 0 and resistance < float('inf'):
            range_size = resistance - support
            if range_size > 0:
                position_in_range = (price - support) / range_size
                
                if position_in_range < 0.2:
                    return "BUY"  # Near support
                elif position_in_range > 0.8:
                    return "SELL"  # Near resistance
        
        return "HOLD"


class WolfPack:
    """
    The Wolf Pack Aggregator.
    Collects votes from all wolves and returns consensus.
    """
    
    def __init__(self, state_manager: Optional[StateManager] = None):
        self.state_manager = state_manager
        # Default inline strategies
        default_wolves = [
            ({'name': 'momentum', 'instance': MomentumWolf()}),
            ({'name': 'mean_reversion', 'instance': MeanReversionWolf()}),
            ({'name': 'breakout', 'instance': BreakoutWolf()}),
            ({'name': 'trend_follow', 'instance': TrendFollowWolf()}),
            ({'name': 'range', 'instance': RangeWolf()}),
            ({'name': 'liquidity_sweep', 'instance': LiquiditySweepWolf()}),
            ({'name': 'supply_demand', 'instance': SupplyDemandWolf()}),
            ({'name': 'multi_tf_confluence', 'instance': MultiTFConfluenceWolf()}),
            ({'name': 'supply_demand_multi_tap', 'instance': SupplyDemandMultiTapWolf()}),
            ({'name': 'chart_pattern_break', 'instance': ChartPatternBreakWolf()}),
            ({'name': 'range_midline_bounce', 'instance': RangeMidlineBounceWolf()}),
            ({'name': 'long_wick_reversal', 'instance': LongWickReversalWolf()}),
            ({'name': 'momentum_shift', 'instance': MomentumShiftWolf()}),
            ({'name': 'cci_divergence', 'instance': CCIDivergenceWolf()}),
            ({'name': 'ema_scalper', 'instance': EMAScalperWolf()}),
            ({'name': 'correlation_wolf', 'instance': CorrelationWolf()}),
            ({'name': 'fibonacci_wolf', 'instance': FibonacciWolf()}),
            ({'name': 'fvg_wolf', 'instance': FVGWolf()}),
        ]
        
        self.wolves = []
        
        # Load configuration from strategies.json
        config_path = Path(__file__).resolve().parents[1] / 'config' / 'strategies.json'
        strategy_config = {}
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    data = json.load(f)
                    
                    # Check for configuration lock
                    if data.get('configuration_locked', False):
                        logger.warning("WolfPack: STRATEGY CONFIGURATION IS LOCKED. Agents are prohibited from modifying strategies without approval.")
                    
                    for item in data.get('strategies', []):
                        strategy_config[item['name']] = item
                logger.info(f"WolfPack: Loaded strategy config from {config_path}")
            except Exception as e:
                logger.error(f"WolfPack: Failed to load strategy config: {e}")

        # 1. Add default wolves if enabled (or if not in config, assume enabled)
        for w in default_wolves:
            name = w['name']
            conf = strategy_config.get(name)
            if conf:
                if conf.get('enabled', True):
                    self.wolves.append(w)
            else:
                # If not in config, include by default
                self.wolves.append(w)

        # 2. Load custom/dynamic strategies from config
        for name, conf in strategy_config.items():
            if not conf.get('enabled', True):
                continue
            # Skip if already loaded (e.g. it was a default one)
            if any(w['name'] == name for w in self.wolves):
                continue
            
            module_path = conf.get('module')
            class_name = conf.get('class')
            if module_path and class_name:
                try:
                    mod = importlib.import_module(module_path)
                    cls = getattr(mod, class_name)
                    instance = cls()
                    self.wolves.append({'name': name, 'instance': instance})
                    logger.info(f"WolfPack: Dynamically loaded strategy {name} from {module_path}")
                except Exception as e:
                    logger.error(f"WolfPack: Failed to load dynamic strategy {name}: {e}")

        # Assign Squads
        self._assign_squads()

        # Minimum consensus not used for Winner-Takes-All logic, but kept as a safeguard
        self.min_consensus = 1
        # If state manager has optimized params for strategies, apply them
        try:
            loaded_names = []
            for w in self.wolves:
                name = w.get('name')
                inst = w.get('instance')
                if not name or not inst:
                    continue
                if self.state_manager:
                    try:
                        params = self.state_manager.get_strategy_params(name)
                        if params and hasattr(inst, 'set_params'):
                            # If the stored params contain a nested 'params' key, use it
                            p = params.get('params') if isinstance(params, dict) and 'params' in params else params
                            if isinstance(p, dict):
                                try:
                                    inst.set_params(**p)
                                except TypeError:
                                    # If set_params signature doesn't match, try passing kwargs individually
                                    try:
                                        for k, v in p.items():
                                            if hasattr(inst, k):
                                                setattr(inst, k, v)
                                    except Exception:
                                        pass
                            else:
                                try:
                                    inst.set_params(**params)
                                except Exception:
                                    pass
                            loaded_names.append(name)
                    except Exception:
                        pass
            if loaded_names:
                logger.info(f"WolfPack: Applied strategy params from StateManager for: {', '.join(loaded_names)}")
        except Exception:
            pass

    def _assign_squads(self):
        """
        Assign strategies to squads for synergy analysis.
        """
        self.squads = {
            'sniper': ['fibonacci_wolf', 'fvg_wolf', 'supply_demand', 'supply_demand_multi_tap', 'liquidity_sweep'],
            'trend': ['trend_follow', 'momentum', 'ema_scalper', 'breakout', 'momentum_shift'],
            'reversion': ['mean_reversion', 'range', 'range_midline_bounce', 'cci_divergence', 'long_wick_reversal'],
            'macro': ['correlation_wolf', 'multi_tf_confluence']
        }
        logger.info(f"WolfPack: Squads assigned: {list(self.squads.keys())}")

    def get_consensus(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Poll all wolves and return consensus vote.
        """
        votes = {"BUY": 0.0, "SELL": 0.0, "HOLD": 0.0}
        counts = {"BUY": 0, "SELL": 0, "HOLD": 0}
        total_weight = 0.0
        strategy_votes = {}
        
        # Squad voting tracking
        squad_votes = {
            'sniper': {'BUY': 0, 'SELL': 0},
            'trend': {'BUY': 0, 'SELL': 0},
            'reversion': {'BUY': 0, 'SELL': 0},
            'macro': {'BUY': 0, 'SELL': 0}
        }

        # If we have a DataFrame of candles, enrich market_data with computed indicators
        df = market_data.get('df') if market_data else None
        # Ensure df behaves like a pandas DataFrame (has iloc and 'close' column)
        df_is_pandas = False
        try:
            if df is not None and hasattr(df, 'iloc') and 'close' in getattr(df, 'columns', []):
                df_is_pandas = True
        except Exception:
            df_is_pandas = False
        if df is not None and df_is_pandas:
            try:
                # Ensure columns are lowercase: open, high, low, close, volume
                cols = [c.lower() for c in df.columns]
                # current price
                last = float(df.iloc[-1]['close'])
                prev = float(df.iloc[-2]['close']) if len(df) > 1 else last
                market_data['price'] = last
                market_data['price_prev'] = prev
                # compute simple moving averages
                market_data['sma_20'] = float(df['close'].rolling(window=min(20, len(df))).mean().iloc[-1]) if len(df) > 1 else last
                market_data['sma_50'] = float(df['close'].rolling(window=min(50, len(df))).mean().iloc[-1]) if len(df) > 1 else last
                market_data['high_20'] = float(df['high'].rolling(window=min(20, len(df))).max().iloc[-1])
                market_data['low_20'] = float(df['low'].rolling(window=min(20, len(df))).min().iloc[-1])
                market_data['volume'] = float(df['volume'].iloc[-1])
                market_data['avg_volume'] = float(df['volume'].rolling(window=min(20, len(df))).mean().iloc[-1])
                # Simple momentum %
                market_data['momentum'] = (last - prev) / prev if prev != 0 else 0
            except Exception:
                # if we cannot compute, leave market_data as-is
                pass

        for w in self.wolves:
            wolf = w['instance']
            name = w.get('name') or getattr(wolf, 'name', wolf.__class__.__name__)
            try:
                vote = wolf.vote(market_data)
            except Exception as e:
                logger.exception(f"Strategy {name} failed: {e}")
                # Treat failed strategy as no-op (HOLD)
                vote = 'HOLD'
            # Determine weight from state manager if available
            weight = 1.0
            # Determine weight from state manager if available and check quarantine
            weight = 1.0
            try:
                if self.state_manager:
                    # If the strategy is quarantined, skip it
                    status = self.state_manager.get_strategy_status(name)
                    if status == 'quarantined' or status == 'kill-switched':
                        logger.info(f"Skipping {name} due to status: {status}")
                        strategy_votes[name] = {'vote': vote, 'weight': 0.0, 'status': status}
                        continue
                    weight = float(self.state_manager.get_strategy_weight(name))
            except Exception:
                weight = 1.0
            votes[vote] = votes.get(vote, 0.0) + weight
            counts[vote] = counts.get(vote, 0) + 1
            strategy_votes[name] = {'vote': vote, 'weight': weight}
            total_weight += weight
            
            # Track squad votes
            if vote in ['BUY', 'SELL']:
                for squad_name, members in self.squads.items():
                    if name in members:
                        squad_votes[squad_name][vote] += 1
        
        # Winner-Takes-All: pick the highest sharpe among BUY/SELL votes
        best_sharpe = -float('inf')
        best_candidate = None
        for name, meta in strategy_votes.items():
            vote = meta.get('vote')
            if vote not in ['BUY', 'SELL']:
                continue
            # Skip quarantined or kill-switched strategies
            if meta.get('status') in ('quarantined', 'kill-switched'):
                continue
            sharpe = 0.0
            try:
                if self.state_manager:
                    sharpe = float(self.state_manager.get_strategy_params(name).get('sharpe', 0.0))
            except Exception:
                sharpe = 0.0
            # fallback to weight if no sharpe
            if sharpe == 0.0:
                sharpe = meta.get('weight', 0.0)
            if sharpe > best_sharpe:
                best_sharpe = sharpe
                best_candidate = (name, meta)

        # SYNERGY FILTER:
        # Require at least one SNIPER vote OR strong consensus (>=2 votes)
        sniper_active = (squad_votes['sniper']['BUY'] > 0) or (squad_votes['sniper']['SELL'] > 0)
        total_buy = counts['BUY']
        total_sell = counts['SELL']
        
        # If we have a candidate, check if it passes the synergy filter
        if best_candidate:
            name, meta = best_candidate
            direction = meta.get('vote')
            
            # Filter Logic:
            # 1. If Sniper Squad votes, we trust it (Precision Entry).
            # 2. If Trend Squad votes, we need at least 2 votes total (Confirmation).
            # 3. If Macro Squad votes, we need at least 2 votes total (Confirmation).
            
            is_valid = False
            if name in self.squads['sniper']:
                is_valid = True # Snipers are trusted solo
            elif counts[direction] >= 2:
                is_valid = True # Consensus is trusted
            elif name in self.squads['macro'] and counts[direction] >= 1:
                 # Macro is allowed solo if weight is high (handled by sharpe logic), but let's be safe
                 is_valid = True
            
            if is_valid:
                weight = meta.get('weight', 1.0)
                # Confidence: relative to total weight, boost for high sharpe
                boost = 1.2 if best_sharpe > 1.5 else 1.0
                confidence = min(1.0, (weight / total_weight) * boost) if total_weight > 0 else boost
                return {
                    'direction': direction,
                    'confidence': float(confidence),
                    'votes': votes,
                    'strategy_votes': strategy_votes,
                    'top_strategy': name,
                    'source': 'WolfPack_WinnerTakesAll',
                    'squad_votes': squad_votes
                }
            else:
                logger.info(f"WolfPack: Signal filtered. {name} voted {direction} but lacked synergy/consensus. (Snipers: {squad_votes['sniper']})")
                return {
                    "direction": "HOLD",
                    "confidence": 0.0,
                    "votes": votes,
                    "strategy_votes": strategy_votes,
                    "source": "WolfPack",
                    "reason": "Filtered by Synergy Logic"
                }
        else:
            return {
                "direction": "HOLD",
                "confidence": 0.0,
                "votes": votes,
                "strategy_votes": strategy_votes,
                "source": "WolfPack"
            }
