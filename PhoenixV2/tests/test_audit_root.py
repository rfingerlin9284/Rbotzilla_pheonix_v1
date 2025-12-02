import unittest
import tempfile
import os
import shutil
import subprocess


class AuditRootTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix='phoenix_audit_test_')
        # Create minimal allowed structure
        os.makedirs(os.path.join(self.tmpdir, 'PhoenixV2'), exist_ok=True)
        with open(os.path.join(self.tmpdir, 'README.md'), 'w') as f:
            f.write('test')
        with open(os.path.join(self.tmpdir, '.env'), 'w') as f:
            f.write('MODE=PAPER')
        os.makedirs(os.path.join(self.tmpdir, 'scripts'), exist_ok=True)
        # Copy audit script into scripts folder so it can be run from tmpdir
        shutil.copyfile('scripts/audit_root.py', os.path.join(self.tmpdir, 'scripts', 'audit_root.py'))

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_audit_clean_root(self):
        # Run audit in tmpdir - expected clean
        cwd = os.getcwd()
        try:
            os.chdir(self.tmpdir)
            res = subprocess.run(['python3', 'scripts/audit_root.py'], capture_output=True, text=True)
            self.assertEqual(res.returncode, 0)
            self.assertIn('ROOT DIRECTORY CLEAN', res.stdout)
        finally:
            os.chdir(cwd)

    def test_audit_detects_violation(self):
        # Create an unexpected file at root
        with open(os.path.join(self.tmpdir, 'rbotzilla_engine.py'), 'w') as f:
            f.write('# legacy file')
        cwd = os.getcwd()
        try:
            os.chdir(self.tmpdir)
            res = subprocess.run(['python3', 'scripts/audit_root.py'], capture_output=True, text=True)
            self.assertNotEqual(res.returncode, 0)
            self.assertIn('VIOLATIONS FOUND IN ROOT', res.stdout)
        finally:
            os.chdir(cwd)


if __name__ == '__main__':
    unittest.main()
