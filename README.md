# Mem0 Deployment Lab

**Self-hosted memory layer with FastAPI + Qdrant vector database**

> **Lab Objective:** Deploy a production-ready AI memory API in 30 minutes

---

## What You'll Build

```
Your App → FastAPI (Port 8000) → Mem0 SDK → Qdrant (Vector DB)
```

**Features:**

- REST API for AI memory management
- Semantic search with vector embeddings
- User isolation & session management
- OpenAI **or** AWS Bedrock (optional track) for embeddings/LLM
- Docker containerized deployment

---

## Prerequisites

- AWS EC2 instance (t3.medium, Amazon Linux 2023)
- OpenAI API key **or** AWS Bedrock access (optional AWS-only track)
- Basic Docker knowledge

---

## Quick Start

### 1. Start Here (Students)

```bash
# Follow the step-by-step deployment guide
cat SETUP.md
```

### 2. Test Your API (Students)

```bash
./test_api.sh
```

### 3. Use Swagger UI (Students)

Visit: `http://YOUR_EC2_IP:8000/docs`

---

## What's Included

```
mem0_deployment_lab/
├── SETUP.md              # START HERE (students): deploy to EC2
├── API.md                # Students: endpoint reference + examples
├── ARCHITECTURE.md       # Students: how it works + Bedrock alternative
├── LAB_GUIDE.md          # Instructors: lesson plan + timing + checkpoints
├── INSTRUCTOR_NOTES.txt  # Instructors: quick run-of-show + reminders
├── src/                  # FastAPI application
├── deployment/           # Docker configuration
├── requirements.txt      # Python dependencies
├── .env.template         # Environment variables template
└── test_api.sh           # API test script
```

---

## Stack Components

| Component  | Technology                      | Port |
| ---------- | ------------------------------- | ---- |
| API Server | FastAPI + Mem0 SDK              | 8000 |
| Vector DB  | Qdrant                          | 6333 |
| Embeddings | OpenAI (text-embedding-3-small) | -    |
| LLM        | OpenAI (gpt-4o-mini)            | -    |

---

## Cost Estimate (Rough)

- EC2 t3.medium: ~$30/month
- OpenAI API: ~$0.01-0.05 per conversation
- **Total: ~$35/month + usage**

---

## Documentation

- **Students (do in order)**
  - `SETUP.md`: deploy the stack + configure `.env`
  - `test_api.sh`: run smoke tests against the API
  - `API.md`: copy/paste examples for each endpoint
  - `ARCHITECTURE.md`: understand why we need an LLM/embeddings + Bedrock option
- **Instructors**
  - `LAB_GUIDE.md`: structure, timing, checkpoints, extensions
  - `INSTRUCTOR_NOTES.txt`: quick reminders and common student pitfalls
- **Infrastructure (optional)**
  - `infra/README.md`: Terraform overview
  - `infra/terraform/README.md`: one-command AWS deploy (`terraform apply`)
- **Interactive docs**
  - Swagger UI: `http://your-server:8000/docs`

---

## Support

- Mem0 Docs: https://docs.mem0.ai
- Qdrant Docs: https://qdrant.tech/documentation/

---

**Ready to deploy?** → Open `SETUP.md`
