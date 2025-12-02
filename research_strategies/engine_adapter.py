from __future__ import annotations
import pandas as pd
from .router import discover_strategies
from util.instrument_router import get_broker_for_symbol
from .pack_manager import run_pack_for_df
from .regime_features import detect_regime

def load_research_packs_config():
    discover_strategies()
    # Return PACKS mapping for engine usage
    from .pack_manager import PACKS
    return PACKS

def get_signals_for_symbol(symbol: str, ohlcv_df: pd.DataFrame):
    # returns the consolidated signals DataFrame from research pack manager
    df = run_pack_for_df(ohlcv_df, symbol)
    try:
        broker = get_broker_for_symbol(symbol)
        # If DataFrame, add broker column
        if isinstance(df, pd.DataFrame) and not df.empty:
            df = df.copy()
            df['broker'] = broker
    except Exception:
        pass
    return df

def get_regime_for_df(ohlcv_df: pd.DataFrame):
    return detect_regime(ohlcv_df)
