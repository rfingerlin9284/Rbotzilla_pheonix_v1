#!/usr/bin/env python3
"""
Rick Local AI Connector - Ollama Integration
Connects Rick to your local Llama 3.1 8B and CodeLlama 13B models
PIN: 841921 | Charter Compliant | LOCAL AI POWER
"""

import json
import requests
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass

# Ollama API Configuration
OLLAMA_BASE_URL = "http://127.0.0.1:11434"
MODELS = {
    "trading": "llama3.1:8b",        # General trading analysis
    "code": "codellama:13b-instruct"  # Code and pattern analysis
}

@dataclass
class RickAIResponse:
    model_used: str
    response: str
    confidence: float
    analysis_type: str
    timestamp: str

class RickLocalAI:
    """Rick's Local AI Brain using Ollama"""
    
    def __init__(self, pin: int = None):
        self.pin_verified = pin == 841921 if pin else False
        self.available_models = []
        self.check_ollama_status()
        
    def check_ollama_status(self) -> bool:
        """Check if Ollama is running and models are available"""
        try:
            response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
            if response.status_code == 200:
                models_data = response.json()
                self.available_models = [model['name'] for model in models_data.get('models', [])]
                logging.info(f"✅ Ollama connected. Available models: {self.available_models}")
                return True
        except Exception as e:
            logging.error(f"❌ Ollama connection failed: {e}")
        return False
    
    def query_model(self, prompt: str, model_name: str, context: str = "") -> Optional[str]:
        """Send query to specific Ollama model"""
        try:
            full_prompt = f"{context}\n\n{prompt}" if context else prompt
            
            payload = {
                "model": model_name,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            }
            
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                logging.error(f"❌ Model query failed: {response.status_code}")
        except Exception as e:
            logging.error(f"❌ Model query error: {e}")
        return None
    
    def analyze_trading_setup(self, market_data: Dict[str, Any]) -> RickAIResponse:
        """Use Llama 3.1 8B for trading analysis"""
        context = f"""You are Rick, a street-smart trading AI assistant. Analyze the following market setup:
Symbol: {market_data.get('symbol', 'Unknown')}
Current Price: {market_data.get('price', 'Unknown')}
Timeframe: {market_data.get('timeframe', '1H')}
"""
        
        prompt = f"""
        Analyze this trading setup and provide:
        1. Signal direction (BUY/SELL/NEUTRAL)
        2. Confidence level (1-10)
        3. Key factors supporting your analysis
        4. Risk management suggestions
        
        Keep your response concise and actionable.
        """
        
        response = self.query_model(prompt, MODELS["trading"], context)
        
        if response:
            return RickAIResponse(
                model_used="Llama 3.1 8B",
                response=response,
                confidence=0.8,  # Could parse from response
                analysis_type="trading",
                timestamp=datetime.now().isoformat()
            )
        
        return self._fallback_response("trading")
    
    def analyze_code_pattern(self, code: str, description: str = "") -> RickAIResponse:
        """Use CodeLlama 13B for code analysis"""
        context = """You are Rick, an expert trading system analyst. Review the following code for:
- Logic correctness
- Potential bugs
- Performance optimizations
- Trading strategy effectiveness"""
        
        prompt = f"""
        {description}
        
        Code to analyze:
        ```python
        {code}
        ```
        
        Provide analysis covering:
        1. Code quality and potential issues
        2. Trading logic effectiveness
        3. Suggestions for improvement
        4. Risk factors to consider
        """
        
        response = self.query_model(prompt, MODELS["code"], context)
        
        if response:
            return RickAIResponse(
                model_used="CodeLlama 13B",
                response=response,
                confidence=0.85,
                analysis_type="code",
                timestamp=datetime.now().isoformat()
            )
        
        return self._fallback_response("code")
    
    def rick_chat(self, message: str) -> RickAIResponse:
        """General chat with Rick using best available model"""
        context = """You are Rick, a street-smart AI trading assistant with personality. 
Respond in a casual, confident tone while being helpful and knowledgeable about trading."""
        
        # Choose model based on message content
        model = MODELS["code"] if any(word in message.lower() for word in ['code', 'debug', 'python', 'strategy', 'algorithm']) else MODELS["trading"]
        
        response = self.query_model(message, model, context)
        
        if response:
            model_name = "CodeLlama 13B" if model == MODELS["code"] else "Llama 3.1 8B"
            return RickAIResponse(
                model_used=model_name,
                response=response,
                confidence=0.8,
                analysis_type="chat",
                timestamp=datetime.now().isoformat()
            )
        
        return self._fallback_response("chat")
    
    def _fallback_response(self, analysis_type: str) -> RickAIResponse:
        """Fallback response when AI is unavailable"""
        fallback_messages = {
            "trading": "Local AI models are currently unavailable. Using basic analysis mode.",
            "code": "Code analysis AI is offline. Please check your code manually.",
            "chat": "Hey! My AI brain is taking a quick break. Try again in a moment!"
        }
        
        return RickAIResponse(
            model_used="Fallback",
            response=fallback_messages.get(analysis_type, "AI unavailable"),
            confidence=0.1,
            analysis_type=analysis_type,
            timestamp=datetime.now().isoformat()
        )
    
    def get_status(self) -> Dict[str, Any]:
        """Get Rick's AI status"""
        return {
            "pin_verified": self.pin_verified,
            "ollama_connected": bool(self.available_models),
            "available_models": self.available_models,
            "trading_model": MODELS["trading"],
            "code_model": MODELS["code"],
            "timestamp": datetime.now().isoformat()
        }

# Global Rick AI instance
_rick_ai = None

def get_rick_local_ai(pin: int = None) -> RickLocalAI:
    """Get or create Rick's local AI instance"""
    global _rick_ai
    if _rick_ai is None:
        _rick_ai = RickLocalAI(pin)
    return _rick_ai

# Test function
if __name__ == "__main__":
    print("🧠 Testing Rick's Local AI...")
    
    rick = RickLocalAI(pin=841921)
    status = rick.get_status()
    
    print(f"📊 Status: {json.dumps(status, indent=2)}")
    
    if rick.available_models:
        # Test trading analysis
        print("\n🎯 Testing trading analysis...")
        result = rick.analyze_trading_setup({
            "symbol": "EUR/USD",
            "price": 1.0850,
            "timeframe": "1H"
        })
        print(f"Model: {result.model_used}")
        print(f"Response: {result.response[:200]}...")
        
        # Test chat
        print("\n💬 Testing chat...")
        chat_result = rick.rick_chat("Hey Rick, what's your take on the current market?")
        print(f"Model: {chat_result.model_used}")
        print(f"Response: {chat_result.response[:200]}...")
    else:
        print("❌ No models available for testing")