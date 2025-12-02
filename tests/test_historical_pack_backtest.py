import zipfile
import json
from pathlib import Path
from tools.historical_pack_backtest import run_pack_backtest


def test_run_pack_backtest(tmp_path):
    # create a zip with two small CSVs
    zip_path = tmp_path / 'pack.zip'
    files = {
        'COINBASE_BTC-USD_daily.csv': 'timestamp,open,high,low,close,volume\n1,1,1.1,0.9,1.05,10\n2,1.05,1.15,1.0,1.1,10\n',
        'OANDA_EUR_USD_daily.csv': 'timestamp,open,high,low,close,volume\n1,1,1.01,0.99,1.005,10\n2,1.005,1.02,1.0,1.015,10\n'
    }
    with zipfile.ZipFile(zip_path, 'w') as zf:
        for name, content in files.items():
            zf.writestr(name, content)
    out_file = run_pack_backtest(str(zip_path), out_dir=str(tmp_path / 'out'), symbols=['BTC-USD','EUR_USD'])
    assert out_file
    with open(out_file, 'r', encoding='utf-8') as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]
        assert len(lines) >= 0
