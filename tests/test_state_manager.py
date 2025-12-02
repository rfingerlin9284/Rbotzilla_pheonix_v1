import os
import sys
import json
from pathlib import Path
import tempfile
sys.path.insert(0, os.path.abspath('.'))
from PhoenixV2.core.state_manager import StateManager


def test_state_manager_basic(tmp_path):
    state_file = tmp_path / 'phoenix_state.json'
    sm = StateManager(str(state_file))
    sm.reset_daily(10000.0)
    state = sm.get_state()
    assert state['daily_start_balance'] == 10000.0
    sm.record_trade(-100.0)
    s2 = sm.get_state()
    assert s2['current_balance'] == 9900.0
    assert 'daily_pnl_pct' in s2
    sm.inc_positions(2)
    assert sm.get_state()['open_positions_count'] == 2
    # Test daily peak PnL ratchet
    sm.reset_daily(10000.0)
    sm.update_balance(10050.0)
    s3 = sm.get_state()
    assert float(s3.get('daily_peak_pnl', 0.0)) == 50.0
    # Lower balance should not reduce peak
    sm.update_balance(10030.0)
    assert float(sm.get_state().get('daily_peak_pnl', 0.0)) == 50.0
    # New high updates peak
    sm.update_balance(10120.0)
    assert float(sm.get_state().get('daily_peak_pnl', 0.0)) == 120.0
    # profit lock level remains inactive if peak < 300
    assert sm.get_profit_lock_level() == float('-inf')
    # Now exceed $300 peak and assert lock level is 80% of peak
    sm.update_balance(10450.0)
    assert float(sm.get_state().get('daily_peak_pnl', 0.0)) == 450.0
    assert sm.get_profit_lock_level() == 450.0 * 0.8
    # Test daily floor: below threshold
    sm.reset_daily(10000.0)
    sm.update_balance(10200.0)
    assert sm.get_daily_floor() == float('-inf')
    # Exceed 300 in peak => floor should now be 300
    sm.update_balance(10400.0)
    assert sm.get_daily_floor() == 300.0


if __name__ == '__main__':
    test_state_manager_basic(Path('/tmp'))
    print('OK')
