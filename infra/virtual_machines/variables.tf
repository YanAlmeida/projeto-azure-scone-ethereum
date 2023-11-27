variable "prefix" {
  description = "A prefix used for naming resources."
  default     = "myapp"
}

variable "location" {
  description = "Azure region for deployment."
  default     = "eastus"
}

variable "ssh_access_ip_address" {
  description = "A prefix used for naming resources."
  default     = "myapp"
}

variable "dockerhub_image_sgx" {
  description = "Docker image for SGX instance."
  default     = "your-dockerhub-image-for-sgx"
}

variable "dockerhub_image_sgx_unstrusted" {
  description = "Docker image for untrusted SGX instance run."
  default     = "your-dockerhub-image-for-sgx"
}

variable "dockerhub_image_blockchain" {
  description = "Docker image for blockchain instance."
  default     = "your-dockerhub-image-for-blockchain"
}

variable "sgx_driver_distro_name" {
  description = "Distro name for URL to download SGX driver"
  default     = "ubuntu20.04-server"
}

variable "sgx_driver_file_name" {
  description = "Filename for URL to download SGX driver"
  default     = "sgx_linux_x64_driver_2.11.54c9c4c.bin"
}

variable "public_ip_blockchain" {
  description = "Public IP of the blockchain machine"
}

variable "network_interface_sgx" {
  description = "Network interface for SGX machine"
}

variable "network_interface_blockchain" {
  description = "Network interface for blockchain machine"
}

variable "contract_abi" {
  description = "ABI do contrato inteligente"
}

variable "contract_address" {
  description = "Endereço do contrato inteligente"
}

variable account_index {
  description = "Index da conta utilizada pela máquina SGX"
  default     = 0
}