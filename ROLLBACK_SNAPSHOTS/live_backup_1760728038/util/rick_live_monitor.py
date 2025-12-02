#!/usr/bin/env python3
"""
Rick Live Trading Monitor - Real-Time SwarmBot Tracking & Market Updates
Comprehensive live feed showing:
- All active SwarmBots and their positions
- Market regime detection and changes
- Trade entries/exits with P&L
- Position management actions (trailing stops, etc.)
PIN: 841921
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from util.rick_narrator import rick_narrate

logger = logging.getLogger(__name__)

@dataclass
class SwarmBotStatus:
    """SwarmBot position status"""
    bot_id: str
    pair: str
    direction: str  # LONG/SHORT
    entry_price: float
    current_price: float
    stop_loss: float
    take_profit: float
    position_size: float
    unrealized_pnl: float
    pnl_pct: float
    duration_minutes: int
    trailing_stop_active: bool
    status: str  # ACTIVE, CLOSING, CLOSED

class LiveTradingMonitor:
    """
    Real-time monitoring and narration of all trading activity
    """
    
    def __init__(self):
        self.active_swarm_bots: Dict[str, SwarmBotStatus] = {}
        self.current_regime = "UNKNOWN"
        self.regime_confidence = 0.0
        self.last_regime_change = None
        self.total_realized_pnl = 0.0
        self.total_trades_today = 0
        self.wins_today = 0
        self.losses_today = 0
    
    def narrate_regime_detection(self, regime: str, confidence: float, 
                                 indicators: Dict[str, Any]) -> None:
        """Narrate market regime detection"""
        regime_change = regime != self.current_regime
        
        details = {
            "regime": regime,
            "confidence": confidence,
            "previous_regime": self.current_regime if regime_change else None,
            "regime_changed": regime_change,
            "indicators": indicators,
            "trend_strength": indicators.get('trend_strength', 0),
            "volatility": indicators.get('volatility', 0)
        }
        
        if regime_change:
            self.current_regime = regime
            self.last_regime_change = datetime.now(timezone.utc)
            rick_narrate("REGIME_CHANGE", details, venue="regime_detector")
        else:
            rick_narrate("REGIME_UPDATE", details, venue="regime_detector")
        
        self.regime_confidence = confidence
    
    def narrate_swarmbot_spawn(self, bot_id: str, pair: str, direction: str,
                               entry_price: float, stop_loss: float, 
                               take_profit: float, position_size: float) -> None:
        """Narrate SwarmBot creation and position entry"""
        risk = abs(entry_price - stop_loss) * position_size
        reward = abs(take_profit - entry_price) * position_size
        rr_ratio = reward / risk if risk > 0 else 0
        
        details = {
            "bot_id": bot_id,
            "pair": pair,
            "direction": direction,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "take_profit": target,
            "position_size": position_size,
            "risk_amount": risk,
            "reward_potential": reward,
            "rr_ratio": rr_ratio,
            "current_regime": self.current_regime
        }
        
        # Create SwarmBot status
        bot_status = SwarmBotStatus(
            bot_id=bot_id,
            pair=pair,
            direction=direction,
            entry_price=entry_price,
            current_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            position_size=position_size,
            unrealized_pnl=0.0,
            pnl_pct=0.0,
            duration_minutes=0,
            trailing_stop_active=False,
            status="ACTIVE"
        )
        
        self.active_swarm_bots[bot_id] = bot_status
        rick_narrate("SWARMBOT_SPAWN", details, symbol=pair, venue="swarm_orchestrator")
    
    def narrate_position_update(self, bot_id: str, current_price: float,
                                unrealized_pnl: float, pnl_pct: float) -> None:
        """Narrate position price update"""
        if bot_id not in self.active_swarm_bots:
            return
        
        bot = self.active_swarm_bots[bot_id]
        bot.current_price = current_price
        bot.unrealized_pnl = unrealized_pnl
        bot.pnl_pct = pnl_pct
        
        # Only narrate significant moves (>0.5% or every 5 minutes)
        if abs(pnl_pct) > 0.5:
            details = {
                "bot_id": bot_id,
                "pair": bot.pair,
                "direction": bot.direction,
                "entry_price": bot.entry_price,
                "current_price": current_price,
                "unrealized_pnl": unrealized_pnl,
                "pnl_pct": pnl_pct,
                "distance_to_tp": abs(bot.take_profit - current_price),
                "distance_to_sl": abs(current_price - bot.stop_loss),
                "status": "winning" if unrealized_pnl > 0 else "losing"
            }
            
            rick_narrate("POSITION_UPDATE", details, symbol=bot.pair, venue="swarmbot")
    
    def narrate_trailing_stop_activated(self, bot_id: str, new_stop_loss: float,
                                       profit_locked: float) -> None:
        """Narrate trailing stop activation"""
        if bot_id not in self.active_swarm_bots:
            return
        
        bot = self.active_swarm_bots[bot_id]
        bot.trailing_stop_active = True
        bot.stop_loss = new_stop_loss
        
        details = {
            "bot_id": bot_id,
            "pair": bot.pair,
            "old_stop_loss": bot.stop_loss,
            "new_stop_loss": new_stop_loss,
            "profit_locked": profit_locked,
            "current_pnl": bot.unrealized_pnl,
            "action": "TRAILING_STOP_ACTIVATED"
        }
        
        rick_narrate("TRAILING_STOP", details, symbol=bot.pair, venue="swarmbot")
    
    def narrate_position_close(self, bot_id: str, exit_price: float, 
                              realized_pnl: float, close_reason: str) -> None:
        """Narrate position closure with P&L"""
        if bot_id not in self.active_swarm_bots:
            return
        
        bot = self.active_swarm_bots[bot_id]
        bot.status = "CLOSED"
        
        outcome = "WIN" if realized_pnl > 0 else "LOSS" if realized_pnl < 0 else "BREAKEVEN"
        self.total_realized_pnl += realized_pnl
        self.total_trades_today += 1
        
        if outcome == "WIN":
            self.wins_today += 1
        elif outcome == "LOSS":
            self.losses_today += 1
        
        win_rate = (self.wins_today / self.total_trades_today * 100) if self.total_trades_today > 0 else 0
        
        details = {
            "bot_id": bot_id,
            "pair": bot.pair,
            "direction": bot.direction,
            "entry_price": bot.entry_price,
            "exit_price": exit_price,
            "position_size": bot.position_size,
            "realized_pnl": realized_pnl,
            "pnl_pct": (realized_pnl / (bot.entry_price * bot.position_size)) * 100,
            "outcome": outcome,
            "close_reason": close_reason,
            "duration_minutes": bot.duration_minutes,
            "total_pnl_today": self.total_realized_pnl,
            "trades_today": self.total_trades_today,
            "win_rate_today": win_rate
        }
        
        rick_narrate("POSITION_CLOSED", details, symbol=bot.pair, venue="swarmbot")
        
        # Remove from active bots
        del self.active_swarm_bots[bot_id]
    
    def narrate_market_update(self, pairs_data: Dict[str, Dict[str, float]]) -> None:
        """Narrate general market conditions"""
        details = {
            "pairs_monitored": list(pairs_data.keys()),
            "pair_count": len(pairs_data),
            "current_regime": self.current_regime,
            "regime_confidence": self.regime_confidence,
            "active_positions": len(self.active_swarm_bots),
            "total_exposure": sum(bot.position_size * bot.current_price 
                                 for bot in self.active_swarm_bots.values()),
            "unrealized_pnl": sum(bot.unrealized_pnl 
                                 for bot in self.active_swarm_bots.values())
        }
        
        rick_narrate("MARKET_UPDATE", details, venue="market_monitor")
    
    def narrate_daily_summary(self) -> None:
        """Narrate end-of-day summary"""
        win_rate = (self.wins_today / self.total_trades_today * 100) if self.total_trades_today > 0 else 0
        avg_win = (self.total_realized_pnl / self.wins_today) if self.wins_today > 0 else 0
        
        details = {
            "total_trades": self.total_trades_today,
            "wins": self.wins_today,
            "losses": self.losses_today,
            "win_rate": win_rate,
            "total_pnl": self.total_realized_pnl,
            "avg_win": avg_win,
            "largest_win": max((bot.unrealized_pnl for bot in self.active_swarm_bots.values()), default=0),
            "regime_today": self.current_regime
        }
        
        rick_narrate("DAILY_SUMMARY", details, venue="session_manager")
    
    def get_active_bots_snapshot(self) -> List[Dict[str, Any]]:
        """Get current snapshot of all active SwarmBots"""
        return [asdict(bot) for bot in self.active_swarm_bots.values()]
    
    def narrate_risk_alert(self, alert_type: str, details_dict: Dict[str, Any]) -> None:
        """Narrate risk management alerts"""
        details = {
            "alert_type": alert_type,
            "severity": details_dict.get('severity', 'MEDIUM'),
            "message": details_dict.get('message', ''),
            "active_positions": len(self.active_swarm_bots),
            "total_exposure": sum(bot.position_size * bot.current_price 
                                 for bot in self.active_swarm_bots.values()),
            "action_required": details_dict.get('action_required', False)
        }
        
        rick_narrate("RISK_ALERT", details, venue="risk_manager")


# Global monitor instance
_live_monitor = None

def get_live_monitor() -> LiveTradingMonitor:
    """Get global live trading monitor instance"""
    global _live_monitor
    if _live_monitor is None:
        _live_monitor = LiveTradingMonitor()
    return _live_monitor


# Convenience functions for easy integration

def narrate_regime_detection(regime: str, confidence: float, 
                            indicators: Dict[str, Any]) -> None:
    """Narrate regime detection"""
    get_live_monitor().narrate_regime_detection(regime, confidence, indicators)

def narrate_swarmbot_spawn(bot_id: str, pair: str, direction: str,
                          entry_price: float, stop_loss: float, 
                          take_profit: float, position_size: float) -> None:
    """Narrate SwarmBot spawn"""
    get_live_monitor().narrate_swarmbot_spawn(bot_id, pair, direction,
                                              entry_price, stop_loss,
                                              take_profit, position_size)

def narrate_position_update(bot_id: str, current_price: float,
                           unrealized_pnl: float, pnl_pct: float) -> None:
    """Narrate position update"""
    get_live_monitor().narrate_position_update(bot_id, current_price,
                                               unrealized_pnl, pnl_pct)

def narrate_trailing_stop_activated(bot_id: str, new_stop_loss: float,
                                   profit_locked: float) -> None:
    """Narrate trailing stop"""
    get_live_monitor().narrate_trailing_stop_activated(bot_id, new_stop_loss,
                                                       profit_locked)

def narrate_position_close(bot_id: str, exit_price: float, 
                          realized_pnl: float, close_reason: str) -> None:
    """Narrate position close"""
    get_live_monitor().narrate_position_close(bot_id, exit_price,
                                              realized_pnl, close_reason)

def narrate_market_update(pairs_data: Dict[str, Dict[str, float]]) -> None:
    """Narrate market update"""
    get_live_monitor().narrate_market_update(pairs_data)

def narrate_risk_alert(alert_type: str, details: Dict[str, Any]) -> None:
    """Narrate risk alert"""
    get_live_monitor().narrate_risk_alert(alert_type, details)

def get_active_bots_snapshot() -> List[Dict[str, Any]]:
    """Get active bots snapshot"""
    return get_live_monitor().get_active_bots_snapshot()


# Test function
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("\n=== Testing Live Trading Monitor ===\n")
    
    monitor = LiveTradingMonitor()
    
    # Test 1: Regime detection
    indicators = {
        "trend_strength": 0.75,
        "volatility": 0.032,
        "momentum": "bullish"
    }
    narrate_regime_detection("BULL", 0.82, indicators)
    
    # Test 2: SwarmBot spawn
    narrate_swarmbot_spawn("BOT_001", "EUR_USD", "LONG", 1.1604, 1.1580, 1.1680, 5000)
    
    # Test 3: Position update
    narrate_position_update("BOT_001", 1.1625, 105.0, 0.9)
    
    # Test 4: Trailing stop
    narrate_trailing_stop_activated("BOT_001", 1.1600, 80.0)
    
    # Test 5: Position close (win)
    narrate_position_close("BOT_001", 1.1675, 355.0, "TAKE_PROFIT")
    
    # Test 6: Regime change
    indicators["momentum"] = "bearish"
    narrate_regime_detection("BEAR", 0.74, indicators)
    
    print("\n✅ Live trading monitor test complete!")
    print(f"Total P&L: ${monitor.total_realized_pnl:.2f}")
    print(f"Trades: {monitor.total_trades_today}")
    print(f"Win Rate: {(monitor.wins_today/monitor.total_trades_today*100):.1f}%")
