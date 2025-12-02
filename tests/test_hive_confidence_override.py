#!/usr/bin/env python3
import os
from oanda.oanda_trading_engine import OandaTradingEngine


def test_hive_confidence_dev_mode(monkeypatch):
    monkeypatch.setenv('RICK_DEV_MODE', '1')
    monkeypatch.setenv('HIVE_TRIGGER_CONFIDENCE', '0.60')
    engine = OandaTradingEngine(environment='practice')
    assert engine.hive_trigger_confidence == 0.60


def test_hive_confidence_non_dev_enforce(monkeypatch):
    monkeypatch.setenv('RICK_DEV_MODE', '0')
    monkeypatch.setenv('HIVE_TRIGGER_CONFIDENCE', '0.60')
    # Ensure the Charter min is present and is higher than 0.60
    try:
        from foundation.rick_charter import RickCharter
        charter_min = getattr(RickCharter, 'HIVE_TRIGGER_CONFIDENCE_MIN', 0.80)
    except Exception:
        charter_min = 0.80

    engine = OandaTradingEngine(environment='practice')
    # The effective value should be no less than charter_min
    assert engine.hive_trigger_confidence >= charter_min


if __name__ == '__main__':
    test_hive_confidence_dev_mode()
    test_hive_confidence_non_dev_enforce()
    print('PASS test_hive_confidence_override')
