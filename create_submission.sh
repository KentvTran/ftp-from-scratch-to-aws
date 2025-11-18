#!/bin/bash
# Script to create p2-[userid].tar submission file
# Usage: ./create_submission.sh [userid]

set -e  # Exit on error

# Get userid from argument or prompt
if [ -z "$1" ]; then
    echo "Usage: ./create_submission.sh [userid]"
    echo "Example: ./create_submission.sh jlopez0627"
    read -p "Enter your userid: " USERID
else
    USERID="$1"
fi

if [ -z "$USERID" ]; then
    echo "Error: userid cannot be empty"
    exit 1
fi

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

# Output filename
OUTPUT_FILE="p2-${USERID}.tar"

echo "=== Creating Submission Archive ==="
echo "User ID: $USERID"
echo "Output file: $OUTPUT_FILE"
echo ""

# List of files/directories to include
# Exclude: .git, __pycache__, *.pyc, server_files/, logs/, etc.
INCLUDE_FILES=(
    "client/"
    "server/"
    "shared/"
    "tests/"
    "deployment/"
    "docs/"
    "README.md"
    "README.txt"
    ".gitignore"
)

# Create temporary directory for clean archive
TEMP_DIR=$(mktemp -d)
echo "Using temporary directory: $TEMP_DIR"

# Copy files to temp directory
echo "Copying files..."
for item in "${INCLUDE_FILES[@]}"; do
    if [ -e "$item" ]; then
        echo "  - $item"
        cp -r "$item" "$TEMP_DIR/"
    else
        echo "  WARNING: $item not found, skipping"
    fi
done

# Create the tar archive
echo ""
echo "Creating tar archive..."
cd "$TEMP_DIR"
tar -cf "$PROJECT_ROOT/$OUTPUT_FILE" *

# Compress the tar file (optional - creates .tar.gz)
# Uncomment the next line if you want compressed archive
# gzip "$PROJECT_ROOT/$OUTPUT_FILE" && OUTPUT_FILE="${OUTPUT_FILE}.gz"

# Clean up
cd "$PROJECT_ROOT"
rm -rf "$TEMP_DIR"

# Display archive contents
echo ""
echo "=== Archive Created Successfully ==="
echo "File: $OUTPUT_FILE"
echo "Size: $(du -h "$OUTPUT_FILE" | cut -f1)"
echo ""
echo "Archive contents:"
tar -tf "$OUTPUT_FILE" | head -20
if [ $(tar -tf "$OUTPUT_FILE" | wc -l) -gt 20 ]; then
    echo "... and $(($(tar -tf "$OUTPUT_FILE" | wc -l) - 20)) more files"
fi
echo ""
echo "To verify contents: tar -tf $OUTPUT_FILE"
echo "To extract: tar -xf $OUTPUT_FILE"

