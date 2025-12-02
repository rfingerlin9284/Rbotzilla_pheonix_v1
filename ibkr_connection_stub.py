import logging
from auth_manager import AuthManager

logger = logging.getLogger("IBKRStub")

class IBKRConnectionStub:
    def __init__(self):
        self.auth = AuthManager()
        self.config = self.auth.get_ibkr_config()
        self.connected = False

    def connect(self):
        self.connected = True
        logger.info(f"IBKR Stub Connected on {self.config['port']}")
        return True

    def place_order(self, order_spec):
        if not self.connected: return False
        logger.info(f"IBKR STUB ORDER: {order_spec}")
        return True
