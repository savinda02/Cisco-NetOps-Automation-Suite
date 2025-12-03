import csv
from netmiko import ConnectHandler

INVENTORY = 'inventory.csv'
OSPF_PROCESS_ID = 1
OSPF_AREA = 0

def generate_config(ip_address):
    """
    Business Logic:
    Extracts unique identifier from the last octet of the IP.
    Returns: router_id, loopback_ip
    """
    octet = ip_address.split('.')[-1]
    r_id = f"{octet}.{octet}.{octet}.{octet}"
    lo_ip = f"10.0.0.{octet}"
    return r_id, lo_ip

def push_ospf(device_row):
    hostname = device_row['hostname']
    mgmt_ip = device_row['ip']
    
    # Netmiko connection dict
    target = {
        'device_type': device_row['device_type'],
        'host': mgmt_ip,
        'username': device_row['username'],
        'password': device_row['password'],
        'secret': device_row['secret'],
    }

    try:
        print(f"[*] Configuring {hostname}...", end=' ')
        
        # Calculate OSPF parameters
        router_id, loopback_ip = generate_config(mgmt_ip)
        
        # Build configuration payload
        commands = [
            f"interface Loopback0",
            f" description AUTO_OSPF_ID_{router_id}",
            f" ip address {loopback_ip} 255.255.255.255",
            f" no shutdown",
            f" exit",
            f"router ospf {OSPF_PROCESS_ID}",
            f" router-id {router_id}",
            f" network 0.0.0.0 255.255.255.255 area {OSPF_AREA}",
            f" exit"
        ]

        # Execute
        with ConnectHandler(**target) as conn:
            conn.enable()
            conn.send_config_set(commands)
            conn.save_config()
            
        print(f"--> [DONE] (RID: {router_id})")

    except Exception as e:
        print(f"\n[!] Error on {hostname}: {e}")

if __name__ == "__main__":
    print(f"--- Initiating OSPF Deployment (Area {OSPF_AREA}) ---")
    
    with open(INVENTORY, 'r') as f:
        reader = csv.DictReader(f)
        devices = list(reader)

    for dev in devices:
        push_ospf(dev)

    print("\n[INFO] Provisioning finished. Verify routing tables manually.")