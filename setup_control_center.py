# RICK PHOENIX V2: "CONTROL CENTER" INTEGRATION
# This script builds the unified, codeless management interface as per the user's core mandate.

import os
import json
import subprocess

print("🚀 Beginning RICK Control Center Integration...")

# ==========================================================================
# PART 1: CREATE THE CORE CONTROL CENTER APPLICATION
# ==========================================================================
# This is a menu-driven application that will become the primary way
# for the user to interact with the Phoenix system.

controller_dir = "controller"
if not os.path.exists(controller_dir):
    os.makedirs(controller_dir)

main_menu_code = r'''
import os
import subprocess
import time

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def run_script(script_path, title):
    """Executes a script and waits for user input to return."""
    clear_screen()
    print(f"==================================================")
    print(f"  Executing: {title}")
    print(f"==================================================")
    try:
        # We use subprocess.run to show live output and wait for completion
        subprocess.run(["python3", script_path], check=True)
    except FileNotFoundError:
        print(f"\n❌ ERROR: Script not found at '{script_path}'.")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ ERROR: Script '{script_path}' failed with exit code {e.returncode}.")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
    
    print("\nPress Enter to return to the main menu...")
    input()

def main_menu():
    """Displays the main menu and handles user choices."""
    while True:
        clear_screen()
        print("==================================================")
        print("  🚀 RICK HIVE AGENT - CONTROL CENTER")
        print("==================================================")
        print("  [1] Start System (Master Orchestrator)")
        print("  [2] Safe Shutdown")
        print("  [3] Adjust Trading Parameters")
        print("  [4] View Live Narration Log")
        print("  [5] Check System Status")
        print("\n  [x] Exit")
        print("==================================================")
        
        choice = input("Enter your choice: ").strip().lower()

        if choice == '1':
            clear_screen()
            print("Starting system in background...")
            # Use the existing shell script for consistency
            subprocess.run(["./start_phoenix.sh"])
            print("✅ System start command issued. Check logs for status.")
            time.sleep(3)
        elif choice == '2':
            clear_screen()
            print("Performing safe shutdown...")
            subprocess.run(["./safe_shutdown.sh"])
            print("✅ System shutdown command issued.")
            time.sleep(3)
        elif choice == '3':
            run_script("scripts/adjust_settings.py", "Adjust Trading Parameters")
        elif choice == '4':
            clear_screen()
            print("Starting live narration stream... (Press Ctrl+C to exit)")
            try:
                subprocess.run(["./scripts/rick_narration_stream.sh"])
            except KeyboardInterrupt:
                print("\nNarration stream stopped.")
            except Exception as e:
                print(f"\n❌ ERROR: Could not start narration stream: {e}")
            print("\nPress Enter to return to the main menu...")
            input()
        elif choice == '5':
            run_script("controller/system_status_check.py", "System Status Check")
        elif choice == 'x':
            print("Exiting Control Center. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
            time.sleep(2)

if __name__ == "__main__":
    main_menu()
'''

with open(os.path.join(controller_dir, "main_menu.py"), "w") as f:
    f.write(main_menu_code)
print("✅ Created controller/main_menu.py")


# ==========================================================================
# PART 2: CREATE A DEDICATED SCRIPT FOR SYSTEM STATUS CHECKS
# ==========================================================================
# This script provides a quick, readable overview of the system's health.

status_check_code = r'''
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
        # Try to find the config file in a few likely locations
        config_path = "PhoenixV2/config/charter.py"
        if not os.path.exists(config_path):
             # Fallback or alternative path if structure differs
             config_path = "config/charter.py"
        
        if not os.path.exists(config_path):
             return "⚠️ Config file not found at expected paths."

        with open(config_path, "r") as f:
            content = f.read()
        
        # Extract values using simple string manipulation
        # Using try-except blocks for individual extractions to be robust
        try:
            max_pos = next(line for line in content.split('\n') if 'MAX_CONCURRENT_POSITIONS' in line).split('=')[1].strip()
        except StopIteration:
            max_pos = "Not Found"
            
        try:
            min_conf = next(line for line in content.split('\n') if 'WOLF_MIN_CONFIDENCE' in line).split('=')[1].strip()
        except StopIteration:
            min_conf = "Not Found"

        try:
            min_sharpe = next(line for line in content.split('\n') if 'WOLF_MIN_TOP_SHARPE' in line).split('=')[1].strip()
        except StopIteration:
            min_sharpe = "Not Found"

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
'''

with open(os.path.join(controller_dir, "system_status_check.py"), "w") as f:
    f.write(status_check_code)
print("✅ Created controller/system_status_check.py")


# ==========================================================================
# PART 3: UPDATE VS CODE TASKS TO USE THE NEW CONTROL CENTER
# ==========================================================================
# This makes the Control Center the primary, easily accessible task.

tasks_file = os.path.join(".vscode", "tasks.json")
if not os.path.exists(".vscode"):
    os.makedirs(".vscode")

