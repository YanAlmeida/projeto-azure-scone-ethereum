resource "aws_internet_gateway" "igw_blockchain" {
  vpc_id = aws_vpc.vpc_blockchain.id

  tags = {
    Name = "${var.prefix}-igw-blockchain"
  }
}


resource "aws_vpc" "vpc_blockchain" {
  cidr_block = "10.0.0.0/28"  # Adjust as needed
  enable_dns_support = true
  enable_dns_hostnames = true
  tags = {
    Name = "${var.prefix}-vpc-blockchain"
  }
}


resource "aws_route_table" "rt_blockchain" {
  vpc_id = aws_vpc.vpc_blockchain.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw_blockchain.id
  }

  tags = {
    Name = "${var.prefix}-rt-blockchain"
  }
}


resource "aws_route_table_association" "subnet_blockchain_route_table_association" {
    subnet_id      = aws_subnet.subnet_blockchain.id
    route_table_id = aws_route_table.rt_blockchain.id
  }


resource "aws_subnet" "subnet_blockchain" {
  vpc_id                  = aws_vpc.vpc_blockchain.id
  cidr_block              = "10.0.0.0/28"  # Adjust as needed
  availability_zone       = var.aws_availability_zone
  map_public_ip_on_launch = true  # Adjust based on your needs

  tags = {
    Name = "${var.prefix}-subnet-blockchain"
  }
}