#!/bin/bash

# Define the source file and destination directory
SOURCE_FILE="ImageToolkitExtension.py"
DEST_DIR="$HOME/.local/share/nautilus-python/extensions"

# Create the destination directory if it doesn't exist
echo "Creating destination directory..."
mkdir -p "$DEST_DIR"

# Copy the file
echo "Installing extension..."
cp -f "$SOURCE_FILE" "$DEST_DIR/"

echo ""
echo "Installation complete!"
echo "Please restart Nautilus to apply the changes (run: nautilus -q)"
