import csv
import os
import datetime
from netmiko import ConnectHandler

# Config
INVENTORY = 'inventory.csv'
BACKUP_DIR = 'backups'

def ensure_backup_dir():
    """Checks if backup directory exists, creates it if not."""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        print(f"[INFO] Created backup directory: ./{BACKUP_DIR}")

def backup_device(device_info):
    hostname = device_info.pop('hostname_label') # Extract hostname for filename
    
    try:
        print(f"[*] Backing up {hostname}...", end=' ', flush=True)
        
        conn = ConnectHandler(**device_info)
        conn.enable()
        
        # Pull config
        output = conn.send_command("show running-config")
        
        # Generate filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"{BACKUP_DIR}/{hostname}_conf_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write(output)
            
        print(f"--> Saved to {filename}")
        conn.disconnect()

    except Exception as e:
        print(f"\n[!] Failed to backup {hostname}. Reason: {e}")

if __name__ == "__main__":
    devices = []
    # Load Inventory (Reusing logic for simplicity)
    with open(INVENTORY, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            devices.append({
                'device_type': row['device_type'],
                'host': row['ip'],
                'username': row['username'],
                'password': row['password'],
                'secret': row['secret'],
                'hostname_label': row['hostname']
            })

    ensure_backup_dir()
    
    print(f"Starting Backup Job for {len(devices)} devices...\n")
    for dev in devices:
        backup_device(dev)
        
    print("\n--- Backup Job Completed ---")