resource "azurerm_network_interface" "ni_client" {
  name                = "${var.prefix}-ni-client"
  location            = var.location
  resource_group_name = var.resource_group_name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = var.subnet_id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.public_ip_client.id
  }
}

resource "azurerm_public_ip" "public_ip_client" {
  name                = "${var.prefix}-publicip-client"
  location            = var.location
  resource_group_name = var.resource_group_name
  allocation_method  = "Static"
}
