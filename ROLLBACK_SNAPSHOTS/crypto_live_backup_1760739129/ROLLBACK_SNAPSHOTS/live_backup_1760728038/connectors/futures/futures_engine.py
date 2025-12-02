import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

from .venue_manager import VenueManager
from .leverage_calculator import LeverageCalculator

logger = logging.getLogger(__name__)

class FuturesEngine:
    """Main futures trading engine"""
    
    def __init__(self, max_positions=8, max_leverage=25, risk_per_trade=0.02):
        self.max_positions = max_positions
        self.max_leverage = max_leverage
        self.risk_per_trade = risk_per_trade
        
        # Initialize components
        self.venue_manager = VenueManager()
        self.leverage_calc = LeverageCalculator(max_leverage, risk_per_trade)
        
        # State tracking
        self.active_positions = {}
        self.position_history = []
        self.emergency_mode = False
        
    def evaluate_futures_signal(self, pair: str, signal: Dict, market_data: Dict) -> Optional[Dict]:
        """Evaluate a futures trading signal and prepare execution plan"""
        
        # Check if we can take more positions
        if len(self.active_positions) >= self.max_positions:
            return None
            
        # Check emergency mode
        if self.emergency_mode:
            return None
            
        # Extract signal data
        confidence = signal.get('confidence', 0.5)
        direction = signal.get('direction', 'long')
        entry_price = market_data.get('price', 0)
        
        if confidence < 0.6:  # Minimum confidence threshold for futures
            return None
            
        # Get best venue for this pair
        required_leverage = min(signal.get('suggested_leverage', 5), self.max_leverage)
        best_venue = self.venue_manager.get_best_venue_for_pair(pair, required_leverage)
        
        if not best_venue:
            return None
            
        venue_info = self.venue_manager.get_venue_info(best_venue)
        
        # Calculate optimal leverage and position size
        price_history = market_data.get('price_history', [entry_price])
        account_balance = market_data.get('account_balance', 10000)
        
        leverage_result = self.leverage_calc.calculate_leverage(
            pair=pair,
            confidence=confidence,
            price_history=price_history,
            account_balance=account_balance,
            current_positions=len(self.active_positions)
        )
        
        # Validate against venue limits
        max_venue_leverage = venue_info['max_leverage']
        final_leverage = self.leverage_calc.validate_leverage(
            leverage_result['leverage'], 
            max_venue_leverage
        )
        
        execution_plan = {
            'pair': pair,
            'direction': direction,
            'venue': best_venue,
            'venue_info': venue_info,
            'leverage': final_leverage,
            'position_size': leverage_result['position_size'],
            'entry_price': entry_price,
            'confidence': confidence,
            'risk_amount': leverage_result['risk_amount'],
            'timestamp': datetime.utcnow().isoformat(),
            'signal_id': signal.get('id', f"{pair}_{int(time.time())}")
        }
        
        return execution_plan
        
    def execute_futures_position(self, execution_plan: Dict) -> bool:
        """Execute a futures position (simulation for now)"""
        
        position_id = f"{execution_plan['pair']}_{execution_plan['venue']}_{int(time.time())}"
        
        # Store in active positions
        self.active_positions[position_id] = {
            **execution_plan,
            'position_id': position_id,
            'status': 'open',
            'opened_at': datetime.utcnow().isoformat(),
            'unrealized_pnl': 0.0
        }
        
        # Log execution
        execution_log = {
            'position_id': position_id,
            'timestamp': datetime.utcnow().isoformat(),
            'action': 'open_position',
            'pair': execution_plan['pair'],
            'direction': execution_plan['direction'],
            'venue': execution_plan['venue'],
            'leverage': execution_plan['leverage'],
            'size': execution_plan['position_size']
        }
        
        with open('logs/futures_executions.jsonl', 'a') as f:
            f.write(json.dumps(execution_log) + '\n')
            
        return True
        
    def close_position(self, position_id: str, reason: str = "manual"):
        """Close a futures position"""
        if position_id not in self.active_positions:
            return False
            
        position = self.active_positions[position_id]
        
        # Move to history
        self.position_history.append({
            **position,
            'closed_at': datetime.utcnow().isoformat(),
            'close_reason': reason
        })
        
        # Remove from active
        del self.active_positions[position_id]
        
        return True
        
    def get_status_report(self) -> Dict:
        """Get comprehensive status report"""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'active_positions': len(self.active_positions),
            'max_positions': self.max_positions,
            'emergency_mode': self.emergency_mode,
            'available_venues': self.venue_manager.get_available_venues()
        }
        
    def emergency_close_all(self, reason: str = "emergency"):
        """Emergency close all positions"""
        position_ids = list(self.active_positions.keys())
        for position_id in position_ids:
            self.close_position(position_id, f"emergency_{reason}")
            
        self.emergency_mode = True
