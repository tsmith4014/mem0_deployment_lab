# Mem0 Deployment Lab

Self-hosted memory layer with FastAPI + Qdrant vector database

> **Lab Objective:** Deploy a production-ready AI memory API on AWS (Bedrock + Titan + Qdrant) in ~30 minutes

---

## What You'll Build

```text
Your App → FastAPI (Port 8000) → Mem0 SDK → Qdrant (Vector DB)
```

**Features:**

- REST API for AI memory management
- Semantic search with vector embeddings
- User isolation & session management
- AWS Bedrock (Titan embeddings + Bedrock LLM) for embeddings/LLM
- OpenAI support (optional provider track)
- Docker containerized deployment

---

## Prerequisites

- AWS account with Bedrock enabled in your region (and model access granted)
- Terraform installed (recommended)
- AWS credentials configured locally (AWS CLI, SSO, or assumed role)
- (Optional) OpenAI API key if you choose the OpenAI provider track

---

## Quick Start

### 1. Start Here (Students)

- Student guide: [`docs/students/README.md`](docs/students/README.md)

### 2. Test Your API (Students)

- Use Swagger UI and the demo seed endpoints (recommended): [`docs/students/api.md`](docs/students/api.md)

### 3. Use Swagger UI (Students)

Visit: `http://YOUR_EC2_IP:8000/docs`

---

## What's Included

```text
mem0_deployment_lab/
├── docs/                 # All guides (students + instructors)
├── src/                  # FastAPI application
├── deployment/           # Docker configuration
├── requirements.txt      # Python dependencies
└── infra/                # Terraform + infra docs
```

---

## Stack Components

| Component  | Technology                 | Port |
| ---------- | -------------------------- | ---- |
| API Server | FastAPI + Mem0 SDK         | 8000 |
| Vector DB  | Qdrant                     | 6333 |
| Embeddings | AWS Bedrock (Titan)        | -    |
| LLM        | AWS Bedrock (e.g., Claude) | -    |

---

## Cost Estimate (Rough)

- EC2 (lab): `t3.small` is usually enough; use `t3.medium` if builds are slow
- Bedrock usage: varies by model and traffic (typically pennies for lab usage)
- **Total: ~$30/month + model usage**

---

## Documentation

- **Students (do in order)**
  - [`docs/students/setup.md`](docs/students/setup.md): deploy + verify (Terraform recommended)
  - [`docs/students/api.md`](docs/students/api.md): Swagger + copy/paste examples for each endpoint
  - [`docs/students/architecture.md`](docs/students/architecture.md) (optional): understand embeddings, vector DBs, and Mem0’s infer pipeline
- **Instructors**
  - [`docs/instructors/lab_guide.md`](docs/instructors/lab_guide.md): structure, timing, checkpoints, extensions
  - [`docs/instructors/instructor_notes.md`](docs/instructors/instructor_notes.md): quick reminders and common student pitfalls
- **Infrastructure**
  - [`infra/terraform/README.md`](infra/terraform/README.md): Terraform details (inputs/outputs, what gets created)
- **Interactive docs**
  - Swagger UI: `http://your-server:8000/docs`

---

## Support

- Mem0 Docs: `https://docs.mem0.ai`
- Qdrant Docs: `https://qdrant.tech/documentation/`

---

**Ready to deploy?** Start at [`docs/students/setup.md`](docs/students/setup.md)
