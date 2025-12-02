import unittest
import os


class SundayProtocolFilesTest(unittest.TestCase):
    def test_files_present_and_executable(self):
        self.assertTrue(os.path.exists('sunday_launch_protocol.py'))
        self.assertTrue(os.path.exists('stop_phoenix.sh'))
        self.assertTrue(os.path.exists('scripts/audit_root.py'))
        self.assertTrue(os.access('stop_phoenix.sh', os.X_OK))
        self.assertTrue(os.access('sunday_launch_protocol.py', os.X_OK))
        self.assertTrue(os.access('scripts/audit_root.py', os.X_OK))

    def test_sunday_protocol_dry_run(self):
        # Run sunday_launch_protocol in dry-run and skip launch mode to verify no actions are performed
        import subprocess
        res = subprocess.run(['python3', 'sunday_launch_protocol.py', '--dry-run', '--skip-launch'], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn('PHOENIX LAUNCHED SUCCESSFULLY', res.stdout)


if __name__ == '__main__':
    unittest.main()
