
import os
import sys
from pathlib import Path

def generate_project_structure(root_dir, ignore_dirs=None, ignore_files=None, max_depth=None, current_depth=0):
    if ignore_dirs is None:
        ignore_dirs = ['.git', '__pycache__', '.idea', '.vscode', 'venv', 'env', '.env']
    if ignore_files is None:
        ignore_files = ['.gitignore', '.DS_Store', '*.pyc', '*.pyo', '*.pyd', '*.so', '*.dll', '*.egg-info']
    
    structure = []
    root = Path(root_dir)
    
    if max_depth is not None and current_depth > max_depth:
        return structure
    
    try:
        # Sort directories first, then files
        items = sorted(root.iterdir(), key=lambda x: (not x.is_dir(), x.name))
        
        for item in items:
            # Skip ignored directories
            if item.is_dir() and any(ignore_pattern in item.name for ignore_pattern in ignore_dirs):
                continue
                
            # Skip ignored files
            if item.is_file() and any(
                item.name.endswith(ignore_pattern.replace('*', '')) 
                or item.name == ignore_pattern.replace('*', '') 
                for ignore_pattern in ignore_files
            ):
                continue
                
            if item.is_dir():
                sub_structure = generate_project_structure(
                    item, 
                    ignore_dirs, 
                    ignore_files, 
                    max_depth, 
                    current_depth + 1
                )
                if sub_structure:  # Only add non-empty directories
                    structure.append({item.name: sub_structure})
            else:
                structure.append(item.name)
                
    except PermissionError:
        pass  # Skip directories we don't have permission to read
        
    return structure

def print_structure(structure, indent=0):
    for item in structure:
        if isinstance(item, dict):
            for dir_name, contents in item.items():
                print('  ' * indent + '├── ' + dir_name + '/')
                print_structure(contents, indent + 1)
        else:
            print('  ' * indent + '├── ' + item)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        root_directory = sys.argv[1]
    else:
        root_directory = "."  # Current directory by default
        
    # Optional command line arguments
    max_depth = 3 # Set to a number to limit directory depth
    
    # Generate the structure
    
    root_directory = '/home/kit/anthropomatik/ln2554/diffusion_rl'
    structure = generate_project_structure(root_directory, max_depth=max_depth)
    
    # Print the root directory name
    print(os.path.basename(os.path.abspath(root_directory)) + '/')
    
    # Print the structure
    print_structure(structure) 