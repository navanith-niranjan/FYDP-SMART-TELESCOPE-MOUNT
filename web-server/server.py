from fastapi import FastAPI, Form, File, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import shutil
import os
import time
import asyncio
import serial
import json
import struct
from astropy.coordinates import Angle
from astropy import units as u

app = FastAPI()

origins = [
    "http://telescope.io", # Frontend served via nginx
    "http://192.168.141.1:3000",
    "http://192.168.141.1:5173",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routing
@app.get("/")
async def get():
    return ""

UPLOAD_FOLDER = os.path.join("..", "astap", "images", "unstaged")
STATUS_FILE = os.path.join("..", "astap", "status.json")

@app.post("/api/upload/")
async def upload_image(file: UploadFile = File(...)):
    if not os.path.exists(UPLOAD_FOLDER):
        print
        raise FileNotFoundError(f"The unstaged folder does not exist: {UPLOAD_FOLDER}")

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print({"message": f"File saved to {file_path}"})

        start_time = time.time()
        while time.time() - start_time < 30:
            if os.path.exists(STATUS_FILE):
                with open(STATUS_FILE, "r") as f:
                    status_data = json.load(f)
                
                if status_data.get("image") == file.filename:
                    if status_data.get("status") == "success":
                        return {"message": "Calibration Successful!", "ra": status_data.get("ra"), "dec": status_data.get("dec")}
                    elif status_data.get("status") == "failure":
                        return {"message": "Calibration Failed"}

            time.sleep(1)

        return {"message": "Calibration Timeout"}

    except Exception as e:
        print({"Error": str(e)})

@app.post("/api/locate/")
async def send_object(rightAscension: str = Form(...), declination: str = Form(...)):
    # Configure so that it recieves ra and dec, converts to decimals, converts to bytes, send via serial
    try:
        if rightAscension == "Sun" or rightAscension == "Moon":

            if rightAscension == "Sun":
                message = bytearray([0x01, 0x02, 0x01, 0xFF])
            elif rightAscension == "Moon":
                message = bytearray([0x01, 0x02, 0x02, 0xFF])

            def write_to_serial(data):
                port = '/dev/ttyUSB0'
                baudrate = 115200
                try:
                    with serial.Serial(port, baudrate, timeout=1) as ser:
                        ser.write(data)
                        ser.flush()  
                except serial.SerialException as e:
                    print(f"Serial communication error: {e}")

            await loop.run_in_executor(None, write_to_serial, bytes(message))

            print("Requesting Sun or Moon Tracking...")

        else:
            ra_deg = Angle(rightAscension, unit=u.hourangle).degree
            dec_deg = Angle(declination, unit=u.deg).degree

            def compute_checksum(data):
                checksum = 0
                for byte in data:
                    checksum += byte
                checksum &= 0xFF
                return checksum

            start_byte = 0x01
            type_byte = 0x02
            end_byte = 0xFF
            
            ra_bytes = struct.pack('d', ra_deg)
            dec_bytes = struct.pack('d', dec_deg)

            message = bytearray([start_byte, type_byte])
            message.extend(ra_bytes)
            message.extend(dec_bytes)
            checksum = compute_checksum(message)
            message.extend([checksum])
            message.extend([end_byte])

            loop = asyncio.get_event_loop()

            def write_to_serial(data):
                port = '/dev/ttyUSB0'
                baudrate = 115200
                try:
                    with serial.Serial(port, baudrate, timeout=1) as ser:
                        ser.write(data)
                        ser.flush()  
                except serial.SerialException as e:
                    print(f"Serial communication error: {e}")

            await loop.run_in_executor(None, write_to_serial, bytes(message))
            
            print("Bytes:", ' '.join(f'{byte:02X}' for byte in message))

    except Exception as e:
        return f"Error with api request to locate object: {e}"

@app.post("/api/calibrate/")
async def send_calibration(ra: str = Form(...), dec: str = Form(...)):
    try:
        ra_deg = Angle(ra, unit=u.deg).degree
        dec_deg = Angle(dec, unit=u.deg).degree

        def compute_checksum(data):
            checksum = 0
            for byte in data:
                checksum += byte
            checksum &= 0xFF
            return checksum

        start_byte = 0x01
        type_byte = 0x01 # Calibration Type is 0x01
        end_byte = 0xFF
        
        ra_bytes = struct.pack('d', ra_deg)
        dec_bytes = struct.pack('d', dec_deg)

        message = bytearray([start_byte, type_byte])
        message.extend(ra_bytes)
        message.extend(dec_bytes)
        checksum = compute_checksum(message)
        message.extend([checksum])
        message.extend([end_byte])

        loop = asyncio.get_event_loop()

        def write_to_serial(data):
            port = '/dev/ttyUSB0'
            baudrate = 115200
            try:
                with serial.Serial(port, baudrate, timeout=1) as ser:
                    ser.write(data)
                    ser.flush()  
            except serial.SerialException as e:
                print(f"Serial communication error: {e}")

        await loop.run_in_executor(None, write_to_serial, bytes(message))
        
        print("Bytes:", ' '.join(f'{byte:02X}' for byte in message))

    except Exception as e:
        return f"Error with api request to locate object: {e}"
    
# class ConnectionManager:
#     def __init__(self):
#         self.client_connections: List[WebSocket] = []
#         self.esp32_connections: List[WebSocket] = []

#     async def connect_client(self, websocket: WebSocket):
#         await websocket.accept()
#         self.client_connections.append(websocket)
#         print("Client is connected!")

#     # When websocket connection is established between server and ESP32, may not be needed if data is sent from server to ESP32 via serial communication
#     # async def connect_esp32(self, websocket: WebSocket):
#     #     await websocket.accept()
#     #     self.esp32_connections.append(websocket)
#     #     print("ESP32 is connected!")
    
#     async def send_data_esp32(self, data):
#         # Handle data transfer via wired connection between server and ESP32 
#         loop = asyncio.get_event_loop()

#         def write_to_serial(data):
#             port = '/dev/ttyUSB0'
#             baudrate = 115200
#             try:
#                 with serial.Serial(port, baudrate, timeout=1) as ser:
#                     ser.write(data)
#                     ser.flush()  
#             except serial.SerialException as e:
#                 print(f"Serial communication error: {e}")

#         await loop.run_in_executor(None, write_to_serial, data)

#         # For sending data when ESP32 connected to wireless Network
#         # for connection in self.esp32_connections:
#         #     await connection.send_bytes(data)

#     def disconnect(self, websocket: WebSocket):
#         if websocket in self.client_connections:
#             self.client_connections.remove(websocket)
#             print("Client is disconnected!")
#         elif websocket in self.esp32_connections:
#             self.esp32_connections.remove(websocket)
#             print("ESP32 is disconnected!")

# # For D-Pad Movement in real-time using WebSockets
# manager = ConnectionManager()

# @app.websocket("/ws/client")
# async def websocket_client(websocket: WebSocket):
#     await manager.connect_client(websocket)
    
#     try:
#         while True:
#             data = await websocket.receive_bytes()
#             print(f"Received from client: {data}")
#             await manager.send_data_esp32(data)
#     except WebSocketDisconnect:
#         manager.disconnect(websocket)

# Needed if ESP32 is connected to wireless network
# @app.websocket("/ws/esp32")
# async def websocket_esp32(websocket: WebSocket):
#     await manager.connect_esp32(websocket)
#     try:
#         while True:
#             data = await websocket.receive_bytes()
#     except WebSocketDisconnect:
#         manager.disconnect(websocket)