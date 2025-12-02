import os

class MicroTradeFilter:
    def __init__(self, atr_threshold=0.0005):
        self.atr_threshold = atr_threshold
        # Pull minimum micro trade size from ENV to allow canary runs
        try:
            self.min_size = int(os.getenv('MIN_MICRO_SIZE', 1000))
        except Exception:
            self.min_size = 1000

    def validate_size(self, size):
        try:
            return abs(int(size)) >= self.min_size
        except Exception:
            return False

    def check_volatility(self, atr_value):
        return atr_value >= self.atr_threshold
