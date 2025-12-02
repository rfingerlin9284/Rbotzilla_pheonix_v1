#!/usr/bin/env python3
"""
Check engine & hive status from narration.jsonl
Provides a quick status summary useful for CI, crons, or local checks.
"""
import argparse
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Dict

from util.narration_logger import NARRATION_FILE


def load_events(narration_file: Path) -> List[Dict]:
    if not narration_file.exists():
        return []

    events = []
    with open(narration_file, 'r') as f:
        for line in f:
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return events


def parse_iso(ts: str) -> datetime:
    # Use fromisoformat which supports ISO timestamps with timezone
    try:
        return datetime.fromisoformat(ts)
    except Exception:
        # Fallback: attempt to parse Z-terminated
        if ts.endswith('Z'):
            ts = ts[:-1] + '+00:00'
        return datetime.fromisoformat(ts)


def last_event(events: List[Dict], event_type: str):
    filtered = [e for e in events if e.get('event_type') == event_type]
    if not filtered:
        return None
    # Return the last one by timestamp
    filtered_sorted = sorted(filtered, key=lambda e: e.get('timestamp', ''))
    return filtered_sorted[-1]


def count_recent(events: List[Dict], event_type: str, cutoff: datetime) -> int:
    return sum(
        1
        for e in events
        if e.get('event_type') == event_type and e.get('timestamp') and parse_iso(e['timestamp']) >= cutoff
    )


def main():
    parser = argparse.ArgumentParser(description="Check service status from narration file")
    parser.add_argument('--narration-file', default=str(NARRATION_FILE), help='Path to narration.jsonl')
    parser.add_argument('--last-minutes', type=int, default=30, help='Window in minutes to look for recent events')
    parser.add_argument('--min-trades', type=int, default=1, help='Minimum number of trades (open/exec) in the winning window')
    parser.add_argument('--json', action='store_true', help='Output machine-readable JSON summary')
    parser.add_argument('--quiet', action='store_true', help='Only return exit code (0=healthy, >0=problem)')

    args = parser.parse_args()
    events = load_events(Path(args.narration_file))
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(minutes=args.last_minutes)

    # Engine started
    engine_start_event = last_event(events, 'ENGINE_START')
    engine_started_at = parse_iso(engine_start_event['timestamp']) if engine_start_event else None

    # Heartbeats
    machine_hb = last_event(events, 'MACHINE_HEARTBEAT')
    cycle_hb = last_event(events, 'CYCLE_HEARTBEAT')
    last_machine_ts = parse_iso(machine_hb['timestamp']) if machine_hb else None
    last_cycle_ts = parse_iso(cycle_hb['timestamp']) if cycle_hb else None

    # Trades
    recent_opened = count_recent(events, 'TRADE_OPENED', cutoff)
    recent_executed = count_recent(events, 'TRADE_EXECUTED', cutoff)
    last_trade_opened = last_event(events, 'TRADE_OPENED')
    last_trade_executed = last_event(events, 'TRADE_EXECUTED')

    last_trade_opened_ts = parse_iso(last_trade_opened['timestamp']) if last_trade_opened else None
    last_trade_exec_ts = parse_iso(last_trade_executed['timestamp']) if last_trade_executed else None

    # Heuristics for healthy status
    engine_ok = engine_started_at is not None and engine_started_at <= now
    machine_ok = last_machine_ts is not None and (now - last_machine_ts) <= timedelta(minutes=max(args.last_minutes, 10))
    cycle_ok = last_cycle_ts is not None and (now - last_cycle_ts) <= timedelta(minutes=max(args.last_minutes, 5))
    trades_ok = (recent_opened + recent_executed) >= args.min_trades

    healthy = engine_ok and machine_ok and cycle_ok and trades_ok

    summary = {
        'now': now.isoformat(),
        'engine_started_at': engine_started_at.isoformat() if engine_started_at else None,
        'last_machine_heartbeat': last_machine_ts.isoformat() if last_machine_ts else None,
        'last_cycle_heartbeat': last_cycle_ts.isoformat() if last_cycle_ts else None,
        'recent_trade_opened_count': recent_opened,
        'recent_trade_executed_count': recent_executed,
        'last_trade_opened_at': last_trade_opened_ts.isoformat() if last_trade_opened_ts else None,
        'last_trade_executed_at': last_trade_exec_ts.isoformat() if last_trade_exec_ts else None,
        'healthy': healthy
    }

    if args.json:
        print(json.dumps(summary, indent=2))
    elif not args.quiet:
        print('Engine status check:')
        print('  Engine started at: ', summary['engine_started_at'])
        print('  Last machine heartbeat:', summary['last_machine_heartbeat'])
        print('  Last cycle heartbeat:', summary['last_cycle_heartbeat'])
        print('  Recent TRADE_OPENED count:', summary['recent_trade_opened_count'])
        print('  Recent TRADE_EXECUTED count:', summary['recent_trade_executed_count'])
        print('  Last TRADE_OPENED at:', summary['last_trade_opened_at'])
        print('  Last TRADE_EXECUTED at:', summary['last_trade_executed_at'])
        print('  Healthy:', 'YES' if healthy else 'NO')

    # Exit with 0 if healthy, else 1
    if healthy:
        return 0
    else:
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
