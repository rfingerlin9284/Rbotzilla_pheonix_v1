import numpy as np
from hive.quant_hedge_rules import QuantHedgeRules, HedgeAction


def test_quant_hedge_basic():
    qh = QuantHedgeRules(pin=841921)
    prices = np.random.normal(100, 2, size=100)
    volume = np.random.uniform(1000, 5000, size=100)
    analysis = qh.analyze_market_conditions(
        prices=prices,
        volume=volume,
        account_nav=10000,
        margin_used=2000,
        open_positions=1,
        correlation_matrix={'EURUSD-GBPUSD': 0.7}
    )

    assert analysis is not None
    assert analysis.primary_action in [a.value for a in HedgeAction]

if __name__ == '__main__':
    test_quant_hedge_basic()
    print('Hedge rules quick test passed')
