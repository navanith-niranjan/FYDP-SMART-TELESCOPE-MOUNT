import os
import shutil
import subprocess
import time
import serial
import struct
from astropy.coordinates import Angle
from astropy import units as u

# Directories
script_dir = os.path.dirname(os.path.abspath(__file__))
unstaged_dir = os.path.join(script_dir, "images", "unstaged")
staged_dir = os.path.join(script_dir, "images", "staged")
database_location = os.path.join(script_dir, "databases")
output_location = os.path.join(script_dir, "output")
astap_cli = "/usr/bin/astap_cli"

# Allowed file extensions
allowed_extensions = {".jpg", ".png", ".fits"}

# ESP32 Configuration
port = '/dev/ttyUSB0'
baudrate = 115200

# Function to send RA and DEC to the ESP32
def write_to_serial(data):
    try:
        with serial.Serial(port, baudrate, timeout=1) as ser:
            ser.write(data)
            ser.flush()
            return True
    except serial.SerialException as e:
        print(f"Serial communication error: {e}")
        return False

# TESTING PURPOSES ONLY
# def read_serial():
#     try:
#         with serial.Serial(port, baudrate, timeout=1) as ser:
#             print("Listening for data from ESP32...")
#             while True:
#                 if ser.in_waiting > 0:
#                     data = ser.read_until(b'\xFF')  # Read until the end byte
#                     print(f"Received: {data}")
#     except serial.SerialException as e:
#         print(f"Error opening serial port: {e}")

# Function to extract RA and Dec from a .wcs file
def extract_from_wcs(wcs_file):
    try:
        with open(wcs_file, 'r') as file:
            lines = file.readlines()

        ra_deg = None
        dec_deg = None

        for line in lines:
            if 'CRVAL1' in line:
                ra_deg = float(line.split('=')[1].strip().split()[0])
            elif 'CRVAL2' in line:
                dec_deg = float(line.split('=')[1].strip().split()[0])

        if ra_deg is not None and dec_deg is not None:
            ra_angle = Angle(ra_deg, u.deg)
            ra_hms = ra_angle.to_string(unit=u.hour, sep=' ', precision=1)
            dec_angle = Angle(dec_deg, u.deg)
            dec_dms = dec_angle.to_string(unit=u.deg, sep=' ', alwayssign=True, precision=0)

            # Construct the message
            def compute_checksum(data):
                checksum = 0
                for byte in data:
                    checksum += byte
                checksum &= 0xFF  # Ensure the checksum is 1 byte (8 bits)
                return checksum

            start_byte = 0x01
            type_byte = 0x01
            end_byte = 0xFF
            
            # RA and DEC converted from angle to bytes
            ra_bytes = struct.pack('f', ra_deg)
            dec_bytes = struct.pack('f', dec_deg)

            message = bytearray([start_byte, type_byte])
            message.extend(ra_bytes)
            message.extend(dec_bytes)
            checksum = compute_checksum(message)
            message.extend([checksum])
            message.extend([end_byte])

            # Send the data to ESP32
            if write_to_serial(bytes(message)):
                # read_serial() # FOR TESTING PURPOSES ONLY
                print(message)
                return "Calibration data successfully sent to ESP32."
            else:
                return "Error: Failed to send data to ESP32."
    
        else:
            return "RA/Dec not found in the .wcs file."
        
    except Exception as e:
        return f"Error reading WCS file: {e}"

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
        ]

    try:
        print(f"Processing {image_path}...")
        subprocess.run(cmd, check=True)
        print(f"Solution found for {image_path}")

        wcs_file = os.path.join(output_location, os.path.splitext(os.path.basename(image_path))[0] + ".wcs")
        solution = extract_from_wcs(wcs_file)
        print(solution)

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