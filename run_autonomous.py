#!/usr/bin/env python3
"""
RBOTzilla autonomous entrypoint

This file is the canonical repo-level entrypoint that the start scripts call. It
tries to import the real engine from `rick_clean_live/canary_trading_engine.py` and
start a ghost/paper trading session. If the real engine is not importable, it
falls back to a simple heartbeat/stub engine so that startup scripts stop
crashing and logs clearly indicate the missing engine module.
"""

import asyncio
import sys
import time
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
PKG = ROOT / "rick_clean_live"

# Ensure package is on sys.path: import modules from rick_clean_live as plain modules
sys.path.insert(0, str(PKG / 'util'))  # prefer rick_clean_live/util for top-level 'util' imports
sys.path.insert(0, str(PKG))
sys.path.append(str(ROOT))  # append repo root so it is only used if earlier paths don't match

ENGINE_LABEL = None

try:
    # Primary: import the real CanaryTradingEngine defined in this repo
    from canary_trading_engine import CanaryTradingEngine as _Engine
    ENGINE_LABEL = "rick_clean_live.canary_trading_engine.CanaryTradingEngine"
except Exception as e:
    # Fallback: define a stub engine so the startup script keeps running and logs
    print("WARN: Could not import CanaryTradingEngine from canary_trading_engine (", type(e).__name__, ":", e, ")")

    class _Engine:
        """Stub engine: logs periodic heartbeats and never places orders."""

        def __init__(self, pin: int = 0) -> None:
            self.pin = pin

        async def start_ghost_trading(self) -> None:
            cycle = 0
            while True:
                cycle += 1
                now = datetime.utcnow().isoformat()
                print(f"[STUB_ENGINE] cycle={cycle} utc={now} pin={self.pin} – CanaryTradingEngine missing; NO ORDERS will be placed.")
                await asyncio.sleep(30)

    ENGINE_LABEL = "STUB_ENGINE (no CanaryTradingEngine)"


async def main() -> None:
    """Main loop: start engine and auto-restart on unhandled exceptions with backoff.

    This makes the entrypoint robust and durable for "set-and-forget" operation.
    """
    print(f"run_autonomous.py – starting engine: {ENGINE_LABEL}")
    attempt = 0
    backoff_seconds = 5
    while True:
        attempt += 1
        print(f"run_autonomous.py – engine start attempt #{attempt}")
        engine = _Engine(pin=841921)
        try:
            await engine.start_ghost_trading()
            # If the engine returns normally (graceful shutdown), log and restart after a short pause
            print("run_autonomous.py – engine exited normally; restarting in 5s")
            await asyncio.sleep(5)
            break
        except KeyboardInterrupt:
            print("run_autonomous.py – received KeyboardInterrupt, stopping")
            raise
        except Exception as e:
            now = datetime.utcnow().isoformat()
            print(f"run_autonomous.py – engine crashed at {now}: {type(e).__name__}: {e}")
            # exponential backoff with ceiling
            print(f"run_autonomous.py – restarting in {backoff_seconds}s (attempt {attempt})")
            await asyncio.sleep(backoff_seconds)
            backoff_seconds = min(300, int(backoff_seconds * 1.5))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("run_autonomous.py – stopped by user")
    except Exception as e:
        print(f"run_autonomous.py – crashed: {type(e).__name__}: {e}")
        raise
