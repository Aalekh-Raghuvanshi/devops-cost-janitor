variable "aws_region" {
  description = "AWS region used by Terraform and LocalStack"
  type        = string
  default     = "us-east-1"
}
variable "environment" {
  description = "Deployment environment name"
  type        = string
  default     = "dev"
}
variable "owner" {
  description = "Person or team responsible for the infrastructure"
  type        = string
  default     = "Aalekh"
}
variable "allowed_ssh_cidrs" {
  description = "CIDR ranges allowed to access EC2 instances using SSH"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}
variable "instance_type" {
  description = "EC2 instance size used for test instances"
  type        = string
  default     = "t2.micro"
}
variable "project" {
  description = "Project name used for naming and tagging AWS resources"
  type        = string
  default     = "cost-janitor"
}
variable "localstack_endpoint" {
  description = "Endpoint URL for LocalStack"
  type        = string
  default     = "http://localhost:4566"
}
variable "vpc_cidr" {
  description = "CIDR block used by the VPC"
  type        = string
  default     = "10.20.0.0/16"
}
variable "public_subnet_cidrs" {
  description = "CIDR blocks used for public subnets"
  type        = list(string)

  default = [
    "10.20.1.0/24",
    "10.20.2.0/24"
  ]
}
variable "availability_zones" {
  description = "Availability zones used for public subnets"
  type        = list(string)

  default = [
    "us-east-1a",
    "us-east-1b"
  ]
}
variable "instance_count" {
  description = "Total number of EC2 instances"
  type        = number
  default     = 2
}
variable "ami_id" {
  description = "AMI ID used for EC2 instances"
  type        = string
  default     = "ami-12345678"
}
variable "s3_bucket_name" {
  description = "S3 bucket used for reports and logs"
  type        = string
  default     = "cost-janitor-reports"
}
variable "enable_s3_lifecycle_configuration" {
  description = "Whether to create the S3 lifecycle configuration resource"
  type        = bool
  default     = false
}
variable "s3_noncurrent_version_expiration_days" {
  description = "Days before old S3 object versions are automatically deleted"
  type        = number
  default     = 30
}
variable "ebs_availability_zone" {
  description = "Availability zone where the EBS volume will be created"
  type        = string
  default     = "us-east-1a"
}
variable "ebs_volume_size" {
  description = "Size of the EBS volume in gigabytes"
  type        = number
  default     = 10
}
variable "ebs_volume_type" {
  description = "Type of EBS storage volume"
  type        = string
  default     = "gp2"
}
