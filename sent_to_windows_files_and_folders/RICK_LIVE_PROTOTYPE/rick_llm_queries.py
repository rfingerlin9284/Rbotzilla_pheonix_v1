#!/usr/bin/env python3
"""
RICK LLM Integration - Ollama Wrapper
Local Llama 3.1 8B Model Integration
PIN 841921 Approved | Charter Compliant

Features:
- Position analysis automation
- Strategy recommendations
- Market commentary generation
- Anomaly detection & alerts
- Interactive query interface
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import time

# Configuration
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "llama3.1:8b"
OLLAMA_TIMEOUT = 30

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class OllamaResponse:
    """Ollama API response wrapper"""
    success: bool
    content: str
    error: Optional[str] = None
    model: str = OLLAMA_MODEL
    timestamp: str = ""
    response_time: float = 0.0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class RickLLMClient:
    """Local Ollama LLM client for Rick trading AI"""

    def __init__(self, host: str = OLLAMA_HOST, model: str = OLLAMA_MODEL):
        self.host = host
        self.model = model
        self.is_available = self._check_availability()

    def _check_availability(self) -> bool:
        """Check if Ollama service is running and model is available"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = [m.get("name", "") for m in data.get("models", [])]
                model_available = any(self.model in m for m in models)
                if model_available:
                    logger.info(f"✅ Ollama available with {self.model}")
                    return True
            logger.warning(f"⚠️ Ollama not fully ready")
            return False
        except requests.exceptions.ConnectionError:
            logger.warning(f"❌ Cannot connect to Ollama at {self.host}")
            return False
        except Exception as e:
            logger.warning(f"❌ Ollama check failed: {e}")
            return False

    def query(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> OllamaResponse:
        """
        Query the LLM with optional trading context
        
        Args:
            prompt: User query
            context: Optional trading context (positions, market data, etc.)
        
        Returns:
            OllamaResponse with result or error
        """
        if not self.is_available:
            return OllamaResponse(
                success=False,
                content="",
                error="Ollama service not available"
            )

        # Build context-aware prompt
        enriched_prompt = self._enrich_prompt(prompt, context)

        try:
            start_time = time.time()
            
            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": enriched_prompt,
                    "stream": False,
                    "temperature": 0.7,
                    "top_p": 0.9,
                },
                timeout=OLLAMA_TIMEOUT
            )

            response.raise_for_status()
            data = response.json()
            
            return OllamaResponse(
                success=True,
                content=data.get("response", "").strip(),
                model=self.model,
                response_time=time.time() - start_time
            )

        except requests.exceptions.Timeout:
            return OllamaResponse(
                success=False,
                content="",
                error=f"Request timeout after {OLLAMA_TIMEOUT}s"
            )
        except requests.exceptions.ConnectionError:
            return OllamaResponse(
                success=False,
                content="",
                error="Cannot connect to Ollama service"
            )
        except json.JSONDecodeError:
            return OllamaResponse(
                success=False,
                content="",
                error="Invalid response from Ollama"
            )
        except Exception as e:
            return OllamaResponse(
                success=False,
                content="",
                error=f"Query error: {str(e)}"
            )

    def analyze_position(self, position: Dict[str, Any]) -> OllamaResponse:
        """Analyze a trading position using LLM"""
        prompt = f"""As an expert trading AI (Rick), analyze this trading position:

Symbol: {position.get('symbol', 'N/A')}
Broker: {position.get('broker', 'N/A')}
Side: {position.get('side', 'N/A')}
Entry Price: {position.get('entry_price', 'N/A')}
Current Price: {position.get('current_price', 'N/A')}
Size: {position.get('size', 'N/A')}
P&L: {position.get('pnl', 'N/A')}
Risk/Reward: {position.get('rr_ratio', 'N/A')}

Provide:
1. Current position health assessment
2. Risk evaluation
3. Suggested action (hold/close/adjust)
4. Key price levels to watch
Keep response concise (3-4 sentences)."""

        return self.query(prompt, context=position)

    def generate_strategy_suggestion(self, market_data: Dict[str, Any]) -> OllamaResponse:
        """Generate strategy recommendations based on market data"""
        prompt = f"""As an expert trading AI (Rick) with 10+ years experience, provide a brief trading strategy suggestion based on this market data:

Current Time: {market_data.get('timestamp', 'N/A')}
Market Conditions: {market_data.get('conditions', 'N/A')}
Recent Volatility: {market_data.get('volatility', 'N/A')}
Key Levels: {market_data.get('key_levels', 'N/A')}
Active Positions: {market_data.get('active_positions', 0)}

Provide:
1. Market sentiment assessment
2. Recommended strategy (e.g., Bullish Wolf, Sideways Wolf, Bearish Wolf)
3. Risk management notes
4. Specific entry/exit considerations
Keep response concise (3-4 sentences)."""

        return self.query(prompt, context=market_data)

    def generate_market_commentary(self, market_snapshot: Dict[str, Any]) -> OllamaResponse:
        """Generate market commentary for display"""
        prompt = f"""As an expert trading AI (Rick), provide brief market commentary:

Time: {market_snapshot.get('timestamp', 'N/A')}
Market: {market_snapshot.get('instruments', 'N/A')}
Volatility: {market_snapshot.get('volatility_level', 'Medium')}
Trend: {market_snapshot.get('trend', 'Mixed')}
Capital Deployed: {market_snapshot.get('capital_deployed', 'N/A')}

Provide 1-2 sentences of actionable market commentary."""

        return self.query(prompt, context=market_snapshot)

    def detect_anomalies(self, system_metrics: Dict[str, Any]) -> OllamaResponse:
        """Detect potential anomalies in system metrics"""
        prompt = f"""As an expert trading AI (Rick), review these system metrics for anomalies:

Total P&L: {system_metrics.get('total_pnl', 'N/A')}
Win Rate: {system_metrics.get('win_rate', 'N/A')}
Max Drawdown: {system_metrics.get('max_drawdown', 'N/A')}
Sharpe Ratio: {system_metrics.get('sharpe_ratio', 'N/A')}
Connection Status: {system_metrics.get('connection_status', 'N/A')}
Last Trade Time: {system_metrics.get('last_trade_time', 'N/A')}

Flag any red flags or anomalies (1-2 sentences). If everything looks normal, say "All metrics nominal"."""

        return self.query(prompt, context=system_metrics)

    def _enrich_prompt(self, prompt: str, context: Optional[Dict] = None) -> str:
        """Enrich prompt with system context"""
        system_context = """You are Rick, an expert AI trading assistant with deep knowledge of:
- Multi-broker trading systems (OANDA, Coinbase, IB)
- Risk management and position sizing
- Technical analysis and market microstructure
- Automated trading strategies (Wolfpack)
- Charter compliance (PIN 841921)

Keep responses concise, actionable, and risk-focused. Always consider position sizing and risk/reward ratios.
Charter Rules: RR ≥ 3.2, Daily loss limit -5%, Max hold 6 hours, Min notional $15k.

"""
        
        if context:
            context_str = "\nContext data:\n" + json.dumps(context, indent=2, default=str)
            return system_context + context_str + "\n\nUser query:\n" + prompt
        
        return system_context + prompt

    def health_check(self) -> Dict[str, Any]:
        """Check Ollama service health"""
        health = {
            "ollama_connected": self.is_available,
            "model": self.model,
            "host": self.host,
            "timestamp": datetime.now().isoformat()
        }

        if self.is_available:
            try:
                response = requests.get(f"{self.host}/api/show", 
                                       json={"name": self.model},
                                       timeout=5)
                if response.status_code == 200:
                    health["model_loaded"] = True
                    health["model_info"] = response.json()
                else:
                    health["model_loaded"] = False
            except:
                health["model_loaded"] = False

        return health


# Singleton instance for use across modules
_rick_client: Optional[RickLLMClient] = None


def get_rick_client() -> RickLLMClient:
    """Get or create Rick LLM client (singleton pattern)"""
    global _rick_client
    if _rick_client is None:
        _rick_client = RickLLMClient()
    return _rick_client


def reset_rick_client():
    """Reset the Rick client (useful for testing)"""
    global _rick_client
    _rick_client = None


if __name__ == "__main__":
    # Test the LLM client
    print("\n🤖 RICK LLM Client Test\n" + "=" * 50)
    
    rick = get_rick_client()
    
    print(f"\n📡 Ollama Health Check:")
    health = rick.health_check()
    for key, value in health.items():
        print(f"  {key}: {value}")
    
    if rick.is_available:
        print(f"\n✅ Rick LLM is ready for queries")
        
        # Test basic query
        print(f"\n🔍 Testing basic query...")
        response = rick.query("What is your primary trading strategy?")
        print(f"Response: {response.content[:200]}...")
        
    else:
        print(f"\n❌ Rick LLM is not available - start Ollama with: ollama serve")
