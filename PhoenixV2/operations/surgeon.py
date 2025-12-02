"""
PhoenixV2 Operations Module - The Surgeon

Background process that actively manages open positions:
1. Trailing Stops - Lock in profits by moving SL
2. Zombie Detection - Kill stagnant positions (> 4 hours, no movement)
3. Tourniquet Law - Close positions missing Stop Loss immediately
4. Winner's Lock - Move SL to breakeven when profit exceeds threshold
5. THE ARCHITECT UPGRADE: Chandelier Exits & Correlation Hedge
"""
import time
import threading
import logging
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from PhoenixV2.brain.architect import AlphaArchitect

logger = logging.getLogger("Surgeon")


class Surgeon(threading.Thread):
    """
    The Position Surgeon.
    Runs in background, continuously monitoring and repairing positions.
    Now powered by The Architect for smart exits.
    """
    
    def __init__(self, router):
        super().__init__()
        self.router = router
        self.running = False
        self.daemon = True
        self.architect = AlphaArchitect()
        
        # Configuration
        self.scan_interval = 5  # seconds between scans (Hyper-Aggressive)
        self.zombie_threshold_hours = 4  # Hours before position is "zombie"
        self.stagnant_winner_hours = 6  # Hours before profitable position is considered stagnant
        self.stagnant_winner_min_profit = 5.0  # Minimum profit to harvest if stagnant (matches zombie threshold)
        self.max_red_hold_hours = 2  # MAX TIME TO HOLD A LOSING TRADE (Rotting Fruit Rule) - TIGHTENED from 6h
        # trailing based on profit % thresholds
        self.breakeven_trigger_pct = 0.0005  # 0.05% profit (~5 pips) -> breakeven (Hyper-Tight)
        self.trailing_activation_pct = 0.0005  # 0.05% profit (~5 pips) -> start trailing (Hyper-Tight)
        
        # Launchpad Failure (Immediate Kill)
        self.launchpad_failure_pct = -0.002 # -0.2% loss
        self.launchpad_window_minutes = 45 # First 45 mins
        
        # micro-trade kill threshold in units (absolute)
        self.micro_trade_threshold = 1000
        
        # State tracking
        self.position_entry_times: Dict[str, datetime] = {}
        self._last_heartbeat = datetime.utcnow()
        self.brain = None # StrategyBrain instance for Vigilante checks
        self._last_vigilante_check: Dict[str, datetime] = {}

    def set_brain(self, brain):
        """Link the StrategyBrain for real-time ML re-evaluation."""
        self.brain = brain
        logger.info("🧠 SURGEON: Linked to StrategyBrain for VIGILANTE protocols.")

    def run(self):
        """Main surgeon loop."""
        self.running = True
        logger.info("🩺 SURGEON ACTIVATED (ARCHITECT ENABLED). Monitoring positions...")
        
        while self.running:
            try:
                # Heartbeat log every 10 seconds to confirm liveness
                if int(time.time()) % 10 == 0:
                    logger.info("🩺 Surgeon heartbeat... Scanning.")
                self.scan_and_repair()
            except Exception as e:
                logger.error(f"Surgeon Error: {e}")
            # Heartbeat summary every 60 seconds
            try:
                if (datetime.utcnow() - self._last_heartbeat).total_seconds() >= 60:
                    try:
                        pstate = self.router.get_portfolio_state() if hasattr(self.router, 'get_portfolio_state') else {}
                        positions = pstate.get('open_positions', []) if pstate else []
                        total_unreal = sum([float(p.get('unrealizedPL', 0.0) or 0.0) for p in positions]) if positions else 0.0
                        logger.info(f"🩺 SURGEON REPORT: Monitoring {len(positions)} active trades. PnL: ${total_unreal:.2f}. Actions Taken: None")
                    except Exception:
                        pass
                    self._last_heartbeat = datetime.utcnow()
            except Exception:
                pass
            time.sleep(self.scan_interval)

    def stop(self):
        """Stop the surgeon."""
        self.running = False
        logger.info("🩺 SURGEON DEACTIVATED.")

    def scan_and_repair(self):
        """
        Main scan routine. Checks all positions and applies fixes.
        """
        # Use aggregated portfolio state across all brokers
        try:
            pstate = self.router.get_portfolio_state() if hasattr(self.router, 'get_portfolio_state') else {}
            positions = pstate.get('open_positions', []) if pstate else []
        except Exception:
            positions = []
        if not positions:
            return
        
        # 0. ARCHITECT: Global Risk Check
        # If we are overexposed to losses, tighten EVERYTHING.
        # Fetch market data for Architect (using EUR_USD as proxy for now)
        market_data = None
        try:
            # Try to get EUR_USD candles as a market proxy
            # If router supports get_candles
            if hasattr(self.router, 'get_candles'):
                df_proxy = self.router.get_candles('EUR_USD', timeframe='M15', limit=100)
                if df_proxy is not None and not df_proxy.empty:
                    market_data = {
                        'prices': df_proxy['close'].values,
                        'volume': df_proxy['volume'].values
                    }
        except Exception:
            pass

        risk_off = self.architect.consult_hive_mind(positions, market_data=market_data)
        
        logger.debug(f"Surgeon scanning {len(positions)} positions...")
        
        for pos in positions:
            # Normalize different position shapes per broker
            if 'instrument' in pos:
                broker_type = 'OANDA'
            elif 'symbol' in pos and 'secType' in pos:
                broker_type = 'IBKR'
            elif 'currency' in pos or 'product_id' in pos:
                broker_type = 'COINBASE'
            else:
                broker_type = 'UNKNOWN'

            trade_id = pos.get('id')
            instrument = pos.get('instrument')
            units = float(pos.get('currentUnits', 0))
            entry_price = float(pos.get('price', 0))
            unrealized_pl = float(pos.get('unrealizedPL', 0))
            
            # Get current SL/TP
            sl_order = pos.get('stopLossOrder', {})
            current_sl = float(sl_order.get('price', 0)) if sl_order else None
            
            # Track entry time for zombie detection
            if trade_id not in self.position_entry_times:
                open_time = pos.get('openTime', '')
                if open_time:
                    try:
                        self.position_entry_times[trade_id] = datetime.fromisoformat(open_time.replace('Z', '+00:00'))
                    except:
                        self.position_entry_times[trade_id] = datetime.utcnow()
                else:
                    self.position_entry_times[trade_id] = datetime.utcnow()
            
            # === RULE 1: TOURNIQUET LAW ===
            # Positions without SL must be closed immediately
            # APPLIES TO ALL BROKERS (Immutable Risk Rule)
            if not current_sl:
                logger.warning(f"🚨 TOURNIQUET: {instrument} ({broker_type}) has NO STOP LOSS! Closing immediately.")
                self.router.close_trade(trade_id, broker=broker_type)
                continue

            # === RULE 1b: MICRO-TRADE KILL ===
            if abs(units) < self.micro_trade_threshold and broker_type != 'COINBASE': # Crypto has small units
                logger.warning(f"🧹 SURGEON: Killing Micro-Trade {trade_id} ({units} units < {self.micro_trade_threshold}).")
                self.router.close_trade(trade_id, broker=broker_type)
                continue
            
            # === RULE 2: ZOMBIE DETECTION ===
            entry_time = self.position_entry_times.get(trade_id, datetime.utcnow())
            age_hours = (datetime.utcnow() - entry_time.replace(tzinfo=None)).total_seconds() / 3600
            
            if age_hours > self.zombie_threshold_hours:
                if abs(unrealized_pl) < 5:  # Less than $5 movement
                    logger.warning(f"🧟 ZOMBIE DETECTED: {instrument} open {age_hours:.1f}h with ${unrealized_pl:.2f} P&L. Closing.")
                    self.router.close_trade(trade_id, broker=broker_type)
                    continue

            # === RULE 2b: STAGNANT WINNER HARVEST ===
            if age_hours > self.stagnant_winner_hours:
                if unrealized_pl > self.stagnant_winner_min_profit:
                    logger.warning(f"💰 STAGNANT WINNER: {instrument} open {age_hours:.1f}h with ${unrealized_pl:.2f} P&L. Harvesting.")
                    self.router.close_trade(trade_id, broker=broker_type)
                    continue

            # === RULE 2c: ROTTING FRUIT (Time Stop for Losers) ===
            # If a trade is RED for too long, cut it to free up margin.
            if age_hours > self.max_red_hold_hours and unrealized_pl < 0:
                 logger.warning(f"🍎 ROTTING FRUIT: {instrument} has been RED for {age_hours:.1f}h. Cutting loss at ${unrealized_pl:.2f}.")
                 self.router.close_trade(trade_id, broker=broker_type)
                 continue
            
            # === RULE 3: WINNER'S LOCK (Breakeven) ===
            is_long = units > 0
            
            # Generic Price Fetch
            current_price = None
            try:
                if hasattr(self.router, 'get_current_price'):
                    # Router should handle broker dispatch
                    price_data = self.router.get_current_price(instrument, broker=broker_type)
                    if price_data:
                        current_price = price_data.get('bid') if is_long else price_data.get('ask')
                        # Fallback if dict not returned or keys missing
                        if not current_price and isinstance(price_data, (float, int)):
                            current_price = float(price_data)
            except Exception:
                pass
            
            if current_price:
                # Calculate Profit %
                try:
                    notional_usd = abs(units) * entry_price if not instrument.startswith('USD') else abs(units)
                except:
                    notional_usd = 1.0
                profit_pct = (unrealized_pl / notional_usd) if notional_usd != 0 else 0.0
                
                # Breakeven Check
                if profit_pct >= self.breakeven_trigger_pct:
                    # Determine pip size
                    pip_size = 0.01 if 'JPY' in instrument else 0.0001
                    if broker_type == 'COINBASE': pip_size = 0.1 # Rough crypto pip
                    
                    if is_long and current_sl < entry_price:
                        new_sl = entry_price + (2 * pip_size)
                        logger.info(f"🔒 WINNER'S LOCK: {instrument} moving SL to breakeven {new_sl}")
                        self.router.modify_trade_sl(trade_id, new_sl, broker=broker_type, instrument=instrument)
                    elif not is_long and current_sl > entry_price:
                        new_sl = entry_price - (2 * pip_size)
                        logger.info(f"🔒 WINNER'S LOCK: {instrument} moving SL to breakeven {new_sl}")
                        self.router.modify_trade_sl(trade_id, new_sl, broker=broker_type, instrument=instrument)

            # === RULE 5: MANUAL STOP LOSS ENFORCEMENT (FAIL-SAFE) ===
            # If price has crossed SL but broker hasn't closed it, do it manually.
            if current_price and current_sl:
                violation = False
                if is_long and current_price <= current_sl:
                    violation = True
                elif not is_long and current_price >= current_sl:
                    violation = True
                
                if violation:
                    logger.warning(f"🚨 MANUAL SL ENFORCEMENT: {instrument} price {current_price} crossed SL {current_sl}. Closing immediately.")
                    self.router.close_trade(trade_id, broker=broker_type)
                    continue

            # === RULE 6: VIGILANTE (Real-Time ML Re-evaluation) ===
            # If trade is RED, ask the Brain if we should abort.
            # Throttled to every 30 seconds per trade to avoid API spam.
            if self.brain and unrealized_pl < 0:
                last_check = self._last_vigilante_check.get(trade_id)
                if not last_check or (datetime.utcnow() - last_check).total_seconds() > 30:
                    self._last_vigilante_check[trade_id] = datetime.utcnow()
                    try:
                        # Ask Brain for fresh signal
                        # We pass None for market_data to force Brain to fetch fresh data
                        fresh_signal = self.brain.get_signal(instrument)
                        
                        if fresh_signal:
                            signal_dir = fresh_signal.get('direction')
                            confidence = fresh_signal.get('confidence', 0)
                            
                            # REVERSAL LOGIC:
                            # If Long and Signal is SELL -> Close
                            # If Short and Signal is BUY -> Close
                            abort = False
                            if is_long and signal_dir == 'SELL':
                                abort = True
                            elif not is_long and signal_dir == 'BUY':
                                abort = True
                                
                            if abort:
                                logger.warning(f"🤖 VIGILANTE: {instrument} is RED and Brain says {signal_dir} ({confidence:.0%}). Aborting trade!")
                                self.router.close_trade(trade_id, broker=broker_type)
                                continue
                    except Exception as e:
                        logger.error(f"Vigilante Check Failed for {instrument}: {e}")

            # === RULE 4: ARCHITECT SMART TRAIL (Chandelier Exit) ===
            # Replaces the old simple trailing. This follows volatility.
            if current_price:
                try:
                    # Only activate Architect Trail if trade is decently profitable or Risk Off is triggered
                    if profit_pct >= self.trailing_activation_pct or risk_off:
                        # Fetch Candles
                        df = self.router.get_candles(instrument, timeframe='M15', limit=50)
                        
                        # Ask Architect for the Chandelier Level
                        # Check for Quant Tightener
                        quant_tightener = 1.0
                        try:
                            if self.architect.quant_rules:
                                # Use simple params for now based on regime
                                # We need regime and volatility
                                regime_data = self.architect.detect_regime(df)
                                vol = regime_data.get('atr', 0.0) / df['close'].iloc[-1] # Approx vol
                                params = self.architect.quant_rules.get_hedge_params(regime_data.get('regime'), vol)
                                quant_tightener = params.get('stop_tightener', 1.0)
                        except Exception:
                            pass

                        chandelier_stop = self.architect.get_chandelier_exit(df, "BUY" if is_long else "SELL", quant_tightener=quant_tightener)
                        
                        if chandelier_stop > 0:
                            # LOGIC: Only move stop closer, never wider
                            if is_long:
                                if chandelier_stop > current_sl:
                                    # Validate it's below current price (don't stop out instantly unless chaos)
                                    if chandelier_stop < current_price:
                                        logger.info(f"🏛️ ARCHITECT TRAIL: {instrument} moving SL {current_sl} -> {chandelier_stop:.5f}")
                                        self.router.modify_trade_sl(trade_id, chandelier_stop, broker=broker_type, instrument=instrument)
                            else: # Short
                                if chandelier_stop < current_sl:
                                    if chandelier_stop > current_price:
                                        logger.info(f"🏛️ ARCHITECT TRAIL: {instrument} moving SL {current_sl} -> {chandelier_stop:.5f}")
                                        self.router.modify_trade_sl(trade_id, chandelier_stop, broker=broker_type, instrument=instrument)

                except Exception as e:
                    pass

    def force_scan(self):
        """Manually trigger a scan."""
        logger.info("🩺 SURGEON: Manual scan triggered")
        self.scan_and_repair()

    def get_status(self) -> Dict[str, Any]:
        """Get surgeon status report."""
        return {
            "running": self.running,
            "scan_interval": self.scan_interval,
            "positions_tracked": len(self.position_entry_times),
            "rules_active": [
                "Tourniquet (No SL = Close)",
                "Zombie Detection",
                "Stagnant Winner Harvest",
                "Rotting Fruit (Max Hold Time for Losers)",
                "Winner's Lock (Breakeven)",
                "🤖 VIGILANTE (Real-Time ML Re-evaluation)",
                "🏛️ Architect Smart Trail (Chandelier)"
            ]
        }
