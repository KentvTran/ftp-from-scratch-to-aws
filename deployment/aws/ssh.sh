#!/bin/bash

#============================================
# CONFIGURATION  
#============================================
KEY_NAME="ftp-project-key"
KEY_PATH="$HOME/.ssh/${KEY_NAME}.pem"
#============================================

# Get to project root (script is in deployment/aws/)
PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$PROJECT_ROOT"

if [ ! -f deployment/aws/instance_id.txt ]; then
    echo "[ERROR] No instance found. Run ./deployment/aws/setup_ec2.sh to create one."
    exit 1
fi

INSTANCE_ID=$(cat deployment/aws/instance_id.txt)

PUBLIC_DNS=$(aws ec2 describe-instances --instance-ids $INSTANCE_ID --query 'Reservations[0].Instances[0].PublicDnsName' --output text)

echo "[INFO] Connecting to $PUBLIC_DNS..."
ssh -i $KEY_PATH ec2-user@$PUBLIC_DNS
