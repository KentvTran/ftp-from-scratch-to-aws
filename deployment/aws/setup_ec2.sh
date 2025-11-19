#!/bin/bash
set -e

#============================================
# CONFIGURATION
#============================================
# AWS Region - Update if deploying to different region
REGION="us-east-1"

# Amazon Linux 2023 AMI ID for us-east-1
# To find AMI for your region, run:
# aws ec2 describe-images --owners amazon --filters "Name=name,Values=al2023-ami-2023.*-x86_64" --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId'
AMI_ID="ami-0f00d706c4a80fd93"

# EC2 Instance Configuration
INSTANCE_TYPE="t3.micro"  # Free tier eligible, ~$0.0104/hour
INSTANCE_NAME="ftp-server-project"

# Security Configuration
KEY_NAME="ftp-project-key"  # SSH key pair name in AWS
KEY_PATH="$HOME/.ssh/${KEY_NAME}.pem"  # Local path for private key
SG_NAME="FTP-SG"  # Security group name for FTP server

# Network Port Configuration (per RFC 959 and project specification)
SSH_PORT=22              # Standard SSH port for remote management
FTP_CONTROL_PORT=2121   # FTP command/control channel (uses 2121 to avoid sudo requirement)
FTP_DATA_PORT_MIN=20000  # Passive mode data transfer range start
FTP_DATA_PORT_MAX=21000  # Passive mode data transfer range end

# Timing Configuration (in seconds)
INSTANCE_BOOT_WAIT=30    # Wait for instance boot and SSH service startup
INSTANCE_START_WAIT=15   # Additional wait when starting stopped instance
SSH_RETRY_WAIT=5         # Wait between SSH connection retries
#============================================

# Get to project root (script is in deployment/aws/)
PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$PROJECT_ROOT"

echo "=== FTP Server EC2 One-Time Setup ==="

# Auto-detect GitHub repo URL from git config, or prompt if not found
if git rev-parse --git-dir > /dev/null 2>&1; then
    GITHUB_REPO=$(git config --get remote.origin.url)
    if [ -z "$GITHUB_REPO" ]; then
        echo "[ERROR] Could not detect git remote URL. Ensure you're in a git repository with a remote configured."
        read -p "Enter your GitHub repo URL (https://github.com/username/ftp-from-scratch-to-aws.git): " GITHUB_REPO
    else
        echo "[OK] Detected repo: $GITHUB_REPO"
    fi
else
    read -p "Enter your GitHub repo URL (https://github.com/username/ftp-from-scratch-to-aws.git): " GITHUB_REPO
fi

# Step 1: Create key pair if it doesn't exist
echo "[1/4] Checking key pair..."
if ! aws ec2 describe-key-pairs --key-names $KEY_NAME &>/dev/null; then
    echo "[INFO] Creating key pair..."
    aws ec2 create-key-pair --key-name $KEY_NAME --query 'KeyMaterial' --output text > $KEY_PATH
    chmod 400 $KEY_PATH
    echo "[SUCCESS] Key saved to $KEY_PATH"
else
    echo "[OK] Key pair already exists"
fi

# Step 2: Create security group if it doesn't exist
echo "[2/4] Checking security group..."
SG_ID=$(aws ec2 describe-security-groups --filters "Name=group-name,Values=$SG_NAME" --query 'SecurityGroups[0].GroupId' --output text 2>/dev/null)

# Check for "None" string - AWS CLI returns this instead of empty/null
if [ "$SG_ID" == "None" ] || [ -z "$SG_ID" ]; then
    echo "[INFO] Creating security group..."
    SG_ID=$(aws ec2 create-security-group --group-name $SG_NAME --description "FTP Server Security Group" --query 'GroupId' --output text)
    
    # Add security group rules for FTP server
    echo "[INFO] Configuring security group rules..."
    aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port $SSH_PORT --cidr 0.0.0.0/0
    aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port $FTP_CONTROL_PORT --cidr 0.0.0.0/0
    
    # Use passive mode port range for FTP data transfers
    # Range 20000-21000 per project specification in docs/protocol_spec.md
    aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port $FTP_DATA_PORT_MIN-$FTP_DATA_PORT_MAX --cidr 0.0.0.0/0
    
    echo "[SUCCESS] Security group created: $SG_ID"
else
    echo "[OK] Security group already exists: $SG_ID"
fi

# Step 3: Launch instance
echo "[3/4] Launching EC2 instance..."
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --instance-type $INSTANCE_TYPE \
    --key-name $KEY_NAME \
    --security-group-ids $SG_ID \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$INSTANCE_NAME}]" \
    --query 'Instances[0].InstanceId' \
    --output text)

echo "[SUCCESS] Instance launched: $INSTANCE_ID"
echo "[INFO] Waiting for instance to be running..."
aws ec2 wait instance-running --instance-ids $INSTANCE_ID

# Wait for instance to complete boot sequence and SSH daemon to start
echo "[INFO] Waiting $INSTANCE_BOOT_WAIT seconds for SSH to be ready..."
sleep $INSTANCE_BOOT_WAIT

# Step 4: Get connection info
PUBLIC_DNS=$(aws ec2 describe-instances --instance-ids $INSTANCE_ID --query 'Reservations[0].Instances[0].PublicDnsName' --output text)
PUBLIC_IP=$(aws ec2 describe-instances --instance-ids $INSTANCE_ID --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)

# Step 5: Initial server setup
echo "[4/4] Installing software and cloning repo..."
# Disable strict host key checking for first-time connection to ephemeral EC2 instance
ssh -i $KEY_PATH -o StrictHostKeyChecking=no ec2-user@$PUBLIC_DNS << EOF
    sudo yum update -y
    sudo yum install git python3 -y
    git clone $GITHUB_REPO
    cd ftp-from-scratch-to-aws
    mkdir -p logs server_files
    chmod +x deployment/manual_deploy.sh deployment/stop_server.sh
    echo "[SUCCESS] Server setup complete!"
EOF

# Save instance ID for other scripts
echo $INSTANCE_ID > deployment/aws/instance_id.txt

echo ""
echo "========================================="
echo "[SUCCESS] SETUP COMPLETE!"
echo "========================================="
echo "Instance ID: $INSTANCE_ID"
echo "Public IP: $PUBLIC_IP"
echo "Public DNS: $PUBLIC_DNS"
echo "Repo: $GITHUB_REPO"
echo ""
echo "[INFO] Instance is now RUNNING and ready to use!"
echo ""
echo "Next steps:"
echo "  - Run ./deployment/aws/start_server.sh to deploy the FTP server"
echo "  - Run ./deployment/aws/stop_instance.sh to stop it and save money"
