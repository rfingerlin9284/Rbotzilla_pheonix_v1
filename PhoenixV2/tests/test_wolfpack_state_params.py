import logging
import os
import json
from PhoenixV2.core.state_manager import StateManager
from PhoenixV2.brain.wolf_pack import WolfPack


def test_wolfpack_applies_state_params(tmp_path, caplog):
    # Setup StateManager with a test file and add a strategy params mapping
    sm_path = os.path.join(str(tmp_path), 'state.json')
    sm = StateManager(sm_path)
    # Ensure the learning file exists and set strategy params
    sm.set_strategy_params('ema_scalper', {'params': {'fast': 12, 'slow': 24}})
    caplog.set_level(logging.INFO)
    wp = WolfPack(state_manager=sm)
    # Verify log indicates it applied params from StateManager
    found = False
    for rec in caplog.records:
        if 'WolfPack: Applied strategy params from StateManager' in rec.getMessage():
            found = True
            break
    assert found, 'WolfPack did not log applying strategy params from StateManager'
