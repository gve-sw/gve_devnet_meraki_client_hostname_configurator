import meraki
import csv
import config
import datetime

# Initialize the Meraki dashboard API
dashboard = meraki.DashboardAPI(api_key=config.api_key, output_log=False)
file_path = config.file_path
org_id = config.org_id
log_file_name = f"provisioned_clients_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.log"

# Function to read clients from CSV into a dictionary for faster lookup
def read_csv_clients(file_path):
    csv_clients = {}
    with open(file_path, mode='r') as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)  # Assuming there is a header
        for row in csv_reader:
            mac, hostname = row[0], row[1]
            csv_clients[mac] = hostname
    return csv_clients

# Get clients from CSV
csv_clients = read_csv_clients(file_path)

# Get all networks for the organization
try:
    print("Fetching networks...")
    networks = dashboard.organizations.getOrganizationNetworks(org_id, total_pages='all')
except Exception as e:
    print(f"Error fetching networks: {e}")
    networks = []

# Process each network
for network in networks:
    net_id = network['id']
    net_name = network['name']
    print(f"Processing network: {net_name} ({net_id})")

    # Get clients for the network
    try:
        meraki_clients = dashboard.networks.getNetworkClients(net_id, total_pages='all')
    except Exception as e:
        print(f"Error fetching clients for network {net_name}: {e}")
        continue

    # Provision clients found in both Meraki and CSV
    with open(log_file_name, "a") as log_file:
        for client in meraki_clients:
            mac = client.get('mac')
            if mac in csv_clients:
                client_info = {
                    'mac': mac,
                    'clientId': client['id'],
                    'name': csv_clients[mac],
                    'message': 'API testing'
                }
                device_policy = 'Normal'
                try:
                    response = dashboard.networks.provisionNetworkClients(net_id, [client_info], device_policy)
                    print(f"Provisioned {mac} in network {net_name}")
                    log_file.write(f"{mac} in network {net_name} provisioned as {csv_clients[mac]}\n")
                except Exception as e:
                    print(f"Error provisioning client {mac} in network {net_name}: {e}")

print(f"Script completed. Check {log_file_name} for details on provisioned clients.")
