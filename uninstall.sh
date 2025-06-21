#!/bin/bash

# Define the file to be removed
DEST_FILE="$HOME/.local/share/nautilus-python/extensions/ImageToolkitExtension.py"

# Check if the file exists and remove it
if [ -f "$DEST_FILE" ]; then
    echo "Uninstalling extension..."
    rm -f "$DEST_FILE"
    echo "Uninstallation complete!"
    echo "Please restart Nautilus to apply the changes (run: nautilus -q)"
else
    echo "Extension not found. Nothing to do."
fi
