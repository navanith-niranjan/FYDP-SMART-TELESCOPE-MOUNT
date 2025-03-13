#!/bin/bash

# Activate virtual environment
cd /home/pi/repos/fydp-smart-telescope-mount
source venv/bin/activate

# Running calibrate.py
echo "Running calibrate.py..."
cd /home/pi/repos/fydp-smart-telescope-mount/astap
python3 calibrate.py & 

# Starting FastAPI server
echo "Starting FastAPI server..."
cd /home/pi/repos/fydp-smart-telescope-mount/web-server
uvicorn server:app --host 0.0.0.0 --port 8000 &

# Starting Vite React frontend
echo "Starting Vite React frontend..."
cd /home/pi/repos/fydp-smart-telescope-mount/web-client
npm run dev -- --host 0.0.0.0 