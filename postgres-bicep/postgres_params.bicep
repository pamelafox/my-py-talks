param serverName string = 'pg-srv-params'
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
}
