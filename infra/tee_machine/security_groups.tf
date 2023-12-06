
resource "azurerm_network_security_group" "sg_sgx" {
  name                = "${var.prefix}-sg-sgx"
  location            = var.location
  resource_group_name = var.resource_group_name

  security_rule {
    name                       = "allow_ssh"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = var.ssh_access_ip_address
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "allow_internet"
    priority                   = 120
    direction                  = "Outbound"
    access                     = "Allow"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}

resource "azurerm_network_interface_security_group_association" "sg_association_sgx" {
  network_interface_id      = azurerm_network_interface.ni_sgx.id
  network_security_group_id = azurerm_network_security_group.sg_sgx.id
}
