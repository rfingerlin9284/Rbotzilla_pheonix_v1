"""
Research strategies package - minimal scaffolding for smoke tests and pack manager
"""
from . import strategy_base, indicators, pack_manager, backtest_engine, ml_models, data_loader, demo_backtest
from . import ema_scalper, breakout_volume_expansion

__all__ = [
    'strategy_base', 'indicators', 'pack_manager', 'backtest_engine', 'ml_models', 'data_loader', 'demo_backtest',
    'ema_scalper', 'breakout_volume_expansion'
]

# Convenience exports
from .backtest_engine import run_backtest
from .pack_backtest import run_pack_backtest
from .full_research_runner import run_full_research
from ._model_selection_core import select_strategies_from_results, select_strategies_for_triage
from .runtime_router import generate_live_signals
from .readiness import check_readiness
