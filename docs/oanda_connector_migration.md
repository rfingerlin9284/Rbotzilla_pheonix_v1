# OANDA Connector Migration Guide

This guide explains how to migrate from the original `OandaConnector` to the enhanced `EnhancedOandaConnector` that integrates with the `ParameterManager` to prevent configuration drift and credential loss.

## Benefits of the Enhanced Connector

1. **Persistent Credential Storage**: API tokens and account IDs are securely stored in the parameter manager
2. **Parameter Locking**: Prevents accidental changes to critical configuration
3. **Audit Trail**: All changes to parameters are logged with timestamps and sources
4. **Environment Switching**: Simplified switching between practice and live environments
5. **Consistent Configuration**: Ensures all components use the same configuration values
6. **Order Tracking**: Maintains a record of all orders placed through the connector

## Migration Steps

### Step 1: Import the Enhanced Connector

Replace imports of the original connector with the enhanced version:

```python
# Old import
from brokers.oanda_connector import OandaConnector

# New import
from brokers.oanda_connector_enhanced import EnhancedOandaConnector
```

### Step 2: Update Initialization

The initialization parameters remain the same, so this change is minimal:

```python
# Old initialization
connector = OandaConnector(pin=841921, environment="practice")

# New initialization
connector = EnhancedOandaConnector(pin=841921, environment="practice")
```

### Step 3: Test the Enhanced Connector

Run the test script to verify the enhanced connector works correctly:

```bash
python test_oanda_enhanced.py
```

### Step 4: Update References in Your Code

Search for all instances of `OandaConnector` in your codebase and replace them with `EnhancedOandaConnector`.

## New Features

### Environment Switching

The enhanced connector provides a method to switch between practice and live environments:

```python
# Switch to live environment
connector.switch_environment("live")

# Switch back to practice
connector.switch_environment("practice")
```

### Parameter Access

You can access the stored parameters directly through the parameter manager:

```python
# Get the current environment
current_env = connector.param_manager.get("oanda.environment")

# Get stored credentials (for debugging only)
account_id = connector.param_manager.get("oanda.practice.account_id")
```

## Troubleshooting

### Missing Credentials

If you encounter issues with missing credentials:

1. Check if your `.env` file contains the correct OANDA API tokens and account IDs
2. Run the test script to initialize the parameter manager with your credentials
3. Verify the credentials were stored correctly:

```python
from util.parameter_manager import ParameterManager

config_path = os.path.join(os.path.dirname(__file__), 'config', 'oanda_parameters.json')
pm = ParameterManager(config_path)
print(pm.get("oanda.practice.account_id"))
```

### Locked Parameters

If you need to update a locked parameter (not recommended):

```python
from util.parameter_manager import ParameterManager

config_path = os.path.join(os.path.dirname(__file__), 'config', 'oanda_parameters.json')
pm = ParameterManager(config_path)
pm.unlock_parameter("oanda.practice.token")
pm.set("oanda.practice.token", "new_token_value", component="manual_update")
pm.lock_parameter("oanda.practice.token")
```

## Best Practices

1. **Always use the parameter manager** for configuration values instead of hardcoding
2. **Lock critical parameters** to prevent accidental changes
3. **Use descriptive parameter names** with proper namespacing (e.g., `oanda.practice.token`)
4. **Include source information** when setting parameters to track where changes come from
5. **Mark sensitive parameters** as `is_sensitive=True` to prevent logging their values

## Complete Example

```python
import os
import logging
from brokers.oanda_connector_enhanced import EnhancedOandaConnector

# Set up logging
logging.basicConfig(level=logging.INFO)

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Create connector
connector = EnhancedOandaConnector(environment="practice")

# Get account info
account = connector.get_account_info()
if account:
    print(f"Account balance: {account.balance} {account.currency}")
    print(f"Open positions: {account.open_positions}")

# Place order
result = connector.place_oco_order(
    instrument="EUR_USD",
    entry_price=1.0500,
    stop_loss=1.0450,
    take_profit=1.0600,
    units=1000,
    order_type="LIMIT"
)

print(f"Order result: {result}")

# Access stored order parameters
order_id = result.get("order_id")
if order_id:
    order_params = connector.param_manager.get(f"oanda.orders.{order_id}")
    print(f"Stored order parameters: {order_params}")
```