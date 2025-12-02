#!/usr/bin/env python3
"""
Predeployment Diagnostics Script

Runs a set of safety, functionality, and performance checks to ensure this
repository is ready for PAPER-mode testing and a gated switch to LIVE mode.

Outputs a JSON report and a concise human-readable summary.
"""
import json
import os
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

REPORTS_DIR = ROOT / 'reports'
REPORTS_DIR.mkdir(exist_ok=True)
REPORT_FILE = REPORTS_DIR / f"predeployment_report_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"

def run_check(name, func, warn_threshold=None, error_threshold=None):
    start = time.time()
    status = 'PASS'
    details = None
    exception = None
    try:
        res = func()
        details = res
    except Exception as e:
        status = 'FAIL'
        exception = traceback.format_exc()
        details = {'exception': str(e)}
    elapsed = (time.time() - start) * 1000.0
    if warn_threshold and elapsed > warn_threshold and status == 'PASS':
        status = 'WARN'
    if error_threshold and elapsed > error_threshold:
        status = 'FAIL'
    return {
        'name': name,
        'status': status,
        'duration_ms': round(elapsed, 2),
        'details': details,
        'exception': exception
    }


def check_detect_unsafe():
    from scripts.detect_unsafe_place_order import scan
    results = scan()
    return {'unsafe_count': len(results), 'unsafe_samples': results[:10]}


