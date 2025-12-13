#!/bin/bash
echo "🛑 Stopping all python processes..."
pkill -f "uvicorn main:app" || true
pkill -f "python3 backend/main.py" || true
pkill -f "backend/.venv/bin/python" || true

echo "🧹 Cleaning up..."
sleep 2

echo "🚀 Starting backend..."
nohup backend/.venv/bin/python3 backend/main.py > backend.log 2>&1 &
echo "Bot started! (PID: $!)"
echo "Check backend.log for output."
