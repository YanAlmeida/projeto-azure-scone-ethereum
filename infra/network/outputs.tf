output "public_ip_sgx" {
  value = azurerm_public_ip.public_ip_sgx.ip_address
}

output "public_ip_blockchain" {
  value = azurerm_public_ip.public_ip_blockchain.ip_address
}

output "network_interface_sgx" {
  value = azurerm_network_interface.ni_sgx.id
}

output "network_interface_blockchain" {
  value = azurerm_network_interface.ni_blockchain.id
}
