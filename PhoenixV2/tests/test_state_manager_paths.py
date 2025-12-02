import unittest
import shutil
import os
from pathlib import Path
from PhoenixV2.core.state_manager import StateManager


class TestStateManagerPaths(unittest.TestCase):
    def test_directories_created(self):
        base = '/tmp/test_phoenix_state'
        # cleanup
        try:
            shutil.rmtree(base)
        except Exception:
            pass
        state_path = os.path.join(base, 'core', 'phoenix_state.json')
        sm = StateManager(state_path)
        # Should have created directories
        self.assertTrue(Path(base).exists())
        # Save should create file
        sm.set_daily_start_balance(1000)
        self.assertTrue(Path(state_path).exists())
        # cleanup
        try:
            shutil.rmtree(base)
        except Exception:
            pass


if __name__ == '__main__':
    unittest.main()
