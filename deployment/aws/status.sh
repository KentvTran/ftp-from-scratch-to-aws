#!/bin/bash

#============================================
# CONFIGURATION  
#============================================
# No additional configuration needed for this script
#============================================

# Get to project root (script is in deployment/aws/)
PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$PROJECT_ROOT"

if [ ! -f deployment/aws/instance_id.txt ]; then
    echo "[ERROR] No instance found. Run ./deployment/aws/setup_ec2.sh first"
    exit 1
fi

INSTANCE_ID=$(cat deployment/aws/instance_id.txt)

echo "=== FTP Server Status ==="
echo ""
aws ec2 describe-instances --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].[InstanceId,State.Name,PublicIpAddress,PublicDnsName]' \
    --output table
