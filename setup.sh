#!/bin/bash
echo "🚀 Installing Anonymous Tool v4.0..."
echo "========================================"

# Detect OS
OS=$(uname -s)
echo "[*] Detected OS: $OS"

# Install Python
if command -v python3 &>/dev/null; then
    echo "[✓] Python found"
else
    echo "[*] Installing Python..."
    if [[ "$OS" == "Linux" ]]; then
        sudo apt update && sudo apt install python3 python3-pip -y
    elif [[ "$OS" == "Darwin" ]]; then
        brew install python3
    fi
fi

# Install dependencies
pip3 install requests urllib3

# Download main.py
curl -o main.py https://raw.githubusercontent.com/your-username/Anonymous-Tool/main/main.py

echo "========================================"
echo "✅ Installation Complete!"
echo "📱 Run: python3 main.py"
echo "========================================"
