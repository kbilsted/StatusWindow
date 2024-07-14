#!/bin/bash

echo "Installing dependencies for AlwaysOnTopApp..."

# Update package list
sudo apt update

# Install Python 3 and pip if not already installed
if ! command -v python3 &>/dev/null; then
  echo "Python 3 not found. Installing Python 3..."
  sudo apt install -y python3 python3-pip
else
  echo "Python 3 is already installed."
fi

# Install tkinter
echo "Installing tkinter..."
sudo apt install -y python3-tk

# Install watchdog
echo "Installing watchdog..."
pip3 install watchdog

echo "Dependencies installed successfully."
