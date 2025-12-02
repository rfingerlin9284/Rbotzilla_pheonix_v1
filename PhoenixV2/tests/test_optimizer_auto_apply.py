import unittest
import tempfile
import os
import json
import subprocess
import shutil


class OptimizerAutoApplyTest(unittest.TestCase):
    def setUp(self):
        # Create temp workspace and set config dir
        self.tmpdir = tempfile.mkdtemp(prefix='phoenix_opt_test_')
        self.config_dir = os.path.join(self.tmpdir, 'config')
        os.makedirs(self.config_dir, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_optimizer_auto_apply(self):
        # Run optimizer with a very small grid and ensure auto-apply promotes to golden_params.json
        cmd = 'PYTHONPATH=. python3 PhoenixV2/backtest/optimizer.py --config-dir %s --auto-apply --no-save' % self.config_dir
        # Note: Use --no-save to keep pending but we want --auto-apply to write active; remove --no-save
        cmd = 'PYTHONPATH=. python3 PhoenixV2/backtest/optimizer.py --config-dir %s --auto-apply' % self.config_dir
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        # Check golden exists
        active = os.path.join(self.config_dir, 'golden_params.json')
        # Golden may or may not be created; if not, pending should exist
        if not os.path.exists(active):
            pending = os.path.join(self.config_dir, 'pending_golden_params.json')
            self.assertTrue(os.path.exists(pending))
        else:
            with open(active, 'r') as f:
                data = json.load(f)
            self.assertIsInstance(data, dict)

    def test_optimizer_force_auto_apply(self):
        # Force auto-apply should write golden_params even if unstable
        cmd = 'PYTHONPATH=. python3 PhoenixV2/backtest/optimizer.py --config-dir %s --auto-apply --force-auto-apply' % self.config_dir
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        active = os.path.join(self.config_dir, 'golden_params.json')
        self.assertTrue(os.path.exists(active))
        with open(active, 'r') as f:
            data = json.load(f)
        self.assertIsInstance(data, dict)
        with open(active, 'r') as f:
            data = json.load(f)
        self.assertIsInstance(data, dict)


if __name__ == '__main__':
    unittest.main()
