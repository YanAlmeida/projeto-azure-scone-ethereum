output "public_ip_blockchain" {
  value = aws_instance.ec2_instance_blockchain.public_ip
}