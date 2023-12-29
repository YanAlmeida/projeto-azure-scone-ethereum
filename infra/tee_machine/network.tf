resource "azurerm_network_interface" "ni_sgx" {
  name                = "${var.prefix}-ni-sgx-${var.account_index}"
  location            = var.location
  resource_group_name = var.resource_group_name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = var.subnet_id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = var.generate_public_ip ? azurerm_public_ip.public_ip_sgx[0].id : null
  }
}

resource "azurerm_public_ip" "public_ip_sgx" {
  count               = var.generate_public_ip ? 1 : 0
  name                = "${var.prefix}-publicip-sgx-${var.account_index}"
  location            = var.location
  resource_group_name = var.resource_group_name
  allocation_method  = "Static"
}
