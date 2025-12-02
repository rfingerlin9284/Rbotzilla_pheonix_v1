#!/usr/bin/env python3
"""
IBKR Gateway Trading Engine - Crypto Futures Edition
Autonomous trading system for Bitcoin/Ethereum futures via TWS API

PIN: 841921 | Mode: Paper Trading (port 7497)
Charter Compliance: MIN_NOTIONAL=$5k, MIN_PNL=$200, MAX_HOLD=6h, MIN_RR=3.2x

Features:
- 24/7 crypto futures trading (BTC, ETH via CME)
- RICK Hive Mind integration
- Wolf Pack strategies (adapted for crypto)
- Funding rate awareness
- Session-aware (CME hourly breaks)
- Paper trading default (safe testing)
"""

import os
import sys
import time
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional

# Add parent for rick_hive access
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# IBKR connector
from ibkr_connector import IBKRConnector, position_police_check
from util.leverage_plan import plan_enabled as leverage_plan_enabled, get_current_leverage
from util.dynamic_leverage import compute_approval_score, compute_dynamic_leverage, get_env_caps
from logic.smart_logic import get_smart_filter
from foundation.trading_mode import safe_place_order

# RICK Hive Mind
try:
    from rick_hive.rick_charter import RickCharter as CHARTER
except ImportError:
    class CHARTER:
        MIN_NOTIONAL_USD = 5000
        MIN_EXPECTED_PNL_USD = 200
        MAX_HOLD_DURATION_HOURS = 6
        MIN_RISK_REWARD_RATIO = 3.2


