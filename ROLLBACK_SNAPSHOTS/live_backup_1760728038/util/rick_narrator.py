#!/usr/bin/env python3
"""
Rick AI Narrator - Plain English Trading Commentary
Generates conversational narration using Ollama LLMs
PIN: 841921
"""

import requests
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pathlib import Path

# Ollama Configuration
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
NARRATION_MODEL = "llama3.1:8b"  # Fast, conversational model

# Narration log file
PROJECT_ROOT = Path("/home/ing/RICK/RICK_LIVE_CLEAN")
LOGS_DIR = PROJECT_ROOT / "pre_upgrade" / "headless" / "logs"
RICK_NARRATION_FILE = LOGS_DIR / "rick_narration.jsonl"

logger = logging.getLogger(__name__)

class RickNarrator:
    """Rick's Conversational AI Narrator"""
    
    def __init__(self):
        self.ollama_available = self.check_ollama()
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    def check_ollama(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get("http://127.0.0.1:11434/api/tags", timeout=2)
            return response.status_code == 200
        except:
            logger.warning("⚠️ Ollama not available - using fallback narration")
            return False
    
    def generate_commentary(self, event_type: str, details: Dict[str, Any]) -> str:
        """Generate Rick's plain English commentary for a trading event"""
        
        # Create context-aware prompt based on event type
        if event_type == "SCAN_START":
            prompt = f"""You are Rick, a trading AI. Starting market scan:
Pairs to scan: {details.get('pairs', [])}
Pair count: {details.get('pair_count', 0)}

Give a brief one-sentence comment about starting the scan. Be professional but casual. Under 25 words."""

        elif event_type == "PAIR_CHECK":
            pair = details.get('pair')
            price = details.get('price')
            spread = details.get('spread_pips')
            prompt = f"""You are Rick, a trading AI. Checking {pair}:
Current price: {price}
Spread: {spread} pips

Give a quick one-sentence observation about this pair. Under 20 words."""

        elif event_type == "PATTERN_DETECTION":
            patterns = details.get('patterns', [])
            confidence = details.get('confidence', 0)
            prompt = f"""You are Rick, a trading AI. Found patterns:
Patterns: {', '.join(patterns)}
Confidence: {confidence:.0%}

Give a one-sentence comment about these patterns. Be analytical. Under 25 words."""

        elif event_type == "ML_ANALYSIS":
            direction = details.get('direction')
            confidence = details.get('confidence')
            regime = details.get('regime')
            prompt = f"""You are Rick, a trading AI. ML analysis complete:
Direction: {direction}
Confidence: {confidence:.0%}
Market regime: {regime}

Give a quick one-sentence take on this signal. Under 25 words."""

        elif event_type == "FILTER_CHECK":
            filter_name = details.get('filter_name')
            passed = details.get('passed')
            score = details.get('score')
            prompt = f"""You are Rick, a trading AI. Filter check:
Filter: {filter_name}
Result: {"PASSED" if passed else "FAILED"}
Score: {score:.0%}

Give a brief one-sentence reaction. Under 20 words."""

        elif event_type == "RR_CALCULATION":
            rr = details.get('rr_ratio')
            passes = details.get('passes_charter')
            prompt = f"""You are Rick, a trading AI. Risk/Reward calculated:
RR Ratio: {rr:.1f}:1
Charter compliant: {"Yes" if passes else "No"}

Give a quick one-sentence assessment. Under 20 words."""

        elif event_type == "CONFLUENCE_CHECK":
            score = details.get('confluence_score')
            filters = details.get('passing_filters', [])
            prompt = f"""You are Rick, a trading AI. Confluence analysis:
Score: {score:.0%}
Passing filters: {len(filters)}

Give a brief one-sentence evaluation. Under 20 words."""

        elif event_type == "POSITION_SIZING":
            size = details.get('position_size')
            notional = details.get('notional_value')
            prompt = f"""You are Rick, a trading AI. Position sizing done:
Position: {size} units
Notional: ${notional:.0f}

Give a quick one-sentence confirmation. Under 20 words."""

        elif event_type == "CORRELATION_CHECK":
            corr = details.get('correlation_level')
            risk = details.get('risk')
            prompt = f"""You are Rick, a trading AI. Correlation check:
Correlation: {corr:.0%}
Risk level: {risk}

Give a brief one-sentence assessment. Under 20 words."""

        elif event_type == "TRADE_DECISION":
            decision = details.get('decision')
            score = details.get('total_score')
            filters = details.get('filters_passed')
            prompt = f"""You are Rick, a trading AI. Final decision:
Decision: {decision}
Total score: {score:.0%}
Filters passed: {filters}

Give a decisive one-sentence verdict. Under 25 words."""

        elif event_type == "TRADE_EXECUTION":
            pair = details.get('pair')
            direction = details.get('direction')
            rr = details.get('take_profit', 0) - details.get('entry_price', 0)
            prompt = f"""You are Rick, a trading AI. Executing trade:
Pair: {pair}
Direction: {direction}

Give an excited but professional one-sentence comment. Under 20 words."""

        elif event_type == "TRADE_REJECTED":
            reason = details.get('rejection_reason')
            prompt = f"""You are Rick, a trading AI. Trade rejected:
Reason: {reason}

Give a brief one-sentence acknowledgment. Stay confident. Under 20 words."""

        elif event_type == "SCAN_COMPLETE":
            scanned = details.get('pairs_scanned')
            opportunities = details.get('opportunities_found')
            executed = details.get('trades_executed')
            prompt = f"""You are Rick, a trading AI. Scan complete:
Pairs scanned: {scanned}
Opportunities: {opportunities}
Trades executed: {executed}

Give a quick one-sentence summary. Under 25 words."""

        elif event_type == "OCO_PLACED":
            prompt = f"""You are Rick, a street-smart trading AI. A trade just got executed:
Symbol: {details.get('symbol', 'Unknown')}
Direction: {details.get('direction', 'Unknown')}
Entry Price: {details.get('entry_price', 'Unknown')}
Stop Loss: {details.get('stop_loss', 'Unknown')}
Take Profit: {details.get('take_profit', 'Unknown')}
Risk/Reward: {details.get('risk_reward', 'Unknown')}

Give me a one-sentence casual commentary about this trade setup. Be confident and conversational, like you're explaining it to a friend. Keep it under 30 words."""

        elif event_type == "POSITION_OPEN":
            prompt = f"""You are Rick, a trading AI. Just opened a position:
Symbol: {details.get('symbol')}
Direction: {details.get('direction')}
Entry: {details.get('entry_price')}

Give a quick one-sentence comment about why this looks good. Be casual and confident. Under 25 words."""

        elif event_type == "POSITION_CLOSED":
            pnl = details.get('pnl', 0)
            outcome = "won" if pnl > 0 else "lost"
            prompt = f"""You are Rick, a trading AI. Just closed a trade:
Symbol: {details.get('symbol')}
Outcome: {outcome} ${abs(pnl):.2f}
Duration: {details.get('duration_minutes', '?')} minutes

Give a brief one-sentence reaction. If it won, be pleased but not cocky. If it lost, acknowledge it but stay confident. Under 25 words."""

        elif event_type == "MARKET_ANALYSIS":
            prompt = f"""You are Rick, a trading AI analyzing the market:
Symbol: {details.get('symbol')}
Current Price: {details.get('price')}
Trend: {details.get('trend', 'Unknown')}
Indicators: {details.get('indicators', {})}

Give a quick one-sentence market observation. Be analytical but casual. Under 30 words."""

        elif event_type == "RISK_ALERT":
            prompt = f"""You are Rick, a trading AI. Risk alert triggered:
Reason: {details.get('reason')}
Current Exposure: {details.get('exposure', 'Unknown')}

Give a quick one-sentence heads-up about this risk situation. Be cautious but not panicked. Under 25 words."""

        else:
            # Generic fallback
            prompt = f"""You are Rick, a trading AI. Event occurred: {event_type}
Details: {json.dumps(details, indent=2)}

Give a brief one-sentence comment. Be casual and informative. Under 30 words."""

        # Generate commentary via Ollama
        if self.ollama_available:
            try:
                commentary = self.query_ollama(prompt)
                if commentary:
                    return commentary
            except Exception as e:
                logger.warning(f"Ollama query failed: {e}")
        
        # Fallback to template-based narration
        return self.fallback_narration(event_type, details)
    
    def query_ollama(self, prompt: str) -> Optional[str]:
        """Query Ollama for commentary"""
        try:
            payload = {
                "model": NARRATION_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.8,  # More creative
                    "top_p": 0.9,
                    "max_tokens": 100  # Keep it short
                }
            }
            
            response = requests.post(OLLAMA_URL, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                commentary = result.get('response', '').strip()
                # Clean up any quotes or formatting
                commentary = commentary.replace('"', '').replace('\n', ' ').strip()
                return commentary
        except Exception as e:
            logger.error(f"Ollama query error: {e}")
        return None
    
    def fallback_narration(self, event_type: str, details: Dict[str, Any]) -> str:
        """Template-based fallback when Ollama unavailable"""
        
        if event_type == "OCO_PLACED":
            symbol = details.get('symbol', 'Unknown')
            direction = details.get('direction', 'Unknown')
            rr = details.get('risk_reward', 0)
            return f"🎯 Just set up a {direction} trade on {symbol} with {rr:.1f}:1 risk/reward. Looking solid."
        
        elif event_type == "POSITION_OPEN":
            symbol = details.get('symbol')
            direction = details.get('direction')
            return f"✅ {symbol} {direction} position is live. Let's see how this plays out."
        
        elif event_type == "POSITION_CLOSED":
            symbol = details.get('symbol')
            pnl = details.get('pnl', 0)
            if pnl > 0:
                return f"💰 Nice! {symbol} closed with ${pnl:.2f} profit. That's what I'm talking about."
            else:
                return f"📉 {symbol} took a ${abs(pnl):.2f} hit. Can't win 'em all, on to the next one."
        
        elif event_type == "MARKET_ANALYSIS":
            symbol = details.get('symbol')
            trend = details.get('trend', 'ranging')
            return f"📊 {symbol} looking {trend} right now. Watching for a clean setup."
        
        elif event_type == "RISK_ALERT":
            reason = details.get('reason')
            return f"⚠️ Hold up - {reason}. Keeping things tight for now."
        
        else:
            return f"📌 {event_type}: {details.get('summary', 'Event logged')}"
    
    def log_narration(self, event_type: str, details: Dict[str, Any], 
                     symbol: Optional[str] = None, venue: Optional[str] = None) -> str:
        """Log event with Rick's conversational commentary"""
        
        # Generate Rick's commentary
        commentary = self.generate_commentary(event_type, details)
        
        # Create narration event
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "symbol": symbol,
            "venue": venue,
            "rick_says": commentary,  # Rick's conversational comment
            "details": details
        }
        
        # Log to file
        try:
            with open(RICK_NARRATION_FILE, 'a') as f:
                f.write(json.dumps(event) + '\n')
            logger.info(f"Rick: {commentary}")
        except Exception as e:
            logger.error(f"Failed to log narration: {e}")
        
        return commentary


