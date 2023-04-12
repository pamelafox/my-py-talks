param serverName string = 'pg-srv'
param location string = 'eastus'
param skuName string = 'Standard_D2s_v3'
param skuTier string = 'GeneralPurpose'
param adminUsername string = 'myadmin'
@secure()
param adminPassword string
param postgresVersion string = '14'
param storageSizeGB int = skuTier == 'Burstable' ? 32 : 128

resource server 'Microsoft.DBforPostgreSQL/flexibleServers@2021-06-01' = {
  name: serverName
  location: location
  sku: {
    name: skuName
    tier: skuTier
  }
  properties: {
    administratorLogin: adminUsername
    administratorLoginPassword: adminPassword
    version: postgresVersion
    storage: {
      storageSizeGB: storageSizeGB
    }
  }
}
