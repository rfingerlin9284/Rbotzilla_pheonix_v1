from engine.execution_router import ExecutionRouter
import os


def test_choose_venue_futures_and_options_and_equity():
    r = ExecutionRouter()
    assert r.choose_venue_for_instrument("ES", "FUTURES") == "IBKR"
    assert r.choose_venue_for_instrument("AAPL", "EQUITY") == "IBKR"
    assert r.choose_venue_for_instrument("BTC_OPTIONS", "OPTIONS") == "IBKR"


def test_choose_venue_crypto_and_fx():
    r = ExecutionRouter()
    assert r.choose_venue_for_instrument("BTC-USD", "CRYPTO_SPOT") == "COINBASE"
    assert r.choose_venue_for_instrument("BTC-PERP", "CRYPTO_PERP") == "COINBASE"
    # FX -> OANDA when present; otherwise IBKR fallback
    venue_for_fx = r.choose_venue_for_instrument("EUR_USD", "FX")
    assert venue_for_fx in ("OANDA", "IBKR")


def test_place_order_dry_run():
    r = ExecutionRouter()
    res = r.place_order("BTC-USD", "CRYPTO_SPOT", dry_run=True)
    assert res.get("success") is True
    assert res.get("order_id", "").startswith("DRY-")
