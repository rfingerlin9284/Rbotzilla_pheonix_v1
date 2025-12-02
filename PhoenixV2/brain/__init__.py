"""
PhoenixV2 Brain Module

Strategy aggregation with HiveMind, WolfPack, and QuantHedge.
"""
from .aggregator import StrategyBrain
from .hive_mind import HiveMindBridge
from .wolf_pack import WolfPack
from .quant_hedge import QuantHedgeRules, RegimeDetector

__all__ = ['StrategyBrain', 'HiveMindBridge', 'WolfPack', 'QuantHedgeRules', 'RegimeDetector']
