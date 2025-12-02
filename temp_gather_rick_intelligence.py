import os
import shutil

def gather_rick_intelligence(temp_dirs, target_dir):
    """
    Temporarily gathers intelligence from specified directories and stores it in the target directory.

    Args:
        temp_dirs (list): List of directories to gather data from.
        target_dir (str): Directory to store the gathered data.
    """
    os.makedirs(target_dir, exist_ok=True)

    for temp_dir in temp_dirs:
        if os.path.exists(temp_dir):
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, temp_dir)
                    target_path = os.path.join(target_dir, relative_path)

                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    shutil.copy2(file_path, target_path)

if __name__ == "__main__":
    TEMP_DIRS = [
        "C:\\Users\\RFing\\temp_access_R_H_UNI_BLOAT_ARCHIVE",
        "C:\\Users\\RFing\\temp_access_RICK_LIVE_CLEAN",
        "C:\\Users\\RFing\\temp_access_Dev_unibot_v001",
        "C:\\Users\\RFing\\temp_access_R_H_UNI"
    ]
    TARGET_DIR = "/home/ing/RICK/RICK_LIVE_CLEAN/temp_intelligence"

    gather_rick_intelligence(TEMP_DIRS, TARGET_DIR)
    print(f"Intelligence gathered in {TARGET_DIR}. You can now review the data.")