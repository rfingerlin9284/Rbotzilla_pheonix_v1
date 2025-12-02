#!/usr/bin/env python3
"""
install_tri_market.py

Installs Tri-Market (OANDA + IBKR + Coinbase) connectors, Hive mind, and engine
with explicit safety steps. Requires PIN authorization when modifying files.

Instructions:
  1) Stop any running engine: pkill -f rbotzilla_engine.py
  2) Run: python3 install_tri_market.py --pin 841921
  3) Verify files created (ibkr_connection.py, util/smart_aggression.py,
     hive_mind_bridge.py, rbotzilla_engine.py)

This script will backup existing files when present with a timestamped .bak
"""
import os
import sys
import argparse
import time
from datetime import datetime

ROOT = os.path.abspath(os.path.dirname(__file__))
BACKUP_TS = datetime.now().strftime('%Y%m%d%H%M%S')

FILES = {
    'ibkr_connection.py': '''import logging
import time
import threading
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
from auth_manager import AuthManager

logger = logging.getLogger("IBKR_Conn")

class IBKRApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.nextOrderId = None
        self.is_connected = False

    def error(self, reqId, errorCode, errorString):
        if errorCode in [2104, 2106, 2158]: # Benign data farm msgs
            return
        logger.warning(f"IBKR Msg {errorCode}: {errorString}")

    def nextValidId(self, orderId: int):
        self.nextOrderId = orderId
        self.is_connected = True
        logger.info(f"✅ IBKR Connected via Gateway. Next Order ID: {orderId}")

class IBKRConnection:
    def __init__(self):
        self.auth = AuthManager()
        self.config = self.auth.get_ibkr_config()
        self.app = IBKRApp()
        self.thread = threading.Thread(target=self.run_loop, daemon=True)
        self.started = False

    def connect(self):
        try:
            host = self.config['host']
            port = self.config['port']
            logger.info(f"🔌 Connecting to IBKR Gateway ({host}:{port})...")
            self.app.connect(host, port, self.config['client_id'])
            if not self.started:
                self.thread.start()
                self.started = True
            for _ in range(20):
                if self.app.is_connected:
                    return True
                time.sleep(0.5)
            logger.error("❌ IBKR Connection Timed Out. Check Gateway config.")
            return False
        except Exception as e:
            logger.error(f"❌ IBKR Exception: {e}")
            return False

    def run_loop(self):
        self.app.run()

    def place_order(self, order_spec):
        if not self.app.is_connected:
            return False
        contract = Contract()
        contract.symbol = order_spec['symbol']
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"
        order = Order()
        order.action = order_spec['action']
        order.totalQuantity = order_spec['qty']
        order.orderType = "MKT"
        if self.app.nextOrderId:
            self.app.placeOrder(self.app.nextOrderId, contract, order)
            self.app.nextOrderId += 1
            logger.info(f"🚀 IBKR ORDER SENT: {order_spec['action']} {order_spec['qty']} {order_spec['symbol']}")
            return True
        return False
''',

    'util/smart_aggression.py': '''import logging

# ==============================================================================
# 🔥 AGGRESSION PROFILES (JANUS STRATEGY)
# ==============================================================================
PROFILES = {
    "BERSERKER": { # Paper
        "min_rr": 2.0,
        "position_size_usd": 1000,
        "confidence_threshold": 0.60,
        "mode": "AGGRESSIVE LEARNING"
    },
    "SNIPER": { # Live
        "min_rr": 3.5,
        "position_size_usd": 25,
        "confidence_threshold": 0.85,
        "mode": "CAPITAL PROTECTION"
    }
}

class MLRewardSystem:
    def __init__(self):
        self.base_confidence = 0.65
        self.logger = logging.getLogger("Brain")

    def evaluate_trade(self, signal, is_live_money):
        profile = PROFILES["SNIPER"] if is_live_money else PROFILES["BERSERKER"]
        entry = signal.get('entry', 0)
        stop = signal.get('sl', 0)
        target = signal.get('tp', 0)
        if entry == 0 or abs(entry-stop) == 0:
            return False, 0.0
        risk = abs(entry - stop)
        reward = abs(target - entry)
        rr_ratio = reward / (risk if risk != 0 else 1)
        if rr_ratio < profile['min_rr']:
            return False, f"REJECTED: RR {rr_ratio:.2f} < {profile['min_rr']}"
        return True, {"size": profile['position_size_usd'], "rr": rr_ratio, "mode": profile['mode']}
''',

    'hive_mind_bridge.py': '''import random
import time
from datetime import datetime
from util.smart_aggression import MLRewardSystem

class HiveMindBridge:
    def __init__(self):
        self.ml_system = MLRewardSystem()
        self.last_scan = time.time()

    def fetch_inference(self):
        now = time.time()
        if now - self.last_scan < 3:
            return None
        self.last_scan = now
        assets = ["EUR_USD", "GBP_USD", "BTC-USD", "ETH-USD", "NVDA", "TSLA"]
        pair = random.choice(assets)
        is_live = '-' in pair
        vol_mul = 50 if is_live else 1
        direction = random.choice(["BUY", "SELL"])
        entry = 150.00 if 'NVDA' in pair else (50000 if 'BTC' in pair else 1.1000)
        risk_pips = random.randint(10, 40) * 0.0001 * vol_mul
        reward_pips = random.randint(20, 200) * 0.0001 * vol_mul
        sl = entry - risk_pips if direction == 'BUY' else entry + risk_pips
        tp = entry + reward_pips if direction == 'BUY' else entry - reward_pips
        candidate = { 'pair': pair, 'direction': direction, 'entry': entry, 'sl': sl, 'tp': tp, 'is_live_money': is_live }
        valid, res = self.ml_system.evaluate_trade(candidate, is_live)
        if valid:
            candidate['ml_data'] = res
            return candidate
        return None
''',

    'rbotzilla_engine.py': '''import time
import logging
import sys
from auth_manager import AuthManager
from oanda_connection import OandaConnection
from coinbase_connection import CoinbaseConnection
from ibkr_connection import IBKRConnection
from hive_mind_bridge import HiveMindBridge
from foundation.trading_mode import safe_place_order

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [RBOTZILLA] - %(message)s', handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger('Engine')

class RBotZillaEngine:
    def __init__(self):
        logger.info('🦖 RBOTZILLA TRI-MARKET INITIALIZING...')
        self.auth = AuthManager()
        self.oanda = OandaConnection()
        self.coinbase = CoinbaseConnection()
        self.ibkr = IBKRConnection()
        self.brain = HiveMindBridge()
        self.running = False

    def start(self):
        ok_o, msg_o = self.oanda.heartbeat()
        ok_c, msg_c = self.coinbase.heartbeat()
        ok_i = self.ibkr.connect()
        logger.info(f'🔌 OANDA: {msg_o}')
        logger.info(f'🔌 COINBASE: {msg_c}')
        logger.info(f'🔌 IBKR: {'Connected' if ok_i else 'Awaiting Gateway'}')
        self.running = True
        try:
            while self.running:
                self.tick()
                time.sleep(1)
        except KeyboardInterrupt:
            self.shutdown()

    def tick(self):
        infer = self.brain.fetch_inference()
        if not infer: return
        asset = infer['pair']
        data = infer['ml_data']
        logger.info(f"🧠 SIGNAL: {asset} {infer['direction']} | {data['mode']} | RR: {data['rr']:.2f}")
            if '-' in asset:
            logger.info('⚡ ROUTING TO COINBASE (Live)')
            safe_place_order(self.coinbase, { 'instrument': asset, 'units': str(data['size']), 'side': 'BUY' if infer['direction']=='BUY' else 'SELL', 'sl': infer.get('sl'), 'tp': infer.get('tp') })
        elif '_' in asset:
            logger.info('⚡ ROUTING TO OANDA (Paper)')
            units = data['size'] * 10
            order_spec = { 'instrument': asset, 'units': int(units) if infer['direction']=='BUY' else int(-units), 'type': 'MARKET', 'sl': infer.get('sl'), 'tp': infer.get('tp') }
            if not order_spec['sl'] or not order_spec['tp']:
                logger.warning('🛡️ BLOCKED: OANDA order prevented — SL/TP required.')
            else:
                safe_place_order(self.oanda, order_spec)
        else:
            logger.info('⚡ ROUTING TO IBKR (Paper)')
            safe_place_order(self.ibkr, { 'symbol': asset, 'action': infer['direction'], 'qty': 50 })

    def shutdown(self):
        logger.info('🛑 RBOTZILLA SHUTTING DOWN...')
        self.running = False

if __name__ == '__main__':
    RBotZillaEngine().start()
'''
}

