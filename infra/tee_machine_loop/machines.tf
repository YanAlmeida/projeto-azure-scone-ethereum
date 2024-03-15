module "vm_instance" {
    source                        = "../tee_machine"
    count                         = var.number_machines

    account_index                 = count.index == 0 ? count.index : count.index + var.number_untrusted_containers - 1
    subnet_id                     = var.subnet_id
    public_key_ssh                = var.public_key_ssh
    ssh_access_ip_address         = var.ssh_access_ip_address
    public_ip_blockchain          = var.public_ip_blockchain
    dockerhub_image_sgx_untrusted = var.dockerhub_image_sgx_untrusted
    dockerhub_image_sgx           = var.dockerhub_image_sgx
    dockerhub_image_nginx         = var.dockerhub_image_nginx
    location                      = var.location
    prefix                        = var.prefix
    manifest_path                 = var.manifest_path
    enclave_key_path              = var.enclave_key_path
    generate_public_ip            = var.generate_public_ip
    number_untrusted_containers   = var.number_untrusted_containers
}
