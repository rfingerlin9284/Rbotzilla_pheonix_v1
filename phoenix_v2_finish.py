#!/usr/bin/env python3
import os

ROOT = "PhoenixV2"
files = {}

files[f"{ROOT}/execution/safety.py"] = """
import logging
from foundation.trading_mode import safe_place_order as foundation_safe_place_order, is_live

logger = logging.getLogger("Safety")

def safe_place_order(broker_instance, order_packet, method='place_order'):
    symbol = order_packet.get('symbol', order_packet.get('product_id', 'UNKNOWN'))
    _is_live = is_live()
    if _is_live:
        logger.warning(f"⚠️ ATTEMPTING LIVE ORDER ON {symbol}")
    else:
        logger.info(f"📝 PAPER ORDER ON {symbol}")
    try:
        if method == 'place_order':
            return foundation_safe_place_order(broker_instance, **order_packet)
        method_func = getattr(broker_instance, method)
        resp = method_func(order_packet)
        if isinstance(resp, tuple) and len(resp) == 2:
            return resp
        return True, resp if resp is not None else {}
    except Exception as e:
        logger.exception("Safety wrapper: error placing order: %s", e)
        return False, {'error': str(e)}
"""

files[f"{ROOT}/execution/router.py"] = """
import logging
from .oanda_broker import OandaBroker
from .ibkr_broker import IBKRBroker
from .coinbase_broker import CoinbaseBroker
from .safety import safe_place_order

logger = logging.getLogger("Router")

class BrokerRouter:
    def __init__(self, auth):
        self.auth = auth
        # initialize connectors
        self._init_connectors()

    def _determine_broker(self, symbol):
        if '_' in symbol: return 'OANDA'
        if '-' in symbol: return 'COINBASE'
        return 'IBKR'

    def _execute_ibkr(self, order_packet):
        if not self.ibkr:
            return False, {'error': 'IBKR not configured'}
        if not self.ibkr._connected and not self.ibkr.connect():
            return False, {'error': 'IBKR not connected'}
        ibkr_order = {
            'symbol': order_packet['symbol'],
            'action': order_packet['direction'],
            'qty': int(order_packet.get('notional_value', 100) / 100),
            'sl': order_packet.get('sl'),
            'tp': order_packet.get('tp')
        }
        success, resp = safe_place_order(self.ibkr, ibkr_order, method='place_bracket_order')
        return success, resp
"""

files["PHOENIX_V2_READY.md"] = """
# PHOENIX V2: READY

Safety wrapper and router modifications were applied.
"""

def install():
    print('Applying Phoenix V2 finish package...')
    for p, content in files.items():
        path = os.path.abspath(p)
        d = os.path.dirname(path)
        os.makedirs(d, exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)
        print('Wrote', path)
    print('Complete')

if __name__ == '__main__':
    install()
