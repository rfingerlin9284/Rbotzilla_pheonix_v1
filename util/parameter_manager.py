"""Top-level wrapper for parameter_manager to satisfy imports across the repo.
If the rick_clean_live implementation exists, import from there; otherwise expose a minimal
fallback implementation used for tests and stubbed runtimes.
"""
try:
    from rick_clean_live.util.parameter_manager import ParameterManager, get_parameter_manager
except Exception:  # pragma: no cover - fallback for tests
    import json
    import os
    import time
    import logging
    from typing import Any, Dict, Optional

    class ParameterManager:
        def __init__(self, config_path: Optional[str] = None):
            self.config_path = config_path or os.path.join(os.getcwd(), 'config', 'system_parameters.json')
            self.params: Dict[str, Any] = {}
            self.locked_params = set()
            self.logger = logging.getLogger('parameter_manager')
            self.logger.setLevel(logging.INFO)
            self.load_config()

        def load_config(self):
            if os.path.exists(self.config_path):
                try:
                    with open(self.config_path, 'r') as f:
                        self.params = json.load(f)
                except Exception:
                    self.params = {}
            else:
                self.params = {}

        def save_config(self) -> bool:
            try:
                os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
                with open(self.config_path, 'w') as f:
                    json.dump(self.params, f, indent=2)
                return True
            except Exception:
                return False

        def get(self, key: str, default: Any = None) -> Any:
            # Allow env var override: convert dot.path to upper snake case
            env_key = key.replace('.', '_').upper()
            if env_key in os.environ:
                return os.environ.get(env_key)
            return self.params.get(key, default)

        def set(self, key: str, value: Any, component: str = 'tester') -> bool:
            if key in self.locked_params:
                return False
            self.params[key] = value
            return self.save_config()

        def lock_parameter(self, key: str):
            self.locked_params.add(key)

        def unlock_parameter(self, key: str):
            self.locked_params.discard(key)

        def get_all_parameters(self):
            return dict(self.params)

        def get_locked_parameters(self):
            return set(self.locked_params)

    _instance: Optional[ParameterManager] = None

    def get_parameter_manager(config_path: Optional[str] = None) -> ParameterManager:
        global _instance
        if _instance is None:
            _instance = ParameterManager(config_path)
        return _instance
else:
    # Ensure compatibility alias methods in the imported ParameterManager class
    import os
    try:
        if not hasattr(ParameterManager, 'set_parameter'):
            def set_parameter(self, key, value, description=None, source=None):
                # rick_clean_live.ParameterManager uses set(key, value, component)
                component = source or description or 'unknown'
                return self.set(key, value, component)

            setattr(ParameterManager, 'set_parameter', set_parameter)
        if not hasattr(ParameterManager, 'get_parameter'):
            def get_parameter(self, key, default=None):
                return self.get(key, default)

            setattr(ParameterManager, 'get_parameter', get_parameter)
    except Exception:
        # Defensive - ignore if ParameterManager is not mutable or contract differs
        pass
    # Add env variable override to existing ParameterManager class so both 'real' and fallback implementations respect .env
    try:
        if hasattr(ParameterManager, 'get') and not getattr(ParameterManager.get, '__wrapped_env_override__', False):
            orig_get = ParameterManager.get
            def _env_override_get(self, key, default=None):
                env_key = key.replace('.', '_').upper()
                if env_key in os.environ:
                    return os.environ.get(env_key)
                return orig_get(self, key, default)
            _env_override_get.__wrapped_env_override__ = True
            setattr(ParameterManager, 'get', _env_override_get)
    except Exception:
        pass
