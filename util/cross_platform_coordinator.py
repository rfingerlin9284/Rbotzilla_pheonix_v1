#!/usr/bin/env python3
from __future__ import annotations
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import json

_CFG_PATH = Path('config/cross_asset_rules.json')


def _load_cfg() -> Dict[str, Any]:
    if not _CFG_PATH.exists():
        return {'rules': []}
    try:
        return json.loads(_CFG_PATH.read_text())
    except Exception:
        return {'rules': []}


class CrossPlatformCoordinator:
    def __init__(self):
        self.cfg = _load_cfg()

    def refresh(self):
        self.cfg = _load_cfg()

    def allowed_to_open(self, candidate: 'TradeCandidate', risk_state) -> Tuple[bool, str]:
        """Return (allowed, reason) applying cross-asset rules in config.

        Rules structure:
          - rules: [ { if: {symbol, direction}, then: {symbol, allow_direction} } ]
        Interpretation: if there exists an open position for `if.symbol` with same direction as `if.direction` in risk_state, then any candidate for `then.symbol` must match the allow_direction; otherwise blocked.
        """
        if not candidate or not candidate.symbol:
            return True, 'no_candidate'
        # refresh config only if empty (keep in-memory override if present)
        if not self.cfg:
            self.refresh()
        rules = self.cfg.get('rules', [])
        try:
            for r in rules:
                print('DBG: checking rule', r)
                if_cond = r.get('if', {})
                then_cond = r.get('then', {})
                if_symbol = if_cond.get('symbol')
                if_direction = if_cond.get('direction')
                then_symbol = then_cond.get('symbol')
                allow_direction = then_cond.get('allow_direction')
                # if candidate is for then_symbol and there exists open position for if_symbol with if_direction
                if candidate.symbol == then_symbol:
                    print('DBG: candidate symbol matches then_symbol', candidate.symbol, then_symbol)
                    open_positions = risk_state.open_positions_by_symbol.get(if_symbol, [])
                    print('DBG: open_positions', open_positions)
                    has_open = any((p.get('direction') == if_direction) for p in open_positions)
                    print('DBG: has_open', has_open, 'if_direction', if_direction)
                    if has_open:
                        # enforce allow_direction on candidate
                        if candidate.side is None:
                            print('DBG: candidate missing side')
                            return False, 'missing_candidate_side'
                        if candidate.side != allow_direction:
                            print('DBG: candidate side mismatch', candidate.side, 'allow', allow_direction)
                            return False, f'cross_rule_blocked_{if_symbol}_to_{then_symbol}'
                        else:
                            # Allowed as hedging direction
                            return True, 'cross_rule_allowed_as_hedge'
        except Exception:
            return True, 'coord_error'
        return True, 'ok'


_GLOBAL_COORD = CrossPlatformCoordinator()


def allowed_to_open(candidate, risk_state) -> Tuple[bool, str]:
    return _GLOBAL_COORD.allowed_to_open(candidate, risk_state)
