param serverName string = 'pg-srv'
param location string = 'eastus'
@secure()
param adminPassword string

resource srv 'Microsoft.DBforPostgreSQL/flexibleServers@2021-06-01' = {
    name: serverName
    location: location
    sku: {
      name: 'Standard_D2s_v3'
      tier: 'GeneralPurpose'
    }
    properties: {
      administratorLogin: 'myadmin'
      administratorLoginPassword: adminPassword
      version: '14'
      storage: { storageSizeGB: 128 }
}  }
