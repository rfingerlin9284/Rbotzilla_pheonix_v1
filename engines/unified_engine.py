#!/usr/bin/env python3
"""Unified engine to orchestrate all trading engines in RICK_LIVE_CLEAN

This lightweight orchestrator will start the OANDA engine, the IBKR engine,
and the Aggressive Money Machine based on environment variables.

It supports a short `UNIFIED_RUN_DURATION_SECONDS` environment variable for
testing, allowing the engines to run for a specified number of seconds and
then shutting down gracefully.
"""
import asyncio
import os
from datetime import datetime, timezone
import logging

from foundation.rick_charter import RickCharter
from util.narration_logger import log_narration

try:
    from oanda.oanda_trading_engine import OandaTradingEngine
except Exception:
    OandaTradingEngine = None

try:
    from ibkr_gateway.ibkr_trading_engine import IBKRTradingEngine
except Exception:
    IBKRTradingEngine = None

try:
    from aggressive_money_machine import AggressiveMoneyMachine
except Exception:
    AggressiveMoneyMachine = None


class UnifiedRunner:
    def __init__(self, pin: int = 841921):
        if not RickCharter.validate_pin(pin):
            raise PermissionError("Invalid Charter PIN")
        self.pin = pin
        self.logger = logging.getLogger("UnifiedRunner")
        self.tasks = []
        self.engines = []

    async def _start_oanda(self):
        if not OandaTradingEngine:
            self.logger.warning("OANDA engine not available: skipping")
            return
        engine = OandaTradingEngine(environment=os.getenv('OANDA_ENVIRONMENT', 'practice'))
        self.engines.append(engine)
        await engine.run_trading_loop()

    async def _start_ibkr(self):
        if not IBKRTradingEngine:
            self.logger.warning("IBKR engine not available: skipping")
            return
        engine = IBKRTradingEngine()
        self.engines.append(engine)
        await engine.run_trading_loop()

    async def _start_aggressive_machine(self):
        if not AggressiveMoneyMachine:
            self.logger.warning("AggressiveMoneyMachine not available: skipping")
            return
        # default parameters in production will be used; tests can set env
        machine = AggressiveMoneyMachine(pin=self.pin)
        self.engines.append(machine)
        # Aggressive machine main is async 'run_autonomous_loop' but also has 'main'
        try:
            await machine.run_autonomous_loop(symbols=["EUR_USD","GBP_USD","USD_JPY"], check_interval_seconds=int(os.getenv('AGGRESSIVE_LOOP_INTERVAL', '60')))
        except Exception as e:
            self.logger.warning(f"Aggressive machine stopped: {e}")

    async def run(self):
        # Announce start
        log_narration(event_type="UNIFIED_ENGINE_START", details={"time": str(datetime.now(timezone.utc))}, symbol='SYSTEM', venue='unified')

        # Read toggles
        enable_oanda = os.getenv('ENABLE_OANDA', '1') == '1'
        enable_ibkr = os.getenv('ENABLE_IBKR', '1') == '1'
        enable_aggressive = os.getenv('ENABLE_AGGRESSIVE', '1') == '1'

        duration = int(os.getenv('UNIFIED_RUN_DURATION_SECONDS', '0'))

        # Optional registry pruning to remove stale records on startup
        try:
            from util.positions_registry import list_positions, unregister_position, normalize_symbol
            # If OANDA connector present, remove any OANDA specific stale entries
            if OandaTradingEngine:
                try:
                    oanda_conn = OandaTradingEngine(environment=os.getenv('OANDA_ENVIRONMENT', 'practice')).oanda
                    open_trades = oanda_conn.get_trades() or []
                    open_ids = set([str(x.get('id') or x.get('tradeId') or x.get('trade_id') or x.get('order_id') or x.get('orderId')) for x in open_trades if x])
                    for entry in list_positions():
                        if entry.get('broker') == 'OANDA':
                            rid = entry.get('order_id')
                            rtid = entry.get('trade_id')
                            if (rid and str(rid) not in open_ids) and (rtid and str(rtid) not in open_ids):
                                unregister_position(order_id=rid, trade_id=rtid, symbol=entry.get('symbol'))
                except Exception:
                    pass
        except Exception:
            pass

        # Build tasks
        if enable_oanda:
            self.tasks.append(asyncio.create_task(self._start_oanda(), name='oanda'))
        if enable_ibkr:
            self.tasks.append(asyncio.create_task(self._start_ibkr(), name='ibkr'))
        if enable_aggressive:
            self.tasks.append(asyncio.create_task(self._start_aggressive_machine(), name='aggressive'))

        if not self.tasks:
            self.logger.warning("No engines enabled; nothing to run")
            return

        # If duration is set (test mode), run for that period and then cancel tasks
        try:
            if duration > 0:
                self.logger.info(f"Running unified engine for {duration}s (test mode)")
                await asyncio.sleep(duration)
                for t in self.tasks:
                    t.cancel()
                await asyncio.gather(*self.tasks, return_exceptions=True)
            else:
                # Run until canceled
                await asyncio.gather(*self.tasks)
        finally:
            log_narration(event_type="UNIFIED_ENGINE_STOP", details={"time": str(datetime.now(timezone.utc))}, symbol='SYSTEM', venue='unified')


async def main():
    runner = UnifiedRunner(pin=int(os.getenv('CHARter_PIN', '841921')))
    await runner.run()


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
