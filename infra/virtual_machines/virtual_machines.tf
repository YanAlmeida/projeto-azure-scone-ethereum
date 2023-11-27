resource "azurerm_linux_virtual_machine" "vm_sgx" {
  name                = "${var.prefix}-vm-sgx"
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name
  size                = "Standard_DC1ds_v3" # This is an SGX-enabled size; please verify if it fits your needs
  priority            = "Spot"
  eviction_policy     = "Deallocate"

  admin_username = "ubuntu"

  os_disk {
    name          = "${var.prefix}-osdisk-sgx"
    caching       = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-focal"
    sku       = "20_04-lts-gen2"
    version   = "latest"
  }

  custom_data = base64encode(<<-CUSTOM_DATA
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
    sudo docker pull ${var.dockerhub_image_sgx_untrusted}

    git clone https://github.com/gramineproject/gsc.git
    cd gsc

    cp config.yaml.template config.yaml
    echo "${tls_private_key.gramine_sgx_signing_key.private_key_pem}" > enclave-key.pem

    sudo ./gsc build --insecure-args ${var.dockerhub_image_sgx} test/generic.manifest
    sudo ./gsc sign-image ${var.dockerhub_image_sgx} enclave-key.pem

    sudo rm enclave-key.pem

    sudo docker run --device=/dev/sgx_enclave gsc-${var.dockerhub_image_sgx}
    sudo docker run -e BLOCKCHAIN_ADDRESS="${var.network_interface_blockchain}:8545" -e CONTRACT_ABI="${var.contract_abi}" -e CONTRACT_ADDRESS="${var.contract_address}" -e ACCOUNT_INDEX="${var.account_index}"
    CUSTOM_DATA
  )

  admin_ssh_key {
    username   = "ubuntu"
    public_key = tls_private_key.ssh_key.public_key_openssh
  }

  network_interface_ids = [var.network_interface_sgx]
}

resource "azurerm_linux_virtual_machine" "vm_blockchain" {
  name                = "${var.prefix}-vm-blockchain"
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name
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
    sudo docker run -p 8545:8545 ${var.dockerhub_image_blockchain}
  CUSTOM_DATA
  )

  admin_ssh_key {
    username   = "ubuntu"
    public_key = tls_private_key.ssh_key.public_key_openssh
  }

  network_interface_ids = [var.network_interface_blockchain]
}
