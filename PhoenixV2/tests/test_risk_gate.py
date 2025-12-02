import unittest
from PhoenixV2.gate.risk_gate import RiskGate
from PhoenixV2.core.auth import AuthManager


class RiskGateTest(unittest.TestCase):
    def test_rejects_notional_exceeding_risk_limit(self):
        auth = AuthManager()
        gate = RiskGate(auth)
        # Setup portfolio with nav 10000
        p_state = {'total_nav': 10000}
        # Entry 100, sl 95 -> risk_pct 0.05 -> allowed_notional = 10000*0.02/0.05 = 4000
        signal = {'symbol': 'EUR_USD', 'direction': 'BUY', 'notional_value': 10000, 'entry': 100.0, 'sl': 95.0, 'timeframe': 'M15', 'sl': 95.0, 'tp': 160.0}
        is_valid, reason = gate.validate_signal(signal, current_positions=None, portfolio_state=p_state)
        self.assertFalse(is_valid)
        self.assertEqual(reason, 'NOTIONAL_EXCEEDS_RISK_LIMIT')

    def test_profit_lock_blocks_when_pnl_below_lock(self):
        auth = AuthManager()
        gate = RiskGate(auth)
        # Simulate a strong winning day that peaked at $450
        p_state = {
            'daily_start_balance': 10000.0,
            'current_balance': 10350.0,  # current pnl = 350
            'daily_peak_pnl': 450.0,
            'profit_lock_level': 450.0 * 0.8
        }
        ok, reason = gate.check_portfolio_state(p_state)
        self.assertFalse(ok)
        self.assertIn('DAILY_PROFIT_PROTECTION_TRIGGERED', reason)

    def test_profit_lock_blocks_on_equal_lock(self):
        auth = AuthManager()
        gate = RiskGate(auth)
        p_state = {
            'daily_start_balance': 10000.0,
            'current_balance': 10360.0,  # current pnl = 360 (equal to lock)
            'daily_peak_pnl': 450.0,
            'profit_lock_level': 450.0 * 0.8
        }
        ok, reason = gate.check_portfolio_state(p_state)
        self.assertFalse(ok)
        self.assertIn('DAILY_PROFIT_PROTECTION_TRIGGERED', reason)

    def test_daily_floor_blocks_when_equal(self):
        auth = AuthManager()
        gate = RiskGate(auth)
        p_state = {
            'daily_start_balance': 10000.0,
            'current_balance': 10300.0,  # current pnl = 300 (equal to daily floor)
            'daily_peak_pnl': 450.0,
            'daily_floor': 300.0
        }
        ok, reason = gate.check_portfolio_state(p_state)
        self.assertFalse(ok)
        self.assertIn('DAILY_PROFIT_FLOOR_TRIGGERED', reason)

    def test_profit_lock_allows_when_pnl_above_lock(self):
        auth = AuthManager()
        gate = RiskGate(auth)
        p_state = {
            'daily_start_balance': 10000.0,
            'current_balance': 10450.0,  # current pnl = 450
            'daily_peak_pnl': 450.0,
            'profit_lock_level': 450.0 * 0.8
        }
        ok, reason = gate.check_portfolio_state(p_state)
        self.assertTrue(ok)

if __name__ == '__main__':
    unittest.main()
