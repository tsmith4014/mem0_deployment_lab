# Infrastructure (Terraform)

This repo includes a **Terraform deployment** that provisions the AWS resources needed to run the Mem0 stack on EC2.

## Start Here

- Go to `infra/terraform/README.md`

## What Terraform Deploys

- **EC2 instance** (Amazon Linux 2023) with Docker installed
- **Security group** allowing:
  - `22/tcp` (SSH)
  - `8000/tcp` (FastAPI API + Swagger)
  - (optional) `6333/tcp` (Qdrant) — disabled by default
- **IAM role + instance profile**
  - Always: permissions to read SSM parameters used for `.env`
  - Optional (AWS-only track): permissions to invoke **AWS Bedrock**

## Provider Choice (AWS Bedrock vs OpenAI optional)

Terraform supports two modes:

- **Default track (AWS Bedrock + Titan)**
  - Uses the EC2 instance IAM role (recommended)
  - `ai_mode = "aws"`
  - `embedder_model = "amazon.titan-embed-text-v1"`
- **Optional track (OpenAI)**
  - Uses `OPENAI_API_KEY`
  - `ai_mode = "openai"`

## Important Notes (Teaching-friendly)

- Your **terraform state may include secrets** if you put them in tfvars.
  - For labs: keep `terraform.tfstate` local and never commit it.
  - For production: use a remote backend (S3 + DynamoDB) with encryption.
