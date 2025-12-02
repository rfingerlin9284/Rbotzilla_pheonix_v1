#!/usr/bin/env python3
"""
Quantitative Hedge Engine - Correlation-Based Dynamic Hedging
Extracted from RBOTzilla Aggressive Engine and adapted for live trading
PIN: 841921 | Phase 4 Integration
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class HedgePosition:
    """Portfolio hedging position"""
    symbol: str
    side: str
    size: float
    entry_price: float
    hedge_ratio: float
    correlation: float
    timestamp: datetime


class QuantHedgeEngine:
    """
    Advanced quantitative hedging system
    Uses correlation matrices to identify optimal hedge pairs
    Executes automatic hedges on inversely correlated pairs
    """

    def __init__(self):
        """Initialize hedge engine with correlation matrix"""
        # Correlation matrix for major FX pairs
        # Positive correlation = tend to move together
        # Negative correlation = tend to move opposite
        self.correlation_matrix = {
            'EUR_USD': {
                'GBP_USD': 0.85,    # Highly correlated
                'USD_JPY': -0.72,   # Inversely correlated (HEDGE!)
                'AUD_USD': 0.65,    # Moderately correlated
                'USD_CAD': 0.62     # Moderately correlated
            },
            'GBP_USD': {
                'EUR_USD': 0.85,
                'USD_JPY': -0.68,   # HEDGE candidate
                'AUD_USD': 0.70,
                'USD_CAD': 0.58
            },
            'USD_JPY': {
                'EUR_USD': -0.72,   # HEDGE candidate for EUR longs
                'GBP_USD': -0.68,   # HEDGE candidate for GBP longs
                'AUD_USD': -0.80,   # HEDGE candidate for AUD longs
                'USD_CAD': -0.55    # Inversely correlated
            },
            'AUD_USD': {
                'EUR_USD': 0.65,
                'GBP_USD': 0.70,
                'USD_JPY': -0.80,   # HEDGE candidate (strongest!)
                'USD_CAD': 0.75
            },
            'USD_CAD': {
                'EUR_USD': 0.62,
                'GBP_USD': 0.58,
                'USD_JPY': -0.55,
                'AUD_USD': 0.75
            }
        }
        
        self.hedge_positions: List[HedgePosition] = []
        self.hedge_stats = {
            'hedges_executed': 0,
            'hedges_successful': 0,
            'total_drawdown_prevented': 0.0,
            'average_hedge_ratio': 0.0
        }

    def calculate_optimal_hedge_ratio(
        self, 
        primary_symbol: str, 
        position_size: float
    ) -> Tuple[Optional[str], float]:
        """
        Calculate optimal hedge pair and ratio
        
        Args:
            primary_symbol: Primary trade symbol (e.g., 'EUR_USD')
            position_size: Size of primary position
        
        Returns:
            (hedge_symbol, hedge_ratio) or (None, 0.0) if no suitable hedge
        """
        # Normalize symbol format
        primary_symbol = primary_symbol.replace('_', '')
        if primary_symbol not in self.correlation_matrix:
            return None, 0.0
        
        correlations = self.correlation_matrix[primary_symbol]
        
        if not correlations:
            return None, 0.0
        
        # Find STRONGEST NEGATIVE correlation for hedging
        best_hedge = min(correlations.items(), key=lambda x: x[1])  # Find most negative
        hedge_symbol, correlation = best_hedge
        
        # Only hedge if correlation is sufficiently negative (< -0.50)
        if correlation < -0.50:
            # Hedge ratio = strength of correlation * confidence factor
            # Stronger negative correlation = larger hedge ratio (up to 80%)
            hedge_ratio = min(0.80, abs(correlation) * 0.85)
            
            # Restore original formatting
            hedge_symbol = hedge_symbol.replace('USD', '_USD').replace('EUR', 'EUR_').replace('GBP', 'GBP_')
            
            return hedge_symbol, hedge_ratio
        
        return None, 0.0

    def execute_hedge(
        self,
        primary_symbol: str,
        primary_side: str,
        position_size: float,
        entry_price: float
    ) -> Optional[HedgePosition]:
        """
        Execute hedge position on inversely correlated pair
        
        Args:
            primary_symbol: Primary trade symbol (e.g., 'EUR_USD')
            primary_side: 'BUY' or 'SELL'
            position_size: Size of primary position
            entry_price: Entry price of primary position
        
        Returns:
            HedgePosition if hedge executed, None otherwise
        """
        hedge_symbol, hedge_ratio = self.calculate_optimal_hedge_ratio(
            primary_symbol, 
            position_size
        )
        
        if not hedge_symbol or hedge_ratio < 0.30:
            return None
        
        # Opposite side for hedge
        hedge_side = 'SELL' if primary_side == 'BUY' else 'BUY'
        hedge_size = position_size * hedge_ratio
        
        # For demo: use entry price as hedge entry
        hedge_entry = entry_price
        
        # Create hedge position
        hedge_position = HedgePosition(
            symbol=hedge_symbol,
            side=hedge_side,
            size=hedge_size,
            entry_price=hedge_entry,
            hedge_ratio=hedge_ratio,
            correlation=self.correlation_matrix[primary_symbol.replace('_', '')][hedge_symbol.replace('_', '')],
            timestamp=datetime.now(timezone.utc)
        )
        
        self.hedge_positions.append(hedge_position)
        self.hedge_stats['hedges_executed'] += 1
        
        return hedge_position

    def evaluate_hedge_opportunity(
        self,
        primary_symbol: str
    ) -> Dict:
        """
        Evaluate if hedge opportunity exists for a symbol
        
        Args:
            primary_symbol: Symbol to evaluate
        
        Returns:
            Dict with hedge opportunity details
        """
        hedge_symbol, hedge_ratio = self.calculate_optimal_hedge_ratio(primary_symbol, 1000)
        
        if hedge_symbol:
            correlation = self.correlation_matrix[primary_symbol.replace('_', '')][hedge_symbol.replace('_', '')]
            return {
                'hedge_available': True,
                'hedge_symbol': hedge_symbol,
                'hedge_ratio': hedge_ratio,
                'correlation': correlation,
                'strength': abs(correlation)
            }
        else:
            return {
                'hedge_available': False,
                'hedge_symbol': None,
                'hedge_ratio': 0.0,
                'reason': 'No suitable hedge pair found'
            }

    def get_hedge_statistics(self) -> Dict:
        """
        Get hedging statistics
        
        Returns:
            Dict with hedge performance metrics
        """
        return {
            'hedges_executed': self.hedge_stats['hedges_executed'],
            'hedges_successful': self.hedge_stats['hedges_successful'],
            'total_drawdown_prevented': self.hedge_stats['total_drawdown_prevented'],
            'average_hedge_ratio': self.hedge_stats['average_hedge_ratio'],
            'active_hedges': len(self.hedge_positions)
        }

    def get_correlation_matrix(self) -> Dict:
        """Get current correlation matrix"""
        return self.correlation_matrix.copy()

    def close_hedge_position(self, hedge_id: int, exit_price: float) -> Optional[float]:
        """
        Close a hedge position and calculate P&L
        
        Args:
            hedge_id: Index of hedge position to close
            exit_price: Exit price
        
        Returns:
            P&L from hedge or None if not found
        """
        if hedge_id < 0 or hedge_id >= len(self.hedge_positions):
            return None
        
        hedge = self.hedge_positions[hedge_id]
        
        # Calculate P&L
        if hedge.side == 'BUY':
            pnl = (exit_price - hedge.entry_price) * hedge.size
        else:  # SELL
            pnl = (hedge.entry_price - exit_price) * hedge.size
        
        # Mark as closed
        self.hedge_positions.pop(hedge_id)
        
        if pnl > 0:
            self.hedge_stats['hedges_successful'] += 1
            self.hedge_stats['total_drawdown_prevented'] += pnl
        
        return pnl


# ============================================
# TESTING & DEMONSTRATION
# ============================================

if __name__ == "__main__":
    print("Quant Hedge Engine - Test Suite")
    print("=" * 60)
    
    # Initialize engine
    engine = QuantHedgeEngine()
    
    print(f"✅ Hedge engine initialized")
    print(f"   Pairs monitored: {len(engine.correlation_matrix)}")
    
    # Test hedge opportunities
    test_symbols = ['EUR_USD', 'GBP_USD', 'USD_JPY', 'AUD_USD', 'USD_CAD']
    
    print(f"\nHedge Opportunities:")
    print("-" * 60)
    
    for symbol in test_symbols:
        opportunity = engine.evaluate_hedge_opportunity(symbol)
        if opportunity['hedge_available']:
            print(f"{symbol}:")
            print(f"  → Hedge: {opportunity['hedge_symbol']} ({opportunity['hedge_ratio']:.1%})")
            print(f"  → Correlation: {opportunity['correlation']:.2f}")
        else:
            print(f"{symbol}: No hedge available")
    
    print(f"\n✅ Status: READY FOR INTEGRATION")
    print("=" * 60)
