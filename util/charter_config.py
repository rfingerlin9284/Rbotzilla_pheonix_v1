import os
import yaml
from typing import Dict, Any

DEFAULT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'charter.yaml')


def load_charter_config(path: str = None) -> Dict[str, Any]:
    path = path or DEFAULT_PATH
    try:
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    except Exception:
        return {}
