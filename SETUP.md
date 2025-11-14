# Mem0 Stack Setup Guide

**Deploy a self-hosted AI memory API in 8 steps**

---

## Step 1: Connect to EC2

```bash
ssh -i your-key.pem ec2-user@YOUR_EC2_IP
```

---

## Step 2: Install Docker

```bash
# Update system
sudo yum update -y

# Install Docker
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify
docker --version
docker-compose --version
```

**Note:** Log out and back in for group changes to take effect.

---

## Step 3: Upload Project Files

**Option A - Using SCP (from your local machine):**

```bash
scp -r mem0_deployment_lab ec2-user@YOUR_EC2_IP:~
```

**Option B - Using Git:**

```bash
git clone YOUR_REPO_URL mem0_deployment_lab
cd mem0_deployment_lab
```

---

## Step 4: Configure Environment

```bash
cd ~/mem0_deployment_lab

# Create .env file from template
cp .env.template .env

# Generate API key
openssl rand -hex 32

# Edit .env file
nano .env
```

**Required values:**

- `OPENAI_API_KEY` - Your OpenAI API key
- `API_KEY` - Output from `openssl rand -hex 32`

---

## Step 5: Build Docker Image

```bash
cd ~/mem0_deployment_lab
sudo docker build -t mem0_api:latest -f deployment/Dockerfile .
```

**Expected:** Build completes successfully

---

## Step 6: Create Docker Network

```bash
sudo docker network create mem0_network
```

---

## Step 7: Start Services

### Start Qdrant (Vector Database)

```bash
sudo docker run -d \
  --name mem0_qdrant \
  --network mem0_network \
  -p 6333:6333 \
  -p 6334:6334 \
  -v qdrant_data:/qdrant/storage \
  -e QDRANT__SERVICE__GRPC_PORT=6334 \
  --restart unless-stopped \
  qdrant/qdrant:latest
```

### Start Mem0 API

```bash
cd ~/mem0_deployment_lab
sudo docker run -d \
  --name mem0_api \
  --network mem0_network \
  -p 8000:8000 \
  --env-file .env \
  -e QDRANT_HOST=mem0_qdrant \
  --restart unless-stopped \
  mem0_api:latest
```

---

## Step 8: Verify Deployment

### Check Containers

```bash
sudo docker ps
```

**Expected:** See `mem0_api` and `mem0_qdrant` running

### Check Logs

```bash
sudo docker logs mem0_api
```

**Expected:** See "Uvicorn running on http://0.0.0.0:8000"

### Test Health Endpoint

```bash
curl http://localhost:8000/health
```

**Expected:**

```json
{
  "status": "healthy",
  "components": {
    "api": "operational",
    "memory": "operational",
    "vector_store": "operational"
  }
}
```

---

## Step 9: Get Public IP

```bash
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/public-ipv4
```

Save this IP address!

---

## Step 10: Test API

### Run Test Script

```bash
cd ~/mem0_deployment_lab

# Set API key from .env file
export API_KEY=$(grep '^API_KEY=' .env | cut -d'=' -f2)

# Make script executable
chmod +x test_api.sh

# Run the test
./test_api.sh
```

### Or Test Manually

```bash
# Add memory
curl -X POST http://YOUR_EC2_IP:8000/v1/memories/add \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "messages": [
      {"role": "user", "content": "My name is Alice"}
    ],
    "user_id": "alice_123"
  }'

# Search memory
curl -X POST http://YOUR_EC2_IP:8000/v1/memories/search \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "query": "What is the user'\''s name?",
    "user_id": "alice_123"
  }'
```

---

## Step 11: Access Swagger UI

Open in browser: `http://YOUR_EC2_IP:8000/docs`

1. Click "Authorize"
2. Enter your API key in both fields
3. Click "Authorize" → "Close"
4. Try endpoints!

---

## Common Commands

### View Logs

```bash
sudo docker logs mem0_api -f
sudo docker logs mem0_qdrant -f
```

### Restart Services

```bash
sudo docker restart mem0_api
sudo docker restart mem0_qdrant
```

### Stop Services

```bash
sudo docker stop mem0_api mem0_qdrant
```

### Update Code

```bash
cd ~/mem0_deployment_lab
# Make changes to src/
sudo docker build -t mem0_api:latest -f deployment/Dockerfile .
sudo docker stop mem0_api && sudo docker rm mem0_api
# Run the docker run command from Step 7
```

---

## Security Group Configuration

Make sure your EC2 security group allows:

- **Port 22** - SSH access
- **Port 8000** - API access

---

## Troubleshooting

### Container Won't Start

```bash
sudo docker logs mem0_api
# Check for OpenAI API key issues or Qdrant connection errors
```

### Can't Connect from Browser

- Check security group (port 8000 open)
- Verify API is running: `curl http://localhost:8000/health`

### Memory Not Persisting

```bash
# Check Qdrant volume exists
sudo docker volume ls | grep qdrant
```

---

## What's Next?

- Integrate with your application
- Review API.md for endpoint details
- Check Swagger UI for interactive docs
- Monitor with `/metrics` endpoint

---

**Deployment Complete!** 🎉

Your self-hosted Mem0 API is running at: `http://YOUR_EC2_IP:8000`
