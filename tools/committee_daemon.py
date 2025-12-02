#!/usr/bin/env python3
"""Headless Rick Hive Committee daemon (tools module) for terminal operation.

This is similar to hive/committee_daemon but lives in tools for improved import reliability in tests.
"""
import os
import json
import time
from pathlib import Path
from typing import Dict, Any

from hive.rick_hive_mind import get_hive_mind

LOGS_DIR = Path('logs')
BACKTEST_SUMMARY = Path('backtests/latest_summary.json')
COMMITTEE_LOG = LOGS_DIR / 'committee.jsonl'
NARRATION_LOG = LOGS_DIR / 'narration.jsonl'


def build_status_packet() -> Dict[str, Any]:
    packet: Dict[str, Any] = {}
    if BACKTEST_SUMMARY.exists():
        try:
            with BACKTEST_SUMMARY.open('r', encoding='utf-8') as f:
                packet['backtest_summary'] = json.load(f)
        except Exception:
            packet['backtest_summary'] = None
    else:
        packet['backtest_summary'] = None

    try:
        narr_file = LOGS_DIR / 'narration.jsonl'
        if narr_file.exists():
            with narr_file.open('r', encoding='utf-8') as f:
                lines = f.readlines()
                packet['latest_narration'] = json.loads(lines[-1]) if lines else None
        else:
            packet['latest_narration'] = None
    except Exception:
        packet['latest_narration'] = None

    try:
        pnl_file = LOGS_DIR / 'pnl.jsonl'
        if pnl_file.exists():
            with pnl_file.open('r', encoding='utf-8') as f:
                lines = f.readlines()
                packet['latest_pnl'] = json.loads(lines[-1]) if lines else None
        else:
            packet['latest_pnl'] = None
    except Exception:
        packet['latest_pnl'] = None

    return packet


def append_committee_log(entry: Dict[str, Any]) -> None:
    LOGS_DIR.mkdir(exist_ok=True)
    with COMMITTEE_LOG.open('a', encoding='utf-8') as f:
        f.write(json.dumps(entry) + '\n')
    with NARRATION_LOG.open('a', encoding='utf-8') as f:
        f.write(json.dumps({'event_type': 'RICK_COMMITTEE', 'details': entry}) + '\n')


def run_once(pin: int = 841921) -> Dict[str, Any]:
    hive = get_hive_mind(pin=pin)
    packet = build_status_packet()
    market_data = {'summary_present': bool(packet.get('backtest_summary'))}
    if packet.get('backtest_summary'):
        market_data['global'] = packet['backtest_summary'].get('global')
    analysis = hive.delegate_analysis(market_data)
    entry = {
        'timestamp': int(time.time()),
        'consensus': analysis.consensus_signal.value,
        'confidence': float(analysis.consensus_confidence),
        'recommendation': analysis.trade_recommendation or {},
        'agent_responses': [
            {
                'agent': r.agent.value,
                'signal': r.signal.value,
                'confidence': r.confidence,
                'reasoning': r.reasoning,
                'risk_reward': r.risk_reward,
            }
            for r in analysis.agent_responses
        ],
    }
    append_committee_log(entry)
    return entry


def main(loop: bool = True, interval: int = 60):
    print('RICK COMMITTEE DAEMON — headless — CTRL+C to stop')
    try:
        if not loop:
            e = run_once()
            print('Entry:', e)
            return
        while True:
            e = run_once()
            print('Committee:', e['consensus'], f"({e['confidence']:.2f})")
            time.sleep(interval)
    except KeyboardInterrupt:
        print('Stopping committee daemon')


if __name__ == '__main__':
    main(loop=True, interval=60)
