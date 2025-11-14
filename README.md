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
- OpenAI integration for embeddings
- Docker containerized deployment

---

## Prerequisites

- AWS EC2 instance (t3.medium, Amazon Linux 2023)
- OpenAI API key
- Basic Docker knowledge

---

## Quick Start

### 1. Follow Setup Guide
```bash
cat SETUP.md
```

### 2. Test Your API
```bash
./test_api.sh
```

### 3. Use Swagger UI
Visit: `http://YOUR_EC2_IP:8000/docs`

---

## What's Included

```
mem0_deployment_lab/
├── SETUP.md              # Step-by-step deployment guide
├── src/                  # FastAPI application
├── deployment/           # Docker configuration
├── requirements.txt      # Python dependencies
├── .env.template         # Environment variables template
└── test_api.sh           # API test script
```

---

## Stack Components

| Component | Technology | Port |
|-----------|-----------|------|
| API Server | FastAPI + Mem0 SDK | 8000 |
| Vector DB | Qdrant | 6333 |
| Embeddings | OpenAI (text-embedding-3-small) | - |
| LLM | OpenAI (gpt-4o-mini) | - |

---

## Cost Estimate

- EC2 t3.medium: ~$30/month
- OpenAI API: ~$0.01-0.05 per conversation
- **Total: ~$35/month + usage**

---

## Documentation

- **SETUP.md** - Complete deployment steps (START HERE)
- **ARCHITECTURE.md** - How it works + AWS Bedrock alternative
- **API.md** - API endpoint reference
- Swagger UI: `http://your-server:8000/docs`

---

## Support

- Mem0 Docs: https://docs.mem0.ai
- Qdrant Docs: https://qdrant.tech/documentation/

---

**Ready to deploy?** → Open `SETUP.md`

