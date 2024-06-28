resource "azurerm_linux_virtual_machine" "vm_sgx" {
  name                = "${var.prefix}-vm-sgx-${var.account_index}"
  location            = var.location
  resource_group_name = var.resource_group_name
  size                = "Standard_DC1ds_v3"
  priority            = "Spot"
  eviction_policy     = "Deallocate"

  admin_username = "ubuntu"

  os_disk {
    name          = "${var.prefix}-osdisk-sgx-${var.account_index}"
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
    sudo docker pull ${var.dockerhub_image_nginx}

    git clone https://github.com/YanAlmeida/gsc-v1.5-adjustment.git
    sudo chmod -R 777 /gsc-v1.5-adjustment
    cd gsc-v1.5-adjustment

    cp config.yaml.template config.yaml
    echo "${file(var.enclave_key_path)}" > enclave-key.pem

    echo '${file(var.manifest_path)}' >> config.manifest

    sudo ./gsc build ${var.dockerhub_image_sgx} config.manifest
    sudo ./gsc sign-image ${var.dockerhub_image_sgx} enclave-key.pem

    sudo rm enclave-key.pem

    sudo docker run --name tee -d --device=/dev/sgx_enclave -v /var/run/aesmd/aesm.socket:/var/run/aesmd/aesm.socket -p 9090:9090 gsc-${var.dockerhub_image_sgx}

    for i in $(seq ${var.account_index} $((${var.account_index} + ${var.number_untrusted_containers} - 1))); do
      sudo docker run --name untrusted -d --network="host" \
        -e BLOCKCHAIN_ADDRESS="${var.public_ip_blockchain}" \
        -e CONTRACT_ABI='${var.contract_abi}' \
        -e CONTRACT_ADDRESS="${var.contract_address}" \
        -e ACCOUNT_INDEX="$i" \
        ${var.dockerhub_image_sgx_untrusted}
    done

    sudo docker run --name nginx -d -p 8080:80 ${var.dockerhub_image_nginx}

    sudo docker run -d --name newrelic-infra --network=host --cap-add=SYS_PTRACE --privileged --pid=host -v "/:/host:ro" -v "/var/run/docker.sock:/var/run/docker.sock" -e NRIA_LICENSE_KEY=3daa2a21235d6c7fdb2c71af4262afddFFFFNRAL newrelic/infrastructure:latest
    CUSTOM_DATA
  )

  admin_ssh_key {
    username   = "ubuntu"
    public_key = var.public_key_ssh
  }

  network_interface_ids = [azurerm_network_interface.ni_sgx.id]
}
