terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
provider "aws" {
  region                      = var.aws_region
  access_key                  = "test"
  secret_key                  = "test"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
  s3_use_path_style           = true

  endpoints {
    ec2 = var.localstack_endpoint
    s3  = var.localstack_endpoint
  }
}
locals {
  common_tags = {
    Project     = var.project
    Environment = var.environment
    Owner       = var.owner
    ManagedBy   = "terraform"
  }
}
module "network" {
  source = "./modules/network"

  project             = var.project
  environment         = var.environment
  owner               = var.owner
  vpc_cidr            = var.vpc_cidr
  public_subnet_cidrs = var.public_subnet_cidrs
  availability_zones  = var.availability_zones
}
resource "aws_security_group" "app_sg" {
  name        = "${var.project}-${var.environment}-app-sg"
  description = "Security group for demo EC2 instances"
  vpc_id      = module.network.vpc_id
  ingress {
    description = "Allow SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.allowed_ssh_cidrs
  }
  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${var.project}-${var.environment}-app-sg"
  })
}
resource "aws_instance" "app" {
  count = var.instance_count

  ami                    = var.ami_id
  instance_type          = var.instance_type
  subnet_id              = module.network.public_subnet_ids[count.index]
  vpc_security_group_ids = [aws_security_group.app_sg.id]

  tags = merge(local.common_tags, {
    Name = "${var.project}-${var.environment}-ec2-${count.index + 1}"
  })
}
resource "aws_s3_bucket" "reports" {
  bucket = var.s3_bucket_name

  tags = merge(local.common_tags, {
    Name = var.s3_bucket_name
  })
}
resource "aws_s3_bucket_versioning" "reports" {
  bucket = aws_s3_bucket.reports.id

  versioning_configuration {
    status = "Enabled"
  }
}
resource "aws_s3_bucket_lifecycle_configuration" "reports" {
  count = var.enable_s3_lifecycle_configuration ? 1 : 0

  bucket = aws_s3_bucket.reports.id

  rule {
    id     = "expire-old-versions"
    status = "Enabled"

    filter {
      prefix = ""
    }

    noncurrent_version_expiration {
      noncurrent_days = var.s3_noncurrent_version_expiration_days
    }
  }

  depends_on = [aws_s3_bucket_versioning.reports]
}
resource "aws_ebs_volume" "unused" {
  availability_zone = var.ebs_availability_zone
  size              = var.ebs_volume_size
  type              = var.ebs_volume_type

  tags = merge(local.common_tags, {
    Name        = "${var.project}-${var.environment}-unused-ebs"
    CostJanitor = "candidate"
    Attached    = "false"
  })
}
