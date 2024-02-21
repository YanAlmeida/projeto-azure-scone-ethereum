variable "prefix" {
  description = "A prefix used for naming resources."
}

variable "aws_region" {
  description = "AWS region for deployment."
  default     = "us-east-2"
}

variable "aws_availability_zone" {
  description = "AWS availability zone for subnet."
  default     = "us-east-2a"
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
