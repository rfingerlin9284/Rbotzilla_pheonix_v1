#!/usr/bin/env python3
"""
Filesystem audit script to verify cleanup and isolation completed.
"""
import os
import sys
import json


def audit_root():
    print("🔍 FILESYSTEM AUDIT")
    root_files = os.listdir('.')
    allowed = {
        'PhoenixV2', '.env', 'requirements.txt', 'README.md', 'venv',
        '.git', '.gitignore', 'scripts', 'legacy_relocate',
        'sunday_launch_protocol.py', 'start_phoenix_v2.sh', 'stop_phoenix.sh', 'install_service.sh'
    }
    violations = []
    for f in root_files:
        if f not in allowed and not f.endswith('.zip'):
            violations.append(f)
    if violations:
        print(f"❌ VIOLATIONS FOUND IN ROOT: {violations}")
        return False
    print("✅ ROOT DIRECTORY CLEAN.")
    return True


def main():
    ok = audit_root()
    if not ok:
        print('Recommendation: run: python3 scripts/isolate_phoenix.py --force')
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
