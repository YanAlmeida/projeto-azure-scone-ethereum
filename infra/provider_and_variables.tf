
provider "azurerm" {
  features {}
}

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

variable "ssh_key" {
  description = "SSH public key for authentication."
  default     = "your-ssh-public-key-here"
}

variable "dockerhub_image_sgx" {
  description = "Docker image for SGX instance."
  default     = "your-dockerhub-image-for-sgx"
}

variable "dockerhub_image_blockchain" {
  description = "Docker image for blockchain instance."
  default     = "your-dockerhub-image-for-blockchain"
}