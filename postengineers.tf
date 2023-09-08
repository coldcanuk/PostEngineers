provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "rgrouppostengineers" {
  name     = "rgrouppostengineers"
  location = "eastus"
}

resource "azurerm_container_registry" "acrpostengineers" {
  name                     = "acrpostengineers"
  resource_group_name      = azurerm_resource_group.rgrouppostengineers.name
  location                 = azurerm_resource_group.rgrouppostengineers.location
  sku                      = "Basic"
  admin_enabled            = true
}
