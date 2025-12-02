#!/usr/bin/env python3
"""
Narration Agent v1 - Folder Activity Translator
Converts technical events into human-readable narrative

PIN: 841921
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class NarrationAgent:
    """
    Converts technical folder activity into human-readable narration
    Each folder has its own agent that logs to logs/{folder_name}/
    """
    
    def __init__(self, folder_name: str, log_dir: str = "logs"):
        """
        Initialize narration agent for a specific folder
        
        Args:
            folder_name: Name of the folder this agent monitors (e.g., "strategy", "hive", "ml")
            log_dir: Root logs directory
        """
        self.folder_name = folder_name
        self.log_path = Path(log_dir) / folder_name
        self.log_path.mkdir(parents=True, exist_ok=True)
        
        self.narration_file = self.log_path / "narration.jsonl"
        self.human_file = self.log_path / "human_readable.log"
        
        # Setup logger
        self.logger = logging.getLogger(f"narrator.{folder_name}")
        self.logger.setLevel(logging.INFO)
        
    def log_event(self, event_type: str, data: Dict[str, Any], context: str = ""):
        """
        Log an event in both JSON and human-readable formats
        
        Args:
            event_type: Type of event (e.g., "signal_generated", "trade_opened", "ml_prediction")
            data: Event data dictionary
            context: Optional human context/explanation
        """
        timestamp = datetime.utcnow()
        
        # JSON event (for machine processing)
        json_event = {
            "timestamp": timestamp.isoformat() + "Z",
            "folder": self.folder_name,
            "event_type": event_type,
            "data": data,
            "context": context
        }
        
        with open(self.narration_file, 'a') as f:
            f.write(json.dumps(json_event) + "\n")
        
        # Human-readable narrative
        human_narrative = self._translate_to_human(event_type, data, context, timestamp)
        
        with open(self.human_file, 'a') as f:
            f.write(human_narrative + "\n")
        
        self.logger.info(human_narrative)
        
        return json_event
    
    def _translate_to_human(self, event_type: str, data: Dict, context: str, timestamp: datetime) -> str:
        """
        Translate technical event into human trader language
        
        Returns:
            Human-readable narrative string
        """
        time_str = timestamp.strftime("%H:%M:%S UTC")
        
        # Strategy folder events
        if self.folder_name == "strategy":
            if event_type == "signal_generated":
                return (f"[{time_str}] 📊 SIGNAL: {data.get('direction', '?')} {data.get('pair', '?')} "
                       f"@ {data.get('price', '?')} | R:R {data.get('rr', '?')}:1 | "
                       f"Confidence: {data.get('confidence', '?')}%")
            elif event_type == "signal_rejected":
                return f"[{time_str}] ⛔ REJECTED: {data.get('pair', '?')} - {data.get('reason', '?')}"
        
        # Hive Mind folder events  
        elif self.folder_name == "hive":
            if event_type == "consensus_reached":
                return (f"[{time_str}] 🧠 HIVE CONSENSUS: {data.get('decision', '?')} "
                       f"| Confidence: {data.get('probability', '?')}% | "
                       f"Sources: {data.get('source_count', '?')}")
            elif event_type == "position_reassessment":
                return (f"[{time_str}] 🔄 RE-EVALUATING: {data.get('pair', '?')} "
                       f"| Current P&L: ${data.get('pnl', '?')} | "
                       f"Recommendation: {data.get('action', '?')}")
        
        # ML folder events
        elif self.folder_name == "ml":
            if event_type == "regime_detected":
                return (f"[{time_str}] 🎯 REGIME: {data.get('regime', '?').upper()} "
                       f"| Confidence: {data.get('confidence', '?')}% | "
                       f"Pack: {data.get('pack_selected', '?')}")
            elif event_type == "pattern_found":
                return f"[{time_str}] 📐 PATTERN: {data.get('pattern_name', '?')} on {data.get('pair', '?')}"
        
        # Broker folder events
        elif self.folder_name == "brokers":
            if event_type == "order_placed":
                return (f"[{time_str}] ✅ ORDER PLACED: {data.get('direction', '?')} "
                       f"{data.get('units', '?')} {data.get('pair', '?')} "
                       f"@ {data.get('price', '?')}")
            elif event_type == "position_closed":
                return (f"[{time_str}] 🏁 CLOSED: {data.get('pair', '?')} "
                       f"| P&L: ${data.get('pnl', '?')} | "
                       f"Reason: {data.get('reason', '?')}")
        
        # Generic fallback
        return f"[{time_str}] [{self.folder_name.upper()}] {event_type}: {context or str(data)}"
    
    def get_recent_events(self, count: int = 10) -> List[Dict]:
        """
        Retrieve recent events from narration log
        
        Args:
            count: Number of recent events to retrieve
            
        Returns:
            List of event dictionaries
        """
        if not self.narration_file.exists():
            return []
        
        events = []
        with open(self.narration_file, 'r') as f:
            lines = f.readlines()
            for line in lines[-count:]:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        
        return events


# Example usage
if __name__ == "__main__":
    # Create agent for strategy folder
    narrator = NarrationAgent("strategy")
    
    # Log a signal event
    narrator.log_event(
        event_type="signal_generated",
        data={
            "pair": "EUR_USD",
            "direction": "BUY",
            "price": 1.0850,
            "rr": 3.5,
            "confidence": 78
        },
        context="Bullish momentum + FVG alignment"
    )
    
    print("✅ Narration agent test complete")
