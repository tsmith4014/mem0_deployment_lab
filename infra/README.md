# Infrastructure (Terraform)

This repo includes an **optional Terraform deployment** that can provision all AWS resources needed to run the Mem0 stack on EC2.

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

## Provider Choice (OpenAI vs AWS Bedrock)

Terraform supports two modes:

- **Default track (OpenAI)**
  - Uses `OPENAI_API_KEY`
  - `LLM_PROVIDER=openai`, `EMBEDDER_PROVIDER=openai`
- **AWS-only track (Bedrock + Titan embeddings)**
  - Uses IAM role (recommended) or AWS keys
  - `LLM_PROVIDER=aws_bedrock`, `EMBEDDER_PROVIDER=aws_bedrock`
  - `EMBEDDER_MODEL=amazon.titan-embed-text-v1`

## Important Notes (Teaching-friendly)

- Your **terraform state may include secrets** if you put them in tfvars.
  - For labs: keep `terraform.tfstate` local and never commit it.
  - For production: use a remote backend (S3 + DynamoDB) with encryption.


