
import os
import json
import subprocess

def get_process_status():
    """Checks if the master orchestrator is running."""
    try:
        result = subprocess.check_output(['pgrep', '-af', 'master_orchestrator.py'])
        return f"✅ ONLINE - Running process found:\n{result.decode('utf-8').strip()}"
    except subprocess.CalledProcessError:
        return "❌ OFFLINE - No running process found."

def get_config_status():
    """Reads key parameters from the charter."""
    try:
        with open("PhoenixV2/config/charter.py", "r") as f:
            content = f.read()
        
        # Extract values using simple string manipulation
        max_pos = next(line for line in content.split('\n') if 'MAX_CONCURRENT_POSITIONS' in line).split('=')[1].strip()
        min_conf = next(line for line in content.split('\n') if 'WOLF_MIN_CONFIDENCE' in line).split('=')[1].strip()
        min_sharpe = next(line for line in content.split('\n') if 'WOLF_MIN_TOP_SHARPE' in line).split('=')[1].strip()

        return (
            f"  - Max Concurrent Positions: {max_pos}\n"
            f"  - Min Signal Confidence: {min_conf}\n"
            f"  - Min Strategy Sharpe Ratio: {min_sharpe}"
        )
    except Exception as e:
        return f"⚠️ Could not read config file: {e}"

def main():
    """Prints the system status report."""
    print("==================================================")
    print("  📊 RICK SYSTEM STATUS REPORT")
    print("==================================================")
    
    print("\n[PROCESS STATUS]")
    print(f"  {get_process_status()}")
    
    print("\n[CURRENT TRADING PARAMETERS]")
    print(get_config_status())
    
    print("\n==================================================")

if __name__ == "__main__":
    main()
