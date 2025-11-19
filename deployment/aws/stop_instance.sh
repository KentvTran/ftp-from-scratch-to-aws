#!/bin/bash
set -e

#============================================
# CONFIGURATION  
#============================================
# No additional configuration needed for this script
#============================================

# Get to project root (script is in deployment/aws/)
PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$PROJECT_ROOT"

if [ ! -f deployment/aws/instance_id.txt ]; then
    echo "[ERROR] No instance found. Run ./deployment/aws/setup_ec2.sh to create one."
    exit 1
fi

INSTANCE_ID=$(cat deployment/aws/instance_id.txt)

echo "=== Stopping EC2 Instance ==="

aws ec2 stop-instances --instance-ids $INSTANCE_ID > /dev/null

echo "[SUCCESS] Instance stopping..."
echo "[INFO] Billing stopped! Instance will be stopped in approximately 1 minute."
