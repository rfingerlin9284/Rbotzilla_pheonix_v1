import os
import shutil
import subprocess
import datetime

# ==============================================================================
# RICK PHOENIX: CRYO-FREEZE SNAPSHOT
# Captures State, Logic, Logs, and Diffs. Moves to Home Directory.
# ==============================================================================

def get_home_directory():
    return os.path.expanduser("~")

def run_git_snapshot():
    print("📜 GENERATING LOGIC DIFFS (GIT)...")
    # Initialize git if not present to track the 'Diffs' you asked for
    if not os.path.exists(".git"):
        subprocess.run(["git", "init"], stdout=subprocess.DEVNULL)
        subprocess.run(["git", "config", "user.email", "rick@phoenix.bot"], stdout=subprocess.DEVNULL)
        subprocess.run(["git", "config", "user.name", "RBotZilla"], stdout=subprocess.DEVNULL)
        subprocess.run(["git", "config", "commit.gpgSign", "false"], stdout=subprocess.DEVNULL)  # Disable GPG signing globally
    
    # Add everything and commit
    subprocess.run(["git", "add", "."], stdout=subprocess.DEVNULL)
    subprocess.run(["git", "commit", "-m", f"Snapshot {datetime.datetime.now()}"], stdout=subprocess.DEVNULL)
    print("✅ Logic State Committed.")

def create_archive(home):
    # Use a short date-only filename to avoid long numeric strings
    date_tag = datetime.datetime.now().strftime("%Y%m%d")
    base_filename = f"RICK_PHOENIX_SNAPSHOT_{date_tag}"
    filename = base_filename
    suffix = 1
    # If a file with this name already exists, append a small counter
    while os.path.exists(os.path.join(home, f"{filename}.tar.gz")):
        filename = f"{base_filename}_{suffix}"
        suffix += 1
    source_dir = os.getcwd()
    output_path = os.path.join(home, filename)
    
    print(f"📦 COMPRESSING TO: {filename}.tar.gz")
    
    # Create tar.gz
    shutil.make_archive(output_path, 'gztar', source_dir)
    
    final_path = output_path + ".tar.gz"
    if os.path.exists(final_path):
        print(f"🚀 EXFILTRATION SUCCESSFUL.")
        print(f"📍 Location: {final_path}")
    else:
        print("❌ Compression Failed.")

def main():
    print("❄️ INITIATING CRYO-FREEZE...")
    
    # 1. Find Target
    home = get_home_directory()

    # 2. Secure Diffs
    run_git_snapshot()

    # 3. Create Artifact
    create_archive(home)

if __name__ == "__main__":
    main()