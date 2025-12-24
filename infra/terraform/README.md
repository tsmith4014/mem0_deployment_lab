# Terraform: One-Command AWS Deploy (EC2 + Docker Compose)

Goal: students can clone this repo, edit a small `terraform.tfvars`, run `terraform apply`, and get a working Mem0 API on EC2.

## Prereqs

- AWS credentials configured locally (one of):
  - `aws configure` (Access Key + Secret)
  - AWS SSO / assumed role
- Terraform installed (v1.5+ recommended)
- An existing EC2 key pair for SSH (optional, but recommended)

## Quick Start

From repo root:

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform apply
```

After apply, Terraform outputs:
- `api_base_url`
- `swagger_url`
- `ec2_public_ip`

## What Gets Provisioned

- **Security Group**
  - SSH `22/tcp` (optional)
  - API `8000/tcp` (required)
  - Qdrant `6333/tcp` (optional; off by default)
- **IAM role for EC2**
  - Reads `.env` values from SSM Parameter Store at boot
  - Optional: Bedrock invoke permissions for the AWS-only track
- **EC2 instance** with `user_data` that:
  - installs Docker + Docker Compose
  - clones this repo
  - writes `.env`
  - runs `docker compose up -d --build`

## Provider Modes (OpenAI vs AWS-only)

### Mode A (Default): OpenAI for embeddings + LLM

In `terraform.tfvars`:

- `ai_mode = "openai"`
- `openai_api_key = "..."` (required)

### Mode B (Optional AWS-only): Bedrock (Titan embeddings + Bedrock LLM)

In `terraform.tfvars`:

- `ai_mode = "aws"`
- `aws_region = "us-east-1"` (or a Bedrock-enabled region)
- `embedder_model = "amazon.titan-embed-text-v1"`
- `llm_model = "anthropic.claude-3-5-sonnet-20240620-v1:0"` (or any Bedrock model you have access to)

Credentials:
- **Best on EC2**: attach an IAM role to the instance (Terraform does this) and do **not** store long-lived AWS keys in `.env`.

## Config You’ll Most Likely Change (Students)

- `project_name` (used for resource naming)
- `aws_region`
- `instance_type`
- `allowed_ssh_cidr` (your IP)
- `ai_mode` (`openai` or `aws`)

## Example tfvars

Use `terraform.tfvars.example` as your starting point.

## Notes on Secrets

Terraform can’t magically avoid ever handling secrets if you pass them via `terraform.tfvars`.
- This lab stores runtime secrets in **SSM Parameter Store** and fetches them on boot.
- **Do not commit**:
  - `terraform.tfvars`
  - `terraform.tfstate*`
  - `.terraform/`