class CryptoWolfPack:
    """
    Consolidated wolf pack strategies for crypto futures
    Adapted from OANDA forex strategies with crypto-specific parameters
    """
    
    # Crypto futures to trade
    INSTRUMENTS = ["BTC", "ETH"]
    
    # Higher volatility = tighter parameters
    RSI_OVERSOLD = 25  # vs 30 for forex
    RSI_OVERBOUGHT = 75  # vs 70 for forex
    
    # CME session breaks (hourly maintenance)
    SESSION_BREAK_HOUR = 16  # 4pm CT
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def calculate_rsi(self, candles: List[Dict], period: int = 14) -> float:
        """Calculate RSI from candle data"""
        if len(candles) < period + 1:
            return 50.0  # Neutral if insufficient data
        
        closes = [c["close"] for c in candles[-(period + 1):]]
        
        gains = []
        losses = []
        for i in range(1, len(closes)):
            change = closes[i] - closes[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_ema(self, candles: List[Dict], period: int) -> float:
        """Calculate EMA from candles"""
        if len(candles) < period:
            return candles[-1]["close"] if candles else 0.0
        
        closes = [c["close"] for c in candles[-period:]]
        
        # Initial SMA
        ema = sum(closes[:period]) / period
        
        # Apply EMA formula
        multiplier = 2 / (period + 1)
        for close in closes[period:]:
            ema = (close - ema) * multiplier + ema
        
        return ema
    
    def check_session_active(self) -> bool:
        """Check if CME crypto session is active (not in hourly break)"""
        now = datetime.now(timezone.utc)
        hour_ct = (now.hour - 6) % 24  # Convert UTC to CT
        
        # CME has 1-hour break at 4pm CT daily
        if hour_ct == self.SESSION_BREAK_HOUR:
            return False
        
        return True
    
    def analyze_crypto_futures(
        self,
        symbol: str,
        candles: List[Dict],
        current_price: float
    ) -> Optional[Dict]:
        """
        Unified wolf pack analysis for crypto futures
        
        Combines:
        - Trend following (EMA crossovers)
        - Mean reversion (RSI extremes)
        - Momentum (recent price action)
        
        Args:
            symbol: BTC or ETH
            candles: Historical OHLCV data
            current_price: Current market price
            
        Returns:
            Signal dict or None
        """
        if len(candles) < 60:
            self.logger.warning(f"{symbol}: Insufficient candles ({len(candles)})")
            return None
        
        # Skip if session break
        if not self.check_session_active():
            self.logger.info(f"{symbol}: CME session break - skipping")
            return None
        
        # Calculate indicators
        rsi = self.calculate_rsi(candles)
        ema_fast = self.calculate_ema(candles, 12)
        ema_slow = self.calculate_ema(candles, 26)
        
        # Trend direction
        trend_bullish = ema_fast > ema_slow
        trend_bearish = ema_fast < ema_slow
        
        # Mean reversion zones
        oversold = rsi < self.RSI_OVERSOLD
        overbought = rsi > self.RSI_OVERBOUGHT
        
        # Recent momentum (last 3 candles)
        recent_candles = candles[-3:]
        momentum_up = all(c["close"] > c["open"] for c in recent_candles)
        momentum_down = all(c["close"] < c["open"] for c in recent_candles)
        
        # Signal generation
        signal = None
        
        # Bullish signals
        if oversold and trend_bullish and momentum_up:
            signal = self._generate_long_signal(symbol, current_price, candles)
        
        # Bearish signals
        elif overbought and trend_bearish and momentum_down:
            signal = self._generate_short_signal(symbol, current_price, candles)
        
        if signal:
            self.logger.info(
                f"📊 {symbol} Signal: {signal['side']} @ {signal['entry']:.2f} "
                f"(RSI: {rsi:.1f}, Trend: {'Bull' if trend_bullish else 'Bear'})"
            )
        
        return signal
    
    def _generate_long_signal(
        self,
        symbol: str,
        entry: float,
        candles: List[Dict]
    ) -> Dict:
        """Generate LONG signal with OCO levels"""
        # ATR for stop/target calculation
        atr = self._calculate_atr(candles, period=14)
        
        # Crypto-adjusted R:R (3.5x due to higher vol)
        stop_loss = entry - (1.5 * atr)
        take_profit = entry + (3.5 * 1.5 * atr)  # 3.5x R:R
        
        # Calculate units for MIN_NOTIONAL
        # For BTC micro futures: multiplier = 0.1 BTC = ~$6000 per contract at $60k BTC
        notional_per_unit = entry * 0.1  # Micro BTC
        units = max(1, int(CHARTER.MIN_NOTIONAL_USD / notional_per_unit))
        
        return {
            "symbol": symbol,
            "side": "BUY",
            "entry": entry,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "units": units,
            "notional": units * notional_per_unit,
            "expected_pnl": (take_profit - entry) * units * 0.1,
            "rr_ratio": 3.5,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def _generate_short_signal(
        self,
        symbol: str,
        entry: float,
        candles: List[Dict]
    ) -> Dict:
        """Generate SHORT signal with OCO levels"""
        atr = self._calculate_atr(candles, period=14)
        
        stop_loss = entry + (1.5 * atr)
        take_profit = entry - (3.5 * 1.5 * atr)
        
        notional_per_unit = entry * 0.1
        units = max(1, int(CHARTER.MIN_NOTIONAL_USD / notional_per_unit))
        
        return {
            "symbol": symbol,
            "side": "SELL",
            "entry": entry,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "units": units,
            "notional": units * notional_per_unit,
            "expected_pnl": (entry - take_profit) * units * 0.1,
            "rr_ratio": 3.5,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def _calculate_atr(self, candles: List[Dict], period: int = 14) -> float:
        """Calculate Average True Range"""
        if len(candles) < period + 1:
            return candles[-1]["high"] - candles[-1]["low"] if candles else 0.0
        
        true_ranges = []
        for i in range(1, len(candles)):
            high = candles[i]["high"]
            low = candles[i]["low"]
            prev_close = candles[i-1]["close"]
            
            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )
            true_ranges.append(tr)
        
        return sum(true_ranges[-period:]) / period


    # FXWolfPack was removed: IBKR gateway handles crypto futures only (BTC/ETH).


class IBKRTradingEngine:
    """
    Main trading engine for IBKR crypto futures
    
    Loop:
    1. Fetch candles for BTC/ETH
    2. Run wolf pack analysis
    3. Generate signals
    4. Validate vs charter gates
    5. Place OCO orders
    6. Monitor positions (max 6h hold)
    7. Run Position Police
    """
    
    def __init__(self, connector=None):
        # Logging
        self.logger = self._setup_logging()
        
        # IBKR connector; allow injection for testing
        if connector is not None:
            self.connector = connector
        else:
            self.connector = IBKRConnector(
            port=int(os.getenv("IBKR_PORT", 7497)),  # Paper trading
            account=os.getenv("IBKR_PAPER_ACCOUNT"),
            logger=self.logger
        )
        
        # Wolf pack strategies
        self.wolf_pack = CryptoWolfPack(self.logger)
        # IBKR engine only handles crypto futures; FX is handled by OANDA engine
        
        # Position tracking
        self.position_open_times = {}
        self.total_trades = 0
        
        # Cycle interval (crypto = faster cycles than forex)
        self.cycle_interval = 300  # 5 minutes (vs 15 min for forex)
        
        self.logger.info("🚀 IBKR Crypto Futures Engine initialized")

    def _set_trade_stop_with_retries(self, order_id: str, price: float, trade_id: Optional[str] = None, symbol: Optional[str] = None, direction: Optional[str] = None, trigger_source: Optional[list] = None, retries: int = 3, backoff: float = 0.5):
        """Attempt to set trade stop with retries and narration logging for IBKR connector.

        Returns: (success: bool, last_resp: dict, attempts: int)
        """
        attempt = 0
        last_resp = None
        while attempt < retries:
            attempt += 1
            try:
                resp = self.connector.set_trade_stop(order_id, price)
                last_resp = resp
                if isinstance(resp, dict) and resp.get('success'):
                    try:
                        from util.narration_logger import log_narration
                        from foundation.trading_mode import safe_place_order
                        log_narration(
                            event_type="TRAILING_SL_SET_CONFIRMED",
                            details={
                                "trade_id": trade_id or order_id,
                                "order_id": order_id,
                                "set_stop": price,
                                "attempt": attempt,
                                "set_resp": resp,
                                "trigger_source": trigger_source
                            },
                            symbol=symbol,
                            venue="ibkr"
                        )
                    except Exception:
                        pass
                    return True, resp, attempt
                else:
                    try:
                        from util.narration_logger import log_narration
                        log_narration(
                            event_type="TRAILING_SL_SET_ATTEMPT_FAILED",
                            details={
                                "trade_id": trade_id or order_id,
                                "order_id": order_id,
                                "set_stop": price,
                                "attempt": attempt,
                                "set_resp": resp,
                                "trigger_source": trigger_source
                            },
                            symbol=symbol,
                            venue="ibkr"
                        )
                    except Exception:
                        pass
            except Exception as e:
                last_resp = {"success": False, "error": str(e)}
                try:
                    from util.narration_logger import log_narration
                    log_narration(
                        event_type="TRAILING_SL_SET_EXCEPTION",
                        details={
                            "trade_id": trade_id or order_id,
                            "order_id": order_id,
                            "set_stop": price,
                            "attempt": attempt,
                            "error": str(e),
                            "trigger_source": trigger_source
                        },
                        symbol=symbol,
                        venue="ibkr"
                    )
                except Exception:
                    pass
            try:
                time.sleep(backoff)
            except Exception:
                pass
        try:
            from util.narration_logger import log_narration
            log_narration(
                event_type="TRAILING_SL_SET_FAILED",
                details={
                    "trade_id": trade_id or order_id,
                    "order_id": order_id,
                    "set_stop": price,
                    "attempts": attempt,
                    "last_resp": last_resp,
                    "trigger_source": trigger_source
                },
                symbol=symbol,
                venue="ibkr"
            )
        except Exception:
            pass
        return False, last_resp, attempt

    def _apply_adaptive_trailing_sl(self, pos: dict, trade_id: str, order_id: str, symbol: str, current_price: float, estimated_atr_pips: float, pip_size: float, profit_atr_multiple: float, direction: str, trigger_source: Optional[list] = None, force_close_on_fail: bool = False):
        """Compute adaptive SL and apply using _set_trade_stop_with_retries; returns boolean success.
        Similar to OANDA apply helper.
        """
        candidate_sl_list = []
        try:
            # Use SmartTrailingSystem heuristics if available
            try:
                from util.momentum_trailing import SmartTrailingSystem
                sts = SmartTrailingSystem()
                if profit_atr_multiple > 0:
                    atr_price = estimated_atr_pips * pip_size
                    trail_distance = sts.calculate_dynamic_trailing_distance(profit_atr_multiple=profit_atr_multiple, atr=atr_price, momentum_active=True)
                    if direction == 'BUY':
                        new_sl = current_price - trail_distance
                    else:
                        new_sl = current_price + trail_distance
                    candidate_sl_list.append(new_sl)
            except Exception:
                # Fallback: compute simple trailing based on ATR
                atr_price = estimated_atr_pips * pip_size
                trail_distance = max(atr_price * 0.8, atr_price * 0.5)
                if direction == 'BUY':
                    new_sl = current_price - trail_distance
                else:
                    new_sl = current_price + trail_distance
                candidate_sl_list.append(new_sl)
        except Exception:
            pass

        # Additional candidate using compute_trailing_sl
        try:
            from util.trailing_engine import PositionSnapshot, compute_trailing_sl
            ps = PositionSnapshot(
                symbol=symbol,
                direction=direction,
                entry_price=pos.get('entry_price'),
                current_price=current_price,
                initial_sl=pos.get('stop_loss'),
                current_sl=pos.get('stop_loss'),
                open_time=pos.get('timestamp'),
                now=datetime.now(timezone.utc),
                last_swing_price=pos.get('stop_loss'),
                last_liquidity_level=pos.get('stop_loss'),
                atr_value=estimated_atr_pips * pip_size,
                rr_initial=pos.get('rr_ratio')
            )
            pip_val = 0.0001 if 'JPY' not in symbol else 0.01
            sug_sl = compute_trailing_sl(ps, pip_val, momentum_active=True)
            candidate_sl_list.append(sug_sl)
        except Exception:
            pass

        original_sl = pos.get('stop_loss')
        adaptive_sl = original_sl
        for c in candidate_sl_list:
            if c is None:
                continue
            if direction == 'BUY' and c > adaptive_sl:
                adaptive_sl = c
            if direction == 'SELL' and c < adaptive_sl:
                adaptive_sl = c

        # skip if no change
        if adaptive_sl == original_sl:
            return False, None

        success, set_resp, attempts = self._set_trade_stop_with_retries(order_id, adaptive_sl, trade_id=trade_id, symbol=symbol, direction=direction, trigger_source=trigger_source)

        if success:
            pos['stop_loss'] = adaptive_sl
            pos['tp_cancelled'] = True
            pos['tp_cancelled_timestamp'] = datetime.now(timezone.utc)
            pos['tp_cancel_source'] = trigger_source
            pos['trailing_set_timestamp'] = datetime.now(timezone.utc)
            self.logger.info(f"✅ Adaptive trailing SL set for trade {trade_id} ({symbol})")
            return True, set_resp
        # If we fail to set SL after retries, optionally escalate by closing position
        if not success and force_close_on_fail:
            try:
                close_resp = self.connector.close_position(symbol)
                try:
                    from util.narration_logger import log_narration
                    log_narration(
                        event_type="TRAILING_SL_SET_FAILED_ESCALATION_CLOSE",
                        details={
                            "trade_id": trade_id,
                            "order_id": order_id,
                            "symbol": symbol,
                            "close_resp": close_resp
                        },
                        symbol=symbol,
                        venue="ibkr"
                    )
                except Exception:
                    pass
            except Exception as e:
                try:
                    from util.narration_logger import log_narration
                    log_narration(
                        event_type="TRAILING_SL_SET_FAILED_ESCALATION_CLOSE_ERROR",
                        details={
                            "trade_id": trade_id,
                            "order_id": order_id,
                            "symbol": symbol,
                            "error": str(e)
                        },
                        symbol=symbol,
                        venue="ibkr"
                    )
                except Exception:
                    pass
        return False, set_resp
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging to console + file"""
        os.makedirs("logs", exist_ok=True)
        
        logger = logging.getLogger("IBKREngine")
        logger.setLevel(logging.INFO)
        
        # Console handler
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(console)
        
        # File handler
        file_handler = logging.FileHandler("logs/ibkr_engine.log")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(file_handler)
        
        return logger
    
    async def run_trading_loop(self):
        """
        Main trading loop
        
        24/7 operation with 5-minute cycles
        """
        if not self.connector.connect():
            self.logger.error("❌ Failed to connect to IBKR Gateway")
            return
        
        self.logger.info("✅ Trading loop started (5-min cycles, paper mode)")
        
        try:
            while True:
                cycle_start = time.time()
                
                # Process each crypto futures instrument
                for symbol in self.wolf_pack.INSTRUMENTS:
                    try:
                        await self._process_instrument(symbol)
                    except Exception as e:
                        self.logger.error(f"Error processing {symbol}: {e}")

                # FX processing intentionally omitted - route forex to OANDA engine
                
                # Position Police (charter enforcement)
                try:
                    position_police_check(self.connector)
                    self._check_hold_time_violations()
                except Exception as e:
                    self.logger.error(f"Position Police error: {e}")
                
                # Wait for next cycle
                elapsed = time.time() - cycle_start
                sleep_time = max(0, self.cycle_interval - elapsed)
                
                self.logger.info(f"💤 Cycle complete ({elapsed:.1f}s), sleeping {sleep_time:.0f}s")
                await asyncio.sleep(sleep_time)
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Shutting down...")
        finally:
            self.connector.disconnect()
    
    async def _process_instrument(self, symbol: str):
        """Process single crypto futures instrument"""
        # Fetch historical data
        candles = self.connector.get_historical_data(symbol, count=60, timeframe="1H")
        
        if not candles:
            self.logger.warning(f"{symbol}: No candles received")
            return
        
        current_price = candles[-1]["close"]
        
        # Check for existing position
        positions = self.connector.get_open_positions()
        has_position = any(p["symbol"] == symbol for p in positions)
        
        if has_position:
            self.logger.info(f"{symbol}: Position already open, monitoring")
            return
        
        # Wolf pack analysis
        signal = self.wolf_pack.analyze_crypto_futures(symbol, candles, current_price)
        
        if not signal:
            return
        
        # Determine if we should use a limit order (due to spread or slippage concerns)
        bid, ask = self.connector.get_best_bid_ask(symbol)
        use_limit = False
        if bid and ask:
            tick = float(self.connector.CRYPTO_FUTURES[symbol]['tick'])
            if (ask - bid) > (tick * 8):  # Arbitrary threshold: 8 ticks
                use_limit = True

                # Compute dynamic leverage if plan is enabled and signal is good
        try:
            if leverage_plan_enabled():
                smart_filter = get_smart_filter(pin=841921)
                validation = smart_filter.validate_signal({
                    'symbol': symbol,
                    'direction': signal['side'],
                    'entry_price': signal['entry'],
                    'target_price': signal['take_profit'],
                    'stop_loss': signal['stop_loss'],
                    'recent_highs': [c['high'] for c in candles[-20:]],
                    'recent_lows': [c['low'] for c in candles[-20:]],
                    'recent_closes': [c['close'] for c in candles[-40:]],
                    'recent_volumes': [c.get('volume', 0) for c in candles[-40:]],
                    'swing_high': max([c['high'] for c in candles]),
                    'swing_low': min([c['low'] for c in candles])
                })
                technical_score = validation.score if validation else 0.0
                # use signal's internal confidence if present
                ml_confidence = signal.get('confidence', 0.0)
                # For IBKR we don't have a hive mind; use technical & ml confidence
                rr_ratio = validation.risk_reward_ratio if validation else 0.0
                rr_factor = min(rr_ratio / 5.0, 1.0) if rr_ratio else 0.0
                approval_score = compute_approval_score(technical_score, hive_confidence=0.0, ml_confidence=ml_confidence, rick_approval=False, rr_factor=rr_factor, historical_win_rate=0.5)
                caps = get_env_caps()
                dyn_leverage, dyn_justification = compute_dynamic_leverage(get_current_leverage(), approval_score, caps.get('max_leverage'), float(caps.get('aggressiveness') or 2.0))
                new_units = int(signal['units'] * dyn_leverage)
                signal['units'] = max(1, new_units)
                try:
                    from util.narration_logger import log_narration
                    log_narration(event_type='AGGRESSIVE_LEVERAGE_APPLIED', details={'symbol': symbol, 'units': signal['units'], 'leverage': dyn_leverage, 'explanation': dyn_justification}, symbol=symbol, venue='ibkr')
                except Exception:
                    pass
        except Exception as e:
            self.logger.warning(f"Aggressive leverage computation failed: {e}")

        # Apply minimum confidence gating (MIN_CONFIDENCE env var default 0.5)
        try:
            from util.confidence import is_confidence_above
            min_conf = float(os.getenv('MIN_CONFIDENCE', '0.5'))
        except Exception:
            min_conf = 0.5
        # approval_score is our technical/approval proxy if available
        score = locals().get('approval_score', None)
        sig_conf = signal.get('confidence') if isinstance(signal, dict) else None
        # prefer approval_score then signal['confidence'], default to 1.0
        effective_conf = score if score is not None else sig_conf if sig_conf is not None else 1.0
        if not is_confidence_above(effective_conf, min_conf):
            self.logger.info(f"Skipping {symbol} {signal.get('side')} due to low confidence ({effective_conf}) < {min_conf}")
            return

        # Place order (charter validation inside connector)
        ok_flag, result = safe_place_order(self.connector,
            symbol=signal["symbol"],
            side=signal["side"],
            units=signal["units"],
            entry_price=signal["entry"],
            use_limit=use_limit,
            stop_loss=signal["stop_loss"],
            take_profit=signal["take_profit"]
            , explanation=dyn_justification if 'dyn_justification' in locals() else None
        )

        # Normalize success flag and result dict
        try:
            success = bool(ok_flag) and (result.get('success') if isinstance(result, dict) and 'success' in result else True)
        except Exception:
            success = bool(ok_flag)

        if success:
            # Track position open time
            self.position_open_times[symbol] = datetime.now(timezone.utc)
            self.total_trades += 1
            trade_id = f"IBKR_AMM_{self.total_trades}_{int(datetime.now(timezone.utc).timestamp())}"
            # Log the mapping event for auditability
            try:
                from util.narration_logger import log_narration
                log_narration(
                    event_type="BROKER_MAPPING",
                    details={
                        "order_ids": result.get('trades', []),
                        "trade_id": trade_id,
                        "symbol": symbol,
                        "units": signal['units'],
                        "entry_price": signal['entry']
                    },
                    symbol=symbol,
                    venue='ibkr'
                )
            except Exception:
                self.logger.warning('Failed to write BROKER_MAPPING to narration log')
            self.logger.info(f"✅ Trade executed: {symbol} {signal['side']} (trade_id: {trade_id})")
        else:
            self.logger.warning(
                f"❌ Trade rejected: {symbol} - {result.get('error', 'Unknown')}"
            )

    # _process_fx_instrument removed - IBKR gateway does not execute FX
    
    def _check_hold_time_violations(self):
        """
        Charter enforcement: Close positions exceeding MAX_HOLD_TIME (6 hours)
        """
        now = datetime.now(timezone.utc)
        max_hold = timedelta(hours=CHARTER.MAX_HOLD_DURATION_HOURS)
        
        for symbol, open_time in list(self.position_open_times.items()):
            hold_duration = now - open_time
            
            if hold_duration > max_hold:
                self.logger.warning(
                    f"🚨 MAX_HOLD violation: {symbol} open for {hold_duration.total_seconds()/3600:.1f}h - CLOSING"
                )
                
                result = self.connector.close_position(symbol)
                
                if result.get("success"):
                    del self.position_open_times[symbol]
                    self.logger.info(f"✅ Closed {symbol} (hold time violation)")


async def main():
    """Entry point"""
    print("=" * 80)
    print("IBKR GATEWAY CRYPTO FUTURES ENGINE")
    print("=" * 80)
    print(f"Mode: Paper Trading (port 7497)")
    print(f"Assets: BTC, ETH futures (CME)")
    print(f"Charter: MIN_NOTIONAL=${CHARTER.MIN_NOTIONAL_USD}, "
          f"MIN_PNL=${CHARTER.MIN_EXPECTED_PNL_USD}, "
          f"MAX_HOLD={CHARTER.MAX_HOLD_DURATION_HOURS}h, "
          f"MIN_RR={CHARTER.MIN_RISK_REWARD_RATIO}x")
    print("=" * 80)
    print()
    
    # Load .env into the process environment (so IBKR uses variables set in .env)
    try:
        from load_env import load_env_file
        # explicitly load .env so our environment changes are used
        load_env_file('.env')  # loads .env into os.environ
    except Exception:
        pass

    engine = IBKRTradingEngine()
    await engine.run_trading_loop()


if __name__ == "__main__":
    asyncio.run(main())
