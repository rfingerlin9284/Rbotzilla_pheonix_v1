# Hedge Upgrade Toggle Commands

## Enable Hedge Upgrade

To enable the hedging upgrade, execute the following command:

```bash
python toggle_upgrade.py --enable-hedge
```

This command activates the hybrid Kalman-based hedge engine, enabling dynamic beta adjustments, volatility forecasting, and regime-based multipliers.

## Disable Hedge Upgrade

To revert to the original version, execute the following command:

```bash
python toggle_upgrade.py --disable-hedge
```

This command disables the hedging upgrade and restores the original trading logic.

## Testing Metrics

After toggling the upgrade, validate the system using the following metrics:

- **Win Rate**: Ensure it is ≥ 55%.
- **Sharpe Ratio**: Target ≥ 0.8.
- **Max Drawdown**: Should be < 30%.
- **Volatility Reduction**: Expect a 25–35% decrease.
- **Drawdown Improvement**: Aim for a 25–40% reduction.

Run the validation script to confirm:

```bash
python validate_upgrade.py
```

The validation script generates a JSON report with detailed metrics and a pass/fail verdict based on the above criteria.