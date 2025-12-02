#!/usr/bin/env python3
"""
CLI for approving pending golden params. Promotes pending params to golden if the operator approves.
"""
import argparse
import json
import os
from datetime import datetime


def load_json(path):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception:
        return {}


def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def print_comparison(strategy, current, pending):
    print('='*60)
    print(f"Strategy: {strategy}")
    print("Current Params:")
    print(json.dumps(current.get('params', current), indent=2))
    print("Pending Params:")
    print(json.dumps(pending.get('params', pending), indent=2))
    # Metrics differ
    curr_metrics = current.get('metrics', {})
    pending_metrics = pending.get('metrics', {})
    if curr_metrics or pending_metrics:
        print("Metrics Comparison:")
        curr_pnl = curr_metrics.get('pnl') if curr_metrics else None
        pend_pnl = pending_metrics.get('pnl') if pending_metrics else None
        # compute improvements if both present
        if curr_pnl is not None and pend_pnl is not None:
            try:
                diff = pend_pnl - curr_pnl
                pct = (diff / (abs(curr_pnl) if curr_pnl != 0 else max(abs(pend_pnl), 1))) * 100.0
            except Exception:
                diff = None
                pct = None
            print(f"  Total PnL: Current {curr_pnl} -> Pending {pend_pnl} | Diff {diff} ({pct:.1f}%)")
        else:
            print(f"  Total PnL: Current {curr_pnl} -> Pending {pend_pnl}")
        # Win rate comparison
        curr_wr = curr_metrics.get('win_rate')
        pend_wr = pending_metrics.get('win_rate')
        if curr_wr is not None and pend_wr is not None:
            try:
                wr_diff = pend_wr - curr_wr
                wr_pct = (wr_diff / (curr_wr if curr_wr != 0 else max(pend_wr, 1e-6))) * 100.0
            except Exception:
                wr_diff = None
                wr_pct = None
            print(f"  Win Rate: Current {curr_wr:.2%} -> Pending {pend_wr:.2%} | Diff {wr_diff:.2%} ({wr_pct:.1f}%)")
    # Validation info
    validation = pending.get('validation')
    if validation:
        wfe = validation.get('wfe_ratio') if validation.get('wfe_ratio') is not None else 0.0
        is_stable = validation.get('is_stable', False)
        atr = validation.get('avg_train_annualized_return') if validation.get('avg_train_annualized_return') is not None else 0.0
        aer = validation.get('avg_test_annualized_return') if validation.get('avg_test_annualized_return') is not None else 0.0
        print(f"  Walk-Forward Efficiency (WFE): {wfe:.4f} (is_stable={is_stable})")
        print(f"  Avg Train Annualized Return: {atr:.4f}")
        print(f"  Avg Test Annualized Return: {aer:.4f}")
    print('='*60)


def archive_file(path):
    if not os.path.exists(path):
        return
    ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    dirname = os.path.dirname(path)
    name = os.path.basename(path)
    backup = os.path.join(dirname, f"{name}.bak.{ts}")
    os.rename(path, backup)
    return backup


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config-dir', default='PhoenixV2/config')
    parser.add_argument('--yes', '-y', action='store_true', help='Auto accept pending promotion')
    parser.add_argument('--force', '-f', action='store_true', help='Force promotion even if validation fails')
    parser.add_argument('--dry-run', action='store_true', help='Show actions but do not write files')
    parser.add_argument('--threshold', type=float, default=0.5, help='Minimum WFE ratio to consider stable')
    parser.add_argument('--audit-message', type=str, default=None, help='Optional message to include in audit log')
    args = parser.parse_args()
    config_dir = args.config_dir
    pending_path = os.path.join(config_dir, 'pending_golden_params.json')
    active_path = os.path.join(config_dir, 'golden_params.json')
    audit_dir = os.path.join('PhoenixV2', 'logs')
    if not os.path.exists(audit_dir):
        os.makedirs(audit_dir)
    audit_path = os.path.join(audit_dir, 'audit.log')
    operator = os.environ.get('USER') or os.environ.get('USERNAME') or 'unknown'
    # Optional message
    args.audit_message = getattr(args, 'audit_message', None)

    pending = load_json(pending_path)
    current = load_json(active_path)

    if not pending:
        print('No pending optimized parameters found')
        return

    # Show comparisons for each strategy
    for strat, pval in pending.items():
        curr = current.get(strat, {})
        print_comparison(strat, curr, pval)

    # Confirm & validations
    if not args.yes:
        ans = input('Promote pending parameters to live? (y/n): ').strip().lower()
        if ans not in ('y', 'yes'):
            print('Promotion aborted by operator')
            return
    # If not forced, ensure all pending are stable
    if not args.force:
        unstable = []
        for strat, val in pending.items():
            v = val.get('validation', {})
            # If no validation, consider warn but not block
            if v:
                if v.get('wfe_ratio', 0.0) < args.threshold:
                    unstable.append((strat, v.get('wfe_ratio', 0.0)))
        if unstable:
            print('The following strategies have low Walk-Forward Efficiency (WFE) and are likely overfitted:')
            for s, w in unstable:
                print(f"  - {s}: WFE={w:.3f} (threshold={args.threshold})")
            print('Aborting promotion. Use --force to override.')
            return

    # Archive existing golden params
    backup = None
    if os.path.exists(active_path):
        backup = archive_file(active_path)

    # Promote by moving pending into active
    promote_payload = {}
    for strat, val in pending.items():
        # Prefer to store only params in active file
        if isinstance(val, dict) and 'params' in val:
            promote_payload[strat] = val['params']
        else:
            promote_payload[strat] = val

    if args.dry_run:
        print('DRY-RUN: Not writing golden_params.json; would have promoted:')
        print(json.dumps(promote_payload, indent=2))
    else:
        save_json(active_path, promote_payload)

    # Log audit
    with open(audit_path, 'a') as al:
        ts = datetime.utcnow().isoformat() + 'Z'
        al.write(f"{ts} PROMOTE: {list(promote_payload.keys())} backup={backup} operator={operator} message={args.audit_message}\n")
        for strat, val in pending.items():
            al.write(f"  {strat}: validation={val.get('validation')}\n")
    if args.dry_run:
        print('DRY-RUN: Promotion skipped; no files changed.')
    else:
        print('Promoted pending_golden_params to golden_params.json')


if __name__ == '__main__':
    main()
