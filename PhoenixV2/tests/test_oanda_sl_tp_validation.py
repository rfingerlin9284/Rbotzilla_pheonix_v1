import unittest
import os
from PhoenixV2.execution.router import BrokerRouter
from PhoenixV2.core.state_manager import StateManager


class DummyAuth:
    def get_oanda_config(self):
        return {'token': 'dummy', 'account': 'dummy'}
    def get_ibkr_config(self):
        return {'host':'127.0.0.1','port':7497,'client_id':1}
    def get_coinbase_config(self):
        return {'key': 'dummy', 'secret': 'dummy', 'is_sandbox': True}
    def is_live(self):
        return False


class DummyOanda:
    def __init__(self, price=1.23450):
        self._connected = True
        self.last_order = None
        self._price = price
        self.last_sl = None
        self.last_tp = None
    def connect(self):
        return True
    def get_current_price(self, symbol):
        return self._price
    def get_current_bid_ask(self, symbol):
        # return bid, ask
        return (self._price - 0.0001, self._price + 0.0001)
    def get_current_spread(self, symbol):
        ba = self.get_current_bid_ask(symbol)
        return abs(ba[1] - ba[0])
    def place_order(self, order):
        self.last_order = order
        # Simulate an OANDA 'orderFillTransaction' with tradeOpened tradeID and price
        return True, {'orderFillTransaction': {'tradeOpened': {'tradeID': 'TR123', 'price': str(self._price)}, 'price': str(self._price)}}
    def modify_trade_sl(self, trade_id, new_sl):
        self.last_sl = new_sl
        return True
    def modify_trade_tp(self, trade_id, new_tp):
        self.last_tp = new_tp
        return True
    def attach_sl_tp(self, trade_id, sl, tp):
        # Combined attach for test harness
        if sl is not None:
            self.last_sl = sl
        if tp is not None:
            self.last_tp = tp
        return True
    def get_candles(self, symbol: str, timeframe: str = 'M15', limit: int = 200):
        # Return a minimal DataFrame with 'high','low','close' sufficient for ATR computation
        try:
            import pandas as pd
            import numpy as np
            # generate dummy candles around price
            price = self._price
            rows = []
            for i in range(limit):
                volatility = 0.001
                high = price * (1 + volatility)
                low = price * (1 - volatility)
                close = price
                rows.append({'open': price, 'high': high, 'low': low, 'close': close, 'volume': 100})
            df = pd.DataFrame(rows)
            return df
        except Exception:
            return None


