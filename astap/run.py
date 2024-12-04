import os
import shutil
import subprocess
import time

# Directories
unstaged_dir = "images/unstaged"
staged_dir = "images/staged"
database_location = "databases"
astap_cli = "/usr/bin/astap_cli"

# Function to process each image
def process_image(image_path):
    cmd = [astap_cli, "-f", image_path, "-d", database_location, "-D", "w08"]

    try:
        print(f"Processing {image_path}...")
        subprocess.run(cmd, check=True)
        print(f"Solution found for {image_path}")
        return True
    except subprocess.CalledProcessError:
        print(f"Error processing {image_path}")
        return False

def process_all_images():
    images = [f for f in os.listdir(unstaged_dir) if os.path.isfile(os.path.join(unstaged_dir, f))]
    
    for image in images:
        image_path = os.path.join(unstaged_dir, image)
        
        if process_image(image_path):
            staged_image_path = os.path.join(staged_dir, image)
            shutil.move(image_path, staged_image_path)
            print(f"Moved {image} to staged folder.")

while True:
    process_all_images()
    time.sleep(10)