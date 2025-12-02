import unittest
from datetime import datetime
from PhoenixV2.operations.surgeon import Surgeon

class FakeRouter:
    def __init__(self, positions):
        self.positions = positions
        self.closed = []
        self.oanda = self # Mock Oanda
    
    def get_portfolio_state(self):
        return {'open_positions': self.positions}
    
    def close_trade(self, trade_id):
        self.closed.append(trade_id)
        
    def get_current_price(self, symbol):
        return 0.65489

    def modify_trade_sl(self, trade_id, new_sl):
        return True

class SurgeonTest(unittest.TestCase):
    def test_kill_micro_trade_and_trail_big(self):
        now_str = datetime.utcnow().isoformat()
        
        # Micro trade: Should be killed (< 1000 units)
        micro = {
            'id': 'micro1',
            'instrument': 'AUD_USD',
            'currentUnits': 61,
            'price': 0.65489,
            'unrealizedPL': 0.0,
            'stopLossOrder': {'price': 0.65},
            'takeProfitOrder': None,
            'openTime': now_str # Fresh
        }
        
        # Large trade: Should NOT be killed (Fresh time, good size)
        large = {
            'id': 'big1',
            'instrument': 'AUD_USD',
            'currentUnits': 14660,
            'price': 0.65489,
            'unrealizedPL': 200.0,
            'stopLossOrder': {'price': 0.65},
            'takeProfitOrder': None,
            'openTime': now_str # Fresh! (Prevents Stagnant Winner trigger)
        }
        
        router = FakeRouter([micro, large])
        surgeon = Surgeon(router)
        surgeon.micro_trade_threshold = 1000
        
        # Act
        surgeon.scan_and_repair()
        
        # Assert
        self.assertIn('micro1', router.closed)
        self.assertNotIn('big1', router.closed) 
