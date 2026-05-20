terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  access_key                  = "test"
  secret_key                  = "test"
  region                      = "us-east-1"

  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  s3_use_path_style           = true

  endpoints {
    s3  = "http://127.0.0.1:4566"
    ec2 = "http://127.0.0.1:4566"
  }
}

resource "aws_s3_bucket" "logs_bucket" {
  bucket = "nimbuskart-logs"

  tags = {
    Project     = "NimbusKart"
    Environment = "staging"
    Owner       = "Aalekh"
    ManagedBy   = "terraform"
  }
}