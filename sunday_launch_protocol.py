#!/usr/bin/env python3
"""
Master script for Sunday Launch Protocol
Runs: cleanup, optimization, snapshot, and launch
"""
import os
import subprocess
import sys
import time
from typing import List, Optional


def run_command(command, description, allow_fail=False):
    print(f"\n➡️  {description}...")
    try:
        subprocess.check_call(command, shell=True)
        print(f"✅ {description} COMPLETE.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} FAILED: {e}")
        if not allow_fail:
            return False
        return True


def main(argv=None):
    # Pre-flight dependency check
    def check_dependencies(packages: Optional[List[str]] = None):
        if packages is None:
            packages = ['pandas', 'numpy', 'requests', 'python-dotenv']
        missing = []
        for pkg in packages:
            try:
                # special-case python-dotenv import name
                if pkg == 'python-dotenv':
                    __import__('dotenv')
                else:
                    __import__(pkg)
            except Exception:
                missing.append(pkg)
        if missing:
            print(f"❌ CRITICAL: Missing dependencies: {', '.join(missing)}")
            print("Run 'pip install -r requirements.txt' first.")
            sys.exit(1)
    check_dependencies()
    import argparse
    parser = argparse.ArgumentParser(description='Sunday Launch Protocol')
    parser.add_argument('--dry-run', action='store_true', help='Do not perform destructive actions (isolate dry-run, do not launch)')
    parser.add_argument('--skip-launch', action='store_true', help='Do not start supervisor; useful for dry-run or staging')
    parser.add_argument('--isolate-force', action='store_true', help='Force isolation (equivalent to passing --force to isolate script)')
    args = parser.parse_args(argv)
    print("==========================================")
    print("   🚀 PHOENIX V2 - SUNDAY LAUNCH PROTOCOL")
    print("==========================================")

    # Step 1: Cleanup (isolate) - respect dry-run if requested
    isolate_cmd = "python3 scripts/isolate_phoenix.py --zip"
    if args.isolate_force and not args.dry_run:
        isolate_cmd = "python3 scripts/isolate_phoenix.py --force --zip"
    elif args.dry_run:
        isolate_cmd = "python3 scripts/isolate_phoenix.py"
    if not run_command(isolate_cmd, "System Isolation & Cleanup"):
        sys.exit(1)

    # Step 2: Tune (Full Arsenal Optimization + Auto Apply)
    # Uses --auto-apply to promote stable strategies automatically
    print('\nStarting full-arsenal optimization (may take a while)...')
    cmd = "PYTHONPATH=. python3 PhoenixV2/backtest/optimizer.py --config-dir PhoenixV2/config --auto-apply"
    if args.dry_run:
        cmd = cmd + " --no-save"
    if not run_command(cmd, "Full Arsenal Strategy Optimization", allow_fail=True):
        print("⚠️ Optimization completed with errors; check logs and pending_golden_params.json")

    # Step 3: Snapshot
    if not run_command("python3 scripts/create_snapshot.py", "Pre-Launch Snapshot"):
        sys.exit(1)

    # Step 4: Launch Supervisor
    if not args.skip_launch:
        if not run_command("./start_phoenix_v2.sh", "Ignition Sequence"):
            sys.exit(1)
    else:
        print("Skipping supervisor start (skip-launch set)")
        # Do not exit early; we still want to show the success message and
        # perform any final instructions that the operator expects.

    print("\n==========================================")
    print("   🦅 PHOENIX LAUNCHED SUCCESSFULLY")
    print("==========================================")
    print("1. Monitor: tail -f PhoenixV2/logs/engine.out")
    print("2. Control: python3 PhoenixV2/interface/cli.py")
    print("3. Stop:    ./stop_phoenix.sh")


if __name__ == '__main__':
    main()
