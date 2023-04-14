param serverName string = 'pg-srv-fwaz'
param location string = 'eastus'
@secure()
param adminPassword string

resource srv 'Microsoft.DBforPostgreSQL/flexibleServers@2021-06-01' = {
  name: serverName
  location: location
  sku: {
    name: 'Standard_B1ms'
    tier: 'Burstable'
  }
  properties: {
    administratorLogin: 'myadmin'
    administratorLoginPassword: adminPassword
    version: '14'
    storage: { storageSizeGB: 128 }
  }
  resource firewallAzure 'firewallRules' = {
    name: 'allow-all-azure-internal-IPs'
    properties: {
        startIpAddress: '0.0.0.0'
        endIpAddress: '0.0.0.0'
    }
  }
}
