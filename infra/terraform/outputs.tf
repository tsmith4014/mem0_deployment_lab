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


