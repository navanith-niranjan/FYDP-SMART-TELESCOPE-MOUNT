import zipfile
import shutil
import os

# Check if the ZIP file exists in the current directory
zip_file = 'astap_command-line_version_Linux_aarch64.zip'

if not os.path.exists(zip_file):
    print(f"{zip_file} is not in the current directory. Please add the file and try again.")
else:
    # Unzip the CLI version
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall('./')

    # Move astap_cli to /usr/bin
    shutil.move('./astap_cli', '/usr/bin/astap_cli')

    print("ASTAP CLI installation complete! - Run astap_cli -h in the terminal for more information")