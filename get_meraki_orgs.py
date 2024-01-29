import meraki
import config
import json

dashboard = meraki.DashboardAPI(api_key=config.api_key,output_log=False)
orgs = dashboard.organizations.getOrganizations()

# Export the organizations to a JSON file
with open('organizations.json', 'w') as file:
    json.dump(orgs, file, indent=4)

print("Organizations data exported to 'organizations.json'")