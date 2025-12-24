output "ec2_public_ip" {
  value       = aws_instance.mem0.public_ip
  description = "Public IP of the EC2 instance."
}

output "api_base_url" {
  value       = "http://${aws_instance.mem0.public_ip}:${var.api_port}"
  description = "Base URL for the API."
}

output "swagger_url" {
  value       = "http://${aws_instance.mem0.public_ip}:${var.api_port}/docs"
  description = "Swagger UI URL."
}

output "api_key" {
  value       = local.effective_api_key
  description = "API key for Swagger / memory endpoints. Get with: terraform output -raw api_key"
  sensitive   = true
}

output "admin_api_key" {
  value       = local.effective_admin_api_key
  description = "Admin API key for /admin endpoints. Get with: terraform output -raw admin_api_key"
  sensitive   = true
}

output "ssm_api_key_name" {
  value       = aws_ssm_parameter.api_key.name
  description = "SSM Parameter Store name that holds the API key."
}

output "ssm_admin_api_key_name" {
  value       = aws_ssm_parameter.admin_api_key.name
  description = "SSM Parameter Store name that holds the admin API key."
}


