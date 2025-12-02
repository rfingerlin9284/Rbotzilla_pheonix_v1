import os
import zipfile
import datetime

def consolidate_system():
    output_filename = "PHOENIX_V2_CONSOLIDATED.zip"
    mega_readme_content = "# PHOENIX V2 MEGA README\n\n"
    
    print(f"Creating consolidated archive: {output_filename}")
    
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 1. Consolidate Markdown Files
        print("Consolidating Markdown files...")
        for root, dirs, files in os.walk("."):
            if "_CONSOLIDATION_BACKUP" in root or ".git" in root or "venv" in root:
                continue
            for file in files:
                if file.endswith(".md"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            mega_readme_content += f"\n\n## FILE: {file}\n\n{content}\n\n---\n"
                    except Exception as e:
                        print(f"Skipping {file}: {e}")
        
        # Write Mega Readme to Zip
        zipf.writestr("MEGA_README.md", mega_readme_content)
        
        # 2. Consolidate Code by Category
        categories = {
            "strategies": "PhoenixV2/strategies",
            "engines": "PhoenixV2/execution",
            "operations": "PhoenixV2/operations",
            "core": "PhoenixV2/core",
            "config": "PhoenixV2/config"
        }
        
        for cat_name, cat_path in categories.items():
            if os.path.exists(cat_path):
                print(f"Consolidating {cat_name}...")
                consolidated_code = f"# CONSOLIDATED {cat_name.upper()} MODULES\n\n"
                for root, dirs, files in os.walk(cat_path):
                    for file in files:
                        if file.endswith(".py"):
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                    consolidated_code += f"\n\n# === FILE: {file} ===\n\n{content}\n"
                            except Exception as e:
                                print(f"Skipping {file}: {e}")
                zipf.writestr(f"{cat_name}_consolidated.py", consolidated_code)
        
        # 3. Add Full Source Tree (excluding junk)
        print("Adding full source tree...")
        for root, dirs, files in os.walk("."):
            if "_CONSOLIDATION_BACKUP" in root or ".git" in root or "venv" in root or "__pycache__" in root:
                continue
            for file in files:
                if file.endswith(".zip"):
                    continue
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, "."))

    print(f"✅ Archive created: {output_filename}")

if __name__ == "__main__":
    consolidate_system()
