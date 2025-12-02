import logging

class StrategyAggregator:
    def __init__(self):
        self.signals = []
        self.logger = logging.getLogger("RBotZilla_Aggregator")

    def enforce_timeframe(self, signal):
        if signal.get("timeframe") in ["M1", "M5"]:
            self.logger.warning(f"RBotZilla: Dropped Hive Mind signal (Timeframe {signal['timeframe']} < M15)")
            return False
        return True

    def ingest_hive_inference(self, inference_packet):
        signal = {
            "symbol": inference_packet.get("pair"),
            "action": inference_packet.get("direction"), 
            "confidence": inference_packet.get("confidence", 0.0),
            "timeframe": inference_packet.get("timeframe"),
            "source": "RICK_HIVE_MIND",
            "timestamp": inference_packet.get("timestamp")
        }

        if self.enforce_timeframe(signal):
            self.signals.append(signal)
            return True, "Inference Accepted"
        
        return False, "Inference Rejected (Safety Violation)"

    def get_valid_signals(self):
        return self.signals
