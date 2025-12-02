#!/usr/bin/env python3
from __future__ import annotations
from datetime import datetime, time, timedelta, timezone
from typing import Optional
import json
from pathlib import Path


def _load_config():
    cfg_path = Path('config/market_sessions.json')
    if not cfg_path.exists():
        # default best-effort sessions
        return {
            "OANDA": {"name": "Forex", "default_open_day": "SUN", "default_open_time_utc": "16:00", "default_close_day": "FRI", "default_close_time_utc": "17:00", "timezone": "UTC"},
            "IBKR": {"name": "Futures", "default_open_day": "MON", "default_open_time_utc": "00:00", "default_close_day": "FRI", "default_close_time_utc": "23:59", "timezone": "UTC"},
            "COINBASE": {"name": "Crypto", "always_open": True, "timezone": "UTC"}
        }
    return json.loads(cfg_path.read_text())


_MARKET_CFG = _load_config()


def _day_str_to_int(day: str) -> int:
    m = {
        'MON': 0, 'TUE': 1, 'WED': 2, 'THU': 3, 'FRI': 4, 'SAT': 5, 'SUN': 6
    }
    return m.get(day.upper(), 0)


def _parse_time(tstr: str) -> time:
    parts = [int(x) for x in tstr.split(':')]
    return time(parts[0], parts[1])


def is_market_open(asset: str, dt: Optional[datetime] = None) -> bool:
    """Return True if asset's market is open at datetime dt (UTC by default)."""
    if asset is None:
        return True
    asset = asset.upper()
    if dt is None:
        dt = datetime.utcnow()
    elif dt.tzinfo is not None:
        # normalize to UTC naive datetime
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    cfg_obj = _load_config()
    cfg = cfg_obj.get(asset) or cfg_obj.get(asset.upper())
    if not cfg:
        # try reload config if it was created after import
        fresh = _load_config()
        if fresh:
            global _MARKET_CFG
            _MARKET_CFG = fresh
            cfg = _MARKET_CFG.get(asset) or _MARKET_CFG.get(asset.upper())
    if not cfg:
        # unknown: default to True
        return True
    if cfg.get('always_open'):
        return True
    try:
        open_day = _day_str_to_int(cfg.get('default_open_day', 'MON'))
        close_day = _day_str_to_int(cfg.get('default_close_day', 'FRI'))
        open_time = _parse_time(cfg.get('default_open_time_utc', '00:00'))
        close_time = _parse_time(cfg.get('default_close_time_utc', '23:59'))
        # check this week and previous week in case of windows crossing week boundary
        for week_offset_days in (0, -7):
            # week starting at Monday (0)
            start_of_week = (dt - timedelta(days=dt.weekday())) + timedelta(days=week_offset_days)
            open_date = start_of_week + timedelta(days=(open_day))
            open_dt = datetime(open_date.year, open_date.month, open_date.day, open_time.hour, open_time.minute)
            close_date = start_of_week + timedelta(days=(close_day))
            close_dt = datetime(close_date.year, close_date.month, close_date.day, close_time.hour, close_time.minute)
            if close_dt < open_dt:
                close_dt += timedelta(days=7)
            if open_dt <= dt <= close_dt:
                return True
        return False
    except Exception:
        return True


def is_strategy_allowed_now(strategy_name: str, dt: Optional[datetime] = None) -> bool:
    """Return True if the strategy is allowed to run given time windows in config. Default True."""
    # For now, strategies may specify trading windows in 'config/strategy_trading_windows.json'
    st_path = Path('config/strategy_trading_windows.json')
    if not st_path.exists():
        return True
    try:
        cfg = json.loads(st_path.read_text())
    except Exception:
        return True
    if dt is None:
        dt = datetime.utcnow()
    windows = cfg.get(strategy_name)
    if not windows:
        return True
    # list of windows; each window has day(s) and start/end times (UTC)
    dow = dt.weekday()
    for win in windows:
        days = win.get('days') or ['MON', 'TUE', 'WED', 'THU', 'FRI']
        days_ints = [_day_str_to_int(d) for d in days]
        if dow not in days_ints:
            continue
        start = _parse_time(win.get('start'))
        end = _parse_time(win.get('end'))
        tnow = dt.time()
        if start <= tnow <= end:
            return True
    return False
