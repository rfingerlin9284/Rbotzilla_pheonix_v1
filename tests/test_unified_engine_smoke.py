#!/usr/bin/env python3
"""Smoke test for unified_engine to ensure runner starts and stops cleanly."""
import os
import asyncio

def test_unified_engine_no_engines(monkeypatch):
    monkeypatch.setenv('USE_UNIFIED_ENGINE', '1')
    monkeypatch.setenv('ENABLE_OANDA', '0')
    monkeypatch.setenv('ENABLE_IBKR', '0')
    monkeypatch.setenv('ENABLE_AGGRESSIVE', '0')
    # A short timeout to make the runner exit if it had anything to run
    monkeypatch.setenv('UNIFIED_RUN_DURATION_SECONDS', '1')

    # Import and run unified_main - should return without raising
    from engines.unified_engine import main as unified_main
    asyncio.run(unified_main())


if __name__ == '__main__':
    import pytest
    pytest.main([__file__])
