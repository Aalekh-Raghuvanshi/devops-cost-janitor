# AWS region where resources will be created.
# Even though LocalStack runs locally, Terraform still expects a region value.
variable "region" {
  description = "AWS region used by Terraform and LocalStack"
  type        = string
  default     = "us-east-1"
}

# Environment name for separating infrastructure.
# Common values:
# - dev
# - test
# - staging
# - prod
variable "environment" {
  description = "Deployment environment name"
  type        = string
  default     = "dev"
}

# Owner of the infrastructure.
# Useful for tracking responsibility and FinOps tagging.
variable "owner" {
  description = "Person or team responsible for the infrastructure"
  type        = string
  default     = "Pranshu"
}

# CIDR block allowed to SSH into EC2 instances.
# 0.0.0.0/0 means anyone on the internet can attempt SSH access.
# For production systems, restrict this to trusted IP ranges.
variable "ssh_allowed_cidr" {
  description = "CIDR range allowed to access EC2 instances using SSH"
  type        = string
  default     = "0.0.0.0/0"
}

# EC2 instance size/type.
# t2.micro is commonly used for lightweight testing environments.
variable "instance_type" {
  description = "EC2 instance size used for test instances"
  type        = string
  default     = "t2.micro"
}

# Main project name used in naming and tagging resources.
# Helps identify resources belonging to this assignment.
variable "project_name" {
  description = "Project name used for naming and tagging AWS resources"
  type        = string
  default     = "cost-janitor"
}

# LocalStack endpoint URL.
# Terraform will send AWS API calls here instead of real AWS.
variable "localstack_endpoint" {
  description = "Endpoint URL for LocalStack"
  type        = string
  default     = "http://localhost:4566"
}

# CIDR block for the VPC.
# Defines the private network range for the environment.
variable "vpc_cidr" {
  description = "CIDR block used by the VPC"
  type        = string
  default     = "10.20.0.0/16"
}

# Public subnet CIDR ranges.
# Two subnets are created in different availability zones.
variable "public_subnet_cidrs" {
  description = "CIDR blocks used for public subnets"
  type        = list(string)

  default = [
    "10.20.1.0/24",
    "10.20.2.0/24"
  ]
}

# Availability zones used for subnet placement.
# Multiple AZs improve resilience and mimic real cloud deployments.
variable "availability_zones" {
  description = "Availability zones used for public subnets"
  type        = list(string)

  default = [
    "us-east-1a",
    "us-east-1b"
  ]
}

# Number of EC2 instances to create.
variable "instance_count" {
  description = "Total number of EC2 instances"
  type        = number
  default     = 2
}

# AMI ID for EC2 instances.
# LocalStack does not validate real AMIs, so a placeholder is sufficient.
variable "ami_id" {
  description = "AMI ID used for EC2 instances"
  type        = string
  default     = "ami-12345678"
}

# Name of the S3 bucket.
# S3 bucket names should generally be globally unique in real AWS.
variable "s3_bucket_name" {
  description = "S3 bucket used for reports and logs"
  type        = string
  default     = "cost-janitor-reports"
}

# Number of days before old object versions expire.
# Helps demonstrate lifecycle cost optimization policies.
variable "s3_noncurrent_version_expiration_days" {
  description = "Days before old S3 object versions are automatically deleted"
  type        = number
  default     = 30
}

# Availability zone for the unattached EBS volume.
variable "ebs_availability_zone" {
  description = "Availability zone where the EBS volume will be created"
  type        = string
  default     = "us-east-1a"
}

# Size of the EBS volume in GB.
variable "ebs_volume_size" {
  description = "Size of the EBS volume in gigabytes"
  type        = number
  default     = 10
}

# EBS storage type.
# gp2 is a common general-purpose SSD type.
variable "ebs_volume_type" {
  description = "Type of EBS storage volume"
  type        = string
  default     = "gp2"
}