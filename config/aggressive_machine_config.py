#!/usr/bin/env python3
"""
Aggressive Money Machine Configuration
1min+ timeframe settings optimized for aggressive capital growth
"""

import json

CONFIG = {
    "pin": 841921,
    "environment": "practice",  # or "live"
    
    # ========================================================================
    # TIMEFRAME SETTINGS
    # ========================================================================
    "timeframes": {
        "primary": "M1",      # 1-minute candles for quick entries
        "confirmation": "M5", # 5-min for trend confirmation
        "long_term": "M15"    # 15-min for regime context
    },
    
    # ========================================================================
    # WOLF PACK STRATEGIES (4 Regime Types)
    # ========================================================================
    "wolf_packs": {
        "bullish": {
            "name": "Bullish Wolf Pack",
            "regime": "bull",
            "entry_signals": [
                "RSI < 50 (oversold bounce)",
                "EMA(9) > EMA(21)",
                "Volume > 20-day average"
            ],
            "position_multiplier": 1.3,      # 30% larger positions
            "trailing_activation_pct": 0.50, # Start trailing at +50% profit
            "hold_time_minutes": 180,        # Max 3 hour holds
            "aggressive_scaling": True       # Increase size on wins
        },
        
        "bearish": {
            "name": "Bearish Wolf Pack",
            "regime": "bear",
            "entry_signals": [
                "RSI > 50 (overbought bounce)",
                "EMA(9) < EMA(21)",
                "Volume confirmation"
            ],
            "position_multiplier": 1.0,
            "trailing_activation_pct": 0.75,
            "hold_time_minutes": 120,        # Max 2 hour holds
            "aggressive_scaling": False
        },
        
        "sideways": {
            "name": "Sideways/Range Wolf Pack",
            "regime": "sideways",
            "entry_signals": [
                "Bollinger Band touches",
                "Support/Resistance bounces",
                "Lower timeframe reversals"
            ],
            "position_multiplier": 0.8,
            "trailing_activation_pct": 0.40,
            "hold_time_minutes": 90,
            "aggressive_scaling": False
        },
        
        "triage": {
            "name": "Triage Wolf Pack (Safe Mode)",
            "regime": "triage",
            "entry_signals": [
                "Only high-confidence setups (>80%)",
                "Major support/resistance",
                "Trend alignment across all timeframes"
            ],
            "position_multiplier": 0.5,      # Conservative
            "trailing_activation_pct": 1.0,   # Tight profit-taking
            "hold_time_minutes": 60,
            "aggressive_scaling": False
        }
    },
    
    # ========================================================================
    # QUANT HEDGE MULTI-CONDITION RULES
    # ========================================================================
    "quant_hedge": {
        "volatility_gates": {
            "low": {"threshold": 0.015, "position_mult": 1.2},
            "moderate": {"threshold": 0.030, "position_mult": 1.0},
            "high": {"threshold": 0.050, "position_mult": 0.7},
            "extreme": {"threshold": 0.075, "position_mult": 0.3}
        },
        
        "margin_utilization_gates": {
            "safe": {"threshold": 0.20, "allow_trading": True},
            "cautious": {"threshold": 0.30, "allow_trading": True, "scale": 0.8},
            "warning": {"threshold": 0.35, "allow_trading": False},
            "critical": {"threshold": 0.40, "action": "close_positions"}
        },
        
        "correlation_gates": {
            "low": {"block": False},
            "moderate": {"block": False, "scale": 0.9},
            "high": {"block": True, "reason": "Same-side USD exposure"}
        }
    },
    
    # ========================================================================
    # AGGRESSIVE TRAILING STOP SETTINGS
    # ========================================================================
    "trailing_stops": {
        "tight_pips": 15,              # Close trailing stop (15 pips)
        "breakeven_activation": "+25", # Move to breakeven at +25 pips profit
        "acceleration": {
            "enabled": True,
            "tighten_by_pips": 5,      # Tighten by 5 pips every hour held
            "max_tightening": 25       # Don't go below 25 pips
        },
        "profit_taking": {
            "level_1": {"profit_pct": 0.50, "close_pct": 0.25},  # Close 25% at +50%
            "level_2": {"profit_pct": 1.00, "close_pct": 0.50},  # Close 50% at +100%
            "level_3": {"profit_pct": 2.00, "close_pct": 1.00}   # Close rest at +200%
        }
    },
    
    # ========================================================================
    # RICK HIVE AUTONOMOUS LOOP
    # ========================================================================
    "rick_hive": {
        "enabled": True,
        "check_interval_seconds": 60,    # Poll every 60 seconds
        "consensus_threshold": 0.80,     # Need 80%+ hive agreement
        "adaptive_learning": True,       # Learn from past trades
        "emotional_damping": {
            "max_consecutive_wins": 5,   # Reduce size after 5 wins
            "max_consecutive_losses": 3  # Stop after 3 losses
        }
    },
    
    # ========================================================================
    # POSITION SIZING FOR CAPITAL GROWTH
    # ========================================================================
    "position_sizing": {
        "risk_per_trade_pct": 0.02,      # Risk 2% per trade (aggressive)
        "initial_position_size": 1000,   # Start with 1000 units per trade
        "max_position_size": 5000,       # Never exceed 5000 units
        "scaling_rule": "kelly_criterion", # Use Kelly formula for sizing
        
        "aggressive_mode": {
            "enabled": True,
            "scale_up_threshold": 0.70,  # If win rate > 70%, increase size
            "scale_up_factor": 1.15,     # Increase by 15%
            "scale_down_threshold": 0.55, # If win rate < 55%, reduce size
            "scale_down_factor": 0.85    # Reduce by 15%
        }
    },
    
    # ========================================================================
    # GUARDIAN GATES (Charter Enforcement)
    # ========================================================================
    "guardian_gates": {
        "margin_cap": 0.35,              # Max 35% margin utilization
        "max_concurrent_positions": 3,   # Max 3 open trades
        "correlation_check": True,       # Block same-side USD exposure
        "notional_minimum": 15000,       # Min $15K per trade (Charter)
        "risk_reward_minimum": 3.2       # Min 3.2:1 ratio (Charter)
    },
    
    # ========================================================================
    # TRADING PAIRS & SCHEDULES
    # ========================================================================
    "trading": {
        "pairs": [
            "EUR_USD",  # Most liquid
            "GBP_USD",
            "USD_JPY",
            "AUD_USD",
            "USD_CAD"
        ],
        
        "session_schedule": {
            "london": {"start": "08:00", "end": "16:30"},  # London
            "newyork": {"start": "13:00", "end": "21:00"}  # New York
        },
        
        "blackout_hours": [
            "22:00-07:00"  # Quiet hours - fewer signals
        ],
        
        "max_daily_trades": 12,
        "max_trades_per_hour": 3
    },
    
    # ========================================================================
    # PERFORMANCE TARGETS (Capital Growth Path)
    # ========================================================================
    "targets": {
        "month_1": {
            "trades": 60,
            "target_win_rate": 0.70,
            "target_pnl": 3600,  # $3.6K profit
            "expected_capital": 9600
        },
        "month_3": {
            "trades": 180,
            "target_win_rate": 0.70,
            "target_pnl": 10800,
            "expected_capital": 18800
        },
        "month_6": {
            "trades": 360,
            "target_win_rate": 0.70,
            "target_pnl": 21600,
            "expected_capital": 32600
        },
        "month_10": {
            "trades": 600,
            "target_win_rate": 0.70,
            "target_pnl": 36000,
            "expected_capital": 51000
        }
    },
    
    # ========================================================================
    # LOGGING & MONITORING
    # ========================================================================
    "logging": {
        "level": "INFO",
        "log_file": "logs/aggressive_money_machine.log",
        "narration_file": "logs/narration.jsonl",
        "heartbeat_interval": 300,  # Log heartbeat every 5 min
        "trade_journal": True
    }
}

if __name__ == "__main__":
    print("🚀 AGGRESSIVE MONEY MACHINE CONFIGURATION")
    print("=" * 80)
    print(json.dumps(CONFIG, indent=2))
