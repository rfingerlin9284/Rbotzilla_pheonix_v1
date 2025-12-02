import os
import json
import tempfile
from PhoenixV2.brain.strategies.high_probability_core import BaseWolf


def test_basewolf_loads_nested_params():
    # Backup original golden params
    config_path = os.path.join('PhoenixV2', 'config', 'golden_params.json')
    backup_path = config_path + '.bak_test'
    if os.path.exists(config_path):
        os.rename(config_path, backup_path)
    try:
        # Create a simple golden_params.json with a TestWolf entry
        payload = {
            'TestWolf': {
                'params': {
                    'foo': 'bar',
                    'baz': 123
                }
            }
        }
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(payload, f)

        class TestWolf(BaseWolf):
            pass

        w = TestWolf()
        assert 'foo' in w.params and w.params['foo'] == 'bar'
        assert w.params['baz'] == 123
    finally:
        # Cleanup: remove test file and restore original
        if os.path.exists(config_path):
            os.unlink(config_path)
        if os.path.exists(backup_path):
            os.rename(backup_path, config_path)
