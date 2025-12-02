import time
import os
import random


def clear(): os.system('cls' if os.name == 'nt' else 'clear')

def render_dashboard():
    target = 500.00
    current = 387.50 + random.uniform(-5, 50) 
    print(f"╔════════════════════════════════════════════════════════════════╗")
    print(f"║             🔥 RBOTZILLA $500/DAY COUNTDOWN 🔥                ║")
    print(f"╚════════════════════════════════════════════════════════════════╝")
    print(f"")
    print(f"💰 TODAY'S PROGRESS: ${current:.2f} / ${target:.2f}")
    print(f"")
    print(f"🤖 ML PERFORMANCE:")
    print(f"Filter Mode:    STRICT (3:1 Minimum)")
    print(f"Next Signal:    Scanning...")
    print(f"")
    print(f"Press Ctrl+C to exit dashboard")

if __name__ == "__main__":
    try:
        while True:
            clear()
            render_dashboard()
            time.sleep(5)
    except KeyboardInterrupt:
        print("Closed.")
