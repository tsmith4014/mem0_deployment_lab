# Terraform: One-Command AWS Deploy (EC2 + Docker)

Goal: students can clone this repo, edit a small `terraform.tfvars`, run `terraform apply`, and get a working Mem0 API on EC2.

## Prereqs

- AWS credentials configured locally (one of):
  - `aws configure` (Access Key + Secret)
  - AWS SSO / assumed role
- Terraform installed (v1.5+ recommended)
- An existing EC2 key pair for SSH (students should use an existing key pair and set `ssh_key_name` in `terraform.tfvars`)

## Quick Start

From repo root:

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform apply
```

Note: after `terraform apply`, the EC2 instance boots via `user_data` and the API may take **a few minutes** before `swagger_url` is reachable.

After apply, Terraform outputs:

- `api_base_url`
- `swagger_url`
- `ec2_public_ip`
- (sensitive) `api_key` and `admin_api_key` (recommended for Swagger testing)

## Get the Swagger API Key (Recommended)

After `terraform apply`:

```bash
terraform output -raw api_key
terraform output -raw admin_api_key
```

## What Gets Provisioned

- **Security Group**
  - SSH `22/tcp` (optional)
  - API `8000/tcp` (required)
  - Qdrant `6333/tcp` (optional; off by default)
- **IAM role for EC2**
  - Reads `.env` values from SSM Parameter Store at boot
  - Optional: Bedrock invoke permissions for the AWS-only track
- **EC2 instance** with `user_data` that:
  - installs Docker
  - clones this repo
  - writes `.env`
  - starts Qdrant + API containers (no Docker Compose required)

## Provider Modes (AWS default vs OpenAI optional)

### Mode A (Default): AWS Bedrock (Titan embeddings + Bedrock LLM)

In `terraform.tfvars`:

- `ai_mode = "aws"`
- `aws_region = "us-east-1"` (or a Bedrock-enabled region)
- `embedder_model = "amazon.titan-embed-text-v1"`
- `llm_model = "anthropic.claude-3-5-sonnet-20240620-v1:0"` (or any Bedrock model you have access to)

### Mode B (Optional): OpenAI for embeddings + LLM

In `terraform.tfvars`:

- `ai_mode = "openai"`
- `openai_api_key = "..."` (required)

Credentials:

- **Best on EC2**: attach an IAM role to the instance (Terraform does this) and do **not** store long-lived AWS keys in `.env`.

## Config You’ll Most Likely Change (Students)

- `project_name` (used for resource naming)
- `aws_region`
- `instance_type` (lab: try `t3.small`; if builds are slow, use `t3.medium`)
- `root_volume_size_gb` (lab: 20 GB; recommended: 30+ GB)
- `ssh_key_name` (required for this lab)
- `allowed_ssh_cidr` (your public IP/32 recommended)
- `ai_mode` (`aws` or `openai`)

## Example tfvars

Use `terraform.tfvars.example` as your starting point.

## Notes on Secrets

Terraform can’t magically avoid ever handling secrets if you pass them via `terraform.tfvars`.

- This lab stores runtime secrets in **SSM Parameter Store** and fetches them on boot.
- **Do not commit**:
  - `terraform.tfvars`
  - `terraform.tfstate*`
  - `.terraform/`

## Getting the Swagger API Key

Swagger uses the `X-API-Key` header. The value is stored as an SSM SecureString:

```bash
aws ssm get-parameter --with-decryption \
  --name "/<project_name>/API_KEY" \
  --region <aws_region> \
  --query Parameter.Value --output text
```

If you SSH to the instance, it’s also written into:

- `/opt/<project_name>/repo/.env`
