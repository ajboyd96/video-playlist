import os

base_path = "/Volumes/easystore/courses"
folders = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]

if not folders:
    print("No folders found.")
    exit()

print("Available folders:\n")
for idx, folder in enumerate(folders, 1):
    print(f"{idx}. {folder}")
