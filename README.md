# Smart Telescope Mount

**University of Waterloo Mechanical Engineering — Final Year Capstone Project (2025)**

An automated smart telescope mount that uses plate-solving, IMU feedback, and custom kinematics to autonomously point a telescope at any celestial object selected through a web app. The mount is driven by DC motors with encoder feedback, controlled by ESP32 microcontrollers running real-time kinematic solvers, and managed by a Raspberry Pi 5 running the plate-solving pipeline and web server.

---

## How It Works

1. **Attach** your telescope to the custom 3-axis mount (pitch, roll, yaw driven by DC motors through custom gears).
2. **Calibrate** — point the telescope at a known region of sky, capture an image, and upload it through the web app. ASTAP runs plate-solving on the Raspberry Pi to determine the telescope's exact pointing coordinates (RA/Dec).
3. **Select a target** from the Messier catalog in the web app and tap "Start Tracking".
4. The Raspberry Pi converts the target's RA/Dec to azimuth/altitude, then the ESP32 applies rotation matrices to compute the required pitch, roll, and yaw motor commands.
5. The mount drives the motors to the correct angles and holds the target in frame.

Sun and Moon tracking are also supported as special modes.

---

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│              Web App  (React + TypeScript)           │
│   Calibrate | Messier Catalog | Manual Settings      │
└───────────────────────┬─────────────────────────────┘
                        │  HTTP / Axios
                        │  POST /api/upload/   ← image for plate-solving
                        │  POST /api/locate/   ← target RA/Dec
                        │  POST /api/calibrate/ ← manual RA/Dec override
                        ▼
┌─────────────────────────────────────────────────────┐
│        FastAPI Server  (Raspberry Pi 5)             │
│   - Coordinate conversion  (astropy)                │
│   - Packs RA/Dec as binary and sends over serial    │
└───────────────────────┬─────────────────────────────┘
       ┌────────────────┤ Serial /dev/ttyUSB0 @ 115200
       │                │
       │  ┌─────────────▼────────────────────────────┐
       │  │  ASTAP Calibration Daemon  (calibrate.py) │
       │  │  - Watches for new images                 │
       │  │  - Runs astap_cli plate-solving           │
       │  │  - Extracts RA/Dec from .wcs files        │
       │  │  - Sends calibration message over serial  │
       │  └──────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────┐
│           ESP32  (Motor Controller)                  │
│   - Receives binary coordinate commands             │
│   - Rotation matrix kinematics (Alt/Az → P/R/Y)    │
│   - PID control of DC motors via encoders           │
│   - IMU sensor fusion for orientation feedback      │
└─────────────────────────────────────────────────────┘
```

---

## Hardware

| Component | Details |
|---|---|
| Compute | Raspberry Pi 5 |
| Motor controllers | ESP32 microcontrollers |
| Actuators | DC motors with quadrature encoders |
| Gearing | Custom-designed gear train |
| Orientation sensor | IMU (accelerometer + gyroscope) |
| Axes | Pitch, Roll, Yaw (3-axis) |

---

## Software Stack

**Backend (Raspberry Pi)**
- Python 3, FastAPI, Uvicorn
- `astropy` — RA/Dec coordinate conversions
- `pyserial` — serial communication with ESP32
- `opencv-contrib-python` — image handling
- ASTAP CLI — plate-solving engine

**Frontend (Web App)**
- React 18 + TypeScript, Vite
- TailwindCSS + shadcn/ui (Radix UI)
- Axios for API calls
- Messier catalog (110+ objects) served as CSV

**Firmware (ESP32)**
- Kinematic solver using rotation matrices to convert Alt/Az coordinates to motor pitch/roll/yaw angles
- Real-time PID motor control with encoder feedback
- IMU sensor fusion for closed-loop orientation

---

## Serial Communication Protocol

All messages between the Raspberry Pi and ESP32 use this binary framing:

```
[0x01] [TYPE] [RA — 8 bytes, little-endian double] [DEC — 8 bytes, little-endian double] [CHECKSUM] [0xFF]
```

| TYPE | Meaning |
|---|---|
| `0x01` | Calibration — tells ESP32 where the telescope is currently pointing |
| `0x02` | Locate — tells ESP32 where to move to |

Special shorthand messages (no coordinate payload):
- **Sun tracking:** `[0x01, 0x02, 0x01, 0xFF]`
- **Moon tracking:** `[0x01, 0x02, 0x02, 0xFF]`

Checksum is the 8-bit sum of all data bytes (excluding start and end bytes).

---

## Project Structure

```
fydp-smart-telescope-mount/
├── astap/
│   ├── calibrate.py          # Plate-solving daemon — watches for images, runs ASTAP, returns RA/Dec
│   ├── images/
│   │   ├── unstaged/         # Drop images here for processing
│   │   └── staged/           # Processed images moved here
│   ├── databases/            # ASTAP star catalogue databases
│   ├── output/               # WCS (World Coordinate System) output files
│   └── install/
│       └── install_cli.py    # ASTAP CLI installer helper
├── web-server/
│   └── server.py             # FastAPI backend — REST API + serial interface
├── web-client/
│   ├── src/
│   │   ├── App.tsx           # Root component — tab layout
│   │   ├── components/
│   │   │   ├── Calibrate.tsx     # Image upload + plate-solve UI
│   │   │   ├── Catalog.tsx       # Messier object selector + tracking trigger
│   │   │   └── SettingsMenu.tsx  # Manual RA/Dec calibration override
│   └── public/
│       └── messier_catalog.csv   # Messier catalog data (110+ objects)
├── requirements.txt
└── start_telescope_services.sh   # Starts all services on the Pi
```

---

## Setup & Installation

### 1. Install ASTAP CLI (on Raspberry Pi)

Download the ARM64 build and place it in `./astap/install/`:

```
astap_command-line_version_Linux_aarch64.zip
```

Download: https://sourceforge.net/projects/astap-program/files/linux_installer/astap_command-line_version_Linux_aarch64.zip/download

Then run the installer and make it executable:

```bash
python astap/install/install_cli.py
sudo chmod +x /usr/bin/astap_cli
```

Place the ASTAP star database files in `astap/databases/`.

### 2. Install Python dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Install frontend dependencies

```bash
cd web-client
npm install
```

### 4. Start all services

```bash
bash start_telescope_services.sh
```

This activates the virtual environment, starts the `calibrate.py` plate-solving daemon in the background, starts the FastAPI server on port 8000, and starts the Vite dev server on port 5173.

---

## Usage

1. Open the web app at `http://<raspberry-pi-ip>:5173`
2. **Calibrate tab** — take a photo of the current sky through the telescope eyepiece, upload it, and wait for plate-solving to determine the pointing coordinates.
3. **Locate tab** — browse or search the Messier catalog, select a target, and press "Start Tracking".
4. **Settings tab** — manually enter RA/Dec if you already know the telescope's current pointing (bypasses plate-solving).

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/upload/` | Upload sky image for plate-solving calibration |
| POST | `/api/locate/` | Send target RA/Dec (or Sun/Moon) to mount |
| POST | `/api/calibrate/` | Manually set current pointing RA/Dec |
