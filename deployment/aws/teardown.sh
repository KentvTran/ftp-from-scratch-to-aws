#!/bin/bash
set -e

#============================================
# CONFIGURATION  
#============================================
KEY_NAME="ftp-project-key"
KEY_PATH="$HOME/.ssh/${KEY_NAME}.pem"
SG_NAME="FTP-SG"
#============================================

# Get to project root (script is in deployment/aws/)
PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$PROJECT_ROOT"

echo ""
echo "========================================="
echo "[WARNING] PERMANENT DELETION"
echo "========================================="
echo ""
echo "This will DELETE:"
echo "  - EC2 Instance"
echo "  - Security Group"
echo "  - Key Pair"
echo "  - Local .pem file"
echo ""
read -p "Type 'DELETE' to confirm: " confirm

if [ "$confirm" != "DELETE" ]; then
    echo "[INFO] Teardown cancelled. No resources were deleted."
    exit 1
fi

if [ ! -f deployment/aws/instance_id.txt ]; then
    echo "[ERROR] No instance found. Run ./deployment/aws/setup_ec2.sh to create one."
    exit 1
fi

INSTANCE_ID=$(cat deployment/aws/instance_id.txt)

echo ""
echo "=== Deleting AWS Resources ==="

# Terminate instance
echo "[1/3] Terminating instance $INSTANCE_ID..."
aws ec2 terminate-instances --instance-ids $INSTANCE_ID > /dev/null
echo "[INFO] Waiting for termination..."
aws ec2 wait instance-terminated --instance-ids $INSTANCE_ID

# Delete security group
echo "[2/3] Deleting security group..."
SG_ID=$(aws ec2 describe-security-groups --filters "Name=group-name,Values=$SG_NAME" --query 'SecurityGroups[0].GroupId' --output text)
# Check for "None" string - AWS CLI returns this instead of empty/null
if [ "$SG_ID" != "None" ] && [ -n "$SG_ID" ]; then
    aws ec2 delete-security-group --group-id $SG_ID
    echo "[SUCCESS] Security group deleted"
else
    echo "[WARNING] Security group not found or already deleted"
fi

# Delete key pair
echo "[3/3] Deleting key pair..."
aws ec2 delete-key-pair --key-name $KEY_NAME 2>/dev/null || echo "[WARNING] Key pair not found in AWS (may have been deleted manually)"
rm -f $KEY_PATH
echo "[SUCCESS] Local key file removed"

# Clean up instance ID file
rm -f deployment/aws/instance_id.txt

echo ""
echo "[SUCCESS] All resources deleted!"
echo "[INFO] Final project cost: < $0.50"
