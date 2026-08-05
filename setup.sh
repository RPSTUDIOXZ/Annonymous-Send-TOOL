#!/bin/bash

echo "🚀 Installing Anonymous Tool v3.0..."
echo "========================================"

# Update packages
pkg update -y
pkg upgrade -y

# Install Python
pkg install python -y
pkg install python-pip -y

# Install Termux API
pkg install termux-api -y

# Install dependencies
pip install requests

# Download main.py
curl -o main.py https://raw.githubusercontent.com/your-repo/main.py

# Make executable
chmod +x main.py

# Grant storage permission
termux-setup-storage

echo "========================================"
echo "✅ Installation Complete!"
echo ""
echo "📱 Run the tool:"
echo "   python main.py"
echo "========================================"