tasks_data = {
    "version": "2.0.0",
    "tasks": [
        {
            "label": "RICK: Control Center",
            "type": "shell",
            "command": "python3",
            "args": ["controller/main_menu.py"],
            "presentation": {
                "reveal": "always",
                "panel": "dedicated",
                "clear": True,
                "close": False
            },
            "problemMatcher": [],
            "detail": "🚀 Launch the main interactive menu to manage the entire system."
        },
        {
            "label": "RICK: Adjust Settings (Direct)",
            "type": "shell",
            "command": "python3",
            "args": ["scripts/adjust_settings.py"],
            "presentation": {
                "reveal": "always",
                "panel": "new",
            },
            "problemMatcher": [],
            "detail": "⚙️ Directly open the trading parameter adjustment tool."
        },
        {
            "label": "RICK: START SYSTEM (BACKGROUND)",
            "type": "shell",
            "command": "./start_phoenix.sh",
            "presentation": {
                "reveal": "silent"
            },
            "problemMatcher": [],
            "detail": "Starts the system without opening the menu."
        },
        {
            "label": "RICK: SAFE SHUTDOWN (BACKGROUND)",
            "type": "shell",
            "command": "./safe_shutdown.sh",
            "presentation": {
                "reveal": "silent"
            },
            "problemMatcher": [],
            "detail": "Stops the system without opening the menu."
        }
    ]
}

with open(tasks_file, "w") as f:
    json.dump(tasks_data, f, indent=4)
print(f"✅ Updated {tasks_file} with new 'RICK: Control Center' task.")


# ==========================================================================
# PART 4: PROVIDE A HAND-OFF PROMPT FOR A SPECIALIZED UI AGENT
# ==========================================================================
# This fulfills the user's directive to generate prompts for other AIs
# when they are better suited for a task.

ui_agent_prompt = '''
# PROMPT FOR A UI/UX DESIGN & FRONTEND DEVELOPMENT AI (e.g., GPT-4)

"""
You are an expert UI/UX designer and frontend developer specializing in creating simple, intuitive dashboards for complex systems.

**Objective:**
Design and provide the complete, single-file source code (HTML with inline CSS and JavaScript) for a simple, clean, and responsive web-based dashboard for a trading bot named "RICK". This dashboard is the graphical version of a text-based Python control center.

**Core Requirements:**

1.  **Simplicity is Key:** The user is non-technical. The interface must be extremely clear, with minimal clutter. Use large, easy-to-read fonts and clear iconography.
2.  **Single File:** All HTML, CSS, and JavaScript must be contained within a single `index.html` file for portability.
3.  **Layout:**
    *   A clean header: "RICK HIVE AGENT - CONTROL CENTER".
    *   **Left Pane (Status):**
        *   **System Status:** A large indicator (e.g., a colored circle) that is either GREEN ("ONLINE") or RED ("OFFLINE").
        *   **Current Parameters:** A simple, non-editable display of the key trading parameters (Max Positions, Min Confidence, Min Sharpe Ratio).
    *   **Right Pane (Actions):**
        *   A series of large, clearly labeled buttons for primary actions:
            *   `[▶️] START SYSTEM`
            *   `[⏹️] SAFE SHUTDOWN`
            *   `[⚙️] ADJUST SETTINGS`
            *   `[📄] VIEW LIVE LOGS`
4.  **Functionality (JavaScript):**
    *   The JavaScript does **NOT** need to perform the actions itself.
    *   Instead, when a button is clicked, it should show a clear "copy-able" command for the user to paste into their terminal.
    *   For example, clicking "START SYSTEM" should pop up a modal or a text area displaying: `Command to run in terminal: ./start_phoenix.sh` with a "Copy to Clipboard" button.
5.  **Styling:**
    *   Use a modern, clean, dark-themed aesthetic.
    *   Colors: Dark grays for the background, white/light-gray text, green for "ON/SUCCESS", red for "OFF/STOP", and a primary color (like a calm blue or purple) for buttons and highlights.

**Deliverable:**
Provide the complete and final `index.html` file containing all the necessary code to create this dashboard.
"""
'''

with open("prompt_for_ui_agent.txt", "w") as f:
    f.write(ui_agent_prompt)
print("✅ Created 'prompt_for_ui_agent.txt' for future web dashboard development.")

# ==========================================================================
# PART 5: FINAL CLEANUP & INSTRUCTIONS
# ==========================================================================
# Ensure all scripts are executable.

def make_executable(path):
    if os.path.exists(path):
        os.system(f"chmod +x {path}")
    else:
        print(f"⚠️ Warning: {path} not found, skipping chmod.")

make_executable("scripts/adjust_settings.py")
make_executable("scripts/rick_narration_stream.sh")
make_executable("start_phoenix.sh")
make_executable("safe_shutdown.sh")

print("\n\n✅ INTEGRATION COMPLETE.")
print("The 'RICK Control Center' is now the primary interface.")
print("To use it, open the VS Code Command Palette (Ctrl+Shift+P), type 'Run Task', and select 'RICK: Control Center'.")
