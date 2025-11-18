#!/bin/bash
# Stop FTP server script
# Kills all running FTP server processes

echo "=== Stopping FTP Server ==="

# Kill any FTP server processes
pkill -f "python3.*ftp_server.py"

if [ $? -eq 0 ]; then
    echo "Server process(es) stopped successfully"
else
    echo "No server process found (or already stopped)"
fi

# Wait a moment to ensure processes are terminated
sleep 1

echo "=== Done ==="

