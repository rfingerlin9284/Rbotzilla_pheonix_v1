#!/usr/bin/env python3
"""
RICK INSTITUTIONAL CHARTER DEPLOYMENT SCRIPT
One-liner command execution for institutional-grade Charter deployment
PIN: 841921 | Generated: 2025-10-29
"""

import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Execute the institutional Charter deployment"""
    print("\n" + "="*80)
    print("🚀 RICK INSTITUTIONAL CHARTER DEPLOYMENT")
    print("Charter Version: 3.0_INSTITUTIONAL_2025_10_29")
    print("="*80)
    
    try:
        from institutional_charter_agent import execute_one_liner_command
        
        # Execute the one-liner command
        agent = execute_one_liner_command()
        
        print(f"\n✅ INSTITUTIONAL CHARTER DEPLOYMENT COMPLETE")
        print(f"Agent Label: {agent.label}")
        print(f"Ready for trading with five-layer gated logic enforcement")
        
        return agent
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all required components are available")
        return None
    except Exception as e:
        print(f"❌ Deployment error: {e}")
        return None

if __name__ == "__main__":
    agent = main()
    
    if agent:
        print(f"\n🎯 INSTITUTIONAL CHARTER ACTIVE")
        print("Use agent.place_institutional_trade() for all orders")
        print("Five-layer gated logic: ENFORCED")
        print("Autonomous auditor: RUNNING")
    else:
        print(f"\n❌ Deployment failed")