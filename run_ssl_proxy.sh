#!/bin/bash

# Step 1: Download and extract the ssl-proxy binary
echo "Downloading and extracting ssl-proxy..."
wget -qO- "https://getbin.io/suyashkumar/ssl-proxy" | tar xvz

# Step 2: Identify the extracted binary name
echo "Identifying the extracted binary..."
BINARY_NAME=$(ls ssl-proxy*)

# Check if the binary was found
if [[ -z "$BINARY_NAME" ]]; then
    echo "Error: Unable to find the ssl-proxy binary."
    exit 1
fi

echo "Found ssl-proxy binary: $BINARY_NAME"

# Step 3: Run the ssl-proxy binary with the specified parameters
echo "Running the ssl-proxy binary..."
./"$BINARY_NAME" -from 0.0.0.0:9080 -to http://127.0.0.1:8501
