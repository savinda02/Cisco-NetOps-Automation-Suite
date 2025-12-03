import csv
from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException

INVENTORY_FILE = 'inventory.csv'

def load_inventory(filepath):
    """Parses CSV file and returns a list of device dictionaries."""
    devices = []
    try:
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Map CSV columns to Netmiko expected arguments
                devices.append({
                    'device_type': row['device_type'],
                    'host': row['ip'],
                    'username': row['username'],
                    'password': row['password'],
                    'secret': row['secret'],
                    'hostname_label': row['hostname'] # Custom key for logging
                })
        return devices
    except FileNotFoundError:
        print(f"[ERROR] Inventory file '{filepath}' not found.")
        exit(1)

def test_connection(device):
    """Attempts SSH login and retrieves the prompt."""
    hostname = device.pop('hostname_label') # Remove custom key before passing to Netmiko
    
    print(f"[*] Probing {hostname} ({device['host']})...", end=' ', flush=True)
    
    try:
        conn = ConnectHandler(**device)
        conn.enable()
        prompt = conn.find_prompt()
        conn.disconnect()
        print(f"--> [SUCCESS] Prompt: {prompt}")
        return True

    except (NetmikoTimeoutException, NetmikoAuthenticationException) as e:
        print(f"--> [FAILED] Error: {str(e)}")
        return False
    except Exception as e:
        print(f"--> [ERROR] Unexpected: {str(e)}")
        return False

if __name__ == "__main__":
    print("--- Network Connectivity Probe Tool ---")
    lab_devices = load_inventory(INVENTORY_FILE)
    
    success_count = 0
    for dev in lab_devices:
        if test_connection(dev):
            success_count += 1
            
    print(f"\nSummary: {success_count}/{len(lab_devices)} devices reachable.")