#!/usr/bin/env python3
"""
Safe .env loader - exports only simple KEY=VALUE pairs, skips multiline blocks
"""
import os
import sys
from pathlib import Path

def load_env(env_path=".env"):
    """Load .env file, skipping multiline keys/certs"""
    if not Path(env_path).exists():
        print(f"⚠️  No {env_path} file found", file=sys.stderr)
        return
    
    in_block = False
    loaded = 0
    
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Skip empty and comments
            if not line or line.startswith('#'):
                continue
            
            # Track multiline blocks (BEGIN/END)
            if 'BEGIN' in line or 'END' in line:
                in_block = 'BEGIN' in line
                continue
            
            # Skip lines inside blocks
            if in_block:
                continue
            
            # Only process lines with = 
            if '=' not in line:
                continue
            
            # Export valid KEY=VALUE
            try:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Skip invalid keys
                if not key or not key.replace('_', '').isalnum():
                    continue
                
                os.environ[key] = value
                loaded += 1
            except Exception:
                continue
    
    print(f"✓ Loaded {loaded} environment variables", file=sys.stderr)

if __name__ == "__main__":
    load_env()
