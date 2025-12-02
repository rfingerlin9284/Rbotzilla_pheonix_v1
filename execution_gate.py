import os
from auth_manager import AuthManager
from micro_trade_filter import MicroTradeFilter

class ExecutionGate:
    def __init__(self):
        self.auth = AuthManager()
        self.micro = MicroTradeFilter()

    def validate_signal(self, signal):
        # Safety switch: global exec enable/disable
        exec_enabled = os.getenv('EXECUTION_ENABLED', 'true').lower()
        if exec_enabled in ['false', '0', 'no', 'off']:
            return False, 'EXECUTION_DISABLED'
        # 1. Timeframe Gate
        if signal.get("timeframe") in ["M1", "M5"]: return False, "M15_NOISE_REJECTED"
        # 2. Micro Gate
        if not self.micro.validate_size(signal.get("size", 10000)): return False, "MICRO_SIZE_REJECTED"
        # 3. Risk Gate - respect MAX_RISK_PER_TRADE from env (default 0.05)
        max_risk = float(os.getenv('MAX_RISK_PER_TRADE', 0.05))
        if signal.get("risk", 0) > max_risk and signal.get("pin") != os.getenv('RICK_PIN', '841921'):
            return False, "HIGH_RISK_MISSING_PIN"

        # 4. Size Gate - Do not exceed MAX_POSITION_SIZE
        try:
            max_pos = int(os.getenv('MAX_POSITION_SIZE', 10000))
            if signal.get('size', 0) > 0 and int(signal.get('size')) > max_pos:
                return False, 'MAX_POSITION_SIZE_EXCEEDED'
        except Exception:
            pass

        return True, "ACCEPTED"
