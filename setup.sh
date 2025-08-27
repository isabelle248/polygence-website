#!/bin/bash
set -e

echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y openjdk-17-jdk python3 python3-pip unzip

echo "Installing Python dependencies..."
pip3 install --upgrade pip
pip3 install -r requirements.txt

echo "Installing Node dependencies..."
npm install

echo "Setup complete!"
