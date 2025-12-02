from util.market_scheduler import is_market_open, is_strategy_allowed_now
import json
from pathlib import Path
from datetime import datetime, timezone


def test_market_open_oanda():
    # Monday noon UTC -> should be open
    dt = datetime(2025, 11, 24, 12, 0, tzinfo=timezone.utc)
    assert is_market_open('OANDA', dt)


def test_market_closed_sunday_before_open():
    # Sunday at 10:00 UTC (before Sunday 17:00 opening) -> closed
    dt = datetime(2025, 11, 23, 10, 0, tzinfo=timezone.utc)
    assert not is_market_open('OANDA', dt)


def test_market_open_sunday_after_open():
    # Sunday at 17:30 UTC -> open
    dt = datetime(2025, 11, 23, 17, 30, tzinfo=timezone.utc)
    assert is_market_open('OANDA', dt)


def test_crypto_always_open():
    dt = datetime(2025, 11, 23, 2, 0, tzinfo=timezone.utc)
    assert is_market_open('COINBASE', dt)


def test_strategy_windows(monkeypatch):
    # ema_scalper windows include 08:00-17:00
    # Ensure config exists for tests by monkeypatching Path.read_text for the strategy file
    orig_read_text = Path.read_text
    orig_exists = Path.exists
    def fake_read_text(self, *args, **kwargs):
        if self.name == 'strategy_trading_windows.json':
            return json.dumps({
                "ema_scalper": [
                    {"days": ["MON", "TUE", "WED", "THU", "FRI"], "start": "08:00", "end": "17:00"}
                ]
            })
        return orig_read_text(self, *args, **kwargs)
    monkeypatch.setattr(Path, 'read_text', fake_read_text)
    def fake_exists(self):
        if self.name == 'strategy_trading_windows.json':
            return True
        return orig_exists(self)
    monkeypatch.setattr(Path, 'exists', fake_exists)
    dt_in = datetime(2025, 11, 24, 10, 0, tzinfo=timezone.utc)
    assert is_strategy_allowed_now('ema_scalper', dt_in)
    dt_out = datetime(2025, 11, 24, 23, 0, tzinfo=timezone.utc)
    assert not is_strategy_allowed_now('ema_scalper', dt_out)
