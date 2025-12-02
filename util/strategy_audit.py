#!/usr/bin/env python3
"""
Strategy auditor - quick checks for strategy file presence and key parameters

This script inspects the repository for presence of core strategies (trap_reversal,
fib_confluence, price_action_holy_grail, liquidity_sweep, ema_scalper) and extracts
obvious constants like RSI thresholds, EMA periods, and min R:R. It also checks
charter config for min_rr and other critical values.

Use: python3 util/strategy_audit.py
"""
import os
import re
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

STRATEGIES = {
    'trap_reversal': ['trap_reversal.py'],
    'fib_confluence': ['fib_confluence.py'],
    'price_action_holy_grail': ['price_action_holy_grail.py'],
    'liquidity_sweep': ['liquidity_sweep.py', 'configs/wolfpack_config.json'],
    'ema_scalper': ['ema_scalper.py'],
}

KEY_PATTERNS = {
    'RSI_OVERSOLD': re.compile(r"RSI_OVERSOLD\s*=\s*([0-9]+)"),
    'RSI_OVERBOUGHT': re.compile(r"RSI_OVERBOUGHT\s*=\s*([0-9]+)"),
    'EMA_FAST': re.compile(r"EMA\(9\)|EMA\(12\)|EMA\(20\)|EMA\(9\)"),
    'MIN_RR': re.compile(r"MIN_RR|MIN_RISK_REWARD_RATIO|min_rr|min_rr_ratio\s*=\s*([0-9.]+)", re.IGNORECASE),
}


def scan_file_for_patterns(path: Path):
    try:
        text = path.read_text()
    except Exception:
        return {}

    found = {}
    for key, patt in KEY_PATTERNS.items():
        m = patt.search(text)
        if m:
            found[key] = m.group(1) if m.groups() else m.group(0)
    return found


def main():
    print("Strategy Audit Report")
    print("====================\n")

    # Charter/Config checks
    charter = PROJECT_ROOT / 'config' / 'charter.yaml'
    charter_min_rr = None
    if charter.exists():
        try:
            import yaml
            y = yaml.safe_load(charter.read_text())
            charter_min_rr = y.get('risk', {}).get('min_rr') if isinstance(y, dict) else None
        except Exception:
            # Fallback naive parse
            import re
            m = re.search(r"min_rr\s*:\s*([0-9.]+)", charter.read_text())
            if m:
                charter_min_rr = m.group(1)

    print(f"Charter min_rr: {charter_min_rr if charter_min_rr else 'UNKNOWN'}\n")

    report = {}
    for strat, path_patterns in STRATEGIES.items():
        report[strat] = {'found_paths': [], 'params': {}}
        for pattern in path_patterns:
            # If a direct path (like configs) is provided, test directly
            direct_path = PROJECT_ROOT / pattern
            if direct_path.exists():
                report[strat]['found_paths'].append(str(direct_path.relative_to(PROJECT_ROOT)))
                report[strat]['params'].update(scan_file_for_patterns(direct_path))
                continue

            # Otherwise search for matching filenames anywhere in repo
            for p in PROJECT_ROOT.rglob(pattern):
                report[strat]['found_paths'].append(str(p.relative_to(PROJECT_ROOT)))
                report[strat]['params'].update(scan_file_for_patterns(p))

    # Wolfpack config
    wolf_cfg = PROJECT_ROOT / 'configs' / 'wolfpack_config.json'
    wolfpack = None
    if wolf_cfg.exists():
        try:
            wolfpack = json.loads(wolf_cfg.read_text())
        except Exception:
            wolfpack = None

    for strat, data in report.items():
        print(f"Strategy: {strat}")
        print(f"  Files: {len(data['found_paths'])} found")
        for f in data['found_paths']:
            print(f"    - {f}")
        if data['params']:
            print("  Key parameters:")
            for k, v in data['params'].items():
                print(f"    {k}: {v}")
        else:
            print("  Key parameters: none found (defaults or delegated to config)")
        print()

    print("Wolfpack config present:", bool(wolfpack))
    if wolfpack and isinstance(wolfpack, dict):
        print("Wolfpack sample keys:", list(wolfpack.keys())[:10])

    print("\nAudit complete. If you want, run this from the project root to check for strategy presence and defaults.")


if __name__ == '__main__':
    main()
