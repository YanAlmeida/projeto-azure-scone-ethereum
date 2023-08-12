output "public_ip_sgx" {
  value = azurerm_public_ip.public_ip_sgx.ip_address
}

output "public_ip_blockchain" {
  value = azurerm_public_ip.public_ip_blockchain.ip_address
}

output "private_key" {
  value = tls_private_key.gramine_sgx_signing_key.private_key_pem
  sensitive = true
}

output "ssh_private_key" {
  value = tls_private_key.ssh_key.private_key_pem
  sensitive = true
}
