import json
from pathlib import Path
from backtest.analyzer import summarize_backtests


def test_summarize_backtests(tmp_path):
    raw = tmp_path / 'raw_results.jsonl'
    entries = [
        {'symbol': 'BTC-USD', 'strategy_code': 'CRYPTO_BREAK', 'net_pnl': 0.5},
        {'symbol': 'BTC-USD', 'strategy_code': 'CRYPTO_BREAK', 'net_pnl': -0.1},
        {'symbol': 'EUR_USD', 'strategy_code': 'INST_SD', 'net_pnl': 0.2},
    ]
    with raw.open('w', encoding='utf-8') as f:
        for e in entries:
            f.write(json.dumps(e) + '\n')
    out = tmp_path / 'summary.json'
    s = summarize_backtests(str(raw), out_summary_path=str(out))
    assert 'global' in s and 'by_strategy_symbol' in s
    assert (out.exists())
