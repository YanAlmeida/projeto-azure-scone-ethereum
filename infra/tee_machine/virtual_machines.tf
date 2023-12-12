resource "azurerm_linux_virtual_machine" "vm_sgx" {
  name                = "${var.prefix}-vm-sgx"
  location            = var.location
  resource_group_name = var.resource_group_name
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

    git clone https://github.com/YanAlmeida/gsc-v1.5-adjustment.git
    sudo chmod -R 777 /gsc-v1.5-adjustment
    cd gsc-v1.5-adjustment

    cp config.yaml.template config.yaml
    echo "${file("./tee_machine_config/enclave-key.pem")}" > enclave-key.pem

    echo '${file("./manifest.txt")}' >> config.manifest

    sudo ./gsc build ${var.dockerhub_image_sgx} config.manifest
    sudo ./gsc sign-image ${var.dockerhub_image_sgx} enclave-key.pem

    sudo rm enclave-key.pem

    sudo docker run -d --device=/dev/sgx_enclave -v /var/run/aesmd/aesm.socket:/var/run/aesmd/aesm.socket -p 9090:9090 gsc-${var.dockerhub_image_sgx}
    sudo docker run -d --network="host" -e BLOCKCHAIN_ADDRESS="http://${var.public_ip_blockchain}:8545" -e CONTRACT_ABI='${var.contract_abi}' -e CONTRACT_ADDRESS="${var.contract_address}" -e ACCOUNT_INDEX="${var.account_index}" ${var.dockerhub_image_sgx_untrusted}
    CUSTOM_DATA
  )

  admin_ssh_key {
    username   = "ubuntu"
    public_key = var.public_key_ssh
  }

  network_interface_ids = [azurerm_network_interface.ni_sgx.id]
}
