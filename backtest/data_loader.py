from __future__ import annotations
from typing import Dict, List, Tuple
from pathlib import Path
import zipfile
import csv

from data.historical_loader import load_csv_candles


def infer_symbol_timeframe_from_filename(name: str) -> Tuple[str, str]:
    # Examples: OANDA_USD_TRY_daily.csv -> USD_TRY, D
    # COINBASE_BTC-USD_daily.csv -> BTC-USD, D
    # BTC-USD_20250101_M15.csv -> BTC-USD, M15
    base = Path(name).name
    parts = base.split('.')
    if len(parts) == 0:
        return (base, 'D')
    noext = parts[0]
    toks = noext.split('_')
    # find timeframe like 'M15','H1','daily','D'
    timeframe = 'D'
    symbol = noext
    for t in toks:
        t_up = t.upper()
        if t_up.startswith('M') and t_up[1:].isdigit():
            timeframe = t_up
            # symbol is preceding parts
            sym = '_'.join([x for x in toks if x.upper() != t_up])
            symbol = sym or noext
            break
        if t_up.startswith('H') and t_up[1:].isdigit():
            timeframe = t_up
            sym = '_'.join([x for x in toks if x.upper() != t_up])
            symbol = sym or noext
            break
        if t_up in ('DAILY', 'D'):
            timeframe = 'D'
            sym = '_'.join([x for x in toks if x.upper() not in ('DAILY', 'D')])
            symbol = sym or noext
            break
    # Normalize OANDA_ prefix or other provider prefix
    # If there is a provider prefix like OANDA/COINBASE, the symbol is likely the next token
    if '_' in symbol:
        # Try to remove common providers
        s = symbol.split('_')
        if s[0].upper() in ('OANDA', 'COINBASE', 'BROKER', 'GATEWAY') and len(s) > 1:
            symbol = '_'.join(s[1:])
    return (symbol.replace('__', '_'), timeframe)


def load_candles_from_csv_file(path: str, symbol: str | None = None, timeframe: str | None = None) -> Tuple[str, str, List[Dict[str, float]]]:
    if symbol is None or timeframe is None:
        inferred_symbol, inferred_tf = infer_symbol_timeframe_from_filename(path)
        symbol = symbol or inferred_symbol
        timeframe = timeframe or inferred_tf
    candles = load_csv_candles(path)
    return (symbol, timeframe, candles)


def load_pack_from_zip(zip_path: str, extract_dir: str | None = None) -> List[Tuple[str, str, List[Dict[str, float]]]]:
    results = []
    zp = Path(zip_path)
    if not zp.exists():
        return results
    extract_dir = extract_dir or '/tmp/historical_pack'
    with zipfile.ZipFile(zp, 'r') as zf:
        zf.extractall(extract_dir)
        for member in zf.namelist():
            if member.lower().endswith('.csv'):
                p = Path(extract_dir) / member
                sym, tf, candles = load_candles_from_csv_file(str(p))
                results.append((sym, tf, candles))
    return results
