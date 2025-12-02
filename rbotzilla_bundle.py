#!/usr/bin/env python3
"""
RBOTZILLA BUNDLE

Single-file portable bundle containing:
- AGENT_CHARTER_v2 (immutable rules)
- Change tracker (simple JSONL logger)
- Execution gate, micro trade filter, and ML reward filter (Smart Aggression)
- Built-in strategies (institutional_sd, ema_scalper, trap_reversal, holy_grail)
- Connectors (OANDA, Coinbase, IBKR stubs)
- RBotZilla engine that ties everything together and logs gating/charter events

Usage: python3 rbotzilla_bundle.py --run-seconds 10 --simulate

Safety: Execution requires EXECUTION_ENABLED=true and proper env keys; by default the engine will NOT execute (safe). Paper mode is default.
"""
import os
import sys
import time
import random
import logging
import json
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from foundation.trading_mode import safe_place_order

LOGFILE = 'rbotzilla_bundle.log'
CHANGELOG = 'rbotzilla_bundle_changes.jsonl'
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [RBOTZILLA_BUNDLE] - %(levelname)s - %(message)s')
logger = logging.getLogger('rbotzilla_bundle')

# -----------------------------------------------------------------------------
# AGENT CHARTER
# -----------------------------------------------------------------------------
AGENT_CHARTER = {
    "AUTH_PIN": 841921,
    "M15_MINIMUM": True,
    "MICRO_TRADING_ENABLED": False,
    "MIN_MICRO_SIZE": 1000,
    "EXECUTION_DEFAULT": False,
    "MIN_RR": 3.0,
    "REQUIRES_OCO": True
}

# -----------------------------------------------------------------------------
# Change tracker (very small - append-only JSONL)
# -----------------------------------------------------------------------------
def log_change(event: str, details: Dict[str, Any], auth_pin: Optional[int] = None):
    record = {
        'timestamp': datetime.utcnow().isoformat(),
        'event': event,
        'details': details,
        'auth_valid': (auth_pin == AGENT_CHARTER['AUTH_PIN']) if auth_pin is not None else False
    }
    try:
        with open(CHANGELOG, 'a') as f:
            f.write(json.dumps(record) + '\n')
    except Exception as e:
        logger.warning('Failed to write change log: %s', e)
    return record

# -----------------------------------------------------------------------------
# Micro trade filter
# -----------------------------------------------------------------------------
class MicroTradeFilter:
    def __init__(self):
        try:
            self.min_size = int(os.getenv('MIN_MICRO_SIZE', AGENT_CHARTER['MIN_MICRO_SIZE']))
        except Exception:
            self.min_size = AGENT_CHARTER['MIN_MICRO_SIZE']

    def validate_size(self, size: int) -> bool:
        try:
            return abs(int(size)) >= int(self.min_size)
        except Exception:
            return False

# -----------------------------------------------------------------------------
# Execution Gate
# -----------------------------------------------------------------------------
class ExecutionGate:
    def __init__(self):
        self.micro = MicroTradeFilter()

    def validate_signal(self, signal: Dict[str, Any]) -> Tuple[bool, str]:
        # GLOBAL EXECUTION ENABLED (env override)
        exec_enabled = os.getenv('EXECUTION_ENABLED', 'false').lower() in ['true', '1', 'yes']
        if not exec_enabled:
            return False, 'EXECUTION_DISABLED'

        # timeframe gate
        if signal.get('timeframe') in ['M1', 'M5']:
            return False, 'M15_NOISE_REJECTED'

        # micro size gate
        size = int(signal.get('size', 0))
        if size and not self.micro.validate_size(size):
            return False, 'MICRO_SIZE_REJECTED'

        # rr gate
        rr = float(signal.get('rr', 0.0))
        if rr < float(os.getenv('MIN_RR', AGENT_CHARTER['MIN_RR'])):
            return False, 'MIN_RR_REJECTED'

        # risk gate
        max_risk = float(os.getenv('MAX_RISK_PER_TRADE', 0.01))
        if float(signal.get('risk', 0.0)) > max_risk:
            return False, 'HIGH_RISK_MISSING_PIN'

        return True, 'ACCEPTED'

# -----------------------------------------------------------------------------
# ML Reward System (Smart Aggression)
# -----------------------------------------------------------------------------
class MLRewardSystem:
    def __init__(self):
        self.base_confidence = 0.65
        self.min_rr = float(os.getenv('MIN_RR', AGENT_CHARTER['MIN_RR']))

    def evaluate_trade_setup(self, signal: Dict[str, Any]) -> Tuple[bool, float]:
        entry = float(signal.get('entry') or 0)
        sl = float(signal.get('sl') or 0)
        tp = float(signal.get('tp') or 0)
        if entry == 0 or abs(entry - sl) == 0:
            return False, 0.0
        risk = abs(entry - sl)
        reward = abs(tp - entry)
        rr_ratio = reward / (risk if risk != 0 else 1)
        return (rr_ratio >= self.min_rr), rr_ratio

