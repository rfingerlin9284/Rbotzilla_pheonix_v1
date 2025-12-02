#!/usr/bin/env python3
"""
Interactive Configuration Manager for RICK Phoenix V2.
Allows non-coders to adjust system settings safely.
"""

import os
import re
import sys

CHARTER_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "PhoenixV2/config/charter.py")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def read_charter():
    if not os.path.exists(CHARTER_PATH):
        print(f"Error: Could not find {CHARTER_PATH}")
        sys.exit(1)
    with open(CHARTER_PATH, 'r') as f:
        return f.read()

def update_charter(content, setting, new_value, comment=""):
    # Regex to find the setting assignment
    # Looks for: SETTING_NAME = value # comment
    pattern = fr"({setting}\s*=\s*)([^#\n]+)(.*)"
    
    match = re.search(pattern, content)
    if match:
        # Construct new line: SETTING = new_value # comment
        current_comment = match.group(3)
        if comment:
            new_line = f"{match.group(1)}{new_value} # {comment}"
        else:
            # Keep existing comment if no new one provided, or add one if missing
            new_line = f"{match.group(1)}{new_value}{current_comment}"
        
        new_content = content.replace(match.group(0), new_line)
        
        with open(CHARTER_PATH, 'w') as f:
            f.write(new_content)
        return True
    return False

def get_current_value(content, setting):
    pattern = fr"{setting}\s*=\s*([^#\n]+)"
    match = re.search(pattern, content)
    if match:
        return match.group(1).strip()
    return "Unknown"

def main():
    while True:
        clear_screen()
        content = read_charter()
        
        max_pos = get_current_value(content, "MAX_CONCURRENT_POSITIONS")
        wolf_conf = get_current_value(content, "WOLF_MIN_CONFIDENCE") # Note: This might be inside a getenv
        wolf_sharpe = get_current_value(content, "WOLF_MIN_TOP_SHARPE")
        
        # Handle the getenv case for WOLF_MIN_CONFIDENCE if strictly parsed
        # The file has: WOLF_MIN_CONFIDENCE = float(os.getenv('WOLF_MIN_CONFIDENCE', '0.60'))
        # We want to extract the default value '0.60'
        wolf_conf_match = re.search(r"WOLF_MIN_CONFIDENCE.*'([\d\.]+)'\)\)", content)
        if wolf_conf_match:
            wolf_conf = wolf_conf_match.group(1)

        print("==================================================")
        print("🎛️  RICK PHOENIX V2 - SETTINGS CONTROL PANEL")
        print("==================================================")
        print(f"1. Max Concurrent Positions  [Current: {max_pos}]")
        print(f"2. WolfPack Confidence       [Current: {wolf_conf}]")
        print(f"3. WolfPack Min Sharpe       [Current: {wolf_sharpe}]")
        print("4. Exit")
        print("==================================================")
        
        choice = input("\nSelect an option (1-4): ")
        
        if choice == '1':
            new_val = input("\nEnter new Max Positions (e.g., 6, 12): ")
            if new_val.isdigit():
                if update_charter(content, "MAX_CONCURRENT_POSITIONS", new_val, "User Adjusted via Menu"):
                    print("✅ Updated successfully!")
                else:
                    print("❌ Failed to update.")
            else:
                print("❌ Invalid input. Must be a number.")
            input("\nPress Enter to continue...")

        elif choice == '2':
            new_val = input("\nEnter new Confidence (0.0 to 1.0, e.g., 0.60): ")
            try:
                val = float(new_val)
                if 0 <= val <= 1.0:
                    # Special handling for the getenv line
                    # We replace the default value inside the getenv call
                    old_line_pattern = r"(WOLF_MIN_CONFIDENCE.*os\.getenv.*, ')([\d\.]+)('\)\))"
                    if re.search(old_line_pattern, content):
                        new_content = re.sub(old_line_pattern, f"\\g<1>{new_val}\\g<3>", content)
                        with open(CHARTER_PATH, 'w') as f:
                            f.write(new_content)
                        print("✅ Updated successfully!")
                    else:
                        print("❌ Could not find the configuration line pattern.")
                else:
                    print("❌ Value must be between 0.0 and 1.0")
            except ValueError:
                print("❌ Invalid number.")
            input("\nPress Enter to continue...")

        elif choice == '3':
            new_val = input("\nEnter new Min Sharpe Ratio (e.g., 0.5, 1.0): ")
            try:
                float(new_val)
                if update_charter(content, "WOLF_MIN_TOP_SHARPE", new_val, "User Adjusted via Menu"):
                    print("✅ Updated successfully!")
                else:
                    print("❌ Failed to update.")
            except ValueError:
                print("❌ Invalid number.")
            input("\nPress Enter to continue...")

        elif choice == '4':
            print("Exiting...")
            break

if __name__ == "__main__":
    main()
