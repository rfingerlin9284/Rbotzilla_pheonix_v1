import os
import sys
import time
import subprocess
from dotenv import load_dotenv

def main():
    load_dotenv()
    print("🚀 MASTER ORCHESTRATOR: Launching Phoenix V2 Engine...")
    while True:
        try:
            # Launch the main engine
            # We use sys.executable to ensure we use the same python interpreter
            # Pass the current environment which now includes .env vars
            # Use -u for unbuffered output
            process = subprocess.Popen([sys.executable, "-u", "PhoenixV2/main.py"], env=os.environ)
            process.wait()
            
            print("⚠️ Phoenix V2 Engine exited. Restarting in 5 seconds...")
            time.sleep(5)
        except KeyboardInterrupt:
            print("🛑 Master Orchestrator stopping.")
            break
        except Exception as e:
            print(f"❌ Error in orchestrator: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
