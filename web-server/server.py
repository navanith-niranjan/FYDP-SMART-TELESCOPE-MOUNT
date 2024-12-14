from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import asyncio
import serial

app = FastAPI()

origins = [
    "http://192.168.141.1:3000",
    "http://192.168.141.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.client_connections: List[WebSocket] = []
        self.esp32_connections: List[WebSocket] = []

    async def connect_client(self, websocket: WebSocket):
        await websocket.accept()
        self.client_connections.append(websocket)
        print("Client is connected!")

    # When websocket connection is established between server and ESP32, may not be needed if data is sent from server to ESP32 via serial communication
    # async def connect_esp32(self, websocket: WebSocket):
    #     await websocket.accept()
    #     self.esp32_connections.append(websocket)
    #     print("ESP32 is connected!")
    
    async def send_data_esp32(self, data):
        # Handle data transfer via wired connection between server and ESP32 
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

        await loop.run_in_executor(None, write_to_serial, data)

        # For sending data when ESP32 connected to wireless Network
        # for connection in self.esp32_connections:
        #     await connection.send_bytes(data)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.client_connections:
            self.client_connections.remove(websocket)
            print("Client is disconnected!")
        elif websocket in self.esp32_connections:
            self.esp32_connections.remove(websocket)
            print("ESP32 is disconnected!")

# Routing

@app.get("/")
async def get():
    return ""

# For D-Pad Movement in real-time using WebSockets
manager = ConnectionManager()

@app.websocket("/ws/client")
async def websocket_client(websocket: WebSocket):
    await manager.connect_client(websocket)
    
    try:
        while True:
            data = await websocket.receive_bytes()
            print(f"Received from client: {data}")
            await manager.send_data_esp32(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Needed if ESP32 is connected to wireless network
# @app.websocket("/ws/esp32")
# async def websocket_esp32(websocket: WebSocket):
#     await manager.connect_esp32(websocket)
#     try:
#         while True:
#             data = await websocket.receive_bytes()
#     except WebSocketDisconnect:
#         manager.disconnect(websocket)