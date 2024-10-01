#!/bin/bash

# Step 1: Install Ollama
function install_ollama {
  echo "Installing Ollama..."
  curl -fsSL https://ollama.com/install.sh | sh
}

# Step 2: Start Ollama server in the background
function start_ollama_server {
  echo "Starting Ollama server..."
  ollama serve &  # Start in the background
  sleep 5         # Optional: Wait for a few seconds to ensure it's up
  if ! pgrep -x "ollama" > /dev/null; then
    echo "Failed to start Ollama server"
    exit 1
  fi
}

# Step 3: Pull the Ollama model
function pull_chat_model {
  echo "Pulling Ollama model..."
  ollama pull gemma2 || { echo "Failed to pull Ollama model"; exit 1; }
}

# Main script execution
function main {
  install_ollama

  # Check if installation was successful
  if command -v ollama &> /dev/null; then
    start_ollama_server
    pull_chat_model
    echo "Ollama server is running in the background."
  else
    echo "Ollama installation failed."
    exit 1
  fi
}

main