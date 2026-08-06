@echo off
echo 🚀 Installing Anonymous Tool v4.0...
echo ========================================

echo [*] Installing Python packages...
pip install requests urllib3

echo [*] Downloading main.py...
curl -o main.py https://raw.githubusercontent.com/your-username/Anonymous-Tool/main/main.py

echo ========================================
echo ✅ Installation Complete!
echo 📱 Run: python main.py
echo ========================================
pause
