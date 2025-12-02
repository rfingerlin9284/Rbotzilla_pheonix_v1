Foundation Trading Mode & API
=================================

This document describes `foundation.trading_mode.safe_place_order` behavior and response format.

safe_place_order wrapper
-------------------------
- Signature: `safe_place_order(broker, *args, **kwargs)`
- Returns: Tuple[bool, Dict[str, Any]]
  - The boolean is an overall `ok` flag (True on success, False on failure).
  - The dict is a normalized response returned by the brokers and always contains at least:
    - `success`: bool - indicates whether the operation succeeded
    - `error`: Optional[str] - contains an error message when `success` is False
    - Any broker-specific data (e.g., `order_id`, `trades`, `status`) will be preserved at the top-level of the dict when possible.

PAPER vs LIVE
--------------
- PAPER mode (default): safe_place_order simulates order execution and returns a simulated order dict with `simulated=True` and an `order_id`.
- LIVE mode: safe_place_order calls the broker's `place_order` (or the method override) and returns the normalized broker response.

Notes
-----
- The wrapper ensures the second element of the return tuple is always a dict with the `success` key to standardize handling across the codebase.
- Code using safe_place_order should not assume a specific nested structure; prefer checking `ok_flag` and `result.get('success')`.
