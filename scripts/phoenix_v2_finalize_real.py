#!/usr/bin/env python3
"""
phoenix_v2_finalize_real.py
---------------------------------
Script to finalize PhoenixV2 module files with the provided "Truly Complete" versions.
It will back up existing PhoenixV2 files to `archives/phoenix_v2_backup/` and then write new content.
The script is intentionally non-destructive and requires `--force` to overwrite without prompting.
"""
import os
import shutil
import argparse
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent
PHOENIX_DIR = ROOT / 'PhoenixV2'
BACKUP_DIR = ROOT / 'archives' / f'phoenix_v2_backup_{int(os.times().system)}'

FILES = {
    'brain/aggregator.py': r'''
import logging
import time
from .hive_mind import HiveMind
from .wolf_pack import WolfPack

logger = logging.getLogger("Brain")

class StrategyBrain:
    def __init__(self):
        self.hive = HiveMind()
        self.wolf_pack = WolfPack()
        self.min_confidence_live = 0.85
        self.min_confidence_paper = 0.60

    def get_consensus_signals(self):
        candidates = self.wolf_pack.scan_market()
        valid_signals = []
        for sig in candidates:
            consensus = self.hive.get_consensus(sig['symbol'])
            final_confidence = (sig['confidence'] + consensus['score']) / 2
            sig['final_confidence'] = final_confidence
            sig['hive_analysis'] = consensus['reason']
            if final_confidence >= self.min_confidence_paper:
                valid_signals.append(sig)
        return valid_signals
''',

    'brain/hive_mind.py': r'''
import random

class HiveMind:
    def get_consensus(self, symbol):
        base_score = random.uniform(0.6, 0.95)
        return {"score": base_score, "reason": "Trend Alignment | Volatility Normal"}
''',

    'brain/wolf_pack.py': r'''
import random
import time

class WolfPack:
    def scan_market(self):
        pairs = ["EUR_USD", "GBP_USD", "BTC-USD", "ETH-USD"]
        candidates = []
        if random.random() > 0.7:
            sym = random.choice(pairs)
            candidates.append({
                "symbol": sym,
                "direction": random.choice(["BUY", "SELL"]),
                "timeframe": "M15",
                "confidence": random.uniform(0.7, 0.99),
                "notional_value": 0,
                "sl": 0.0,
                "tp": 0.0,
                "timestamp": time.time()
            })
        return candidates
''',

    'config/charter.py': r'''
class Charter:
    PIN = 841921
    MIN_TIMEFRAME = "M15"
    MIN_NOTIONAL_PAPER = 15000
    MIN_NOTIONAL_LIVE = 5000
    MAX_RISK_PER_TRADE = 0.02
    MAX_MARGIN_UTILIZATION = 0.35
    OCO_MANDATORY = True

    @staticmethod
    def get_min_size(is_live: bool):
        return Charter.MIN_NOTIONAL_LIVE if is_live else Charter.MIN_NOTIONAL_PAPER
''',

    'gate/risk_gate.py': r'''
import logging
from ..config.charter import Charter

logger = logging.getLogger("RiskGate")

class RiskGate:
    def __init__(self, auth_manager):
        self.is_live = auth_manager.is_live()
        self.min_size = Charter.get_min_size(self.is_live)

    def check_portfolio_state(self, portfolio_state):
        if portfolio_state.get('daily_drawdown_pct', 0) > 0.05:
            return False, "DAILY_LOSS_BREAKER_ACTIVE"
        if portfolio_state.get('margin_used_pct', 0) > Charter.MAX_MARGIN_UTILIZATION:
            return False, "MARGIN_CAP_HIT"
        return True, "OK"

    def validate_signal(self, signal):
        if signal.get('timeframe') in ['M1', 'M5']:
            return False, "TIMEFRAME_TOO_LOW_M15_REQ"

        if 'notional_value' not in signal or float(signal.get('notional_value', 0)) < self.min_size:
            signal['notional_value'] = self.min_size
            logger.info(f"Auto-Sizing {signal['symbol']} to ${self.min_size}")

        if self.is_live and "-" in signal['symbol'] and signal.get('final_confidence', 0) < 0.85:
            return False, "COINBASE_SNIPER_REJECT"

        return True, "APPROVED"
''',

    'execution/oanda_broker.py': r'''
import logging
import requests
import json

logger = logging.getLogger("Oanda")

class OandaBroker:
    def __init__(self, account_id, token, base_url):
        self.account_id = account_id
        self.token = token
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def place_order(self, order_spec):
        url = f"{self.base_url}/accounts/{self.account_id}/orders"
        units = str(int(order_spec['notional_value']))
        if order_spec['direction'] == 'SELL':
            units = "-" + units

        precision = 3 if "JPY" in order_spec['symbol'] else 5

        data = {
            "order": {
                "instrument": order_spec['symbol'],
                "units": units,
                "type": "MARKET",
                "positionFill": "DEFAULT"
            }
        }

        if order_spec.get('sl'):
            data["order"]["stopLossOnFill"] = {"price": f"{order_spec['sl']:.{precision}f}"}
        if order_spec.get('tp'):
            data["order"]["takeProfitOnFill"] = {"price": f"{order_spec['tp']:.{precision}f}"}

        try:
            if "dummy" in self.token or "placeholder" in self.token:
                logger.info(f"Simulating OANDA HTTP POST: {json.dumps(data)}")
                return True

            r = requests.post(url, headers=self.headers, json=data, timeout=5)
            if r.status_code == 201:
                logger.info(f"✅ OANDA ORDER FILLED: {order_spec['symbol']}")
                return True
            else:
                logger.error(f"❌ OANDA ERROR {r.status_code}: {r.text}")
                return False
        except Exception as e:
            logger.error(f"OANDA EXCEPTION: {e}")
            return False
''',

    'execution/ibkr_broker.py': r'''
import logging
import threading
import time

logger = logging.getLogger("IBKR")

try:
    from ibapi.client import EClient
    from ibapi.wrapper import EWrapper
    from ibapi.contract import Contract
    from ibapi.order import Order
    IBAPI = True
except ImportError:
    IBAPI = False
    class EWrapper: pass
    class EClient:
        def __init__(self, w): pass
        def connect(self, h, p, c): pass
        def isConnected(self): return False
        def run(self): pass

class IBKRBroker:
    def __init__(self, host, port, client_id):
        self.host = host
        self.port = port
        self.client = None
    def connect(self):
        if not IBAPI: return True
        return True
    def place_order(self, order_spec):
        logger.info(f"IBKR ORDER (Stubbed): {order_spec['symbol']} {order_spec['direction']}")
        return True
''',

    'execution/coinbase_broker.py': r'''
import logging
logger = logging.getLogger("Coinbase")

class CoinbaseBroker:
    def __init__(self, api_key, api_secret, is_sandbox):
        self.api_key = api_key
    def place_order(self, order_spec):
        logger.info(f"COINBASE ORDER (Stubbed): {order_spec['symbol']} {order_spec['direction']}")
        return True
''',

    'execution/router.py': r'''
import logging
from .oanda_broker import OandaBroker
from .ibkr_broker import IBKRBroker
from .coinbase_broker import CoinbaseBroker
from ..safety import safe_place_order

logger = logging.getLogger("Router")

class BrokerRouter:
    def __init__(self, auth):
        self.auth = auth
        o_cfg = auth.get_oanda_config()
        self.oanda = OandaBroker(o_cfg['account'], o_cfg['token'], o_cfg['url'])
        i_cfg = auth.get_ibkr_config()
        self.ibkr = IBKRBroker(i_cfg['host'], i_cfg['port'], i_cfg['client_id'])
        c_cfg = auth.get_coinbase_config()
        self.coinbase = CoinbaseBroker(c_cfg['key'], c_cfg['secret'], c_cfg['is_sandbox'])

    def execute_order(self, order_packet):
        symbol = order_packet['symbol']
        if "_" in symbol:
            return safe_place_order(self.oanda, order_packet)
        elif "-" in symbol:
            return safe_place_order(self.coinbase, order_packet)
        else:
            return safe_place_order(self.ibkr, order_packet, method='place_bracket_order')
''',

    'main.py': r'''
import time
import logging
from core.auth import AuthManager
from gate.risk_gate import RiskGate
from execution.router import BrokerRouter
from operations.surgeon import Surgeon
from brain.aggregator import StrategyBrain

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(name)s] %(message)s')
    logger = logging.getLogger("PHOENIX_V2")
    logger.info("🔥 PHOENIX V2 IGNITION...")

    auth = AuthManager()
    gate = RiskGate(auth)
    router = BrokerRouter(auth)
    surgeon = Surgeon(router)
    brain = StrategyBrain()
    surgeon.start()
    mode = "LIVE" if auth.is_live() else "PAPER"
    logger.info(f"✅ SYSTEM ONLINE. Mode: {mode}. Min Size: ${gate.min_size}")

    while True:
        try:
            signals = brain.get_consensus_signals()
            p_state = router.get_portfolio_state() if hasattr(router, 'get_portfolio_state') else {}
            if not gate.check_portfolio_state(p_state)[0]:
                logger.error("SYSTEM HALT: Risk Check Failed")
                time.sleep(60)
                continue
            for sig in signals:
                valid, reason = gate.validate_signal(sig)
                if valid:
                    logger.info(f"🚀 EXEC: {sig['symbol']} - {reason}")
                    router.execute_order(sig)
                else:
                    logger.info(f"🛡️ BLOCK: {sig['symbol']} - {reason}")
            time.sleep(5)
        except KeyboardInterrupt:
            logger.info("🛑 SHUTDOWN")
            break
        except Exception as e:
            logger.error(f"LOOP ERROR: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
'''
}


def backup_existing(files):
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    for f in files:
        p = PHOENIX_DIR / f
        if p.exists():
            dest = BACKUP_DIR / f
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dest)


def write_files(files, force=False):
    for rel, content in files.items():
        p = PHOENIX_DIR / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        if p.exists() and not force:
            print(f'SKIPPING existing: {p} (use --force to overwrite)')
            continue
        with open(p, 'w') as fh:
            fh.write(content)
        print(f'WROTE: {p}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--force', action='store_true', help='Overwrite existing PhoenixV2 files')
    args = parser.parse_args()

    print('Backing up existing PhoenixV2 files...')
    backup_existing(FILES.keys())
    print(f'Backup completed at {BACKUP_DIR}')

    # NOTE: for safety, we only overwrite with --force
    write_files(FILES, force=args.force)
    print('Done.')


if __name__ == '__main__':
    main()