# -----------------------------------------------------------------------------
# Built-in strategies (very small simplified placeholders)
# -----------------------------------------------------------------------------
def institutional_sd_signal(symbol: str) -> Optional[Dict[str, Any]]:
    price = random.random() * 1.2
    direction = random.choice(['BUY', 'SELL'])
    entry = round(price, 5)
    sl = round(entry - 0.001 if direction == 'BUY' else entry + 0.001, 5)
    tp = round(entry + 0.003 if direction == 'BUY' else entry - 0.003, 5)
    rr = abs(tp - entry) / (abs(entry - sl) if entry!=sl else 1)
    return {
        'pair': symbol,
        'direction': direction,
        'timeframe': 'M15',
        'entry': entry,
        'sl': sl,
        'tp': tp,
        'size': 1000,
        'rr': rr,
        'source': 'institutional_sd'
    }

def ema_scalper_signal(symbol: str) -> Optional[Dict[str, Any]]:
    price = random.random() + 1.0
    direction = 'BUY' if random.random() > 0.5 else 'SELL'
    entry = round(price, 5)
    sl = round(entry - 0.0005 if direction == 'BUY' else entry + 0.0005, 5)
    tp = round(entry + 0.0015 if direction == 'BUY' else entry - 0.0015, 5)
    rr = abs(tp - entry) / (abs(entry - sl) if entry!=sl else 1)
    return {
        'pair': symbol,
        'direction': direction,
        'timeframe': 'M15',
        'entry': entry,
        'sl': sl,
        'tp': tp,
        'size': 200,
        'rr': rr,
        'source': 'ema_scalper'
    }

def trap_reversal_signal(symbol: str):
    # generate wider RR
    entry = round(random.random() * 1.5 + 1.1, 5)
    direction = random.choice(['BUY', 'SELL'])
    sl = round(entry - 0.002 if direction == 'BUY' else entry + 0.002, 5)
    tp = round(entry + 0.007 if direction == 'BUY' else entry - 0.007, 5)
    rr = abs(tp - entry) / (abs(entry - sl) if entry!=sl else 1)
    return {'pair': symbol, 'direction': direction, 'timeframe': 'M15', 'entry': entry, 'sl': sl, 'tp': tp, 'size': 1500, 'rr': rr, 'source': 'trap_reversal'}

def holy_grail_signal(symbol: str):
    entry = round(random.random() + 1.0, 5)
    direction = 'BUY' if random.random() > 0.4 else 'SELL'
    sl = round(entry - 0.0015 if direction == 'BUY' else entry + 0.0015, 5)
    tp = round(entry + 0.005 if direction == 'BUY' else entry - 0.005, 5)
    rr = abs(tp - entry) / (abs(entry - sl) if entry!=sl else 1)
    return {'pair': symbol, 'direction': direction, 'timeframe': 'M15', 'entry': entry, 'sl': sl, 'tp': tp, 'size': 2000, 'rr': rr, 'source': 'holy_grail'}

# -----------------------------------------------------------------------------
# Simple connector stubs (simulate behavior)
# -----------------------------------------------------------------------------
class OandaConnector:
    def __init__(self):
        self.name = 'OANDA'
    def heartbeat(self):
        return True, 'OANDA PAPER OK'
    def place_order(self, order_spec: Dict[str, Any]):
        logger.info('OANDA PLACE ORDER: %s', order_spec)
        return True

class CoinbaseConnector:
    def __init__(self):
        self.name = 'COINBASE'
    def heartbeat(self):
        return True, 'COINBASE SANDBOX OK'
    def place_order(self, order_spec: Dict[str, Any]):
        logger.info('COINBASE PLACE ORDER: %s', order_spec)
        return True

class IBKRConnectorStub:
    def __init__(self):
        self.name = 'IBKR'
    def heartbeat(self):
        return True, 'IBKR STUB OK'
    def place_order(self, order_spec: Dict[str, Any]):
        logger.info('IBKR PLACE ORDER (STUB): %s', order_spec)
        return True

