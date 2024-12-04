from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import asyncio
import serial

from fastapi.responses import HTMLResponse

app = FastAPI()

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
            port = 'COM5'
            baudrate = 115200 # Replace with your ESP32's baud rate
            try:
                with serial.Serial(port, baudrate, timeout=1) as ser:
                    ser.write(data)
                    ser.flush()  
            except serial.SerialException as e:
                print(f"Serial communication error: {e}")

        # Run the blocking serial write operation in an executor
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

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>TEST ENVIRONMENT</title>
    </head>
    <body style="background-color: #FF474C;">
        <h1>CLIENT</h1>
        <div class="dpad">
            <button class="dpad-button" onclick="sendCommand('up')">UP</button>
            <div class="dpad-row">
                <button class="dpad-button" onclick="sendCommand('left')">LEFT</button>
                <button class="dpad-button" onclick="sendCommand('right')">RIGHT</button>
            </div>
            <button class="dpad-button" onclick="sendCommand('down')">DOWN</button>
        </div>
        <script>
            var ws = new WebSocket("ws://" + window.location.host + "/ws/client");
            
            console.log(window.location.host)

            ws.binaryType = "arraybuffer";

            ws.onopen = function(event) {
                console.log("WebSocket is open now.");
            };

            ws.onclose = function(event) {
                console.log("WebSocket is closed now.");
            };

            function sendCommand(direction) {
                let commandCode = getCommandCode(direction);
                let buffer = new Uint8Array([commandCode]);
                ws.send(buffer);
            }

            function getCommandCode(direction) {
                switch(direction) {
                    case 'up':
                        return 1;
                    case 'down':
                        return 2;
                    case 'left':
                        return 3;
                    case 'right':
                        return 4;
                    default:
                        return 0;
                }
            }
        </script>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

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