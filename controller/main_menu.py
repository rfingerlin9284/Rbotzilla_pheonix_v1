
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
