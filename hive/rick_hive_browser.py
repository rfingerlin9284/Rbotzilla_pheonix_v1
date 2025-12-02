#!/usr/bin/env python3
"""
rick_hive_browser.py - Rick with Browser-Based Hive Mind
PIN 841921 Approved | Charter Compliant | NO API KEYS NEEDED

Integrates browser_ai_connector with Rick's existing hive mind system.
Provides multi-AI consensus without requiring API keys.

Usage:
    from hive.rick_hive_browser import get_hive_browser_mind
    
    hive = get_hive_browser_mind(pin=841921)
    analysis = hive.consult_hive("Analyze EUR/USD setup at 1.0850")
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# Import existing hive mind
try:
    from hive.rick_hive_mind import RickHiveMind, AIAgent, SignalStrength
    HIVE_MIND_AVAILABLE = True
except ImportError:
    HIVE_MIND_AVAILABLE = False
    logging.warning("rick_hive_mind not available")

# Import browser connector
try:
    from hive.browser_ai_connector import BrowserAIConnector, AIProvider, AIResponse
    BROWSER_CONNECTOR_AVAILABLE = True
except ImportError:
    BROWSER_CONNECTOR_AVAILABLE = False
    logging.warning("browser_ai_connector not available")

# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.resolve())
LOGS_DIR = PROJECT_ROOT / "pre_upgrade" / "headless" / "logs"

@dataclass
class HiveConsensus:
    """Aggregated response from all AI providers."""
    query: str
    responses: List[AIResponse]
    consensus_text: str
    avg_confidence: float
    total_latency_ms: int
    providers_count: int
    timestamp: datetime
    
    def to_dict(self) -> Dict:
        return {
            "query": self.query,
            "responses": [
                {
                    "provider": r.provider.value,
                    "response": r.response,
                    "confidence": r.confidence,
                    "latency_ms": r.latency_ms
                }
                for r in self.responses
            ],
            "consensus": self.consensus_text,
            "avg_confidence": self.avg_confidence,
            "total_latency_ms": self.total_latency_ms,
            "providers_count": self.providers_count,
            "timestamp": self.timestamp.isoformat()
        }

# ============================================================================
# RICK HIVE BROWSER MIND
# ============================================================================

class RickHiveBrowserMind:
    """
    Enhanced hive mind that uses browser automation to consult
    multiple AI services (ChatGPT, Grok, DeepSeek, GitHub Copilot)
    without requiring API keys.
    """
    
    def __init__(self, pin: int = None, headless: bool = True):
        self.pin_verified = pin == 841921 if pin else False
        self.headless = headless
        
        # Initialize browser connector
        if BROWSER_CONNECTOR_AVAILABLE:
            self.browser_connector = BrowserAIConnector(headless=headless)
            self.browser_enabled = True
        else:
            self.browser_connector = None
            self.browser_enabled = False
            logging.warning("Browser connector not available - install selenium")
        
        # Initialize traditional hive mind as fallback
        if HIVE_MIND_AVAILABLE:
            self.hive_mind = RickHiveMind(pin=pin)
            self.hive_available = True
        else:
            self.hive_mind = None
            self.hive_available = False
        
        # Provider weights for consensus
        self.provider_weights = {
            AIProvider.CHATGPT: 0.35,
            AIProvider.GROK: 0.25,
            AIProvider.DEEPSEEK: 0.30,
            AIProvider.GITHUB_COPILOT: 0.10
        }
    
    def _get_system_context(self) -> str:
        """Build system context from real data."""
        context_parts = []
        
        # Read mode
        try:
            toggle_file = PROJECT_ROOT / ".upgrade_toggle"
            if toggle_file.exists():
                mode = toggle_file.read_text().strip()
                context_parts.append(f"Mode: {mode}")
        except:
            pass
        
        # Read latest narration
        try:
            narration_file = LOGS_DIR / "narration.jsonl"
            if narration_file.exists():
                with open(narration_file, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        try:
                            latest = json.loads(lines[-1])
                            context_parts.append(f"Latest: {latest.get('text', 'N/A')}")
                        except:
                            pass
        except:
            pass
        
        # Read P&L
        try:
            pnl_file = LOGS_DIR / "pnl.jsonl"
            if pnl_file.exists():
                with open(pnl_file, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        try:
                            latest_pnl = json.loads(lines[-1])
                            net = latest_pnl.get('net_pnl', 0)
                            context_parts.append(f"P&L: ${net:.2f}")
                        except:
                            pass
        except:
            pass
        
        return " | ".join(context_parts) if context_parts else "No context available"
    
    def consult_hive(self, query: str, include_context: bool = True) -> HiveConsensus:
        """
        Consult the hive mind by querying multiple AI providers.
        
        Args:
            query: The question or analysis request
            include_context: Whether to include RICK system context
        
        Returns:
            HiveConsensus with aggregated responses
        """
        if not self.pin_verified:
            logging.warning("PIN not verified - returning fallback response")
            return HiveConsensus(
                query=query,
                responses=[],
                consensus_text="PIN 841921 required for hive mind access",
                avg_confidence=0.0,
                total_latency_ms=0,
                providers_count=0,
                timestamp=datetime.now()
            )
        
        if not self.browser_enabled:
            logging.warning("Browser connector not available")
            return HiveConsensus(
                query=query,
                responses=[],
                consensus_text="Browser automation not available - install selenium and webdriver-manager",
                avg_confidence=0.0,
                total_latency_ms=0,
                providers_count=0,
                timestamp=datetime.now()
            )
        
        # Build full query with context
        full_query = query
        if include_context:
            context = self._get_system_context()
            full_query = f"{query}\n\nSystem Context: {context}"
        
        # Query all providers
        start_time = datetime.now()
        responses = self.browser_connector.query_all(full_query)
        
        # Calculate metrics
        total_latency = sum(r.latency_ms for r in responses)
        avg_confidence = sum(r.confidence for r in responses) / len(responses) if responses else 0.0
        
        # Build consensus text
        consensus_parts = []
        for response in responses:
            if response.response and not response.error:
                consensus_parts.append(f"[{response.provider.value.upper()}] {response.response[:200]}...")
        
        consensus_text = "\n\n".join(consensus_parts) if consensus_parts else "No valid responses received"
        
        return HiveConsensus(
            query=query,
            responses=responses,
            consensus_text=consensus_text,
            avg_confidence=avg_confidence,
            total_latency_ms=total_latency,
            providers_count=len(responses),
            timestamp=datetime.now()
        )
    
    def query_single_provider(self, provider: AIProvider, query: str) -> AIResponse:
        """Query a single AI provider."""
        if not self.pin_verified:
            return AIResponse(
                provider=provider,
                query=query,
                response="",
                confidence=0.0,
                latency_ms=0,
                timestamp=datetime.now(),
                error="PIN 841921 required"
            )
        
        if not self.browser_enabled:
            return AIResponse(
                provider=provider,
                query=query,
                response="",
                confidence=0.0,
                latency_ms=0,
                timestamp=datetime.now(),
                error="Browser connector not available"
            )
        
        if provider == AIProvider.CHATGPT:
            return self.browser_connector.query_chatgpt(query)
        elif provider == AIProvider.GROK:
            return self.browser_connector.query_grok(query)
        elif provider == AIProvider.DEEPSEEK:
            return self.browser_connector.query_deepseek(query)
        elif provider == AIProvider.GITHUB_COPILOT:
            return self.browser_connector.query_github_copilot(query)
        else:
            return AIResponse(
                provider=provider,
                query=query,
                response="",
                confidence=0.0,
                latency_ms=0,
                timestamp=datetime.now(),
                error=f"Unknown provider: {provider}"
            )
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all AI providers."""
        if not self.browser_enabled:
            return {"error": "Browser connector not available"}
        
        return {
            "browser_enabled": self.browser_enabled,
            "hive_available": self.hive_available,
            "pin_verified": self.pin_verified,
            "providers": {
                provider.value: {
                    "connected": provider in self.browser_connector.sessions_active,
                    "active": self.browser_connector.sessions_active.get(provider, False),
                    "weight": self.provider_weights.get(provider, 0.0)
                }
                for provider in AIProvider
            }
        }
    
    def cleanup(self):
        """Close all browser sessions."""
        if self.browser_connector:
            self.browser_connector.cleanup()

