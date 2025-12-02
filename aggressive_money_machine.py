#!/usr/bin/env python3
"""
🚀 RICK AGGRESSIVE MONEY MACHINE
Full autonomous trading system combining:
- Wolf pack regime strategies (Bullish/Bearish/Sideways/Triage)
- Quant hedge multi-condition analysis
- Smart tight trailing stops
- Rick Hive autonomous closed loop

PIN: 841921 | $5K → $50K Capital Growth Mode
Designed for 1min+ timeframes with aggressive position management
"""

import asyncio
import logging
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
import json

sys.path.insert(0, str(Path(__file__).parent))

from foundation.rick_charter import RickCharter
from hive.quant_hedge_rules import QuantHedgeRules, HedgeAction
from logic.regime_detector import StochasticRegimeDetector, MarketRegime
from brokers.oanda_connector import OandaConnector
from util.narration_logger import log_narration
from util.mode_manager import get_connector_environment, get_mode_info
from capital_manager import CapitalManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/aggressive_money_machine.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AggressiveMoneyMachine:
    """
    Autonomous money-making engine combining all RICK systems
    - Regime detection → Wolf pack strategy selection
    - Quant hedge analysis → Position sizing
    - Smart trailing → Profit extraction
    - Rick Hive → Autonomous decision making
    """
    
    def __init__(self, pin: int = 841921, environment: Optional[str] = None):
        """Initialize aggressive money machine"""
        if not RickCharter.validate_pin(pin):
            raise PermissionError("Invalid PIN - access denied")
        
        self.pin = pin
        self.charter = RickCharter()
        # If no explicit environment passed, read from mode toggles
        if environment is None:
            try:
                self.environment = get_connector_environment("oanda")
            except Exception:
                self.environment = "practice"
        else:
            self.environment = environment
        
        # Initialize subsystems
        logger.info("🚀 Initializing RICK Aggressive Money Machine...")
        
        try:
            self.oanda = OandaConnector(pin=pin, environment=self.environment)
            logger.info(f"✅ OANDA {self.environment.upper()} connected")
        except Exception as e:
            logger.error(f"❌ OANDA connection failed: {e}")
            self.oanda = None
        
        self.regime_detector = StochasticRegimeDetector(pin=pin)
        self.quant_hedge = QuantHedgeRules(pin=pin)
        self.capital_manager = CapitalManager(pin=pin)
        
        # Trading state
        self.current_regime = None
        self.open_positions: Dict[str, Dict] = {}
        self.trade_history: List[Dict] = []
        self.session_pnl = 0.0
        self.session_trades = 0
        
        # Aggressive settings
        self.risk_per_trade_pct = 0.02  # 2% risk (aggressive)
        self.trailing_stop_distance_pips = 15  # Tight trailing
        self.min_win_rate_target = 0.70  # Need 70%+ to reach goals
        
        # Canary/Live mode detection
        self.is_live_mode = environment == "live"
        
        logger.info("=" * 80)
        logger.info("🤖 RICK AGGRESSIVE MONEY MACHINE - READY")
        logger.info("=" * 80)
        logger.info(f"Mode: {self.environment.upper()}")
        logger.info(f"Capital: ${self.capital_manager.current_capital:,.2f}")
        logger.info(f"Risk/Trade: {self.risk_per_trade_pct:.0%}")
        logger.info(f"Trailing Stop: {self.trailing_stop_distance_pips} pips")
        logger.info(f"Target Win Rate: {self.min_win_rate_target:.0%}+")
        logger.info("=" * 80)
        print()
    
    async def run_autonomous_loop(self, symbols: List[str], check_interval_seconds: int = 60):
        """
        Main autonomous trading loop
        Continuously monitors market, detects regime, places trades, manages positions
        """
        logger.info(f"📊 Starting autonomous loop for {symbols}")
        logger.info(f"    Check interval: {check_interval_seconds}s")
        
        iteration = 0
        start_time = datetime.now(timezone.utc)
        
        while True:
            iteration += 1
            loop_start = datetime.now(timezone.utc)
            
            try:
                # =====================================================================
                # STEP 1: DETECT MARKET REGIME
                # =====================================================================
                regime_data = await self._detect_regime(symbols)
                self.current_regime = regime_data['regime']
                
                # =====================================================================
                # STEP 2: EVALUATE QUANT HEDGE CONDITIONS
                # =====================================================================
                hedge_analysis = await self._analyze_hedge_conditions()
                
                # =====================================================================
                # STEP 3: SELECT WOLF PACK STRATEGY
                # =====================================================================
                wolf_pack_config = self._select_wolf_pack_strategy(
                    regime=self.current_regime,
                    hedge_action=hedge_analysis['primary_action']
                )
                
                # =====================================================================
                # STEP 4: SCAN FOR TRADE OPPORTUNITIES
                # =====================================================================
                opportunities = await self._scan_trade_opportunities(
                    symbols=symbols,
                    wolf_pack=wolf_pack_config
                )
                
                # =====================================================================
                # STEP 5: PLACE TRADES (With Guardian Gates)
                # =====================================================================
                for opp in opportunities:
                    await self._execute_trade_with_hedging(opp, hedge_analysis)
                
                # =====================================================================
                # STEP 6: MANAGE OPEN POSITIONS (Tight Trailing Stops)
                # =====================================================================
                await self._manage_open_positions()
                
                # =====================================================================
                # STEP 7: LOG SESSION ACTIVITY
                # =====================================================================
                loop_duration_ms = (datetime.now(timezone.utc) - loop_start).total_seconds() * 1000
                
                if iteration % 10 == 0:  # Log every 10 iterations
                    logger.info(f"Iteration {iteration} | "
                               f"Regime: {self.current_regime} | "
                               f"Open: {len(self.open_positions)} | "
                               f"Session PnL: ${self.session_pnl:+,.2f} | "
                               f"Loop: {loop_duration_ms:.0f}ms")
                    
                    log_narration(
                        event_type="MACHINE_HEARTBEAT",
                        details={
                            "iteration": iteration,
                            "regime": self.current_regime,
                            "open_positions": len(self.open_positions),
                            "session_pnl": self.session_pnl,
                            "trades_today": self.session_trades,
                            "loop_ms": loop_duration_ms
                        },
                        symbol="SYSTEM",
                        venue="aggressive_machine"
                    )
                
                # Wait for next check
                await asyncio.sleep(check_interval_seconds)
                
            except KeyboardInterrupt:
                logger.warning("⚠️  Autonomous loop interrupted by user")
                await self._emergency_close_all_positions()
                break
            except Exception as e:
                logger.error(f"❌ Loop error: {e}", exc_info=True)
                await asyncio.sleep(5)  # Brief wait before retry
    
    async def _detect_regime(self, symbols: List[str]) -> Dict:
        """Detect current market regime using stochastic analysis"""
        try:
            # Get price data for regime detection
            price_samples = []
            for symbol in symbols[:3]:  # Sample 3 symbols for regime
                try:
                    prices = await self._get_price_history(symbol, periods=50)
                    price_samples.extend(prices)
                except:
                    pass
            
            if not price_samples:
                return {'regime': MarketRegime.TRIAGE, 'confidence': 0.5}
            
            # Detect regime
            regime_data = self.regime_detector.detect_regime(price_samples)
            
            logger.debug(f"Regime detected: {regime_data.regime.value} "
                        f"(conf: {regime_data.confidence:.2f})")
            
            return {
                'regime': regime_data.regime.value,
                'confidence': regime_data.confidence,
                'volatility': regime_data.volatility,
                'trend_strength': regime_data.trend_strength
            }
        except Exception as e:
            logger.warning(f"Regime detection error: {e}")
            return {'regime': 'triage', 'confidence': 0.3}
    
    async def _analyze_hedge_conditions(self) -> Dict:
        """Analyze quant hedge conditions for position sizing"""
        try:
            # Use capital manager for account info
            nav = self.capital_manager.current_capital
            margin_used = 0  # Simplified for now
            
            # Mock price data for quant hedge analysis
            prices = np.array([100, 101, 99, 102, 100, 103] * 10, dtype=float)
            volume = np.array([1000] * len(prices), dtype=float)
            
            analysis = self.quant_hedge.analyze_market_conditions(
                prices=prices,
                volume=volume,
                account_nav=nav,
                margin_used=margin_used,
                open_positions=len(self.open_positions)
            )
            
            return {
                'primary_action': analysis.primary_action,
                'position_size_multiplier': analysis.position_size_multiplier,
                'risk_level': analysis.risk_level,
                'severity': analysis.severity_score
            }
        except Exception as e:
            logger.warning(f"Hedge analysis error: {e}")
            return {
                'primary_action': HedgeAction.MODERATE_LONG.value,
                'position_size_multiplier': 1.0,
                'risk_level': 'moderate',
                'severity': 50
            }
    
    def _select_wolf_pack_strategy(self, regime: str, hedge_action: str) -> Dict:
        """Select wolf pack strategy based on regime and hedge action"""
        
        # Wolf pack configurations
        wolf_packs = {
            'bull': {
                'name': 'Bullish Wolf Pack',
                'entry_signals': ['RSI < 50', 'MA crossover up', 'EMA(20) > EMA(50)'],
                'position_multiplier': 1.2,
                'trailing_activation_pct': 0.50,  # Activate trailing at +50% profit
                'aggressive': True
            },
            'bear': {
                'name': 'Bearish Wolf Pack',
                'entry_signals': ['RSI > 50', 'MA crossover down', 'EMA(20) < EMA(50)'],
                'position_multiplier': 1.0,
                'trailing_activation_pct': 0.75,
                'aggressive': False
            },
            'sideways': {
                'name': 'Sideways/Range Wolf Pack',
                'entry_signals': ['Bollinger Band touch', 'Support/Resistance bounce'],
                'position_multiplier': 0.8,
                'trailing_activation_pct': 0.40,
                'aggressive': False
            },
            'triage': {
                'name': 'Triage Wolf Pack (Safe)',
                'entry_signals': ['High confidence setups only'],
                'position_multiplier': 0.5,
                'trailing_activation_pct': 1.0,  # Tight profit taking
                'aggressive': False
            }
        }
        
        # Adjust for hedge action
        config = wolf_packs.get(regime, wolf_packs['triage'])
        
        if hedge_action in ['reduce_exposure', 'pause_trading']:
            config['position_multiplier'] *= 0.5
        elif hedge_action == 'full_long':
            config['position_multiplier'] *= 1.3
        
        return config
    
    async def _scan_trade_opportunities(self, symbols: List[str], wolf_pack: Dict) -> List[Dict]:
        """Scan for trade opportunities matching wolf pack pattern"""
        opportunities = []
        
        for symbol in symbols:
            try:
                # Get latest price action
                prices = await self._get_price_history(symbol, periods=20)
                if not prices or len(prices) < 5:
                    continue
                
                # Simple pattern detection (mock implementation)
                # In production: use proper technical analysis
                latest_price = prices[-1]
                prev_price = prices[-2]
                
                # BUY signal: price up with volume
                if latest_price > prev_price:
                    opportunities.append({
                        'symbol': symbol,
                        'side': 'BUY',
                        'entry_price': latest_price,
                        'confidence': 0.75,
                        'signal_source': 'wolf_pack',
                        'wolf_pack': wolf_pack['name']
                    })
                
                # SELL signal: price down
                elif latest_price < prev_price:
                    opportunities.append({
                        'symbol': symbol,
                        'side': 'SELL',
                        'entry_price': latest_price,
                        'confidence': 0.70,
                        'signal_source': 'wolf_pack',
                        'wolf_pack': wolf_pack['name']
                    })
            
            except Exception as e:
                logger.debug(f"Opportunity scan error for {symbol}: {e}")
        
        return opportunities
    
    async def _execute_trade_with_hedging(self, opportunity: Dict, hedge_analysis: Dict):
        """Execute trade with proper hedging and position sizing"""
        try:
            symbol = opportunity['symbol']
            side = opportunity['side']
            entry_price = opportunity['entry_price']
            
            # Calculate position size with hedging multiplier
            account_nav = self.capital_manager.current_capital
            risk_amount = account_nav * self.risk_per_trade_pct
            
            # Apply hedge multiplier
            position_size = risk_amount / 100  # Simplified calc
            position_size *= hedge_analysis['position_size_multiplier']
            
            # Calculate SL/TP
            sl_distance = 100  # pips
            tp_distance = int(sl_distance * self.charter.MIN_RISK_REWARD_RATIO)
            
            if side == "BUY":
                stop_loss = entry_price - (sl_distance * 0.0001)
                take_profit = entry_price + (tp_distance * 0.0001)
            else:
                stop_loss = entry_price + (sl_distance * 0.0001)
                take_profit = entry_price - (tp_distance * 0.0001)
            
            # Log trade
            trade_id = f"AMM_{len(self.trade_history)+1}_{int(datetime.now().timestamp())}"
            
            self.open_positions[trade_id] = {
                'symbol': symbol,
                'side': side,
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'position_size': position_size,
                'entry_time': datetime.now(timezone.utc),
                'trailing_stop': entry_price + (self.trailing_stop_distance_pips * 0.0001 if side == "BUY" else -self.trailing_stop_distance_pips * 0.0001),
                'trailing_active': False
            }
            
            self.session_trades += 1
            
            logger.info(f"✅ TRADE OPENED: {trade_id}")
            logger.info(f"   {side} {symbol} @ {entry_price:.5f}")
            logger.info(f"   SL: {stop_loss:.5f} | TP: {take_profit:.5f}")
            
            log_narration(
                event_type="TRADE_EXECUTED",
                details={
                    "trade_id": trade_id,
                    "symbol": symbol,
                    "side": side,
                    "entry": entry_price,
                    "sl": stop_loss,
                    "tp": take_profit,
                    "wolf_pack": opportunity.get('wolf_pack', 'unknown')
                },
                symbol=symbol,
                venue="aggressive_machine"
            )
        
        except Exception as e:
            logger.error(f"Trade execution error: {e}")
    
    async def _manage_open_positions(self):
        """Manage open positions with tight trailing stops"""
        closed_trades = []
        
        for trade_id, trade in list(self.open_positions.items()):
            try:
                # Get current price
                current_price = await self._get_current_price(trade['symbol'])
                if not current_price:
                    continue
                
                # Check TP/SL
                if trade['side'] == 'BUY':
                    if current_price >= trade['take_profit']:
                        self._close_trade(trade_id, current_price, 'TP_HIT')
                        closed_trades.append((trade_id, 'win'))
                    elif current_price <= trade['stop_loss']:
                        self._close_trade(trade_id, current_price, 'SL_HIT')
                        closed_trades.append((trade_id, 'loss'))
                    else:
                        # Update trailing stop if profitable
                        profit_pct = (current_price - trade['entry_price']) / trade['entry_price']
                        if profit_pct > 0.01:  # 1% profit triggers trailing
                            trade['trailing_active'] = True
                            trade['trailing_stop'] = max(
                                trade['trailing_stop'],
                                current_price - (self.trailing_stop_distance_pips * 0.0001)
                            )
                        
                        if trade['trailing_active'] and current_price < trade['trailing_stop']:
                            self._close_trade(trade_id, current_price, 'TRAILING_HIT')
                            closed_trades.append((trade_id, 'win'))
                
                else:  # SELL
                    if current_price <= trade['take_profit']:
                        self._close_trade(trade_id, current_price, 'TP_HIT')
                        closed_trades.append((trade_id, 'win'))
                    elif current_price >= trade['stop_loss']:
                        self._close_trade(trade_id, current_price, 'SL_HIT')
                        closed_trades.append((trade_id, 'loss'))
                    else:
                        # Trailing stop for short
                        profit_pct = (trade['entry_price'] - current_price) / trade['entry_price']
                        if profit_pct > 0.01:
                            trade['trailing_active'] = True
                            trade['trailing_stop'] = min(
                                trade['trailing_stop'],
                                current_price + (self.trailing_stop_distance_pips * 0.0001)
                            )
                        
                        if trade['trailing_active'] and current_price > trade['trailing_stop']:
                            self._close_trade(trade_id, current_price, 'TRAILING_HIT')
                            closed_trades.append((trade_id, 'win'))
            
            except Exception as e:
                logger.debug(f"Position management error for {trade_id}: {e}")
        
        # Update session PnL
        for trade_id, outcome in closed_trades:
            if trade_id in self.trade_history:
                if outcome == 'win':
                    self.session_pnl += 100  # Simplified
                else:
                    self.session_pnl -= 100
    
    def _close_trade(self, trade_id: str, exit_price: float, reason: str):
        """Close a trade and record result"""
        if trade_id not in self.open_positions:
            return
        
        trade = self.open_positions.pop(trade_id)
        
        # Calculate P&L
        if trade['side'] == 'BUY':
            pnl = (exit_price - trade['entry_price']) * trade['position_size']
        else:
            pnl = (trade['entry_price'] - exit_price) * trade['position_size']
        
        self.trade_history.append({
            'trade_id': trade_id,
            'symbol': trade['symbol'],
            'side': trade['side'],
            'entry': trade['entry_price'],
            'exit': exit_price,
            'pnl': pnl,
            'reason': reason,
            'duration': (datetime.now(timezone.utc) - trade['entry_time']).total_seconds()
        })
        
        logger.info(f"✅ TRADE CLOSED: {trade_id} | Reason: {reason} | PnL: ${pnl:+,.2f}")
    
    async def _get_price_history(self, symbol: str, periods: int = 50) -> List[float]:
        """Get historical price data (mock implementation)"""
        # In production: fetch from OANDA or data provider
        import random
        return [100 + random.uniform(-2, 2) for _ in range(periods)]
    
    async def _get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price (mock implementation)"""
        # In production: fetch from OANDA
        import random
        return 100 + random.uniform(-1, 1)
    
    async def _emergency_close_all_positions(self):
        """Emergency close all open positions"""
        logger.warning("🚨 EMERGENCY: Closing all positions...")
        for trade_id in list(self.open_positions.keys()):
            self._close_trade(trade_id, 0, "EMERGENCY_CLOSE")
        logger.warning(f"Closed {len(self.trade_history)} positions")

# Required import for numpy operations
import numpy as np

async def main():
    """Launch aggressive money machine"""
    try:
        machine = AggressiveMoneyMachine(
            pin=841921,
            environment=None  # Dynamically determined from util.mode_manager (.upgrade_toggle)
        )
        
        # Symbols to trade (major pairs + crypto)
        symbols = [
            'EUR_USD', 'GBP_USD', 'USD_JPY',
            'AUD_USD', 'USD_CAD',
        ]
        
        # Run autonomous loop
        await machine.run_autonomous_loop(
            symbols=symbols,
            check_interval_seconds=60  # Check every 60 seconds
        )
    
    except KeyboardInterrupt:
        logger.info("✋ Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())
