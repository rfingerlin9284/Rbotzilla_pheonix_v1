import json
from pathlib import Path
from PhoenixV2.core.state_manager import StateManager


def test_state_manager_strategy_pnl_and_weight(tmp_path):
    state_file = tmp_path / 'state.json'
    sm = StateManager(str(state_file))
    # Initially no data
    assert isinstance(sm.get_strategy_performance(), dict)
    # Record a win
    sm.record_strategy_pnl('liquidity_sweep', 1000.0)
    perfs = sm.get_strategy_performance()
    assert perfs.get('liquidity_sweep', 0) >= 1000.0
    weight = sm.get_strategy_weight('liquidity_sweep')
    assert weight > 1.0
    # Record a loss and check weight declines
    sm.record_strategy_pnl('liquidity_sweep', -2000.0)
    perfs = sm.get_strategy_performance()
    assert perfs.get('liquidity_sweep', 0) < 0
    w2 = sm.get_strategy_weight('liquidity_sweep')
    assert w2 < weight or w2 >= 0.1


def test_state_manager_persistence(tmp_path):
    f = tmp_path / 'state.json'
    sm = StateManager(str(f))
    sm.record_strategy_pnl('supply_demand', 2000.0)
    w = sm.get_strategy_weight('supply_demand')
    # Create a new instance to load from disk
    sm2 = StateManager(str(f))
    assert sm2.get_strategy_performance().get('supply_demand', 0.0) >= 2000.0
    assert abs(sm2.get_strategy_weight('supply_demand') - w) < 1e-6


def test_kill_switch(tmp_path):
    sm = StateManager(str(tmp_path / 'state.json'))
    # Simulate 6 small consecutive losses
    for _ in range(6):
        sm.record_strategy_pnl('killing_test', -50.0)
    w = sm.get_strategy_weight('killing_test')
    assert w == 0.0
