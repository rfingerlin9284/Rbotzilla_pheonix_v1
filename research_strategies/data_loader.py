import os
import zipfile
from typing import Dict, List, Optional

try:
    import pandas as pd
except Exception:
    pd = None  # tests may stub pandas


def _read_csv(path: str):
    if pd is None:
        raise RuntimeError('pandas is required to load CSV historical data')
    return pd.read_csv(path)


def list_symbols_in_root(root: str) -> Dict[str, List[str]]:
    """List available symbols by asset class in a data root (folder or zip). Returns mapping asset_class -> list of symbols"""
    symbols = {'OANDA': [], 'COINBASE': [], 'IBKR': []}
    if os.path.isdir(root):
        for asset in symbols.keys():
            sub = os.path.join(root, asset.lower())
            if os.path.isdir(sub):
                for f in os.listdir(sub):
                    if f.lower().endswith('.csv'):
                        symbols[asset].append(os.path.splitext(f)[0])
    elif zipfile.is_zipfile(root):
        with zipfile.ZipFile(root, 'r') as z:
            for name in z.namelist():
                parts = name.split('/')
                if len(parts) >= 2:
                    asset = parts[0].upper()
                    if asset in symbols and parts[-1].lower().endswith('.csv'):
                        symbols[asset].append(os.path.splitext(parts[-1])[0])
    return symbols


def load_symbol_df(root: str, asset: str, symbol: str, timeframe: Optional[str] = None):
    """Loads a CSV for a given asset/symbol. Supports directories and zip file roots.

    CSV columns expected: time, open, high, low, close, volume
    """
    if pd is None:
        raise RuntimeError('pandas not installed; cannot load historical data')

    asset_dir = asset.lower()
    # look for CSV
    if os.path.isdir(root):
        # if timeframe is given, prefer symbol_timeframe.csv
        if timeframe:
            path = os.path.join(root, asset_dir, f'{symbol}_{timeframe}.csv')
            if not os.path.exists(path):
                path = os.path.join(root, asset_dir, f'{symbol}.csv')
        else:
            path = os.path.join(root, asset_dir, f'{symbol}.csv')
        if not os.path.exists(path):
            raise FileNotFoundError(f'CSV {symbol}.csv not found under {root}/{asset_dir}')
        df = pd.read_csv(path)
    elif zipfile.is_zipfile(root):
        with zipfile.ZipFile(root, 'r') as z:
            candidate = f'{asset_dir}/{symbol}.csv'
            if candidate not in z.namelist():
                raise FileNotFoundError(f'{candidate} not in zip archive')
            import io
            with z.open(candidate) as fh:
                df = pd.read_csv(io.TextIOWrapper(fh))
    else:
        raise FileNotFoundError(f'{root} is not a directory or zip')

    # minimal cleansing
    df = df.rename(columns={c: c.lower() for c in df.columns})
    if 'time' not in df.columns and 'timestamp' in df.columns:
        df['time'] = df['timestamp']
    return df


def load_for_assets(root: str, asset_class: str, symbols: Optional[List[str]] = None):
    """Load multiple symbol data frames for asset_class from root. Returns dict symbol->df"""
    found = list_symbols_in_root(root).get(asset_class.upper(), [])
    if not found:
        return {}
    to_load = symbols or found
    dfs = {}
    for s in to_load:
        try:
            dfs[s] = load_symbol_df(root, asset_class, s)
        except Exception:
            continue
    return dfs
