#!/usr/bin/env python3
"""
Daily Audit Report Generator

Runs predeployment diagnostics (if not present or outdated) and compares the latest
metrics against a baseline. Flags deviations beyond a threshold and writes a daily
report JSON and a short markdown summary.
"""
import json
import os
from pathlib import Path
import sys
from datetime import datetime, timezone
import glob
import subprocess

ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = ROOT / 'reports'
REPORTS_DIR.mkdir(exist_ok=True)
BASELINE_FILE = REPORTS_DIR / 'baseline_predeployment.json'
THRESHOLD_PCT = 0.10  # 10%


def latest_predeployment_report():
    files = sorted(glob.glob(str(REPORTS_DIR / 'predeployment_report_*.json')))
    if not files:
        return None
    return Path(files[-1])


def run_predeployment_if_needed():
    latest = latest_predeployment_report()
    if not latest:
        # Run predeployment diagnostics
        print('No predeployment report found; running diagnostics...')
        subprocess.check_call(['python3', 'scripts/predeployment_diagnostics.py'], env={**os.environ, 'PYTHONPATH': str(ROOT)})
    return latest_predeployment_report()


def load_json(path: Path):
    with open(path, 'r') as f:
        return json.load(f)


def create_baseline(report):
    data = load_json(report)
    baseline = {
        'timestamp': data['timestamp'],
        'report_file': str(report),
        'metrics': {}
    }
    for r in data['results']:
        baseline['metrics'][r['name']] = r['duration_ms']
    with open(BASELINE_FILE, 'w') as f:
        json.dump(baseline, f, indent=2)
    print('Baseline created:', BASELINE_FILE)
    return baseline


def compare_and_report(report, baseline):
    data = load_json(report)
    baseline_metrics = baseline.get('metrics', {})
    deltas = {}
    flagged = []
    for r in data['results']:
        name = r['name']
        val = r['duration_ms']
        base = baseline_metrics.get(name, None)
        if base is None:
            deltas[name] = {'base': None, 'current': val, 'pct': None}
            continue
        # Avoid divide by zero
        if base == 0:
            pct = float('inf') if val != 0 else 0.0
        else:
            pct = (val - base) / base
        deltas[name] = {'base': base, 'current': val, 'pct': round(pct, 4)}
        if abs(pct) > THRESHOLD_PCT:
            flagged.append({'name': name, 'base': base, 'current': val, 'pct': round(pct, 4)})

    daily = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'report_file': str(report),
        'baseline_file': str(BASELINE_FILE),
        'deltas': deltas,
        'flagged': flagged
    }
    out_file = REPORTS_DIR / f"daily_audit_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    with open(out_file, 'w') as f:
        json.dump(daily, f, indent=2)
    # Write md summary
    summary_md = REPORTS_DIR / f"daily_audit_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.md"
    with open(summary_md, 'w') as f:
        f.write(f"# Daily Audit Report - {daily['timestamp']}\n\n")
        f.write(f"Linked predeployment report: {daily['report_file']}\n")
        f.write(f"Baseline: {daily['baseline_file']}\n\n")
        f.write('## Flagged Checks (beyond 10%):\n')
        if not flagged:
            f.write('- No flagged checks.\n')
        else:
            for ff in flagged:
                f.write(f"- {ff['name']}: baseline {ff['base']}ms, current {ff['current']}ms, delta {ff['pct']*100:.2f}%\n")
    print('Daily audit written:', out_file, summary_md)
    return daily


def main():
    report = run_predeployment_if_needed()
    if not report:
        print('Failed to produce predeployment report. Exiting')
        sys.exit(2)
    baseline = None
    if BASELINE_FILE.exists():
        baseline = load_json(BASELINE_FILE)
    else:
        print('No baseline found. Creating baseline from latest predeployment report...')
        baseline = create_baseline(report)
        print('Baseline created; run again to compare metrics.')
        sys.exit(0)
    daily = compare_and_report(report, baseline)
    if daily['flagged']:
        print('Warning: flagged items found in daily audit. Check reports for details.')
        sys.exit(1)
    print('Daily audit OK: No flagged performance deviations')


if __name__ == '__main__':
    main()