# ============================================================================
# FACTORY FUNCTION
# ============================================================================

def get_hive_browser_mind(pin: int = None, headless: bool = True) -> RickHiveBrowserMind:
    """
    Factory function to create hive mind instance.
    
    Args:
        pin: Authorization PIN (841921)
        headless: Run browsers in headless mode (True for production)
    
    Returns:
        RickHiveBrowserMind instance
    """
    return RickHiveBrowserMind(pin=pin, headless=headless)

# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("🧠 Rick Hive Browser Mind Test")
    print("=" * 60)
    
    # Create hive mind
    hive = get_hive_browser_mind(pin=841921, headless=False)
    
    try:
        # Test status
        print("\n📊 Provider Status:")
        status = hive.get_provider_status()
        print(json.dumps(status, indent=2))
        
        # Test single query
        print("\n💬 Testing single provider (ChatGPT):")
        response = hive.query_single_provider(
            AIProvider.CHATGPT,
            "What is the current market sentiment for EUR/USD? Answer in one sentence."
        )
        print(f"Response: {response.response}")
        print(f"Confidence: {response.confidence}")
        print(f"Latency: {response.latency_ms}ms")
        
        # Test hive consensus
        print("\n🧠 Testing hive consensus (all providers):")
        consensus = hive.consult_hive(
            "Analyze EUR/USD at 1.0850 for a potential long entry. Consider RR ≥3.2:1 requirement."
        )
        print(f"\nQuery: {consensus.query}")
        print(f"Providers: {consensus.providers_count}")
        print(f"Avg Confidence: {consensus.avg_confidence:.2f}")
        print(f"Total Latency: {consensus.total_latency_ms}ms")
        print(f"\nConsensus:")
        print(consensus.consensus_text)
    
    finally:
        print("\n🧹 Cleaning up...")
        hive.cleanup()
        print("✅ Test complete")
