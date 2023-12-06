variable "prefix" {
  description = "A prefix used for naming resources."
}

variable "location" {
  description = "Azure region for deployment."
}

variable "resource_group_name" {
  description = "Resource group name"
  default     = "pgc-resources"
}

variable "ssh_access_ip_address" {
  description = "A prefix used for naming resources."
}

variable "public_key_ssh" {
  description = "Public key for SSH access"
}

variable "dockerhub_image_blockchain" {
  description = "Docker image for blockchain instance."
}

variable "subnet_id" {
  description = "Subnet ID"
}