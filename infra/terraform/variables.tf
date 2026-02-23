variable "project_name" {
  type        = string
  description = "Prefix used for naming AWS resources."
  default     = "mem0-deployment-lab"
}

variable "owner" {
  type        = string
  description = "Tag value for ownership (e.g., instructor name or student handle)."
  default     = "student"
}

variable "aws_region" {
  type        = string
  description = "AWS region for infrastructure resources."
  default     = "us-east-1"
}

variable "instance_type" {
  type        = string
  description = "EC2 instance type."
  default     = "t3.small"
}

variable "root_volume_size_gb" {
  type        = number
  description = "Root EBS volume size (GB)."
  default     = 30
}

variable "ssh_key_name" {
  type        = string
  description = "EC2 Key Pair name for SSH access."
  default     = ""
}

variable "ssh_public_key_path" {
  type        = string
  description = "Path to SSH public key file. If provided, creates a new key pair. Leave empty to skip key pair creation."
  default     = ""
}

variable "allowed_ssh_cidr" {
  type        = string
  description = "CIDR allowed to SSH to the instance (only used if ssh_key_name is set)."
  default     = "0.0.0.0/0"
}

variable "api_port" {
  type        = number
  description = "Public API port exposed on the instance."
  default     = 8000
}

variable "expose_qdrant_public" {
  type        = bool
  description = "If true, open port 6333 to the internet. Default false."
  default     = false
}

variable "api_host" {
  type        = string
  description = "Bind address inside the API container."
  default     = "0.0.0.0"
}

variable "docker_network_name" {
  type        = string
  description = "Docker network name used to connect the API and Qdrant containers."
  default     = "mem0_network"
}

variable "api_container_name" {
  type        = string
  description = "Docker container name for the Mem0 API."
  default     = "mem0_api"
}

variable "api_image_name" {
  type        = string
  description = "Docker image name/tag for the Mem0 API built on the instance."
  default     = "mem0_api:latest"
}

variable "qdrant_container_name" {
  type        = string
  description = "Docker container name for Qdrant."
  default     = "mem0_qdrant"
}

variable "qdrant_image" {
  type        = string
  description = "Qdrant Docker image (tagged). Consider pinning for classroom stability."
  default     = "qdrant/qdrant:latest"
}

variable "qdrant_volume_name" {
  type        = string
  description = "Docker volume name for Qdrant persistence."
  default     = "qdrant_data"
}

variable "qdrant_http_port" {
  type        = number
  description = "Qdrant HTTP port."
  default     = 6333
}

variable "qdrant_grpc_port" {
  type        = number
  description = "Qdrant gRPC port."
  default     = 6334
}

variable "repo_url" {
  type        = string
  description = "Git URL of this repo (public recommended for labs)."
}

variable "repo_ref" {
  type        = string
  description = "Git ref to deploy (branch/tag/sha)."
  default     = "main"
}

# AI mode:
# - openai: OpenAI for embeddings + LLM
# - aws:    AWS Bedrock for embeddings + LLM (Titan + Claude, etc.)
variable "ai_mode" {
  type        = string
  description = "AI provider mode: openai | aws"
  default     = "aws"
  validation {
    condition     = contains(["openai", "aws"], var.ai_mode)
    error_message = "ai_mode must be one of: openai, aws"
  }
}

variable "openai_api_key" {
  type        = string
  description = "OpenAI API key (required when ai_mode=openai). Runtime validation in dependencies.py will catch missing keys."
  default     = ""
  sensitive   = true
}

variable "openai_base_url" {
  type        = string
  description = "Optional OpenAI-compatible base URL."
  default     = ""
}

variable "aws_region_runtime" {
  type        = string
  description = "AWS Bedrock runtime region (used when ai_mode=aws)."
  default     = "us-east-1"
}

variable "embedder_model" {
  type        = string
  description = "Embedding model. For Bedrock Titan: amazon.titan-embed-text-v1. For OpenAI: text-embedding-3-small."
  default     = "amazon.titan-embed-text-v1"
}

variable "llm_model" {
  type        = string
  description = "LLM model id. For OpenAI: gpt-4o-mini. For Bedrock: e.g. anthropic.claude-3-5-sonnet-20240620-v1:0"
  default     = "anthropic.claude-3-5-sonnet-20240620-v1:0"
}

variable "llm_temperature" {
  type        = number
  description = "LLM temperature."
  default     = 0.7
}

variable "api_key" {
  type        = string
  description = "API key for this service. Leave blank to auto-generate."
  default     = ""
  sensitive   = true
}

variable "admin_api_key" {
  type        = string
  description = "Admin API key. Leave blank to default to api_key."
  default     = ""
  sensitive   = true
}


