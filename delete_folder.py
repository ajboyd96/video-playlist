import os
import shutil
import sys

base_path = "/Volumes/easystore/courses"

# Get all folders
folders = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]

if not folders:
    print("No folders found.")
    exit()

# If folder number is passed as an argument
if len(sys.argv) < 2:
    print("Usage: python3 delete_folder.py [folder_number]")
    print("Available folders:")
    for idx, folder in enumerate(folders, 1):
        print(f"{idx}. {folder}")
    exit()

try:
    selection = int(sys.argv[1])
    selected_folder = folders[selection - 1]
except (ValueError, IndexError):
    print("Invalid folder number.")
    exit()

# Confirm (bypassable in headless script)
confirm = "yes"  # hardcoded for Shortcut use

if confirm.lower() != "yes":
    print("Cancelled.")
    exit()

# Delete the folder
folder_path = os.path.join(base_path, selected_folder)
try:
    shutil.rmtree(folder_path)
    print(f"Deleted folder: {selected_folder}")
except Exception as e:
    print(f"Error deleting folder: {e}")
