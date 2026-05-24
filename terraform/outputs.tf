output "vpc_id" {
  description = "ID of the created VPC"
  value       = module.network.vpc_id
}
output "subnet_ids" {
  description = "IDs of the public subnets"
  value       = module.network.public_subnet_ids
}
output "bucket_name" {
  description = "Name of the created S3 bucket"
  value       = aws_s3_bucket.reports.bucket
}
