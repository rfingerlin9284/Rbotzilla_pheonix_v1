"""
PhoenixV2 Brain Module - Wolf Pack Strategies

The Wolf Pack is a collection of simple, independent strategies that vote
on trade direction. When 2+ strategies agree, the signal is stronger.
"""
import logging
from typing import Dict, List, Any

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
    
    def __init__(self):
        self.wolves = [
            MomentumWolf(),
            MeanReversionWolf(),
            BreakoutWolf(),
            TrendFollowWolf(),
            RangeWolf()
        ]
        self.min_consensus = 2  # Need 2+ wolves to agree

    def get_consensus(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Poll all wolves and return consensus vote.
        """
        votes = {"BUY": 0, "SELL": 0, "HOLD": 0}
        
        for wolf in self.wolves:
            vote = wolf.vote(market_data)
            votes[vote] = votes.get(vote, 0) + 1
        
        # Determine winner
        buy_votes = votes["BUY"]
        sell_votes = votes["SELL"]
        
        if buy_votes >= self.min_consensus and buy_votes > sell_votes:
            return {
                "direction": "BUY",
                "confidence": buy_votes / len(self.wolves),
                "votes": votes,
                "source": "WolfPack"
            }
        elif sell_votes >= self.min_consensus and sell_votes > buy_votes:
            return {
                "direction": "SELL",
                "confidence": sell_votes / len(self.wolves),
                "votes": votes,
                "source": "WolfPack"
            }
        else:
            return {
                "direction": "HOLD",
                "confidence": 0.0,
                "votes": votes,
                "source": "WolfPack"
            }
