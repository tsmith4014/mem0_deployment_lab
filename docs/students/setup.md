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

### Deploy

From repo root:

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform apply
```

### Get URLs + keys (for Swagger)

```bash
cd infra/terraform
terraform output -raw swagger_url
terraform output -raw api_base_url
terraform output -raw api_key
terraform output -raw admin_api_key
```

### Smoke test (run on the EC2 instance)

SSH in, then:

```bash
cd /opt/<project_name>/repo
export API_KEY=$(grep '^API_KEY=' .env | cut -d'=' -f2)
chmod +x scripts/test_api.sh
./scripts/test_api.sh
```

---

## Path B (Optional): Manual Docker on EC2

Use this if you want students to practice Docker setup steps, or if Terraform isn’t available.

### 1) SSH to the instance

```bash
ssh -i your-key.pem ec2-user@YOUR_EC2_IP
```

### 2) Install Docker (Amazon Linux 2023)

```bash
sudo dnf update -y
sudo dnf install -y docker
sudo systemctl enable --now docker
sudo usermod -aG docker ec2-user
docker --version
```

Log out/in so group changes take effect.

### 3) Get the repo and create `.env`

```bash
git clone YOUR_REPO_URL mem0_deployment_lab
cd mem0_deployment_lab
cp .env.template .env
openssl rand -hex 32   # generate API_KEY
nano .env
```

Default lab config (AWS Bedrock):

- `LLM_PROVIDER=aws_bedrock`
- `EMBEDDER_PROVIDER=aws_bedrock`
- `AWS_REGION=...`
- `EMBEDDER_MODEL=amazon.titan-embed-text-v1`
- `LLM_MODEL=...`

### 4) Build + run

```bash
sudo docker build -t mem0_api:latest -f deployment/Dockerfile .
sudo docker network create mem0_network

sudo docker run -d \
  --name mem0_qdrant \
  --network mem0_network \
  -p 6333:6333 \
  -v qdrant_data:/qdrant/storage \
  --restart unless-stopped \
  qdrant/qdrant:latest

sudo docker run -d \
  --name mem0_api \
  --network mem0_network \
  -p 8000:8000 \
  --env-file .env \
  -e QDRANT_HOST=mem0_qdrant \
  --restart unless-stopped \
  mem0_api:latest
```

### 5) Verify + test

```bash
curl http://localhost:8000/health
export API_KEY=$(grep '^API_KEY=' .env | cut -d'=' -f2)
chmod +x scripts/test_api.sh
./scripts/test_api.sh
```

Open Swagger:

- `http://YOUR_EC2_IP:8000/docs`

---

## Optional Provider Track: OpenAI

If you want to use OpenAI instead of Bedrock, set in `.env`:

- `LLM_PROVIDER=openai`
- `EMBEDDER_PROVIDER=openai`
- `OPENAI_API_KEY=...`

Everything else stays the same.

---

## Debugging `infer=true` (Bedrock)

If you see `{"results":[]}` when calling `/v1/memories/add` with `infer=true`, enable Mem0's Bedrock LLM debug logging:

- Set `MEM0_DEBUG_LLM=1` in the API container environment (Terraform writes `.env` on the instance)
- Then check logs:

```bash
sudo docker logs mem0_api --tail 200
```

You should see `[MEM0_DEBUG_LLM]` lines showing the raw model response so you can confirm whether it returned valid JSON facts.

---

Next: [`api.md`](api.md)
