#!/usr/bin/env python3
"""
Simple cross-platform positions registry

Stores an authoritative list of currently open positions across brokers to enforce
unique-symbol constraints. Uses a JSON file store (atomic writes via tmp file
and os.replace) with optional environment override for PATH.

Functions:
  - normalize_symbol(symbol)
  - read_registry()
  - write_registry(data)
  - register_position(broker, order_id, trade_id, symbol, units, details)
  - unregister_position(order_id=None, trade_id=None, symbol=None)
  - is_symbol_taken(symbol)
  - list_positions()

This is intentionally small and dependency-free to make testing easier.
"""
import os
import json
import tempfile
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
import uuid

REGISTRY_FILE = os.getenv('POSITIONS_REGISTRY_FILE', '/tmp/rick_positions_registry.json')
#!/usr/bin/env python3
"""
Simple cross-platform positions registry

Stores an authoritative list of currently open positions across brokers to enforce
unique-symbol constraints. Uses a JSON file store (atomic writes via tmp file
and os.replace) with optional environment override for PATH.

Functions:
  - normalize_symbol(symbol)
  - read_registry()
  - write_registry(data)
  - register_position(broker, order_id, trade_id, symbol, units, details)
  - unregister_position(order_id=None, trade_id=None, symbol=None)
  - is_symbol_taken(symbol)
  - list_positions()

This is intentionally small and dependency-free to make testing easier.
"""
import os
import json
import tempfile
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
import uuid

REGISTRY_FILE = os.getenv('POSITIONS_REGISTRY_FILE', '/tmp/rick_positions_registry.json')


def normalize_symbol(symbol: str) -> str:
    """Normalize symbols into uppercase underscore-separated form.
    Examples: 'EURUSD' -> 'EUR_USD', 'EUR_USD' -> 'EUR_USD', 'BTC' -> 'BTC'
    """
    if not symbol:
        return symbol
    s = symbol.upper().replace('-', '_').replace(' ', '_')
    if '_' in s:
        return s
    # If it looks like a 6-letter FX pair (3/3)
    if len(s) == 6 and s.isalpha():
        return s[:3] + '_' + s[3:]
    return s


def _ensure_registry_exists():
    if not os.path.exists(REGISTRY_FILE):
        try:
            with open(REGISTRY_FILE, 'w') as f:
                json.dump({'positions': []}, f)
        except Exception:
            # ignore write errors - registry is optional
            pass


def read_registry() -> Dict[str, Any]:
    _ensure_registry_exists()
    try:
        with open(REGISTRY_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {'positions': []}


def write_registry(data: Dict[str, Any]):
    # Atomic write via temp file
    dirpath = os.path.dirname(REGISTRY_FILE)
    fd, tmpname = tempfile.mkstemp(dir=dirpath)
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(data, f)
        os.replace(tmpname, REGISTRY_FILE)
    except Exception:
        try:
            os.remove(tmpname)
        except Exception:
            pass


def register_position(broker: str, order_id: Optional[str], trade_id: Optional[str], symbol: str, units: float, details: Optional[Dict[str, Any]] = None) -> bool:
    """Register a new open position.

    Returns True if successfully registered, False if symbol is already taken.
    """
    # Require at least one identifier (order_id or trade_id) and a symbol
    if not broker or not symbol or (not order_id and not trade_id):
        return False
    norm = normalize_symbol(symbol)
    data = read_registry()
    positions: List[Dict[str, Any]] = data.get('positions', [])
    # Check duplicates by symbol unless override is set
    allow_duplicates = os.getenv('RICK_ALLOW_CROSS_BROKER_DUPLICATES', '0') == '1'
    if not allow_duplicates:
        for p in positions:
            p_sym = p.get('symbol') or ''
            if normalize_symbol(p_sym) == norm:
                return False
    # Fallback: ensure there is an internal id to reference (use order_id or trade_id or generated uuid)
    entry_order_id = order_id or trade_id or str(uuid.uuid4())
    entry_trade_id = trade_id or order_id or None
    entry = {
        'broker': broker,
        'order_id': entry_order_id,
        'trade_id': entry_trade_id,
        'symbol': norm,
        'units': units,
        'details': details or {},
        'timestamp': datetime.now(timezone.utc).isoformat()
    }
    positions.append(entry)
    data['positions'] = positions
    write_registry(data)
    return True


def unregister_position(order_id: Optional[str] = None, trade_id: Optional[str] = None, symbol: Optional[str] = None) -> bool:
    """Unregister a position by order_id, trade_id, or symbol.
    Returns True if a position was removed.
    """
    if not (order_id or trade_id or symbol):
        return False
    data = read_registry()
    positions = data.get('positions', [])
    new_positions = []
    removed = False
    norm_target = normalize_symbol(symbol) if symbol else None
    for p in positions:
        if order_id and p.get('order_id') == order_id:
            removed = True
            continue
        if trade_id and p.get('trade_id') == trade_id:
            removed = True
            continue
        if norm_target and normalize_symbol(p.get('symbol') or '') == norm_target:
            removed = True
            continue
        new_positions.append(p)
    data['positions'] = new_positions
    write_registry(data)
    return removed


def is_symbol_taken(symbol: str) -> bool:
    # Allow environment override to disable cross-broker uniqueness checks
    if os.getenv('RICK_ALLOW_CROSS_BROKER_DUPLICATES', '0') == '1':
        return False
    norm = normalize_symbol(symbol)
    data = read_registry()
    for p in data.get('positions', []):
        if normalize_symbol(p.get('symbol') or '') == norm:
            return True
    return False


def get_position_by_symbol(symbol: str) -> Optional[Dict[str, Any]]:
    norm = normalize_symbol(symbol)
    data = read_registry()
    for p in data.get('positions', []):
        if normalize_symbol(p.get('symbol') or '') == norm:
            return p
    return None


def get_positions_by_broker(broker: str) -> List[Dict[str, Any]]:
    data = read_registry()
    return [p for p in data.get('positions', []) if p.get('broker') == broker]


def list_positions() -> List[Dict[str, Any]]:
    data = read_registry()
    return data.get('positions', [])


if __name__ == '__main__':
    print("Positions Registry Path:", REGISTRY_FILE)
    print(json.dumps(read_registry(), indent=2))