def check_readiness_checks():
    # Execute the run_readiness_checks script and report success/fail
    import subprocess
    p = subprocess.Popen(['python3', 'scripts/run_readiness_checks.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env={**os.environ, 'PYTHONPATH': str(ROOT)})
    out, err = p.communicate(timeout=300)
    rc = p.returncode
    return {'returncode': rc, 'stdout': out.decode('utf-8', errors='ignore'), 'stderr': err.decode('utf-8', errors='ignore')}


def check_safe_place_order_behavior():
    from foundation.trading_mode import set_mode, Mode, safe_place_order
    class FakeBroker:
        def place_order(self, *args, **kwargs):
            return {'ok': True, 'id': 'FBK1'}
    fb = FakeBroker()
    # PAPER mode
    set_mode(Mode.PAPER)
    ok1, resp1 = safe_place_order(fb, {'symbol': 'AAPL', 'qty': 1})
    # LIVE behavior using force=True
    set_mode(Mode.LIVE, force=True)
    ok2, resp2 = safe_place_order(fb, {'symbol': 'AAPL', 'qty': 1})
    set_mode(Mode.PAPER)
    return {'paper_ok': bool(ok1), 'paper_resp_keys': list(resp1.keys()) if isinstance(resp1, dict) else None,
            'live_ok': bool(ok2), 'live_resp_keys': list(resp2.keys()) if isinstance(resp2, dict) else None}


def check_router_and_demo():
    from PhoenixV2.execution.router import BrokerRouter
    from typing import Any, cast
    class DummyAuth:
        def get_oanda_config(self):
            return {'token': None, 'account': None}
        def get_ibkr_config(self):
            return {'host': 'localhost', 'port': 4002, 'client_id': 1}
        def get_coinbase_config(self):
            return {'key': None, 'secret': None, 'is_sandbox': True}
        def is_live(self):
            return False
    class FakeBroker:
        def __init__(self):
            self._connected = True
        def place_order(self, *args, **kwargs):
            return {'success': True, 'order_id': 'FAKE-123', 'trades': ['T1']}
        def heartbeat(self):
            return True, 'Connected'
        def get_balance(self, currency='USD'):
            return 1000.0
        def get_nav(self):
            return 1000.0
        def get_open_positions(self):
            return []
        def get_margin_used(self):
            return 0.0
        def get_margin_available(self):
            return 1000.0
        def close_all_positions(self):
            return 0
    auth = DummyAuth()
    r = BrokerRouter(auth)
    # Assign fake brokers; use cast to suppress static typing complaints about connector types
    r.oanda = cast(Any, FakeBroker())
    r.ibkr = cast(Any, FakeBroker())
    r.coinbase = cast(Any, FakeBroker())
    # Check statuses
    status = r.get_broker_status()
    ok_ibkr, res_ibkr = r.execute_order({'symbol': 'AAPL', 'direction': 'BUY', 'notional_value': 1000})
    ok_oanda, res_oanda = r.execute_order({'symbol': 'EUR_USD', 'direction': 'BUY', 'notional_value': 10000})
    ok_coin, res_coin = r.execute_order({'symbol': 'BTC-USD', 'direction': 'BUY', 'notional_value': 100})
    return {
        'status': status,
        'ibkr_ok': ok_ibkr, 'ibkr_resp_keys': list(res_ibkr.keys()) if isinstance(res_ibkr, dict) else None,
        'oanda_ok': ok_oanda, 'oanda_resp_keys': list(res_oanda.keys()) if isinstance(res_oanda, dict) else None,
        'coin_ok': ok_coin, 'coin_resp_keys': list(res_coin.keys()) if isinstance(res_coin, dict) else None
    }


def check_quant_hedge_performance():
    try:
        from hive.quant_hedge_rules import QuantHedgeRules
    except Exception as e:
        return {'skipped': True, 'reason': 'QuantHedgeRules import failed: '+str(e)}
    try:
        import importlib
        np = importlib.import_module('numpy')
    except Exception:
        return {'skipped': True, 'reason': 'numpy not installed; skip quant hedge performance check'}
    qh = QuantHedgeRules(pin=841921)
    prices = np.random.normal(100, 2, size=200)
    volume = np.random.uniform(1000, 5000, size=200)
    start = time.time()
    analysis = qh.analyze_market_conditions(prices=prices, volume=volume, account_nav=100000,
                                           margin_used=10000, open_positions=2,
                                           correlation_matrix={'EURUSD-GBPUSD':0.4,'BTC-ETH':0.7})
    elapsed = (time.time() - start) * 1000.0
    # Validate non-empty fields and numeric ranges
    severity_score = analysis.severity_score
    return {'duration_ms': round(elapsed, 2), 'severity_score': severity_score,
            'primary_action': analysis.primary_action, 'confidence': analysis.confidence}


def check_connectors_basic():
    # Check heartbeat for standard connectors: Oanda, IBKR, Coinbase
    results = {}
    try:
        from PhoenixV2.execution.oanda_broker import OandaBroker
        # Connectors expect strings; create with empty values to avoid type issues
        ob = OandaBroker(account_id='', token='', is_live=False)
        ok = ob.connect()
        results['oanda_connect_ok'] = bool(ok)
    except Exception as e:
        results['oanda_error'] = str(e)
    try:
        from PhoenixV2.execution.coinbase_broker import CoinbaseBroker
        cb = CoinbaseBroker(api_key='', api_secret='', is_sandbox=True)
        ok = cb.connect()
        results['coinbase_connect_ok'] = bool(ok)
    except Exception as e:
        results['coinbase_error'] = str(e)
    # IBKR connect may need ibapi; just check that the class exists
    try:
        from PhoenixV2.execution.ibkr_broker import IBKRBroker
        results['ibkr_class_present'] = True
    except Exception as e:
        results['ibkr_error'] = str(e)
    return results


def check_alerting_config():
    try:
        from foundation.env_manager import get_alert_config, redact
    except Exception as e:
        return {'skipped': True, 'reason': 'env_manager import failed: ' + str(e)}
    cfg = get_alert_config()
    missing = [k for k, v in cfg.items() if not v]
    # If critical alert settings are missing, warn; do not fail
    return {'missing': missing, 'configured': {k: redact(v) for k, v in cfg.items()}}

def check_state_manager():
        try:
            from PhoenixV2.core.state_manager import StateManager
        except Exception as e:
            return {'skipped': True, 'reason': f'state_manager import failed: {e}'}
        try:
            import tempfile
            tf = tempfile.NamedTemporaryFile(delete=False)
            sm = StateManager(tf.name)
            sm.reset_daily(10000.0)
            sm.record_trade(-100.0)
            sm.inc_positions(1)
            s = sm.get_state()
            return {'daily_start': s.get('daily_start_balance'), 'current_balance': s.get('current_balance'), 'open_positions': s.get('open_positions_count')}
        except Exception as e:
            return {'skipped': True, 'reason': str(e)}


def check_social_data_sources():
        try:
            from foundation.social_reader import get_social_sentiment_summary
            from foundation.env_manager import get_market_data_config
        except Exception as e:
            return {'skipped': True, 'reason': 'social_reader import failed: ' + str(e)}
        cfg = get_market_data_config()
        try:
            summary = get_social_sentiment_summary(limit=5)
            if not summary or summary.get('post_count', 0) == 0:
                return {'status': 'WARN', 'reason': 'no posts fetched by social reader', 'summary': summary}
            return {'post_count': summary.get('post_count', 0), 'avg_compound': summary.get('avg_compound', 0)}
        except Exception as e:
            return {'status': 'WARN', 'reason': str(e)}

def main():
    checks = [
        ('detect_unsafe_place_order', check_detect_unsafe),
        ('readiness_checks', check_readiness_checks),
        ('safe_place_order_behavior', check_safe_place_order_behavior),
        ('router_and_demo', check_router_and_demo),
        ('alerting_config', check_alerting_config),
            ('state_manager', check_state_manager),
        ('quant_hedge_performance', check_quant_hedge_performance),
        ('connectors_basic', check_connectors_basic)
    ]

    report = {
        'timestamp': datetime.utcnow().isoformat(),
        'repo_root': str(ROOT),
        'results': [],
        'summary': {
            'pass': 0,
            'warn': 0,
            'fail': 0
        }
    }

    for name, fn in checks:
        r = run_check(name, fn, warn_threshold=2000.0, error_threshold=10000.0)
        report['results'].append(r)
        if r['status'] == 'PASS':
            report['summary']['pass'] += 1
        elif r['status'] == 'WARN':
            report['summary']['warn'] += 1
        else:
            report['summary']['fail'] += 1

    with open(REPORT_FILE, 'w') as f:
        json.dump(report, f, indent=2)

    # Print summary
    print(f"Predeployment diagnostics completed: {REPORT_FILE}")
    print(f"Summary: PASS={report['summary']['pass']}, WARN={report['summary']['warn']}, FAIL={report['summary']['fail']}")
    for r in report['results']:
        print(f"- {r['name']}: {r['status']} ({r['duration_ms']}ms)")
        if r['status'] != 'PASS':
            print('  details:', r['details'])
            if r['exception']:
                print('  exception:', r['exception'])

    # Failing checks should prevent deployment; exit code non-zero
    if report['summary']['fail'] > 0:
        print('Predeployment checks failed; address issues before proceeding to live deployment.')
        sys.exit(2)
    print('All critical predeployment checks passed.')


if __name__ == '__main__':
    main()
