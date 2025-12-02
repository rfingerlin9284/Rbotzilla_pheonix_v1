import os
from pathlib import Path
from risk.session_breaker import SessionBreakerEngine


def test_bot_max_trades_global():
    os.environ['BOT_MAX_TRADES'] = '2'
    # Ensure no stale lock exists
    lock_path = Path('.') / '.session_breaker.lock'
    try:
        if lock_path.exists():
            lock_path.unlink()
    except Exception:
        pass
    breaker = SessionBreakerEngine()
    # 1 trade - should continue
    assert breaker.check_breaker(current_pnl=10.0, account_balance=10000.0, trade_stats={'total_trades':1})
    # 2 trades - should trigger and halt
    assert breaker.check_breaker(current_pnl=5.0, account_balance=10000.0, trade_stats={'total_trades':2}) is False
    # teardown
    breaker.reset_session()
    del os.environ['BOT_MAX_TRADES']


def test_bot_max_trades_venues():
    os.environ['BOT_MAX_TRADES_OANDA'] = '1'
    os.environ['BOT_MAX_TRADES_IBKR'] = '1'
    # Ensure no stale lock exists
    lock_path = Path('.') / '.session_breaker.lock'
    try:
        if lock_path.exists():
            lock_path.unlink()
    except Exception:
        pass
    breaker = SessionBreakerEngine()
    # No per-venue counts: continue
    assert breaker.check_breaker(current_pnl=0.0, account_balance=10000.0, trade_stats={'total_trades':0})
    # OANDA count 1 should trigger - because >= limit
    assert breaker.check_breaker(current_pnl=0.0, account_balance=10000.0, trade_stats={'total_trades':1,'by_venue':{'OANDA':1}}) is False
    # IBKR count 1 should trigger - because >= limit
    assert breaker.check_breaker(current_pnl=0.0, account_balance=10000.0, trade_stats={'total_trades':1,'by_venue':{'IBKR':1}}) is False
    # teardown
    breaker.reset_session()
    del os.environ['BOT_MAX_TRADES_OANDA']
    del os.environ['BOT_MAX_TRADES_IBKR']
