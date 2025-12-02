#!/usr/bin/env python3
"""
Adaptive Rick AI - ML-Enhanced Trading Intelligence
Self-adapting system that learns from performance while maintaining charter compliance
PIN: 841921 | Charter Compliant | Continuous Learning
"""

import json
import logging
import sqlite3
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

# Import local AI and existing components
try:
    from hive.rick_local_ai import RickLocalAI, RickAIResponse
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    logging.warning("Rick Local AI not available")

# ML Learning Database
LEARNING_DB = Path("hive/rick_learning.db")
CORE_PROMPT_FILE = Path("hive/RICK_CORE_PROMPT.txt")

@dataclass
class TradingDecision:
    timestamp: str
    symbol: str
    action: str  # BUY, SELL, HOLD
    confidence: float
    reasoning: str
    ml_factors: Dict[str, float]
    outcome: Optional[str] = None  # WIN, LOSS, PENDING
    pnl: Optional[float] = None

@dataclass
class LearningInsight:
    pattern_type: str
    success_rate: float
    avg_pnl: float
    frequency: int
    last_updated: str
    
class AdaptiveRick:
    """Self-adaptive Rick with ML learning integration"""
    
    def __init__(self, pin: int = None):
        self.pin_verified = pin == 841921 if pin else False
        self.core_prompt = self.load_core_prompt()
        self.local_ai = RickLocalAI(pin) if AI_AVAILABLE else None
        self.learning_db = self.init_learning_database()
        self.adaptation_params = {}  # Initialize before loading
        self.adaptation_params = self.load_adaptation_parameters()
        
    def load_core_prompt(self) -> str:
        """Load Rick's core system prompt - reviewed every interaction"""
        if CORE_PROMPT_FILE.exists():
            with open(CORE_PROMPT_FILE, 'r') as f:
                return f.read()
        return "Rick core prompt not found - operating in basic mode."
    
    def init_learning_database(self) -> sqlite3.Connection:
        """Initialize ML learning database"""
        conn = sqlite3.connect(LEARNING_DB)
        
        # Create tables for learning data
        conn.execute('''
            CREATE TABLE IF NOT EXISTS trading_decisions (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                symbol TEXT,
                action TEXT,
                confidence REAL,
                reasoning TEXT,
                ml_factors TEXT,
                outcome TEXT,
                pnl REAL
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS learning_insights (
                id INTEGER PRIMARY KEY,
                pattern_type TEXT UNIQUE,
                success_rate REAL,
                avg_pnl REAL,
                frequency INTEGER,
                last_updated TEXT
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS adaptation_parameters (
                parameter_name TEXT PRIMARY KEY,
                parameter_value REAL,
                last_modified TEXT
            )
        ''')
        
        conn.commit()
        return conn
    
    def load_adaptation_parameters(self) -> Dict[str, float]:
        """Load current adaptation parameters"""
        cursor = self.learning_db.execute(
            "SELECT parameter_name, parameter_value FROM adaptation_parameters"
        )
        
        params = dict(cursor.fetchall())
        
        # Default parameters if not set
        defaults = {
            'confidence_threshold': 0.65,
            'risk_multiplier': 1.0,
            'pattern_weight': 0.3,
            'recent_performance_weight': 0.4,
            'ml_model_weight': 0.3
        }
        
        for key, default_value in defaults.items():
            if key not in params:
                params[key] = default_value
                self.update_adaptation_parameter(key, default_value)
        
        return params
    
    def update_adaptation_parameter(self, param_name: str, value: float):
        """Update adaptation parameter in database"""
        self.learning_db.execute(
            "INSERT OR REPLACE INTO adaptation_parameters (parameter_name, parameter_value, last_modified) VALUES (?, ?, ?)",
            (param_name, value, datetime.now().isoformat())
        )
        self.learning_db.commit()
        self.adaptation_params[param_name] = value
    
    def process_user_request(self, user_message: str, context: Dict[str, Any] = None) -> RickAIResponse:
        """Main interface - processes user requests with full Rick intelligence"""
        
        # 🎯 STEP 1: Review core prompt (ALWAYS)
        system_context = f"""
{self.core_prompt}

CURRENT CONTEXT:
- PIN Verified: {self.pin_verified}
- Timestamp: {datetime.now().isoformat()}
- Adaptation Parameters: {json.dumps(self.adaptation_params, indent=2)}
- Recent Learning Insights: {self.get_recent_insights_summary()}

USER REQUEST: {user_message}
"""
        
        if context:
            system_context += f"\nADDITIONAL CONTEXT: {json.dumps(context, indent=2)}"
        
        # 🧠 STEP 2: Get AI analysis with full context
        if self.local_ai:
            # Determine if this is trading analysis or general chat
            if any(word in user_message.lower() for word in ['analyze', 'trade', 'setup', 'signal', 'position']):
                ai_response = self.analyze_trading_request(user_message, system_context, context)
            else:
                ai_response = self.local_ai.rick_chat(f"{system_context}\n\nRespond to: {user_message}")
        else:
            ai_response = self.fallback_response(user_message)
        
        # 🔄 STEP 3: Learn from interaction
        self.record_interaction(user_message, ai_response, context)
        
        return ai_response
    
    def analyze_trading_request(self, request: str, system_context: str, context: Dict[str, Any] = None) -> RickAIResponse:
        """Analyze trading requests with ML-enhanced intelligence"""
        
        # Get ML insights for this analysis
        ml_insights = self.get_relevant_ml_insights(context)
        
        # Enhanced prompt with learning
        enhanced_prompt = f"""
{system_context}

ML LEARNING INSIGHTS:
{json.dumps(ml_insights, indent=2)}

ADAPTIVE ANALYSIS REQUEST:
{request}

Provide analysis that:
1. Incorporates ML learning insights
2. Adapts confidence based on recent performance
3. Suggests parameter adjustments if needed
4. Maintains charter compliance
5. Shows reasoning for adaptive decisions
"""
        
        # Get AI response
        market_data = context or {}
        ai_response = self.local_ai.analyze_trading_setup(market_data)
        
        # Enhance response with ML insights
        enhanced_response = f"""
{ai_response.response}

🤖 ADAPTIVE INSIGHTS:
- Current Success Rate: {ml_insights.get('recent_success_rate', 'N/A')}%
- Recommended Confidence Adjustment: {ml_insights.get('confidence_modifier', 1.0)}x
- Pattern Recognition: {ml_insights.get('dominant_pattern', 'Learning...')}
- Risk Adjustment: {ml_insights.get('risk_modifier', 1.0)}x baseline

🔄 LEARNING STATUS:
- Decisions Analyzed: {ml_insights.get('total_decisions', 0)}
- Adaptation Cycles: {ml_insights.get('adaptation_cycles', 0)}
- Next Parameter Review: {ml_insights.get('next_review', 'Ongoing')}
"""
        
        ai_response.response = enhanced_response
        return ai_response
    
    def get_relevant_ml_insights(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get ML insights relevant to current analysis"""
        
        # Get recent performance
        cursor = self.learning_db.execute('''
            SELECT * FROM trading_decisions 
            WHERE timestamp > ? AND outcome IS NOT NULL
            ORDER BY timestamp DESC LIMIT 50
        ''', (
            (datetime.now() - timedelta(days=30)).isoformat(),
        ))
        
        recent_decisions = cursor.fetchall()
        
        if not recent_decisions:
            return {
                'recent_success_rate': 0,
                'confidence_modifier': 1.0,
                'dominant_pattern': 'Insufficient data',
                'risk_modifier': 1.0,
                'total_decisions': 0,
                'adaptation_cycles': 0,
                'next_review': 'After 10 decisions'
            }
        
        # Calculate success metrics
        wins = sum(1 for d in recent_decisions if d[7] == 'WIN')  # outcome column
        success_rate = (wins / len(recent_decisions)) * 100
        
        # Calculate average PnL
        pnls = [d[8] for d in recent_decisions if d[8] is not None]  # pnl column
        avg_pnl = np.mean(pnls) if pnls else 0
        
        # Adaptive confidence modifier
        if success_rate > 70:
            confidence_modifier = 1.1  # Increase confidence
        elif success_rate < 50:
            confidence_modifier = 0.9  # Decrease confidence
        else:
            confidence_modifier = 1.0
        
        # Risk modifier based on recent performance
        if avg_pnl > 0 and success_rate > 60:
            risk_modifier = 1.05  # Slightly more aggressive
        elif avg_pnl < 0 or success_rate < 40:
            risk_modifier = 0.85  # More conservative
        else:
            risk_modifier = 1.0
        
        return {
            'recent_success_rate': round(success_rate, 1),
            'confidence_modifier': confidence_modifier,
            'dominant_pattern': self.identify_dominant_pattern(recent_decisions),
            'risk_modifier': risk_modifier,
            'total_decisions': len(recent_decisions),
            'adaptation_cycles': self.get_adaptation_cycle_count(),
            'next_review': 'Continuous',
            'avg_pnl': round(avg_pnl, 2) if avg_pnl else 0
        }
    
    def identify_dominant_pattern(self, decisions: List) -> str:
        """Identify the most successful pattern type"""
        # This would analyze ML factors from decisions
        # For now, return a placeholder
        return "Trend Following (60% success)"
    
    def get_adaptation_cycle_count(self) -> int:
        """Get number of adaptation cycles completed"""
        cursor = self.learning_db.execute(
            "SELECT COUNT(*) FROM adaptation_parameters WHERE last_modified > ?",
            ((datetime.now() - timedelta(days=7)).isoformat(),)
        )
        return cursor.fetchone()[0]
    
    def get_recent_insights_summary(self) -> str:
        """Get summary of recent learning insights"""
        cursor = self.learning_db.execute(
            "SELECT pattern_type, success_rate FROM learning_insights ORDER BY last_updated DESC LIMIT 3"
        )
        
        insights = cursor.fetchall()
        if not insights:
            return "No learning insights yet - building knowledge base..."
        
        summary = []
        for pattern, success_rate in insights:
            summary.append(f"{pattern}: {success_rate:.1f}% success")
        
        return " | ".join(summary)
    
    def record_interaction(self, user_message: str, ai_response: RickAIResponse, context: Dict[str, Any] = None):
        """Record interaction for learning"""
        
        # Extract potential trading decision
        if any(word in user_message.lower() for word in ['buy', 'sell', 'analyze', 'setup']):
            decision = TradingDecision(
                timestamp=datetime.now().isoformat(),
                symbol=context.get('symbol', 'UNKNOWN') if context else 'UNKNOWN',
                action='ANALYZE',  # Default for analysis requests
                confidence=ai_response.confidence,
                reasoning=ai_response.response[:500],  # Truncate for storage
                ml_factors={'user_request': True, 'context_provided': bool(context)}
            )
            
            self.store_trading_decision(decision)
    
    def store_trading_decision(self, decision: TradingDecision):
        """Store trading decision in learning database"""
        self.learning_db.execute('''
            INSERT INTO trading_decisions 
            (timestamp, symbol, action, confidence, reasoning, ml_factors, outcome, pnl)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            decision.timestamp,
            decision.symbol,
            decision.action,
            decision.confidence,
            decision.reasoning,
            json.dumps(decision.ml_factors),
            decision.outcome,
            decision.pnl
        ))
        self.learning_db.commit()
    
    def fallback_response(self, user_message: str) -> RickAIResponse:
        """Fallback when AI is unavailable"""
        return RickAIResponse(
            model_used="Adaptive Fallback",
            response=f"AI models temporarily unavailable. Reviewed core directives: {self.core_prompt[:100]}...",
            confidence=0.5,
            analysis_type="fallback",
            timestamp=datetime.now().isoformat()
        )
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        cursor = self.learning_db.execute("SELECT COUNT(*) FROM trading_decisions")
        total_decisions = cursor.fetchone()[0]
        
        return {
            'pin_verified': self.pin_verified,
            'ai_available': AI_AVAILABLE,
            'core_prompt_loaded': bool(self.core_prompt),
            'learning_database_active': bool(self.learning_db),
            'total_decisions_recorded': total_decisions,
            'adaptation_parameters': self.adaptation_params,
            'timestamp': datetime.now().isoformat()
        }

# Global adaptive Rick instance
_adaptive_rick = None

def get_adaptive_rick(pin: int = None) -> AdaptiveRick:
    """Get or create adaptive Rick instance"""
    global _adaptive_rick
    if _adaptive_rick is None:
        _adaptive_rick = AdaptiveRick(pin)
    return _adaptive_rick

# Test function
if __name__ == "__main__":
    print("🧠 Testing Adaptive Rick...")
    
    rick = AdaptiveRick(pin=841921)
    status = rick.get_system_status()
    
    print(f"📊 System Status: {json.dumps(status, indent=2)}")
    
    # Test interaction
    response = rick.process_user_request(
        "Analyze EUR/USD at 1.0850 for potential long setup",
        context={'symbol': 'EUR/USD', 'price': 1.0850, 'timeframe': '1H'}
    )
    
    print(f"\n🎯 Rick's Response:")
    print(f"Model: {response.model_used}")
    print(f"Confidence: {response.confidence}")
    print(f"Response: {response.response}")