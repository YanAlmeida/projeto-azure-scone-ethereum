resource "tls_private_key" "gramine_sgx_signing_key" {
  algorithm = "RSA"
  rsa_bits  = 3072
}

resource "tls_private_key" "ssh_key" {
  algorithm = "RSA"
}