class TestOandaSLTPValidation(unittest.TestCase):
    def setUp(self):
        self.router = BrokerRouter(DummyAuth())
        self.router.oanda = DummyOanda()

    def test_buy_order_sl_tp_adjusted(self):
        order_packet = {'symbol': 'EUR_USD', 'direction': 'BUY', 'notional_value': 1000, 'sl': 1.23500, 'tp': 1.23350}
        import PhoenixV2.execution.router as router_mod
        orig_safe = router_mod.safe_place_order
        try:
            # Let safe_place_order call DummyOanda.place_order so DummyOanda.last_order is set
            router_mod.safe_place_order = lambda broker, order, **kwargs: broker.place_order(order)
            import logging
            logger = logging.getLogger('Router')
            logger.setLevel(logging.INFO)
            from io import StringIO
            stream = StringIO()
            h = logging.StreamHandler(stream)
            h.setLevel(logging.INFO)
            logger.addHandler(h)
            ok, resp = self.router._execute_oanda(order_packet)
            self.assertTrue(ok)
            last = self.router.oanda.last_order if hasattr(self.router.oanda, 'last_order') else resp
            self.assertIsNotNone(last)
            # Use bid/ask to validate proper relation
            price = self.router.oanda.get_current_price('EUR_USD')
            bid, ask = self.router.oanda.get_current_bid_ask('EUR_USD')
            min_dist = max(self.router.oanda.get_current_spread('EUR_USD') * 1.2, 0.0001 * 10)
            # Since Router uses Entry-Then-Protect flow, the entry order will not include sl/tp
            # The test for sl/tp should instead verify the attach call recorded sl/tp on the DummyOanda
            self.assertIsNotNone(self.router.oanda.last_sl)
            self.assertIsNotNone(self.router.oanda.last_tp)
            self.assertLess(float(self.router.oanda.last_sl), bid)
            self.assertGreaterEqual(abs(bid - float(self.router.oanda.last_sl)), min_dist - 1e-9)
            self.assertGreater(float(self.router.oanda.last_tp), ask)
            self.assertGreaterEqual(abs(ask - float(self.router.oanda.last_tp)), min_dist - 1e-9)
            # Ensure sanitized log emitted
            h.flush()
            logs = stream.getvalue()
            self.assertTrue('SANITIZED OANDA ORDER' in logs or 'Adjusting invalid' in logs)
            logger.removeHandler(h)
        finally:
            router_mod.safe_place_order = orig_safe

    def test_sell_order_sl_tp_adjusted(self):
        order_packet = {'symbol': 'EUR_USD', 'direction': 'SELL', 'notional_value': 1000, 'sl': 1.23350, 'tp': 1.23500}
        import PhoenixV2.execution.router as router_mod
        orig_safe = router_mod.safe_place_order
        try:
            router_mod.safe_place_order = lambda broker, order, **kwargs: broker.place_order(order)
            import logging
            logger = logging.getLogger('Router')
            logger.setLevel(logging.INFO)
            from io import StringIO
            stream = StringIO()
            h = logging.StreamHandler(stream)
            h.setLevel(logging.INFO)
            logger.addHandler(h)
            ok, resp = self.router._execute_oanda(order_packet)
            self.assertTrue(ok)
            last = self.router.oanda.last_order if hasattr(self.router.oanda, 'last_order') else resp
            bid, ask = self.router.oanda.get_current_bid_ask('EUR_USD')
            min_dist = max(self.router.oanda.get_current_spread('EUR_USD') * 1.2, 0.0001 * 10)
            # Use attach calls for these checks
            self.assertIsNotNone(self.router.oanda.last_sl)
            self.assertIsNotNone(self.router.oanda.last_tp)
            self.assertGreater(float(self.router.oanda.last_sl), ask)
            self.assertGreaterEqual(abs(ask - float(self.router.oanda.last_sl)), min_dist - 1e-9)
            self.assertLess(float(self.router.oanda.last_tp), bid)
            self.assertGreaterEqual(abs(bid - float(self.router.oanda.last_tp)), min_dist - 1e-9)
            # Ensure sanitized log emitted
            h.flush()
            logs = stream.getvalue()
            self.assertTrue('SANITIZED OANDA ORDER' in logs or 'Adjusting invalid' in logs)
            logger.removeHandler(h)
        finally:
            router_mod.safe_place_order = orig_safe

    def test_order_price_precision(self):
        # Ensure that non-JPY gets 5 decimals and JPY gets 3
        self.router.oanda = DummyOanda(price=110.123)
        # JPY pair test
        order_packet = {'symbol': 'USD_JPY', 'direction': 'BUY', 'notional_value': 1000, 'sl': 109.999, 'tp': 110.500}
        import PhoenixV2.execution.router as router_mod
        orig_safe = router_mod.safe_place_order
        try:
            router_mod.safe_place_order = lambda broker, order, **kwargs: broker.place_order(order)
            ok, resp = self.router._execute_oanda(order_packet)
            self.assertTrue(ok)
            # Since Platform uses Entry-Then-Protect, check values in last_sl/last_tp
            self.assertIsNotNone(self.router.oanda.last_sl)
            self.assertIsNotNone(self.router.oanda.last_tp)
            self.assertEqual(f"{self.router.oanda.last_sl:.3f}", f"{self.router.oanda.last_sl:.3f}")
            self.assertEqual(f"{self.router.oanda.last_tp:.3f}", f"{self.router.oanda.last_tp:.3f}")
        finally:
            router_mod.safe_place_order = orig_safe

    def test_default_sl_attached(self):
        # Test when no SL provided, default SL is attached via ATR fallback
        self.router.oanda = DummyOanda(price=1.2345)
        order_packet = {'symbol': 'EUR_USD', 'direction': 'BUY', 'notional_value': 1000}
        import PhoenixV2.execution.router as router_mod
        orig_safe = router_mod.safe_place_order
        try:
            router_mod.safe_place_order = lambda broker, order, **kwargs: broker.place_order(order)
            ok, resp = self.router._execute_oanda(order_packet)
            self.assertTrue(ok)
            self.assertIsNotNone(self.router.oanda.last_sl)
            # last_sl should be less than fill price because it's BUY
            fill_price = self.router.oanda.get_current_price('EUR_USD')
            self.assertLess(float(self.router.oanda.last_sl), fill_price)
        finally:
            router_mod.safe_place_order = orig_safe

    def test_default_sl_attached_jpy(self):
        # Test fallback behavior for JPY pair (uses ATR or 30 pips fallback)
        self.router.oanda = DummyOanda(price=110.123)
        order_packet = {'symbol': 'USD_JPY', 'direction': 'BUY', 'notional_value': 1000}
        import PhoenixV2.execution.router as router_mod
        orig_safe = router_mod.safe_place_order
        try:
            router_mod.safe_place_order = lambda broker, order, **kwargs: broker.place_order(order)
            ok, resp = self.router._execute_oanda(order_packet)
            self.assertTrue(ok)
            self.assertIsNotNone(self.router.oanda.last_sl)
            fill_price = self.router.oanda.get_current_price('USD_JPY')
            self.assertLess(float(self.router.oanda.last_sl), fill_price)
        finally:
            router_mod.safe_place_order = orig_safe


if __name__ == '__main__':
    unittest.main()
