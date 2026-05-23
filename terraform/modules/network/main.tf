locals {
  common_tags = {
    Project     = var.project
    Environment = var.environment
    Owner       = var.owner
    ManagedBy   = "terraform"
  }
}

# Creates the main VPC.
# A VPC is the private network boundary where AWS resources like EC2 instances live.
resource "aws_vpc" "main" {
  cidr_block = var.vpc_cidr

  tags = merge(local.common_tags, {
    Name = "${var.project}-${var.environment}-vpc"
  })
}

# Creates two public subnets inside the VPC.
# Subnets divide the VPC network into smaller network sections.
# count = 2 means Terraform creates one subnet for each CIDR in var.public_subnet_cidrs.
resource "aws_subnet" "public" {
  count = length(var.public_subnet_cidrs)

  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidrs[count.index]
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true

  tags = merge(local.common_tags, {
    Name = "${var.project}-${var.environment}-public-subnet-${count.index + 1}"
    Type = "public"
  })
}

# Creates an Internet Gateway.
# An Internet Gateway allows resources in public subnets to reach the internet.
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = merge(local.common_tags, {
    Name = "${var.project}-${var.environment}-igw"
  })
}

# Creates a public route table.
# A route table controls where network traffic is sent.
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  tags = merge(local.common_tags, {
    Name = "${var.project}-${var.environment}-public-rt"
  })
}

# Adds a default route to the public route table.
# 0.0.0.0/0 means all external traffic.
# The traffic is routed through the Internet Gateway.
resource "aws_route" "public_internet_access" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.main.id
}

# Associates each public subnet with the public route table.
# This makes both subnets public because they use the route table with internet access.
resource "aws_route_table_association" "public" {
  count = length(aws_subnet.public)

  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}