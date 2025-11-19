#!/bin/bash
set -e

#============================================
# CONFIGURATION  
#============================================
KEY_NAME="ftp-project-key"
KEY_PATH="$HOME/.ssh/${KEY_NAME}.pem"
SSH_RETRY_WAIT=5        # Seconds between connection attempts
#============================================

# Get to project root (script is in deployment/aws/)
PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$PROJECT_ROOT"

if [ ! -f deployment/aws/instance_id.txt ]; then
    echo "[ERROR] No instance found. Run ./deployment/aws/setup_ec2.sh to create one."
    exit 1
fi

INSTANCE_ID=$(cat deployment/aws/instance_id.txt)

echo "=== Stopping FTP Server ==="

PUBLIC_DNS=$(aws ec2 describe-instances --instance-ids $INSTANCE_ID --query 'Reservations[0].Instances[0].PublicDnsName' --output text)

# Disable strict host key checking for ephemeral EC2 instance connections
ssh -i $KEY_PATH -o StrictHostKeyChecking=no ec2-user@$PUBLIC_DNS << 'EOF'
    cd ftp-from-scratch-to-aws
    ./deployment/stop_server.sh
EOF

echo "[SUCCESS] FTP server stopped (instance still running)"
echo "[INFO] To stop the instance too: ./deployment/aws/stop_instance.sh"
