#!/bin/bash
set -e

#============================================
# CONFIGURATION  
#============================================
KEY_NAME="ftp-project-key"
KEY_PATH="$HOME/.ssh/${KEY_NAME}.pem"
INSTANCE_START_WAIT=15  # Seconds to wait after starting instance
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

echo "=== Starting FTP Server Demo ==="

# Check if instance is running
STATE=$(aws ec2 describe-instances --instance-ids $INSTANCE_ID --query 'Reservations[0].Instances[0].State.Name' --output text)

if [ "$STATE" != "running" ]; then
    echo "[1/4] Starting EC2 instance..."
    aws ec2 start-instances --instance-ids $INSTANCE_ID > /dev/null
    echo "[INFO] Waiting for instance to be running..."
    aws ec2 wait instance-running --instance-ids $INSTANCE_ID
    echo "[INFO] Waiting $INSTANCE_START_WAIT seconds for instance to be ready..."
    sleep $INSTANCE_START_WAIT
else
    echo "[1/4] Instance already running"
fi

# Get connection info
echo "[2/4] Getting connection info..."
PUBLIC_IP=$(aws ec2 describe-instances --instance-ids $INSTANCE_ID --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)
PUBLIC_DNS=$(aws ec2 describe-instances --instance-ids $INSTANCE_ID --query 'Reservations[0].Instances[0].PublicDnsName' --output text)

echo "[3/4] Pulling latest code..."
# Disable strict host key checking for ephemeral EC2 instance connections
ssh -i $KEY_PATH -o StrictHostKeyChecking=no ec2-user@$PUBLIC_DNS << 'EOF'
    cd ftp-from-scratch-to-aws
    git pull origin main
EOF

echo "[4/4] Starting FTP server..."
ssh -i $KEY_PATH -o StrictHostKeyChecking=no ec2-user@$PUBLIC_DNS << 'EOF'
    cd ftp-from-scratch-to-aws
    ./deployment/manual_deploy.sh
EOF

echo ""
echo "========================================="
echo "[SUCCESS] FTP SERVER IS LIVE!"
echo "========================================="
echo ""
echo "Public IP: $PUBLIC_IP"
echo ""
echo "Connect from your local machine:"
echo "  ./run_client.sh $PUBLIC_IP 21"
echo ""
echo "When done: ./deployment/aws/stop_server.sh"