def backup_file(path):
    if os.path.exists(path):
        bak = f"{path}.bak_{BACKUP_TS}"
        print(f"Backing up {path} -> {bak}")
        os.rename(path, bak)
        return bak
    return None

def write_file(path, content, pin=None):
    # Requires PIN to modify files
    if pin != 841921:
        raise PermissionError('PIN required to install tri-market files')
    abs_path = os.path.join(ROOT, path)
    # Backup if exists
    backup_file(abs_path)
    # Ensure directory exists
    dirpath = os.path.dirname(abs_path)
    if dirpath and not os.path.exists(dirpath):
        os.makedirs(dirpath, exist_ok=True)
    with open(abs_path, 'w') as f:
        f.write(content)
    print(f"Wrote {path}")

def main(pin):
    print('Installing Tri-Market architecture...')
    for fname, content in FILES.items():
        write_file(fname, content, pin=pin)
    print('Installation complete. Compiling files to verify...')
    # Attempt a short compile check
    try:
        import py_compile
        for fname in FILES.keys():
            p = os.path.join(ROOT, fname)
            py_compile.compile(p, doraise=True)
            print(f'Compiled OK: {fname}')
    except Exception as e:
        print('Compilation error:', e)
    print('Done.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pin', type=int, required=True)
    args = parser.parse_args()
    try:
        main(args.pin)
    except PermissionError as pe:
        print('PermissionError:', pe)
        sys.exit(2)
    except Exception as e:
        print('Install failed:', e)
        sys.exit(1)
