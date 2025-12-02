from dataclasses import dataclass
from typing import Dict, Any
import pandas as pd


@dataclass
class StrategyConfig:
    symbol: str
    timeframe: str
    params: Dict[str, Any]


class Strategy:
    def __init__(self, config: StrategyConfig):
        self.config = config

    def compute_features(self, df: pd.DataFrame) -> pd.DataFrame:
        # Minimal features: copy and add timestamp if not present
        return df.copy()

    def generate_signals(self, df: pd.DataFrame):
        # Return empty signals by default
        return []
