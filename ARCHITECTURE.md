# How the Mem0 Stack Works

## What is Mem0?

Mem0 is an **intelligent memory layer** for AI applications. It remembers user conversations and context across sessions, making AI assistants smarter over time.

**Think of it like this:**

- Regular chatbot: Forgets everything after each conversation
- With Mem0: Remembers "Alice prefers emails in the morning" and uses that context forever

---

## The Stack

```
┌─────────────────────────────────────────────────┐
│  Your Application (Chatbot, Agent, etc.)       │
└────────────────┬────────────────────────────────┘
                 │ HTTP Requests
┌────────────────▼────────────────────────────────┐
│  FastAPI Server (Port 8000)                     │
│  - Routes: Add, Search, Update memories         │
│  - Auth: API Key validation                     │
└────────┬──────────────────────┬─────────────────┘
         │                      │
         │ Embeddings           │ Storage
         ▼                      ▼
┌────────────────────┐  ┌──────────────────┐
│  OpenAI API        │  │  Qdrant DB       │
│  - LLM (gpt-4o)    │  │  - Vector Store  │
│  - Embeddings      │  │  - Port 6333     │
└────────────────────┘  └──────────────────┘
```

---

## Why OpenAI API Key?

Mem0 uses OpenAI for **two critical functions**:

### 1. Creating Embeddings (Vector Representations)

When you add a memory like "User loves pizza", Mem0:

1. Sends text to OpenAI: `"User loves pizza"`
2. Gets back a 1536-number vector: `[0.023, -0.15, 0.87, ...]`
3. Stores vector in Qdrant for similarity search

**Why vectors?** So we can find semantically similar memories:

- Query: "What food does the user like?"
- Matches: "User loves pizza" (even though words differ!)

### 2. Memory Extraction (Optional)

OpenAI's LLM analyzes conversations to extract key facts:

- Input: Chat transcript
- Output: "User's name is Alice. Lives in Austin. Prefers morning emails."

---

## Cost Breakdown

For a typical student lab session:

- **Embeddings**: $0.02 per 1M tokens (~200 memories = $0.0001)
- **LLM calls**: $0.15 per 1M tokens (~10 conversations = $0.001)
- **Total per student**: < $0.01

For production app with 1000 users:

- ~$5-20/month depending on activity

---

## Can We Use AWS Bedrock Instead?

**YES!** Mem0 supports multiple providers. Here's how:

### Option 1: AWS Bedrock (Titan/Claude)

This repo supports Bedrock **without code changes** (it’s controlled by `.env`).

**AWS-only track (no OpenAI):**

```bash
# Switch providers
LLM_PROVIDER=aws_bedrock
EMBEDDER_PROVIDER=aws_bedrock

# Pick models (examples)
EMBEDDER_MODEL=amazon.titan-embed-text-v1
LLM_MODEL=anthropic.claude-3-5-sonnet-20240620-v1:0

# Region (must be Bedrock-enabled)
AWS_REGION=us-east-1

# Credentials (optional on EC2 if using an instance role)
# AWS_ACCESS_KEY_ID=...
# AWS_SECRET_ACCESS_KEY=...
# AWS_SESSION_TOKEN=...
```

**Important:** On EC2, the cleanest approach is an **IAM role** on the instance with Bedrock permissions (no long-lived keys in `.env`).

**Pros:**

- No OpenAI dependency
- Potentially lower cost at scale
- AWS credits can be used
- Data stays in AWS ecosystem

**Cons:**

- More complex AWS IAM setup
- Need AWS account with Bedrock access
- Different API quotas/limits

### Option 2: Local Models (Ollama)

For **completely free** option:

```python
"llm": {
    "provider": "ollama",
    "config": {
        "model": "llama2",
        "ollama_base_url": "http://localhost:11434"
    }
}
```

**Pros:**

- Free
- No API keys needed
- Privacy (everything local)

**Cons:**

- Slower
- Lower quality embeddings
- Needs GPU for reasonable speed

---

## What Each Component Does

| Component          | Purpose              | Why It Matters                                 |
| ------------------ | -------------------- | ---------------------------------------------- |
| **FastAPI**        | HTTP API server      | Students learn REST API design                 |
| **Mem0 SDK**       | Memory orchestration | Handles complex logic (deduplication, updates) |
| **Qdrant**         | Vector database      | Learn about semantic search vs SQL             |
| **OpenAI/Bedrock** | Embeddings + LLM     | Understand AI model integration                |
| **Docker**         | Containerization     | Production deployment skills                   |

---

## Key Concepts Students Learn

1. **Vector Embeddings**: Text → Numbers for similarity search
2. **Semantic Search**: Find meaning, not exact text matches
3. **API Design**: REST endpoints, auth, error handling
4. **Docker Networking**: Container communication
5. **Environment Variables**: Secure configuration management
6. **Cloud Deployment**: EC2, security groups, SSH
7. **Cost Management**: Understanding AI API pricing

---

## Common Questions

**Q: Why not just use a SQL database?**  
A: SQL finds exact matches. Vectors find similar meaning. "car accident" and "vehicle collision" are different text but similar meaning.

**Q: What if OpenAI goes down?**  
A: Your API still runs, but add/search operations will fail. That's why multi-provider support matters.

**Q: Can I use free tier OpenAI?**  
A: Yes! Free tier gives $5 credit, enough for ~500 lab sessions.

**Q: Is Qdrant the only vector DB?**  
A: No. Mem0 also supports Pinecone, Weaviate, Milvus, Chroma. Qdrant is easiest to self-host.

---

## For Instructors

**Teaching Tip:** Have students:

1. Deploy with OpenAI (quick setup)
2. Monitor costs at `/metrics` endpoint
3. Discuss why vectors work for memory
4. (Advanced) Swap to Bedrock as extension activity

**Demo Idea:** Show students:

```bash
# Add memory
curl -X POST .../memories/add -d '{"messages": [{"role": "user", "content": "I drive a Tesla"}]}'

# Search with different wording
curl -X POST .../memories/search -d '{"query": "What car does the user have?"}'
# Returns: "I drive a Tesla" (even though "car" ≠ "drive")
```

---

## Resources

- **Mem0 Docs**: https://docs.mem0.ai
- **Supported Providers**: https://docs.mem0.ai/components/llms/overview
- **Qdrant Docs**: https://qdrant.tech/documentation/
- **Vector Search Explainer**: https://www.pinecone.io/learn/vector-embeddings/

---

**Bottom Line**: OpenAI is used because it's easy and high-quality. But you can swap it out for AWS Bedrock, local models, or other providers. The architecture is **provider-agnostic**.