# -----------------------------------------------------------------------------
# Hive mind - generate M15 candidates including crypto
# -----------------------------------------------------------------------------
class HiveMindBridge:
    def __init__(self):
        self.last_scan = 0
        self.ml = MLRewardSystem()
        self.assets = ['EUR_USD', 'GBP_USD', 'USD_JPY', 'BTC-USD', 'ETH-USD']

    def fetch_inference(self):
        now = time.time()
        if now - self.last_scan < 1:  # more active for demo
            return None
        self.last_scan = now
        sym = random.choice(self.assets)
        if '-' in sym:  # crypto
            base = 50000 if 'BTC' in sym else 3000
            entry = base + (random.random() - 0.5) * 100
            direction = random.choice(['BUY', 'SELL'])
            risk = random.uniform(0.5, 2.0)
            sl = entry - (0.002 * entry) if direction == 'BUY' else entry + (0.002 * entry)
            tp = entry + (0.010 * entry) if direction == 'BUY' else entry - (0.010 * entry)
            size = 50  # $50 initial notional
        else:
            entry = round(1.1 + random.random() * 0.1, 5)
            direction = random.choice(['BUY', 'SELL'])
            risk = random.uniform(0.001, 0.01)
            sl = entry - 0.0005 if direction == 'BUY' else entry + 0.0005
            tp = entry + 0.002 if direction == 'BUY' else entry - 0.002
            size = 1000
        candidate = {'pair': sym, 'direction': direction, 'entry': entry, 'sl': sl, 'tp': tp, 'timeframe': 'M15', 'size': size, 'risk': risk}
        ok, rr = self.ml.evaluate_trade_setup(candidate)
        candidate['rr'] = rr
        candidate['ml_note'] = f'APPROVED (RR: {rr:.2f})' if ok else f'REJECTED (RR: {rr:.2f})'
        return candidate if ok else None

# -----------------------------------------------------------------------------
# Strategy aggregator (combines strategies and hive mind signals)
# -----------------------------------------------------------------------------
class StrategyAggregator:
    def __init__(self):
        self.signals = []
    def ingest(self, sig: Dict[str, Any]):
        self.signals.append(sig)
        return True, 'accepted'
    def get_latest(self):
        return self.signals[-1] if self.signals else None

# -----------------------------------------------------------------------------
# RBotZilla engine (lite)
# -----------------------------------------------------------------------------
class RBotZillaEngine:
    def __init__(self):
        self.hive = HiveMindBridge()
        self.aggregator = StrategyAggregator()
        self.gate = ExecutionGate()
        self.oanda = OandaConnector()
        self.coinbase = CoinbaseConnector()
        self.ibkr = IBKRConnectorStub()
        log_change('SYSTEM_START', {'version': 'bundle_v1'}, auth_pin=AGENT_CHARTER['AUTH_PIN'])

    def tick(self):
        sig = self.hive.fetch_inference()
        if not sig:
            return
        logger.info('Hive signal: %s %s (RR: %.2f)', sig['pair'], sig['direction'], sig['rr'])
        valid, msg = self.aggregator.ingest(sig)
        if not valid:
            logger.warning('Aggregator rejected: %s', msg)
            return
        latest = self.aggregator.get_latest()
        if latest is None:
            return
        approved, reason = self.gate.validate_signal(latest)
        if not approved:
            logger.warning('Gate blocked: %s', reason)
            log_change('GATE_BLOCK', {'reason': reason, 'signal': latest}, auth_pin=AGENT_CHARTER['AUTH_PIN'])
            return
        # route to broker
        if '-' in latest['pair']:
            order_spec = {'instrument': latest['pair'], 'units': latest['size'], 'side': latest['direction']}
            if 'sl' in latest and 'tp' in latest:
                order_spec['sl'] = latest['sl']
                order_spec['tp'] = latest['tp']
                safe_place_order(self.coinbase, order_spec)
        elif latest['pair'].endswith('JPY'):
            order_spec = {'instrument': latest['pair'], 'units': latest['size'], 'sl': latest.get('sl'), 'tp': latest.get('tp')}
            if not order_spec['sl'] or not order_spec['tp']:
                logger.warning('OANDA ORDER BLOCKED (NO SL/TP)')
            else:
                    safe_place_order(self.oanda, order_spec)
        else:
            order_spec = {'instrument': latest['pair'], 'units': latest['size'], 'sl': latest.get('sl'), 'tp': latest.get('tp')}
            if not order_spec['sl'] or not order_spec['tp']:
                logger.warning('OANDA ORDER BLOCKED (NO SL/TP)')
            else:
                    safe_place_order(self.oanda, order_spec)
        log_change('TRADE_EXECUTED', {'signal': latest}, auth_pin=AGENT_CHARTER['AUTH_PIN'])

    def run(self, seconds: int = 10):
        end = time.time() + seconds
        while time.time() < end:
            self.tick()
            time.sleep(0.5)

if __name__ == '__main__':
    # Small demo run
    run_seconds = 10
    try:
        import argparse
        p = argparse.ArgumentParser()
        p.add_argument('--run-seconds', type=int, default=10)
        p.add_argument('--simulate', action='store_true')
        args = p.parse_args()
        if args.simulate:
            os.environ['EXECUTION_ENABLED'] = os.getenv('EXECUTION_ENABLED', 'false')
        # run engine
        engine = RBotZillaEngine()
        engine.run(args.run_seconds)
        logger.info('Demo run complete')
    except Exception as e:
        logger.exception('Failed to run bundle: %s', e)
