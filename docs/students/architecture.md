# How the Mem0 Stack Works

Prev: [`api.md`](api.md) • Start: [`README.md`](README.md)

## What is Mem0?

Mem0 is an **intelligent memory layer** for AI applications. It remembers user conversations and context across sessions, making AI assistants smarter over time.

**Think of it like this:**

- Regular chatbot: Forgets everything after each conversation
- With Mem0: Remembers "Riley prefers SMS after 8pm while on-call" and uses that context later

---

## The Stack (AWS-first)

```text
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
┌──────────────────────────────┐  ┌──────────────────┐
│  AWS Bedrock                 │  │  Qdrant DB       │
│  - Titan embeddings (vectors)│  │  - Vector Store  │
│  - Bedrock LLM (infer=true)  │  │  - Port 6333     │
└──────────────────────────────┘  └──────────────────┘
```

---

## Why Bedrock?

Mem0 uses Bedrock for **two critical functions**:

### 1. Creating Embeddings (Vector Representations)

When you add a memory like "Riley prefers SMS after 8pm while on-call", Mem0:

1. Sends text to Bedrock Titan: `"Riley prefers SMS after 8pm while on-call"`
2. Gets back a 1536-number vector: `[0.023, -0.15, 0.87, ...]`
3. Stores vector in Qdrant for similarity search

**Why vectors?** So we can find semantically similar memories:

- Query: "What food does the user like?"
- Matches: "Riley prefers SMS after 8pm while on-call" (even if the query uses different wording)

### 2. Memory Extraction / Memory Actions (Optional but recommended)

When `infer=true`, a Bedrock LLM analyzes conversation text to extract key facts and decide what to store:

- Input: Chat transcript
- Output: "User is Riley. Prefers SMS after 8pm while on-call."

---

## Cost Breakdown

For a typical student lab session:

- **Embeddings**: $0.02 per 1M tokens (~200 memories = $0.0001)
- **LLM calls**: $0.15 per 1M tokens (~10 conversations = $0.001)
- **Total per student**: < $0.01

For production app with 1000 users:

- ~$5-20/month depending on activity

---

## Optional Provider: OpenAI

This repo supports OpenAI as an optional provider track (controlled by `.env`):

```bash
# Use OpenAI instead of Bedrock
LLM_PROVIDER=openai
EMBEDDER_PROVIDER=openai
OPENAI_API_KEY=...
```

## Optional Provider: Local models (Ollama)

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

**Q: What if Bedrock is unavailable or I don’t have model access?**  
A: Your API can still run, but `add`/`search` may fail because embeddings/LLM calls can’t complete. For labs, the most common issue is missing Bedrock model access.

**Q: Can I use OpenAI instead?**  
A: Yes, OpenAI is an optional provider track (see [`setup.md`](setup.md)).

**Q: Is Qdrant the only vector DB?**  
A: No. Mem0 also supports Pinecone, Weaviate, Milvus, Chroma. Qdrant is easiest to self-host.

---

## For Instructors

**Teaching Tip:** Have students:

1. Deploy AWS-first with Terraform (fast path)
2. Use Swagger UI to explore endpoints
3. Discuss why embeddings + vector search work
4. (Optional) Swap providers to OpenAI as an extension

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

- **Mem0 Docs**: `https://docs.mem0.ai`
- **Supported Providers**: `https://docs.mem0.ai/components/llms/overview`
- **Qdrant Docs**: `https://qdrant.tech/documentation/`
- **Vector Search Explainer**: `https://www.pinecone.io/learn/vector-embeddings/`

---

**Bottom Line**: This lab is AWS-first (Bedrock + Titan). OpenAI and local models remain optional provider tracks. The architecture is provider-agnostic.
