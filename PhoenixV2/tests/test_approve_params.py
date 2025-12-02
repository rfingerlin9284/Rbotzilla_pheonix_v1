import unittest
import tempfile
import os
import json
import subprocess


class ApproveParamsCLITest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix='phoenix_test_')
        self.config_dir = os.path.join(self.tmpdir, 'config')
        os.makedirs(self.config_dir, exist_ok=True)
        self.pending_path = os.path.join(self.config_dir, 'pending_golden_params.json')
        self.active_path = os.path.join(self.config_dir, 'golden_params.json')
        # write an active golden params
        with open(self.active_path, 'w') as f:
            json.dump({'EMAScalperWolf': {'fast': 20, 'slow': 40}}, f)
        # write a pending with low WFE
        pending = {
            'EMAScalperWolf': {
                'params': {'fast': 10, 'slow': 40},
                'metrics': {'pnl': 1.0, 'win_rate': 0.5},
                'validation': {'wfe_ratio': 0.1, 'is_stable': False}
            }
        }
        with open(self.pending_path, 'w') as f:
            json.dump(pending, f)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_abort_on_low_wfe(self):
        cmd = ['PYTHONPATH=.', 'python3', 'PhoenixV2/interface/approve_params.py', '--config-dir', self.config_dir, '-y']
        # Using shell to pass PYTHONPATH env var
        result = subprocess.run(' '.join(cmd), shell=True, capture_output=True, text=True)
        # After this, active file should be unmodified (same as set)
        with open(self.active_path, 'r') as f:
            data = json.load(f)
        self.assertEqual(data.get('EMAScalperWolf', {}).get('fast'), 20)

    def test_force_promote(self):
        cmd = ['PYTHONPATH=.', 'python3', 'PhoenixV2/interface/approve_params.py', '--config-dir', self.config_dir, '-y', '--force']
        result = subprocess.run(' '.join(cmd), shell=True, capture_output=True, text=True)
        with open(self.active_path, 'r') as f:
            data = json.load(f)
        self.assertEqual(data.get('EMAScalperWolf', {}).get('fast'), 10)


if __name__ == '__main__':
    unittest.main()
