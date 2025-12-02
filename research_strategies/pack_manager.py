import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from .strategy_base import StrategyConfig
from importlib import import_module
from typing import Tuple

DEFAULT_PACKS = {
    'FX_BULL_PACK': ['ema_scalper', 'breakout_volume_expansion'],
    'FX_SIDEWAYS_PACK': ['ema_scalper'],
    'CRYPTO_BULL_PACK': ['breakout_volume_expansion']
}

# Default mapping for triage allowed strategies per pack. This is used if a config file is unavailable.
DEFAULT_TRIAGE_ALLOWED = {
    'FX_BULL_PACK': ['breakout_volume_expansion'],
    'FX_SIDEWAYS_PACK': ['ema_scalper'],
    'CRYPTO_BULL_PACK': ['breakout_volume_expansion']
}


def read_packs_from_file(path: str) -> Dict[str, List[str]]:
    try:
        # prefer explicit path; otherwise fall back to final packs or default
        if path and Path(path).exists():
            with open(path, 'r') as f:
                return json.load(f)
        elif Path('config/packs_final.json').exists():
            with open('config/packs_final.json', 'r') as f:
                return json.load(f)
        elif Path('config/packs.json').exists():
            with open('config/packs.json', 'r') as f:
                return json.load(f)
        else:
            return DEFAULT_PACKS
    except Exception:
        return DEFAULT_PACKS


def get_pack_strategies(pack_name: str, config_overrides: Optional[Dict[str, Any]] = None) -> Tuple[List[str], List[StrategyConfig]]:
    # prefer finalized packs file, fallback to packs.json or defaults
    packs = read_packs_from_file('config/packs_final.json')
    if not packs:
        packs = read_packs_from_file('config/packs.json')
    package_value = packs.get(pack_name, [])
    if isinstance(package_value, dict):
        strategy_names = package_value.get('strategies', [])
    else:
        strategy_names = package_value
    configs = []
    timeframe = 'M15'
    pack_info = packs.get(pack_name, {})
    if isinstance(pack_info, dict):
        timeframe = pack_info.get('timeframe', timeframe)
    for s in strategy_names:
        params = (config_overrides or {}).get(s, {})
        configs.append(StrategyConfig(symbol='EUR_USD', timeframe=timeframe, params=params))
    return strategy_names, configs


def run_pack_for_df(pack_name: str, df, symbol: str, regime: str, asset_class: str, advanced_features: bool = True, risk_manager=None, triage_limit: int = 1):
    """Run the pack's strategies against a single OHLCV DataFrame and return combined signals.

    Pack_name is a key in config/packs.json; df is a pandas DataFrame with columns: time, open, high, low, close, volume.
    """
    strategy_names, configs = get_pack_strategies(pack_name)
    signals_all = []
    selected = list(zip(strategy_names, configs))
    # If triage mode is active, reduce strategies to triage_limit
    if risk_manager is not None and getattr(risk_manager.get_state(), 'triage_mode', False):
        # read triage_allowed list from the packs.json file if present
        packs_cfg_path = 'config/packs.json'
        try:
            with open(packs_cfg_path, 'r') as f:
                import json
                cfg = json.load(f)
                triage_allowed = cfg.get('triage_allowed', {})
                allowed_list = triage_allowed.get(pack_name, None)
                if allowed_list:
                    selected = [pair for pair in selected if pair[0] in allowed_list]
                else:
                    selected = selected[:triage_limit]
        except Exception:
            selected = selected[:triage_limit]

    for sname, cfg in selected:
        # ensure the strategy config uses the actual symbol being tested
        try:
            cfg.symbol = symbol
        except Exception:
            pass
        try:
            mod = import_module(f'research_strategies.{sname}')
            clsname = ''.join([p.capitalize() for p in sname.split('_')])
            if hasattr(mod, clsname):
                StrategyClass = getattr(mod, clsname)
            else:
                # fallback – try to find class in module that inherits Strategy
                StrategyClass = getattr(mod, list(mod.__dict__.keys())[-1])
            strat = StrategyClass(cfg)
            # map module/class to strategy code if available
            try:
                from strategies.registry import get_all_strategy_classes
                all_cls = get_all_strategy_classes()
                # invert mapping class->code
                code_map = {v: k for k, v in all_cls.items()}
                if StrategyClass in code_map:
                    code = code_map[StrategyClass]
                else:
                    code = sname
            except Exception:
                code = sname
            df_features = strat.compute_features(df)
            sigs = strat.generate_signals(df_features)
            for s in sigs:
                s['pack'] = pack_name
                s['strategy'] = code
                s['regime'] = regime
                s['asset_class'] = asset_class
                # attach effective risk pct based on RiskManager if available
                s['effective_risk_pct'] = None
                if risk_manager is not None:
                    from util.dynamic_sizing import get_effective_risk_pct
                    base = risk_manager.config.get('default_risk_per_trade_pct', 0.0075)
                    s['effective_risk_pct'] = get_effective_risk_pct(base, risk_manager)
                signals_all.append(s)
        except Exception:
            # skip a strategy if it fails in this demo
            continue
    return signals_all


def compute_triage_allowed_from_results(results_path: str, min_sharpe: float = 1.0, max_dd: float = 0.3, top_n: int = 1):
    try:
        from .model_selection import compute_triage_allowed_from_path
        return compute_triage_allowed_from_path(results_path, min_sharpe=min_sharpe, max_dd=max_dd, top_n=top_n)
    except Exception:
        return DEFAULT_TRIAGE_ALLOWED
