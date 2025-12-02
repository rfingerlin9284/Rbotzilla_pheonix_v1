from __future__ import annotations

import pkgutil
import importlib
from pathlib import Path
from typing import Dict

AVAILABLE = {}

def discover_strategies() -> Dict[str, str]:
    root = Path(__file__).resolve().parents[1] / 'research_strategies'
    for m in pkgutil.iter_modules([str(root)]):
        AVAILABLE[m.name] = f'research_strategies.{m.name}'
    return AVAILABLE

def load_strategy(module_name: str):
    if module_name not in AVAILABLE:
        discover_strategies()
    if module_name not in AVAILABLE:
        raise ImportError(f"Strategy module {module_name} not found in research_strategies")
    return importlib.import_module(AVAILABLE[module_name])

def generate_signals_for_module(module_name: str, cfg, df):
    mod = load_strategy(module_name)
    if hasattr(mod, 'Strategy'):
        strat = mod.Strategy(cfg)
        df2 = strat.compute_features(df)
        return strat.generate_signals(df2)
    raise AttributeError('Strategy class not found in module')
