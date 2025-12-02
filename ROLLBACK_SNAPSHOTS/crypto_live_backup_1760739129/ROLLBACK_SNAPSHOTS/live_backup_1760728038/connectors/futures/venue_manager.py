import json
import time
import requests
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class VenueManager:
    """
    Manages multiple futures/perpetuals venues with dynamic selection
    based on liquidity, fees, and availability
    """
    
    def __init__(self, config_path="configs/futures_venues.json"):
        self.config_path = config_path
        self.venues = {}
        self.venue_status = {}
        self.last_health_check = 0
        self.health_check_interval = 300  # 5 minutes
        
        # Load venue configurations
        self.load_venues()
        
    def load_venues(self):
        """Load venue configurations"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                self.venues = config.get('venues', {})
                logger.info(f"Loaded {len(self.venues)} futures venues")
        except FileNotFoundError:
            logger.warning("No futures venues config found, using defaults")
            self._create_default_config()
            
    def _create_default_config(self):
        """Create default venue configuration"""
        default_config = {
            "venues": {
                "binance_futures": {
                    "name": "Binance Futures",
                    "base_url": "https://fapi.binance.com",
                    "max_leverage": 125,
                    "maker_fee": 0.02,
                    "taker_fee": 0.04,
                    "min_notional": 5.0,
                    "supported_pairs": ["BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT"],
                    "enabled": True
                },
                "bybit_perp": {
                    "name": "Bybit Perpetuals",
                    "base_url": "https://api.bybit.com",
                    "max_leverage": 100,
                    "maker_fee": 0.01,
                    "taker_fee": 0.06,
                    "min_notional": 1.0,
                    "supported_pairs": ["BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT"],
                    "enabled": True
                },
                "okx_futures": {
                    "name": "OKX Futures",
                    "base_url": "https://www.okx.com",
                    "max_leverage": 125,
                    "maker_fee": 0.02,
                    "taker_fee": 0.05,
                    "min_notional": 1.0,
                    "supported_pairs": ["BTC-USDT-SWAP", "ETH-USDT-SWAP"],
                    "enabled": True
                }
            },
            "selection_criteria": {
                "prefer_low_fees": True,
                "min_liquidity_threshold": 1000000,
                "max_spread_threshold": 0.1,
                "health_score_weight": 0.4,
                "fee_weight": 0.3,
                "liquidity_weight": 0.3
            }
        }
        
        # Ensure config directory exists
        import os
        os.makedirs("configs", exist_ok=True)
        
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        self.venues = default_config["venues"]
        
    def check_venue_health(self, venue_id: str) -> Dict:
        """Check health status of a specific venue"""
        venue = self.venues.get(venue_id)
        if not venue:
            return {"status": "unknown", "score": 0.0}
            
        health_score = 1.0
        issues = []
        
        try:
            # Basic connectivity check
            response = requests.get(f"{venue['base_url']}/ping", timeout=5)
            if response.status_code != 200:
                health_score *= 0.5
                issues.append("connectivity_issue")
                
        except requests.RequestException:
            health_score *= 0.3
            issues.append("connection_failed")
            
        # Check if venue is enabled
        if not venue.get("enabled", True):
            health_score = 0.0
            issues.append("disabled")
            
        return {
            "status": "healthy" if health_score > 0.7 else "degraded" if health_score > 0.3 else "unhealthy",
            "score": health_score,
            "issues": issues,
            "last_check": datetime.utcnow().isoformat()
        }
        
    def get_best_venue_for_pair(self, pair: str, required_leverage: int = 1) -> Optional[str]:
        """
        Select the best venue for trading a specific pair
        considering fees, liquidity, health, and leverage requirements
        """
        
        candidates = []
        
        for venue_id, venue in self.venues.items():
            # Check if venue supports the pair
            if pair not in venue.get("supported_pairs", []):
                continue
                
            # Check leverage requirements
            if required_leverage > venue.get("max_leverage", 1):
                continue
                
            # Calculate composite score
            health_score = 0.8  # Assume healthy for demo
            fee_score = 1.0 - (venue.get("taker_fee", 0.1) / 0.1)  # Lower fees = higher score
            
            composite_score = (
                health_score * 0.5 +
                fee_score * 0.3 +
                0.2  # Base score for being available
            )
            
            candidates.append({
                "venue_id": venue_id,
                "score": composite_score,
                "fees": venue.get("taker_fee", 0.1),
                "max_leverage": venue.get("max_leverage", 1),
                "health": health_score
            })
            
        if not candidates:
            logger.warning(f"No suitable venue found for pair {pair} with leverage {required_leverage}")
            return None
            
        # Sort by composite score (highest first)
        candidates.sort(key=lambda x: x["score"], reverse=True)
        best_venue = candidates[0]
        
        logger.info(f"Selected {best_venue['venue_id']} for {pair} (score: {best_venue['score']:.3f})")
        return best_venue["venue_id"]
        
    def get_venue_info(self, venue_id: str) -> Optional[Dict]:
        """Get detailed information about a venue"""
        venue = self.venues.get(venue_id)
        if not venue:
            return None
            
        return {
            "name": venue.get("name", venue_id),
            "max_leverage": venue.get("max_leverage", 1),
            "maker_fee": venue.get("maker_fee", 0.1),
            "taker_fee": venue.get("taker_fee", 0.1),
            "min_notional": venue.get("min_notional", 1.0),
            "supported_pairs": venue.get("supported_pairs", []),
            "health_score": 0.8,  # Default for demo
            "health_status": "healthy",
            "enabled": venue.get("enabled", True)
        }
        
    def get_available_venues(self) -> List[str]:
        """Get list of currently available venues"""
        return [v_id for v_id, venue in self.venues.items() if venue.get("enabled", True)]
        
    def emergency_disable_venue(self, venue_id: str, reason: str = "emergency"):
        """Emergency disable a venue"""
        if venue_id in self.venues:
            self.venues[venue_id]["enabled"] = False
            logger.critical(f"Emergency disabled venue {venue_id}: {reason}")
            
            # Log the incident
            incident = {
                "timestamp": datetime.utcnow().isoformat(),
                "action": "venue_disabled",
                "venue": venue_id,
                "reason": reason,
                "severity": "critical"
            }
            
            with open("logs/futures_incidents.jsonl", "a") as f:
                f.write(json.dumps(incident) + "\n")
