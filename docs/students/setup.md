# Mem0 Stack Setup Guide (AWS-first)

Start here: [`README.md`](README.md) • Next: [`api.md`](api.md)

Deploy a self-hosted AI memory API on AWS using:

- FastAPI + Mem0
- Qdrant (vector DB)
- AWS Bedrock: Titan embeddings + a Bedrock LLM

---

## Path A (Recommended): Terraform + AWS Bedrock

This is the default for the lab: one `terraform apply` provisions the AWS resources and boots the containers.

### Prereqs (your laptop)

- AWS credentials configured (AWS CLI / SSO / assumed role)
- Terraform installed
- Bedrock enabled in your AWS region and **model access granted**
- An existing EC2 key pair (for SSH)

### Deploy

From repo root:

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
```

**STOP: Edit `terraform.tfvars` before running Terraform!**

Open `terraform.tfvars` and set:

1. **`project_name`** → Make this unique (e.g., `"mem0-lab-alice"`) to avoid conflicts with other students
2. **`owner`** → Set to your name or student ID (for tracking)
3. **`ssh_key_name`** → Set to an existing EC2 key pair name in your AWS account/region
4. **`allowed_ssh_cidr`** → Set to your public IP with `/32` (optional, but recommended for security)

Then run:

```bash
terraform init
terraform apply
```

**About `.terraform.lock.hcl`**: When you run `terraform init`, you'll notice a `.terraform.lock.hcl` file already exists in the repo. This is Terraform's **dependency lock file** that pins specific provider versions (similar to `package-lock.json` in Node.js or `requirements.txt` in Python). It ensures everyone in the class uses the exact same AWS provider version, preventing "works on my machine" issues. The lock file is committed to git and should not be deleted.

Note: after `terraform apply`, the instance boots via `user_data` and the API may take **a few minutes** before `swagger_url` is reachable.

### Get URLs + keys (for Swagger)

```bash
cd infra/terraform
terraform output -raw swagger_url
terraform output -raw api_base_url
terraform output -raw api_key
terraform output -raw admin_api_key
```

**SSH Access**: If you configured `ssh_key_name` in your `terraform.tfvars`, you can get a ready-to-use SSH command:

```bash
terraform output -raw ssh_command
```

This will output something like: `ssh -i "your-key.pem" ec2-user@ec2-x-x-x-x.compute-1.amazonaws.com`

You can copy and paste this directly into your terminal to connect to the EC2 instance for debugging.

### Use Swagger (this is the exploration part of the lab)

- Open the Swagger URL from Terraform output: `terraform output -raw swagger_url`
- Click **Authorize**
- Paste:
  - `terraform output -raw api_key` into **X-API-Key**
  - `terraform output -raw admin_api_key` into **X-Admin-Key**

Then run:

- `POST /v1/demo/seed/tony-stark`
- `POST /v1/demo/seed/leia-organa`
- `POST /v1/demo/seed/hermione-granger`

---

## Optional Provider Track: OpenAI

If you want to use OpenAI instead of Bedrock, set in **Terraform** (`infra/terraform/terraform.tfvars`):

- `ai_mode = "openai"`
- `openai_api_key = "..."` (required)

Everything else stays the same.

---

## Debugging `infer=true` (Bedrock)

If you see `{"results":[]}` when calling `/v1/memories/add` with `infer=true`, enable Mem0's Bedrock LLM debug logging:

- Check logs:

```bash
sudo docker logs mem0_api --tail 200
```

If debug logging is enabled for the lab, you’ll see extra lines showing the raw model response so you can confirm whether it returned valid JSON facts.

---

Next: [`api.md`](api.md)
