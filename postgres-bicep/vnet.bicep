param name string = 'pgvnet6'
param location string = 'eastus'
@secure()
param adminPassword string

var pgServerPrefix = '${name}-postgres-server'

resource virtualNetwork 'Microsoft.Network/virtualNetworks@2019-11-01' = {
  name: '${name}-vnet'
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [
        '10.0.0.0/16'
      ]
    }
  }

  resource databaseSubnet 'subnets' = {
    name: 'database-subnet'
    properties: {
      addressPrefix: '10.0.0.0/24'
      delegations: [
        {
          name: '${name}-subnet-delegation'
          properties: {
            serviceName: 'Microsoft.DBforPostgreSQL/flexibleServers'
          }
        }
      ]
    }
  }

  resource webappSubnet 'subnets' = {
    name: 'webapp-subnet'
    properties: {
      addressPrefix: '10.0.1.0/24'
      delegations: [
        {
          name: '${name}-subnet-delegation-web'
          properties: {
            serviceName: 'Microsoft.Web/serverFarms'
          }
        }
      ]
    }
  }
}

resource privateDnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' = {
  name: '${pgServerPrefix}.private.postgres.database.azure.com'
  location: 'global'

  resource vnetLink 'virtualNetworkLinks' = {
    name: '${pgServerPrefix}-link'
    location: 'global'
    properties: {
      registrationEnabled: false
      virtualNetwork: {
        id: virtualNetwork.id
      }
    }
  }
}

resource web 'Microsoft.Web/sites@2022-03-01' = {
  name: '${name}-app-service'
  location: location
  kind: 'app,linux'
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      alwaysOn: true
      linuxFxVersion: 'PYTHON|3.11'
      ftpsState: 'Disabled'
      appCommandLine: 'startup.sh'
    }
    httpsOnly: true
  }
  identity: {
    type: 'SystemAssigned'
  }

  resource appSettings 'config' = {
    name: 'appsettings'
    properties: {
      AZURE_POSTGRESQL_HOST: '${postgresServer.name}.postgres.database.azure.com'
      AZURE_POSTGRESQL_USER: postgresServer.properties.administratorLogin
      AZURE_POSTGRESQL_PASS: adminPassword
      AZURE_POSTGRESQL_DBNAME: 'postgres'
    }
  }

  resource webappVnetConfig 'networkConfig' = {
    name: 'virtualNetwork'
    properties: {
      subnetResourceId: virtualNetwork::webappSubnet.id
    }
  }
}

resource appServicePlan 'Microsoft.Web/serverfarms@2021-03-01' = {
  name: '${name}-service-plan'
  location: location
  sku: {
    name: 'B1'
  }
  properties: {
    reserved: true
  }
}

resource postgresServer 'Microsoft.DBforPostgreSQL/flexibleServers@2022-01-20-preview' = {
  name: pgServerPrefix
  location: location
  sku: {
    name: 'Standard_B1ms'
    tier: 'Burstable'
  }
  properties: {
    administratorLogin: 'postgresadmin'
    administratorLoginPassword: adminPassword
    storage: {
      storageSizeGB: 128
    }
    version: '14'
    network: {
      delegatedSubnetResourceId: virtualNetwork::databaseSubnet.id
      privateDnsZoneArmResourceId: privateDnsZone.id
    }
  }
}