# Global narrator instance
_narrator = None

def get_narrator() -> RickNarrator:
    """Get global narrator instance"""
    global _narrator
    if _narrator is None:
        _narrator = RickNarrator()
    return _narrator


def rick_narrate(event_type: str, details: Dict[str, Any], 
                 symbol: Optional[str] = None, venue: Optional[str] = None) -> str:
    """Convenience function to generate and log Rick's narration"""
    narrator = get_narrator()
    return narrator.log_narration(event_type, details, symbol, venue)


def get_latest_rick_narration(n: int = 50) -> list:
    """Get latest Rick narration entries"""
    try:
        if not RICK_NARRATION_FILE.exists():
            return []
        
        events = []
        with open(RICK_NARRATION_FILE, 'r') as f:
            for line in f:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        
        return events[-n:]
    except Exception as e:
        logger.error(f"Failed to read Rick narration: {e}")
        return []


# Test function
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    narrator = RickNarrator()
    
    # Test different event types
    print("\n=== Testing Rick Narrator ===\n")
    
    # Test 1: Trade placement
    trade_details = {
        "symbol": "EUR_USD",
        "direction": "LONG",
        "entry_price": 1.1604,
        "stop_loss": 1.1580,
        "take_profit": 1.1680,
        "risk_reward": 3.2
    }
    commentary = narrator.log_narration("OCO_PLACED", trade_details, "EUR_USD", "oanda")
    print(f"✅ Trade Commentary: {commentary}\n")
    
    # Test 2: Position closed (win)
    win_details = {
        "symbol": "GBP_USD",
        "pnl": 47.23,
        "duration_minutes": 35
    }
    commentary = narrator.log_narration("POSITION_CLOSED", win_details, "GBP_USD", "oanda")
    print(f"✅ Win Commentary: {commentary}\n")
    
    # Test 3: Market analysis
    market_details = {
        "symbol": "USD_JPY",
        "price": 149.825,
        "trend": "bullish",
        "indicators": {"RSI": 68, "MACD": "positive"}
    }
    commentary = narrator.log_narration("MARKET_ANALYSIS", market_details, "USD_JPY", "oanda")
    print(f"✅ Analysis Commentary: {commentary}\n")
    
    # Test 4: Get latest narration
    print("=== Latest Rick Narration ===")
    latest = get_latest_rick_narration(5)
    for entry in latest:
        print(f"[{entry['timestamp'][:19]}] Rick: {entry['rick_says']}")
