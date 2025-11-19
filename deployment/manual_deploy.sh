#!/bin/bash
# Manual deployment script for FTP server
# This script: pulls latest code, stops old server, starts new server

set -e  # Exit on error

echo "=== FTP Server Manual Deployment ==="

# Get the project root directory (assuming script is in deployment/)
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "[1/3] Pulling latest code from git..."
git pull origin main

echo "[2/3] Stopping old server processes..."
# Kill any existing FTP server processes
pkill -f "python3.*ftp_server.py" || echo "No existing server process found"

# Wait a moment for processes to terminate
sleep 2

echo "[3/3] Starting new server..."
# Set PYTHONPATH and start server in background
export PYTHONPATH="${PYTHONPATH}:${PROJECT_ROOT}"
FTP_PORT=21 nohup python3 server/ftp_server.py > server.log 2>&1 &

# Get the PID
SERVER_PID=$!
echo "Server started with PID: $SERVER_PID"
echo "Server logs: $PROJECT_ROOT/server.log"
echo ""
echo "=== Deployment Complete ==="
echo "To stop the server, run: ./deployment/stop_server.sh"

