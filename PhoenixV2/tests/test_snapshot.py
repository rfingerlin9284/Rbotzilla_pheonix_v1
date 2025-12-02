import unittest
import tempfile
import os
import zipfile
from scripts.create_snapshot import create_snapshot


class SnapshotTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='phoenix_snap_test_')
        # copy minimal structure
        os.makedirs(os.path.join(self.tmp, 'PhoenixV2', 'logs'), exist_ok=True)
        with open(os.path.join(self.tmp, 'PhoenixV2', 'README.md'), 'w') as f:
            f.write('test')
        with open(os.path.join(self.tmp, '.env'), 'w') as f:
            f.write('MODE=PAPER')

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_snapshot_created(self):
        snap = create_snapshot(self.tmp)
        self.assertTrue(os.path.exists(snap))
        with zipfile.ZipFile(snap, 'r') as zf:
            names = zf.namelist()
            # Should include PhoenixV2/README.md and .env
            self.assertTrue(any('PhoenixV2/README.md' in n for n in names))
            self.assertTrue(any('.env' in n for n in names))


if __name__ == '__main__':
    unittest.main()
