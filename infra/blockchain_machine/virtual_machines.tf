resource "aws_key_pair" "ssh_key" {
  key_name   = "pgc-key"
  public_key = var.public_key_ssh
}


resource "aws_instance" "ec2_instance_blockchain" {
  ami           = "ami-0c55b159cbfafe1f0"  # Amazon Linux 2
  instance_type = "t3.micro"  # AWS Free Tier eligible instance type
  key_name      = aws_key_pair.ssh_key.key_name

  subnet_id = aws_subnet.subnet_blockchain.id
  vpc_security_group_ids = [aws_security_group.sg_blockchain.id]

  associate_public_ip_address = true

  user_data = <<-USERDATA
              #!/bin/bash
              sudo apt-get update
              sudo apt-get install -y docker.io
              sudo docker pull ${var.dockerhub_image_blockchain}
              sudo docker run -d -v /tmp:/tmp -p 8545:8545 ${var.dockerhub_image_blockchain}
              USERDATA

  tags = {
    Name = "${var.prefix}-ec2-blockchain"
  }
}
