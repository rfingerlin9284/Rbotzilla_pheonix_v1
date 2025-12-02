import unittest
import re
from pathlib import Path


class NoLegacyImportsTest(unittest.TestCase):
    def test_no_foundation_imports_in_phoenixv2(self):
        root = Path(__file__).resolve().parents[1]
        files = list(root.rglob('*.py'))
        forbidden = re.compile(r"(^|\s)from\s+foundation\.|(^|\s)import\s+foundation\.")
        violations = []
        for f in files:
            if 'PhoenixV2' not in str(f):
                continue
            txt = f.read_text()
            if forbidden.search(txt):
                violations.append(str(f))
        self.assertEqual(violations, [], f"Legacy foundation imports found: {violations}")

if __name__ == '__main__':
    unittest.main()
