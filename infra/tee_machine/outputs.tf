output "public_ip_sgx" {
  value = var.generate_public_ip ? azurerm_public_ip.public_ip_sgx[0].ip_address : null
}
