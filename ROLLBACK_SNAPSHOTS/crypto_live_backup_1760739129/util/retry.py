"""Small retry decorator with exponential backoff and optional jitter."""
import time
from typing import Callable, Type, Tuple, Any

# Use project stochastic helpers instead of the stdlib `random` to follow
# the repository's stochastic-first policy.
from stochastic import random_bytes


def retry(tries: int = 3, backoff: float = 0.5, exceptions: Tuple[Type[BaseException], ...] = (Exception,), jitter: bool = True):
    def _decorator(fn: Callable):
        def _wrapped(*args, **kwargs):
            last_exc = None
            for attempt in range(1, tries + 1):
                try:
                    return fn(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    if attempt == tries:
                        raise
                    sleep = backoff * (2 ** (attempt - 1))
                    if jitter:
                        # derive a small float in [0,1) from secure bytes
                        b = random_bytes(2)
                        num = int.from_bytes(b, 'big') / 65535.0
                        sleep = sleep * (0.75 + num * 0.5)
                    time.sleep(sleep)
            # unreachable
            raise last_exc

        return _wrapped

    return _decorator
