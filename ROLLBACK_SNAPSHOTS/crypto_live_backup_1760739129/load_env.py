#!/usr/bin/env python3
"""
Load environment variables from env_new2.env
Handles multi-line values properly
"""
import os
from pathlib import Path

def load_env_file(env_file='env_new2.env'):
    """Load environment variables from file"""
    env_path = Path(__file__).parent / env_file
    
    if not env_path.exists():
        print(f"⚠️ {env_file} not found, trying .env...")
        env_path = Path(__file__).parent / '.env'
    
    if not env_path.exists():
        print(f"❌ No environment file found")
        return
    
    print(f"📋 Loading environment from: {env_path.name}")
    
    current_key = None
    current_value = []
    
    with open(env_path, 'r') as f:
        for line in f:
            line = line.rstrip('\n')
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Check if this is a new key=value pair
            if '=' in line and not line.startswith(' '):
                # Save previous key if exists
                if current_key:
                    os.environ[current_key] = '\n'.join(current_value)
                
                # Parse new key
                key, value = line.split('=', 1)
                current_key = key.strip()
                current_value = [value]
            else:
                # Continuation of multi-line value
                if current_key:
                    current_value.append(line)
        
        # Save last key
        if current_key:
            os.environ[current_key] = '\n'.join(current_value)
    
    print(f"✅ Loaded environment variables")

if __name__ == "__main__":
    load_env_file()
    print(f"\n📊 Key variables loaded:")
    print(f"   RICK_PIN: {os.getenv('RICK_PIN', 'NOT SET')}")
    print(f"   IB_GATEWAY_PORT: {os.getenv('IB_GATEWAY_PORT', 'NOT SET')}")
    print(f"   IB_ACCOUNT_ID: {os.getenv('IB_ACCOUNT_ID', 'NOT SET')}")
    print(f"   IB_TRADING_MODE: {os.getenv('IB_TRADING_MODE', 'NOT SET')}")
    print(f"   OANDA_PRACTICE_ACCOUNT_ID: {os.getenv('OANDA_PRACTICE_ACCOUNT_ID', 'NOT SET')}")
