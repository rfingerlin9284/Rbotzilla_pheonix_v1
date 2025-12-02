import os
from dotenv import load_dotenv
import logging
from foundation.trading_mode import Mode, set_mode

MODE_ALIASES = {
    'DEMO': 'PAPER',
    'PRACTICE': 'PAPER',
    'SANDBOX': 'PAPER',
    'PAPER': 'PAPER',
    'LIVE': 'LIVE'
}

class AuthManager:
    def __init__(self, env_file='.env'):
        load_dotenv(env_file)
        logger = logging.getLogger('Auth')
        try:
            # Report which env file was loaded. If file doesn't exist, load_dotenv is silent.
            exists = os.path.exists(env_file)
            logger.info(f"AuthManager: Loaded env_file='{env_file}' exists={exists}")
        except Exception:
            pass
        raw_mode = os.getenv('MODE', 'PAPER').upper()
        normalized = MODE_ALIASES.get(raw_mode, 'PAPER')
        # Set the global trading mode to normalized mode (do not force)
        try:
            set_mode(Mode(normalized))
        except Exception:
            # If switching to LIVE is blocked by env, stay in PAPER
            set_mode(Mode.PAPER)
        self.mode = normalized
        # Additional info log showing the mode used by the runtime
        try:
            logger.info(f"AuthManager: Effective trading mode set to {self.mode}")
        except Exception:
            pass

    def is_live(self): return self.mode == 'LIVE'
    def is_paper(self): return self.mode == 'PAPER'

    def get_oanda_token(self):
        return os.getenv('OANDA_LIVE_TOKEN') if self.is_live() else os.getenv('OANDA_PRACTICE_TOKEN')

    def get_oanda_account(self):
        return os.getenv('OANDA_LIVE_ACCOUNT_ID') if self.is_live() else os.getenv('OANDA_PRACTICE_ACCOUNT_ID')

    def get_ibkr_config(self):
        return {
            "host": os.getenv('IBKR_HOST', '127.0.0.1'),
            "port": int(os.getenv('IBKR_PORT', 7497)),
            "client_id": int(os.getenv('IBKR_CLIENT_ID', 1))
        }
