import os
import shutil
import subprocess
import time

# Directories
script_dir = os.path.dirname(os.path.abspath(__file__))
unstaged_dir = os.path.join(script_dir, "images", "unstaged")
staged_dir = os.path.join(script_dir, "images", "staged")
database_location = os.path.join(script_dir, "databases")
output_location = os.path.join(script_dir, "output")
astap_cli = "/usr/bin/astap_cli"

# Allowed file extensions
allowed_extensions = {".jpg", ".png", ".fits"}

# Function to process each image
def process_image(image_path):
    output_file = os.path.join(output_location, os.path.basename(image_path))

    cmd = [
           astap_cli, 
           "-f", image_path, 
           "-r", "60", 
           "-fov", "0", 
           "-d", database_location, 
           "-D", "w08", 
           "-o", output_file,
           "-log",
        ]

    try:
        print(f"Processing {image_path}...")
        subprocess.run(cmd, check=True)
        print(f"Solution found for {image_path}")
        return True
    except subprocess.CalledProcessError:
        print(f"Error processing {image_path}")
        return False

def process_all_images():
    images = [f for f in os.listdir(unstaged_dir) if os.path.isfile(os.path.join(unstaged_dir, f)) and os.path.splitext(f)[1].lower() in allowed_extensions]
    
    for image in images:
        image_path = os.path.join(unstaged_dir, image)
        
        if process_image(image_path):
            staged_image_path = os.path.join(staged_dir, image)
            shutil.move(image_path, staged_image_path)
            print(f"{image} has been processed and was moved to staged folder.")

while True:
    process_all_images()
    time.sleep(10)