"""Environment manager and helpers for safe access to secrets & config.

This module centralizes access to environment configuration values. It supports
loading a local `.env` for convenience (not committed) and provides redaction
helpers to avoid accidental leakage to logs.
"""
from pathlib import Path
import os
from typing import Optional, Dict, Any

ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT / '.env'


def _load_dotenv():
    """Load simple key=value `.env` file into os.environ if present.
    This is a non-strict loader; it does not overwrite existing env vars by default.
    """
    if not ENV_PATH.exists():
        return
    with ENV_PATH.open() as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue
            key, val = line.split('=', 1)
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = val


# Lazy load
_load_dotenv()


def get_env_var(name: str, default: Optional[Any] = None, required: bool = False) -> Optional[str]:
    """Retrieve environment variable, optionally requiring it and returning default.
    Throws ValueError if required and missing.
    """
    val = os.getenv(name, default)
    if required and (val is None or val == ''):
        raise ValueError(f"Required environment variable '{name}' not set")
    return val


def redact(val: Optional[str]) -> str:
    if not val:
        return '<MISSING>'
    if len(val) < 8:
        return 'REDACTED'
    return val[:4] + '...' + val[-4:]


def get_alert_config() -> Dict[str, Optional[str]]:
    """Return a dict with configured alert destinations (redacted for logs)."""
    cfg = {
        'ALERT_PHONE_NUMBER': get_env_var('ALERT_PHONE_NUMBER'),
        'ALERT_EMAIL': get_env_var('ALERT_EMAIL'),
        'SMS_GATEWAY': get_env_var('SMS_GATEWAY'),
        'USER_PHONE_NUMBER': get_env_var('USER_PHONE_NUMBER'),
        'TELEGRAM_CHAT_ID': get_env_var('TELEGRAM_CHAT_ID'),
        'TELEGRAM_BOT_TOKEN': get_env_var('TELEGRAM_BOT_TOKEN'),
        'DISCORD_WEBHOOK_URL': get_env_var('DISCORD_WEBHOOK_URL')
    }
    # return raw values; for logs call redact() on individual values
    return cfg


def get_market_data_config() -> Dict[str, Optional[str]]:
    return {
        'CRYPTOPANIC_API_KEY': get_env_var('CRYPTOPANIC_API_KEY'),
        # Reddit API credentials (client-only for read-only sentiment)
        'REDDIT_CLIENT_ID': get_env_var('REDDIT_CLIENT_ID'),
        'REDDIT_CLIENT_SECRET': get_env_var('REDDIT_CLIENT_SECRET'),
        'REDDIT_USER_AGENT': get_env_var('REDDIT_USER_AGENT'),
        'REDDIT_SUBREDDITS': get_env_var('REDDIT_SUBREDDITS'),
        # Add more market data APIs (free or otherwise) here as needed
    }


def require_market_data_config():
    missing = []
    for k in ['REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET', 'REDDIT_USER_AGENT']:
        if not os.getenv(k):
            missing.append(k)
    if missing:
        raise ValueError('Missing required market-data env vars: ' + ', '.join(missing))


def require_alert_config():
    missing = []
    for k in ['TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID', 'DISCORD_WEBHOOK_URL']:
        if not os.getenv(k):
            missing.append(k)
    if missing:
        raise ValueError('Missing required alert env vars: ' + ', '.join(missing))
