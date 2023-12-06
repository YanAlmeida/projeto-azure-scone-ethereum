resource "azurerm_linux_virtual_machine" "vm_blockchain" {
  name                = "${var.prefix}-vm-blockchain"
  location            = var.location
  resource_group_name = var.resource_group_name
  size                = "Standard_DS1_v2" # Cheapest available size, verify if it fits your needs
  priority            = "Spot"
  eviction_policy     = "Deallocate"

  admin_username = "ubuntu"

  os_disk {
    name          = "${var.prefix}-osdisk-blockchain"
    caching       = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "18.04-LTS"
    version   = "latest"
  }

  custom_data = base64encode(<<-CUSTOM_DATA
    #!/bin/bash
    sudo apt-get update
    sudo apt-get install -y docker.io
    sudo docker pull ${var.dockerhub_image_blockchain}
    sudo docker run -d -p 8545:8545 ${var.dockerhub_image_blockchain}
  CUSTOM_DATA
  )

  admin_ssh_key {
    username   = "ubuntu"
    public_key = var.public_key_ssh
  }

  network_interface_ids = [azurerm_network_interface.ni_blockchain.id]
}
