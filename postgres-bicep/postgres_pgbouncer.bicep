param serverName string = 'pg-bounce'
param location string = 'eastus'
@secure()
param adminPassword string

resource srv 'Microsoft.DBforPostgreSQL/flexibleServers@2021-06-01' = {
    name: serverName
    location: location
    sku: {
      name: 'Standard_D2ds_v4'
      tier: 'GeneralPurpose'
    }
    properties: {
      administratorLogin: 'myadmin'
      administratorLoginPassword: adminPassword
      version: '14'
      storage: { storageSizeGB: 128 }
  }  

  resource pgBouncer 'configurations' = {
    name: 'pgbouncer.enabled'
    properties: {
      value: 'TRUE'
      source: 'user-override'
    }
  }
}
