# Outputs the ID of the created VPC.
# Useful when other infrastructure needs to reference this network.
output "vpc_id" {
  description = "ID of the created VPC"
  value       = module.network.vpc_id
}

# Outputs IDs of all public subnets.
# Useful when deploying EC2 instances, load balancers, or databases.
output "subnet_ids" {
  description = "IDs of the public subnets"
  value       = module.network.public_subnet_ids
}

# Outputs the name of the created S3 bucket.
# Useful for scripts, applications, and reports.
output "bucket_name" {
  description = "Name of the created S3 bucket"
  value       = aws_s3_bucket.reports.bucket
}
