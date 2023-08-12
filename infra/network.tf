resource "azurerm_resource_group" "rg" {
  name     = "pgc-resources"
  location = var.location
}

resource "azurerm_virtual_network" "vnet" {
  name                = "${var.prefix}-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name
}

resource "azurerm_subnet" "subnet" {
  name                 = "${var.prefix}-subnet"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.1.0/24"]
}

resource "azurerm_public_ip" "public_ip_sgx" {
  name                = "${var.prefix}-publicip-sgx"
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name
  allocation_method  = "Static"
}

resource "azurerm_public_ip" "public_ip_blockchain" {
  name                = "${var.prefix}-publicip-blockchain"
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name
  allocation_method  = "Static"
}

resource "azurerm_network_interface" "ni_sgx" {
  name                = "${var.prefix}-ni-sgx"
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.public_ip_sgx.id
  }
}

resource "azurerm_network_interface" "ni_blockchain" {
  name                = "${var.prefix}-ni-blockchain"
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.public_ip_blockchain.id
  }
}

