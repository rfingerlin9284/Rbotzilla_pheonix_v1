import os

def print_tree(start_path, indent=""):
    # Get list of files and folders
    items = sorted(os.listdir(start_path))
    total_items = len(items)

    for index, item in enumerate(items):
        path = os.path.join(start_path, item)
        connector = "└── " if index == total_items - 1 else "├── "

        print(indent + connector + item)

        # If it's a directory, recurse
        if os.path.isdir(path):
            new_indent = indent + ("    " if index == total_items - 1 else "│   ")
            print_tree(path, new_indent)

if __name__ == "__main__":
    # Change this to the directory you want to scan
    root_dir = "/home/projects/viteapp/"

    if not os.path.exists(root_dir):
        print(f"Error: The directory '{root_dir}' does not exist.")
    else:
        print(os.path.basename(root_dir) + "/")
        print_tree(root_dir)
