param serverName string = 'pg-srv-fwall'
param location string = 'eastus'
@secure()
param adminPassword string
param allowAllIPsFirewall bool

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
  resource firewallAll 'firewallRules' = if (allowAllIPsFirewall) {
    name: 'allow-all-IPs'
    properties: {
        startIpAddress: '0.0.0.0'
        endIpAddress: '255.255.255.255'
    }
  }
}
