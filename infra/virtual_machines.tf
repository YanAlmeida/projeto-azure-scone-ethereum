
resource "azurerm_virtual_machine" "vm_sgx" {
  name                  = "${var.prefix}-vm-sgx"
  location              = var.location
  resource_group_name   = azurerm_resource_group.rg.name
  network_interface_ids = [azurerm_network_interface.ni_sgx.id]
  vm_size               = "Standard_DC1ds_v3" # This is an SGX-enabled size; please verify if it fits your needs
  priority = "Spot"
  eviction_policy = "Deallocate"

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
            sudo apt-get install -y build-essential ocaml automake autoconf libtool wget python3 python3-pip libssl-dev dkms
            sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 1
            sudo wget https://download.01.org/intel-sgx/latest/dcap-latest/linux/distro/${var.sgx_driver_distro_name}/${var.sgx_driver_file_name}
            sudo chmod 777 ${var.sgx_driver_file_name}
            sudo ./${var.sgx_driver_file_name}
            sudo apt-get install -y docker.io

            sudo apt-get install git
            sudo pip3 install docker jinja2 tomli tomli-w pyyaml

            sudo docker pull ${var.dockerhub_image_sgx}

            git clone https://github.com/gramineproject/gsc.git
            cd gsc

            cp config.yaml.template config.yaml
            echo ${var.enclave_sign_private_key} >> enclave-key.pem

            sudo ./gsc build --insecure-args ${var.dockerhub_image_sgx} test/generic.manifest
            sudo ./gsc sign-image ${var.dockerhub_image_sgx} enclave-key.pem

            sudo rm enclave-key.pem

            sudo docker run --device=/dev/sgx_enclave gsc-${var.dockerhub_image_sgx}
            CUSTOM_DATA
  }

  os_profile_linux_config {
    disable_password_authentication = true

    ssh_keys {
      path     = "/home/ubuntu/.ssh/authorized_keys"
      key_data = var.ssh_public_key
    }
  }

}

resource "azurerm_virtual_machine" "vm_blockchain" {
  name                  = "${var.prefix}-vm-blockchain"
  location              = var.location
  resource_group_name   = azurerm_resource_group.rg.name
  network_interface_ids = [azurerm_network_interface.ni_blockchain.id]
  vm_size               = "Standard_B1ls" # Cheapest available size, verify if it fits your needs
  priority = "Spot"
  eviction_policy = "Deallocate"

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
      key_data = var.ssh_public_key
    }
  }

}