import os
from dotenv import load_dotenv
import logging
try:
    from .mode import set_mode, Mode
except Exception:
    from PhoenixV2.core.mode import set_mode, Mode

class AuthManager:
    def __init__(self, env_path=None):
        # Try multiple locations for .env
        logger = logging.getLogger('Auth')
        if env_path:
            load_dotenv(env_path)
            try:
                logger.info(f"AuthManager: Loaded env_path='{env_path}' exists={os.path.exists(env_path)}")
            except Exception:
                pass
        else:
            load_dotenv('../.env')
            load_dotenv('.env')
        env_mode = os.getenv('MODE', 'PAPER').upper()
        # Normalize mode aliases
        norm = 'PAPER' if env_mode in ['DEMO','PRACTICE','SANDBOX'] else env_mode
        try:
            set_mode(Mode(norm))
        except Exception:
            set_mode(Mode.PAPER)
        self.mode = norm
        try:
            logger.info(f"AuthManager: Effective trading mode set to {self.mode} (env_mode={env_mode})")
            if self.mode == 'LIVE':
                logger.warning(f"AuthManager: LIVE MODE DETECTED. Using LIVE credentials.")
            else:
                logger.info(f"AuthManager: PAPER MODE DETECTED. Using PRACTICE credentials.")
        except Exception:
            pass
        
    def is_live(self):
        return self.mode == 'LIVE'

    def get_oanda_config(self):
        return {
            "token": os.getenv('OANDA_LIVE_TOKEN') if self.is_live() else os.getenv('OANDA_PRACTICE_TOKEN'),
            "account": os.getenv('OANDA_LIVE_ACCOUNT_ID') if self.is_live() else os.getenv('OANDA_PRACTICE_ACCOUNT_ID'),
            "url": "https://api-fxtrade.oanda.com/v3" if self.is_live() else "https://api-fxpractice.oanda.com/v3"
        }

    def get_ibkr_config(self):
        # Prefer explicit environment overrides for host/port (useful for WSL/Windows host setups)
        return {
            "host": os.getenv('IBKR_HOST', '172.25.80.1'),
            "port": int(os.getenv('IBKR_PORT', '4002')),
            "client_id": int(os.getenv('IBKR_CLIENT_ID', '1'))
        }

    def get_coinbase_config(self):
        return {
            "key": os.getenv('COINBASE_API_KEY'),
            "secret": os.getenv('COINBASE_API_SECRET'),
            "is_sandbox": not self.is_live()
        }
