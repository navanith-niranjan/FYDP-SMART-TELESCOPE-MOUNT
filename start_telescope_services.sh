#!/bin/bash
source venv/bin/activate

echo "Running calibrate.py..."
cd astap/
python3 calibrate.py & 

echo "Starting FastAPI server..."
cd ../web-server
uvicorn server:app --host 0.0.0.0 --port 8000 &

echo "Starting Vite React frontend..."
cd ../web-client
npm run dev -- --host 0.0.0.0 