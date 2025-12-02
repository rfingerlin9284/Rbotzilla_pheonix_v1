#!/usr/bin/env python3
"""
RBOTzilla UNI - Correlation Monitor Engine
Portfolio correlation tracking and exposure control for risk diversification.
PIN: 841921 | Phase 14
"""

import json
import os
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Set
import logging
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, asdict
import threading
from collections import defaultdict
import itertools

@dataclass
class CorrelationResult:
    """
    ENGINEER (35%): Correlation analysis result data structure
    """
    symbol_pair: Tuple[str, str]
    correlation: float
    lookback_days: int
    data_points: int
    confidence: float
    last_updated: str
    correlation_strength: str  # WEAK, MODERATE, STRONG, VERY_STRONG

@dataclass
class PortfolioExposure:
    """
    TRADER_PSYCH (20%): Portfolio exposure tracking
    """
    symbol: str
    position_size: float
    entry_time: str
    regime: Optional[str] = None
    correlation_group: Optional[str] = None
    risk_weight: float = 1.0

class CorrelationMonitor:
    """
    PROF_QUANT (40%): Advanced correlation mathematics and portfolio risk modeling
    ENGINEER (35%): Real-time correlation tracking and position control systems  
    TRADER_PSYCH (20%): Portfolio exposure psychology and diversification behavior
    MENTOR_BK (5%): Risk parity adaptation and system reliability
    
    Correlation monitoring system that:
    - Calculates real-time correlations between trading symbols
    - Prevents over-exposure to correlated assets (>0.7 correlation)
    - Tracks portfolio diversification and risk concentration
    - Provides correlation-based position sizing adjustments
    - Monitors FX and crypto correlations separately
    """
    
    def __init__(self, pin: int = 841921, correlation_file: str = "correlations.json"):
        """Initialize Correlation Monitor with PIN authentication"""
        if pin != 841921:
            raise ValueError("Invalid PIN for Correlation Monitor")
        
        self.pin_verified = True
        self.correlation_file = correlation_file
        self.max_correlation_threshold = 0.7  # Block trades above this correlation
        self.warning_correlation_threshold = 0.5  # Warning level
        self.min_data_points = 20  # Minimum data points for reliable correlation
        self.lookback_days = 30  # Days of data for correlation calculation
        
        # Price data storage for correlation calculation
        self.price_data: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.correlation_matrix: Dict[Tuple[str, str], CorrelationResult] = {}
        self.current_positions: Dict[str, PortfolioExposure] = {}
        self.lock = threading.Lock()
        
        # Asset groupings for enhanced correlation tracking
        self.asset_groups = {
            'fx_major': ['EUR_USD', 'GBP_USD', 'USD_JPY', 'USD_CHF', 'AUD_USD', 'USD_CAD', 'NZD_USD'],
            'fx_minor': ['EUR_GBP', 'EUR_JPY', 'EUR_CHF', 'EUR_AUD', 'GBP_JPY', 'CHF_JPY'],
            'crypto_major': ['BTC-USD', 'ETH-USD', 'BNB-USD', 'SOL-USD', 'XRP-USD'],
            'crypto_alt': ['ADA-USD', 'DOT-USD', 'LINK-USD', 'LTC-USD', 'BCH-USD'],
            'indices': ['US30', 'SPX500', 'NAS100', 'UK100', 'GER40', 'JPN225']
        }
        
        # Correlation update frequency
        self.last_correlation_update = {}
        self.correlation_update_interval = 3600  # 1 hour in seconds
        
        self.logger = logging.getLogger(f"CorrelationMonitor_{pin}")
        self.logger.info("Correlation Monitor initialized")
        
        # Load existing correlation data
        self._load_correlations()
    
    def _load_correlations(self):
        """
        ENGINEER: Load correlation data from persistent storage
        """
        if os.path.exists(self.correlation_file):
            try:
                with open(self.correlation_file, 'r') as f:
                    corr_data = json.load(f)
                
                # Load correlation matrix
                for pair_str, corr_dict in corr_data.get('correlations', {}).items():
                    try:
                        # Parse symbol pair from string
                        symbols = pair_str.split('_vs_')
                        if len(symbols) == 2:
                            pair = (symbols[0], symbols[1])
                            result = CorrelationResult(**corr_dict)
                            self.correlation_matrix[pair] = result
                    except Exception as e:
                        self.logger.warning(f"Failed to load correlation for {pair_str}: {e}")
                
                # Load price data (keep recent data only)
                for symbol, prices in corr_data.get('price_data', {}).items():
                    self.price_data[symbol] = prices[-100:]  # Keep last 100 data points
                
                self.logger.info(f"Loaded {len(self.correlation_matrix)} correlation pairs")
                
            except Exception as e:
                self.logger.error(f"Failed to load correlations: {e}")
        else:
            self.logger.info("No existing correlation file found - starting fresh")
    
    def _save_correlations(self):
        """
        ENGINEER: Save correlation data to persistent storage
        """
        try:
            # Prepare correlation data for JSON serialization
            correlations = {}
            for (symbol1, symbol2), result in self.correlation_matrix.items():
                pair_key = f"{symbol1}_vs_{symbol2}"
                correlations[pair_key] = asdict(result)
            
            corr_data = {
                'correlations': correlations,
                'price_data': dict(self.price_data),
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
            
            # Write to temporary file first, then rename for atomic operation
            temp_file = f"{self.correlation_file}.tmp"
            with open(temp_file, 'w') as f:
                json.dump(corr_data, f, indent=2)
            
            os.rename(temp_file, self.correlation_file)
            self.logger.debug("Saved correlation data")
            
        except Exception as e:
            self.logger.error(f"Failed to save correlations: {e}")
    
    def update_price_data(self, symbol: str, price: float, timestamp: Optional[str] = None):
        """
        ENGINEER: Update price data for correlation calculations
        """
        try:
            if timestamp is None:
                timestamp = datetime.now(timezone.utc).isoformat()
            
            with self.lock:
                price_record = {
                    'timestamp': timestamp,
                    'price': price
                }
                
                self.price_data[symbol].append(price_record)
                
                # Keep only recent data
                cutoff_time = datetime.now(timezone.utc) - timedelta(days=self.lookback_days * 2)
                self.price_data[symbol] = [
                    p for p in self.price_data[symbol]
                    if datetime.fromisoformat(p['timestamp'].replace('Z', '+00:00')) >= cutoff_time
                ]
                
        except Exception as e:
            self.logger.error(f"Failed to update price data for {symbol}: {e}")
    
    def calculate_correlation(self, symbol1: str, symbol2: str) -> Optional[CorrelationResult]:
        """
        PROF_QUANT: Calculate correlation between two symbols using price returns
        """
        try:
            if symbol1 == symbol2:
                return None  # Same symbol
            
            # Ensure consistent ordering
            pair = tuple(sorted([symbol1, symbol2]))
            symbol1, symbol2 = pair
            
            # Check if we have sufficient data for both symbols
            if (symbol1 not in self.price_data or symbol2 not in self.price_data or
                len(self.price_data[symbol1]) < self.min_data_points or
                len(self.price_data[symbol2]) < self.min_data_points):
                return None
            
            # Get price data for correlation calculation
            prices1 = self.price_data[symbol1]
            prices2 = self.price_data[symbol2]
            
            # Create aligned price series (matching timestamps)
            aligned_data = []
            
            # Convert to dictionaries for faster lookup
            prices1_dict = {p['timestamp']: p['price'] for p in prices1}
            prices2_dict = {p['timestamp']: p['price'] for p in prices2}
            
            # Find common timestamps
            common_times = set(prices1_dict.keys()) & set(prices2_dict.keys())
            
            if len(common_times) < self.min_data_points:
                return None
            
            # Sort timestamps and extract aligned prices
            sorted_times = sorted(common_times)
            aligned_prices1 = [prices1_dict[t] for t in sorted_times]
            aligned_prices2 = [prices2_dict[t] for t in sorted_times]
            
            # Calculate returns
            returns1 = np.diff(np.log(aligned_prices1))
            returns2 = np.diff(np.log(aligned_prices2))
            
            if len(returns1) < 10:  # Need minimum returns for reliable correlation
                return None
            
            # Calculate correlation
            correlation = np.corrcoef(returns1, returns2)[0, 1]
            
            # Handle NaN correlations
            if np.isnan(correlation):
                return None
            
            # Determine correlation strength
            abs_corr = abs(correlation)
            if abs_corr >= 0.8:
                strength = "VERY_STRONG"
            elif abs_corr >= 0.6:
                strength = "STRONG"
            elif abs_corr >= 0.3:
                strength = "MODERATE"
            else:
                strength = "WEAK"
            
            # Calculate confidence based on data quality
            confidence = min(len(returns1) / 50.0, 1.0)  # Max confidence at 50+ data points
            
            result = CorrelationResult(
                symbol_pair=pair,
                correlation=correlation,
                lookback_days=self.lookback_days,
                data_points=len(returns1),
                confidence=confidence,
                last_updated=datetime.now(timezone.utc).isoformat(),
                correlation_strength=strength
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Correlation calculation failed for {symbol1}/{symbol2}: {e}")
            return None
    
    def update_correlations(self, symbols: Optional[List[str]] = None):
        """
        PROF_QUANT: Update correlation matrix for specified symbols or all available symbols
        """
        try:
            with self.lock:
                if symbols is None:
                    symbols = list(self.price_data.keys())
                
                if len(symbols) < 2:
                    return
                
                updated_count = 0
                
                # Calculate correlations for all symbol pairs
                for symbol1, symbol2 in itertools.combinations(symbols, 2):
                    pair = tuple(sorted([symbol1, symbol2]))
                    
                    # Check if update is needed
                    if pair in self.last_correlation_update:
                        last_update = self.last_correlation_update[pair]
                        time_since_update = datetime.now(timezone.utc) - datetime.fromisoformat(last_update)
                        if time_since_update.total_seconds() < self.correlation_update_interval:
                            continue  # Skip if recently updated
                    
                    correlation_result = self.calculate_correlation(symbol1, symbol2)
                    
                    if correlation_result:
                        self.correlation_matrix[pair] = correlation_result
                        self.last_correlation_update[pair] = datetime.now(timezone.utc).isoformat()
                        updated_count += 1
                
                if updated_count > 0:
                    self._save_correlations()
                    self.logger.info(f"Updated {updated_count} correlation pairs")
                
        except Exception as e:
            self.logger.error(f"Correlation update failed: {e}")
    
    def get_correlation(self, symbol1: str, symbol2: str) -> Optional[float]:
        """
        Get correlation between two symbols
        """
        pair = tuple(sorted([symbol1, symbol2]))
        
        if pair in self.correlation_matrix:
            return self.correlation_matrix[pair].correlation
        
        return None
    
    def check_correlation_risk(self, new_symbol: str, proposed_position_size: float) -> Dict[str, Any]:
        """
        TRADER_PSYCH: Check correlation risk for a new position
        """
        try:
            correlation_risks = []
            total_correlated_exposure = 0.0
            max_correlation = 0.0
            
            # Check against all current positions
            for existing_symbol, position in self.current_positions.items():
                correlation = self.get_correlation(new_symbol, existing_symbol)
                
                if correlation is not None:
                    abs_correlation = abs(correlation)
                    max_correlation = max(max_correlation, abs_correlation)
                    
                    if abs_correlation >= self.warning_correlation_threshold:
                        correlated_exposure = position.position_size * abs_correlation
                        total_correlated_exposure += correlated_exposure
                        
                        risk_level = "HIGH" if abs_correlation >= self.max_correlation_threshold else "MODERATE"
                        
                        correlation_risks.append({
                            'existing_symbol': existing_symbol,
                            'correlation': correlation,
                            'existing_position_size': position.position_size,
                            'correlated_exposure': correlated_exposure,
                            'risk_level': risk_level
                        })
            
            # Determine overall risk assessment
            should_block = max_correlation >= self.max_correlation_threshold
            should_warn = max_correlation >= self.warning_correlation_threshold
            
            # Calculate adjusted position size if needed
            adjusted_position_size = proposed_position_size
            if total_correlated_exposure > 0:
                # Reduce position size based on correlation exposure
                correlation_adjustment = 1.0 - min(total_correlated_exposure, 0.5)  # Max 50% reduction
                adjusted_position_size = proposed_position_size * correlation_adjustment
            
            return {
                'symbol': new_symbol,
                'proposed_position_size': proposed_position_size,
                'adjusted_position_size': adjusted_position_size,
                'max_correlation': max_correlation,
                'total_correlated_exposure': total_correlated_exposure,
                'correlation_risks': correlation_risks,
                'should_block': should_block,
                'should_warn': should_warn,
                'risk_assessment': 'HIGH' if should_block else 'MODERATE' if should_warn else 'LOW'
            }
            
        except Exception as e:
            self.logger.error(f"Correlation risk check failed for {new_symbol}: {e}")
            return {
                'symbol': new_symbol,
                'error': str(e),
                'should_block': False,
                'should_warn': False,
                'risk_assessment': 'UNKNOWN'
            }
    
    def add_position(self, symbol: str, position_size: float, regime: Optional[str] = None):
        """
        ENGINEER: Add a new position to portfolio tracking
        """
        try:
            with self.lock:
                # Determine correlation group
                correlation_group = None
                for group_name, symbols in self.asset_groups.items():
                    if symbol in symbols:
                        correlation_group = group_name
                        break
                
                position = PortfolioExposure(
                    symbol=symbol,
                    position_size=position_size,
                    entry_time=datetime.now(timezone.utc).isoformat(),
                    regime=regime,
                    correlation_group=correlation_group
                )
                
                self.current_positions[symbol] = position
                self.logger.info(f"Added position: {symbol} ({position_size:.2%})")
                
        except Exception as e:
            self.logger.error(f"Failed to add position for {symbol}: {e}")
    
    def remove_position(self, symbol: str):
        """
        ENGINEER: Remove position from portfolio tracking
        """
        try:
            with self.lock:
                if symbol in self.current_positions:
                    del self.current_positions[symbol]
                    self.logger.info(f"Removed position: {symbol}")
                
        except Exception as e:
            self.logger.error(f"Failed to remove position for {symbol}: {e}")
    
    def get_portfolio_diversification_report(self) -> Dict[str, Any]:
        """
        TRADER_PSYCH: Generate portfolio diversification analysis
        """
        try:
            with self.lock:
                if not self.current_positions:
                    return {
                        'total_positions': 0,
                        'diversification_score': 1.0,
                        'correlation_groups': {},
                        'high_correlation_pairs': [],
                        'recommendations': []
                    }
                
                # Group positions by correlation groups
                group_exposure = defaultdict(float)
                for position in self.current_positions.values():
                    group = position.correlation_group or 'uncategorized'
                    group_exposure[group] += position.position_size
                
                # Find high correlation pairs within portfolio
                high_corr_pairs = []
                positions_list = list(self.current_positions.items())
                
                for i, (symbol1, pos1) in enumerate(positions_list):
                    for symbol2, pos2 in positions_list[i+1:]:
                        correlation = self.get_correlation(symbol1, symbol2)
                        if correlation is not None and abs(correlation) >= self.warning_correlation_threshold:
                            high_corr_pairs.append({
                                'symbol1': symbol1,
                                'symbol2': symbol2,
                                'correlation': correlation,
                                'combined_exposure': pos1.position_size + pos2.position_size
                            })
                
                # Calculate diversification score
                # Based on: 1) number of positions, 2) correlation spread, 3) group diversification
                num_positions = len(self.current_positions)
                num_groups = len(group_exposure)
                max_group_exposure = max(group_exposure.values()) if group_exposure else 0
                
                diversification_score = 1.0
                
                # Penalize concentration
                if max_group_exposure > 0.5:  # >50% in one group
                    diversification_score *= 0.7
                elif max_group_exposure > 0.3:  # >30% in one group
                    diversification_score *= 0.85
                
                # Penalize high correlations
                if high_corr_pairs:
                    avg_high_corr = np.mean([abs(p['correlation']) for p in high_corr_pairs])
                    correlation_penalty = avg_high_corr * 0.5
                    diversification_score *= (1 - correlation_penalty)
                
                # Reward more positions and groups
                position_bonus = min(num_positions / 10.0, 0.1)  # Up to 10% bonus
                group_bonus = min(num_groups / 5.0, 0.1)  # Up to 10% bonus
                diversification_score += position_bonus + group_bonus
                
                diversification_score = max(0.0, min(1.0, diversification_score))
                
                # Generate recommendations
                recommendations = []
                if max_group_exposure > 0.4:
                    recommendations.append(f"Reduce concentration in {max(group_exposure, key=group_exposure.get)} group")
                if len(high_corr_pairs) > 2:
                    recommendations.append("Consider reducing highly correlated positions")
                if num_positions < 3:
                    recommendations.append("Consider diversifying with more uncorrelated positions")
                
                return {
                    'total_positions': num_positions,
                    'diversification_score': diversification_score,
                    'correlation_groups': dict(group_exposure),
                    'high_correlation_pairs': high_corr_pairs,
                    'recommendations': recommendations,
                    'max_group_exposure': max_group_exposure,
                    'correlation_matrix_size': len(self.correlation_matrix)
                }
                
        except Exception as e:
            self.logger.error(f"Diversification report failed: {e}")
            return {'error': str(e)}
    
    def save_now(self):
        """Force save correlation data to disk"""
        with self.lock:
            self._save_correlations()

def get_correlation_monitor(pin: int = 841921) -> CorrelationMonitor:
    """Convenience function to get Correlation Monitor instance"""
    return CorrelationMonitor(pin=pin)

# Example usage
if __name__ == "__main__":
    # Test Correlation Monitor
    monitor = CorrelationMonitor(pin=841921)
    
    print("📊 CORRELATION MONITOR TEST RESULTS 📊")
    print("=" * 50)
    
    # Simulate price data for correlated symbols
    test_symbols = ['EUR_USD', 'GBP_USD', 'USD_JPY', 'BTC-USD', 'ETH-USD']
    
    # Generate sample price data with some correlation
    np.random.seed(42)
    base_prices = {'EUR_USD': 1.1000, 'GBP_USD': 1.3000, 'USD_JPY': 110.0, 'BTC-USD': 45000.0, 'ETH-USD': 3000.0}
    
    for day in range(30):
        # Create correlated price movements
        market_factor = np.random.normal(0, 0.01)  # Common market factor
        
        for symbol in test_symbols:
            # Individual symbol movement + correlated market movement
            individual_move = np.random.normal(0, 0.005)
            
            # EUR_USD and GBP_USD are more correlated
            if symbol in ['EUR_USD', 'GBP_USD']:
                correlated_move = market_factor * 0.7 + individual_move * 0.3
            # BTC and ETH are highly correlated
            elif symbol in ['BTC-USD', 'ETH-USD']:
                correlated_move = market_factor * 0.8 + individual_move * 0.2
            else:
                correlated_move = market_factor * 0.3 + individual_move * 0.7
            
            new_price = base_prices[symbol] * (1 + correlated_move)
            base_prices[symbol] = new_price
            
            timestamp = (datetime.now(timezone.utc) - timedelta(days=29-day)).isoformat()
            monitor.update_price_data(symbol, new_price, timestamp)
    
    print(f"Updated price data for {len(test_symbols)} symbols over 30 days")
    
    # Calculate correlations
    monitor.update_correlations(test_symbols)
    
    # Test correlation retrieval
    eur_gbp_corr = monitor.get_correlation('EUR_USD', 'GBP_USD')
    btc_eth_corr = monitor.get_correlation('BTC-USD', 'ETH-USD')
    eur_btc_corr = monitor.get_correlation('EUR_USD', 'BTC-USD')
    
    print(f"\nCorrelation Results:")
    print(f"EUR_USD vs GBP_USD: {eur_gbp_corr:.3f}" if eur_gbp_corr else "EUR_USD vs GBP_USD: No data")
    print(f"BTC-USD vs ETH-USD: {btc_eth_corr:.3f}" if btc_eth_corr else "BTC-USD vs ETH-USD: No data")
    print(f"EUR_USD vs BTC-USD: {eur_btc_corr:.3f}" if eur_btc_corr else "EUR_USD vs BTC-USD: No data")
    
    # Test position management
    monitor.add_position('EUR_USD', 0.08, 'BULLISH')
    monitor.add_position('USD_JPY', 0.05, 'BEARISH')
    
    print(f"\nAdded 2 positions to portfolio")
    
    # Test correlation risk check
    risk_check = monitor.check_correlation_risk('GBP_USD', 0.06)
    print(f"\nCorrelation Risk Check for GBP_USD (6% position):")
    print(f"Should block: {risk_check['should_block']}")
    print(f"Should warn: {risk_check['should_warn']}")
    print(f"Risk assessment: {risk_check['risk_assessment']}")
    print(f"Adjusted position size: {risk_check['adjusted_position_size']:.1%}")
    
    # Test diversification report
    div_report = monitor.get_portfolio_diversification_report()
    print(f"\nDiversification Report:")
    print(f"Total positions: {div_report['total_positions']}")
    print(f"Diversification score: {div_report['diversification_score']:.3f}")
    print(f"Correlation groups: {div_report['correlation_groups']}")
    
    print("\n✅ Correlation Monitor operational")