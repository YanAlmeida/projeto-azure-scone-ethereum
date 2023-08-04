
resource "azurerm_virtual_machine" "vm_sgx" {
  name                  = "${var.prefix}-vm-sgx"
  location              = var.location
  resource_group_name   = azurerm_resource_group.rg.name
  network_interface_ids = [azurerm_network_interface.ni_sgx.id]
  vm_size               = "Standard_DC1s_v2" # This is an SGX-enabled size; please verify if it fits your needs

  delete_os_disk_on_termination    = true
  delete_data_disks_on_termination = true

  storage_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "18.04-LTS"
    version   = "latest"
  }

  storage_os_disk {
    name              = "${var.prefix}-osdisk-sgx"
    caching           = "ReadWrite"
    create_option     = "FromImage"
    managed_disk_type = "Standard_LRS"
  }

  os_profile {
    computer_name  = "${var.prefix}-vm-sgx"
    admin_username = "ubuntu"
    custom_data = <<-CUSTOM_DATA
            #!/bin/bash
            sudo apt-get update
            sudo apt-get install -y docker.io
            sudo docker pull ${var.dockerhub_image_sgx}
            sudo docker run ${var.dockerhub_image_sgx}
            CUSTOM_DATA
  }

  os_profile_linux_config {
    disable_password_authentication = true

    ssh_keys {
      path     = "/home/ubuntu/.ssh/authorized_keys"
      key_data = var.ssh_key
    }
  }

}

resource "azurerm_virtual_machine" "vm_blockchain" {
  name                  = "${var.prefix}-vm-blockchain"
  location              = var.location
  resource_group_name   = azurerm_resource_group.rg.name
  network_interface_ids = [azurerm_network_interface.ni_blockchain.id]
  vm_size               = "Standard_B1ls" # Cheapest available size, verify if it fits your needs

  delete_os_disk_on_termination    = true
  delete_data_disks_on_termination = true

  storage_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "18.04-LTS"
    version   = "latest"
  }

  storage_os_disk {
    name              = "${var.prefix}-osdisk-blockchain"
    caching           = "ReadWrite"
    create_option     = "FromImage"
    managed_disk_type = "Standard_LRS"
  }

  os_profile {
    computer_name  = "${var.prefix}-vm-blockchain"
    admin_username = "ubuntu"
    custom_data = <<-CUSTOM_DATA
                    #!/bin/bash
                    sudo apt-get update
                    sudo apt-get install -y docker.io
                    sudo docker pull ${var.dockerhub_image_blockchain}
                    sudo docker run ${var.dockerhub_image_blockchain}
                    CUSTOM_DATA
  }

  os_profile_linux_config {
    disable_password_authentication = true

    ssh_keys {
      path     = "/home/ubuntu/.ssh/authorized_keys"
      key_data = var.ssh_key
    }
  }

}