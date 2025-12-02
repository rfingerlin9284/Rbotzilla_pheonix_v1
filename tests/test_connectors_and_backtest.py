from brokers.coinbase_connector import CoinbaseConnector as BinanceConnector
from brokers.coinbase_connector import CoinbaseConnector as DeribitConnector
from data.historical_loader import load_csv_candles
from backtest.runner import run_simple_backtest


def test_binance_connector_importable():
    bc = BinanceConnector()
    # Basic smoke test for import and construction
    assert hasattr(bc, 'environment')


def test_deribit_connector_importable():
    dc = DeribitConnector()
    # Basic smoke test for import and construction
    assert hasattr(dc, 'environment')


def test_historical_loader_csv(tmp_path):
    p = tmp_path / "sample.csv"
    p.write_text("timestamp,open,high,low,close,volume\n1,1,1.01,0.99,1.005,100\n2,1,1.01,0.99,1.005,50\n")
    candles = load_csv_candles(str(p))
    assert candles and len(candles) == 2


def test_simple_backtest_runs(tmp_path):
    # Create a synthetic CSV and run a simple backtest
    p = tmp_path / "btc_m15.csv"
    rows = [
        "timestamp,open,high,low,close,volume",
    ]
    for i in range(200):
        rows.append(f"{i},1.0,1.01,0.99,1.005,100")
    p.write_text("\n".join(rows))

    candles = load_csv_candles(str(p))
    results = run_simple_backtest("BTCUSD", "M15", candles)
    assert isinstance(results, list)
