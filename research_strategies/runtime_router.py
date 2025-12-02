#!/usr/bin/env python3
"""Runtime router: convert recent OHLCV into candidate trades using packs, regimes, and risk gate checks.
"""
from __future__ import annotations
from typing import List, Dict, Any
from pathlib import Path
from util.risk_manager import RiskManager, get_risk_manager
from util.regime_detector import detect_symbol_regime
from research_strategies.pack_manager import run_pack_for_df
from util.trade_risk_gate import TradeCandidate, can_open_trade, TradeDecision
from util.market_scheduler import is_market_open, is_strategy_allowed_now


def load_runtime_config(selected: bool = True):
    # if selected (.selected) configs exist, prefer them
    cfg_path = Path('config/packs_final.selected.json') if selected and Path('config/packs_final.selected.json').exists() else Path('config/packs_final.json')
    if not cfg_path.exists():
        return {}
    import json
    return json.loads(cfg_path.read_text())


def generate_live_signals(symbol: str, df, env: Dict[str, Any] | None = None, risk_manager: RiskManager | None = None) -> List[Dict[str, Any]]:
    if risk_manager is None:
        risk_manager = get_risk_manager()
    packs_cfg = load_runtime_config()
    signals = []
    # run through packs that mention the symbol
    for pack_name, pack in packs_cfg.items():
        symbols = pack.get('symbols', [])
        if symbol not in symbols:
            continue
        # detect regime for symbol and update risk manager state
        try:
            regime_obj = detect_symbol_regime(df)
            # detect_symbol_regime returns a dict like {'trend': 'BULL', 'vol': 'NORMAL'} or a string
            if isinstance(regime_obj, dict):
                regime_name = regime_obj.get('trend', 'UNKNOWN')
            else:
                regime_name = regime_obj
            if hasattr(risk_manager, 'state'):
                try:
                    # expect a dict with trend & vol
                    risk_manager.state.regime_by_symbol[symbol] = regime_obj if isinstance(regime_obj, dict) else {'trend': regime_name, 'vol': 'NORMAL'}
                except Exception:
                    # ignore assignment errors
                    pass
            regime = regime_name
        except Exception:
            regime = 'UNKNOWN'
        # run pack for df, returns signals
        raw_signals = run_pack_for_df(pack_name, df, symbol, regime if isinstance(regime, str) else 'BULLISH', pack.get('asset', 'UNKNOWN'), risk_manager=risk_manager)
        # filter by trade gate
        for s in raw_signals:
            cand = TradeCandidate(strategy_id=s.get('strategy'), symbol=s.get('symbol') or symbol, platform=s.get('asset_class') or pack.get('asset'), entry_price=s.get('entry'), stop_loss=s.get('stop'), side=s.get('side'))
            # check market session open and strategy allowed windows
            ts = None
            try:
                ts = s.get('timestamp')
            except Exception:
                ts = None
            # if timestamp present, parse into datetime; otherwise use now
            import datetime as _dt
            try:
                dt_val = _dt.datetime.fromisoformat(ts) if ts else _dt.datetime.utcnow()
            except Exception:
                dt_val = _dt.datetime.utcnow()
            # if platform not open, skip
            platform_asset = s.get('asset_class') or pack.get('asset')
            if not is_market_open(platform_asset, dt_val):
                continue
            # check strategy windows
            if not is_strategy_allowed_now(s.get('strategy') or '', dt_val):
                continue
            decision = can_open_trade(cand, risk_manager.state.equity_now if hasattr(risk_manager.state, 'equity_now') else 10000.0)
            if decision.allowed:
                # annotate with sizing
                s['risk_pct'] = decision.risk_pct
                s['size'] = decision.size
                signals.append(s)
    # apply a minimal cross-platform deduplication: don't open duplicate same-direction trades for same symbol across platforms
    def _filter_cross_platform(signals_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not signals_list:
            return signals_list
        # define platform priority: higher in list => prefer
        platform_priority = ['OANDA', 'IBKR', 'COINBASE']
        # group by (symbol, direction/side)
        grouped = {}
        for s in signals_list:
            key = (s.get('symbol'), (s.get('side') or s.get('direction') or s.get('dir')))
            grouped.setdefault(key, []).append(s)
        result = []
        for key, cand_list in grouped.items():
            if len(cand_list) == 1:
                result.append(cand_list[0])
            else:
                # pick candidate with highest platform priority or fallback to first
                cand_list_sorted = sorted(cand_list, key=lambda x: platform_priority.index(x.get('asset_class')) if x.get('asset_class') in platform_priority else len(platform_priority))
                result.append(cand_list_sorted[0])
        return result

    filtered = _filter_cross_platform(signals)
    return filtered
