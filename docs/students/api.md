# API Quick Reference

Prev: [`setup.md`](setup.md) • Optional reading: [`architecture.md`](architecture.md)

## Authentication

All endpoints (except `/health`) require `X-API-Key` header:

```bash
-H 'X-API-Key: YOUR_API_KEY_HERE'
```

### Swagger UI (Recommended for Testing)

Open Swagger UI:

- `http://YOUR_EC2_IP:8000/docs`

Click **Authorize** and set:

- **X-API-Key**: your `API_KEY`
- **X-Admin-Key**: only needed for `/admin/*` endpoints (you can set it to the same value as `API_KEY` if you didn’t configure a separate admin key)

### Where is my API key?

Your Swagger key is the value of **`API_KEY`**.

- **Terraform (recommended)**: grab it from Terraform outputs:

```bash
cd infra/terraform
terraform output -raw api_key
terraform output -raw admin_api_key
```

- **Manual setup**: it’s in your `.env` file on the EC2 instance:

```bash
grep '^API_KEY=' .env
```

- **Terraform (alternative)**: it’s stored in SSM Parameter Store (AWS CLI):

```bash
aws ssm get-parameter --with-decryption \
  --name "/<project_name>/API_KEY" \
  --region <aws_region> \
  --query Parameter.Value --output text
```

---

## Core Endpoints

### Health Check

```bash
GET /health
```

No authentication required.

---

### Add Memory

```bash
POST /v1/memories/add
Content-Type: application/json
X-API-Key: YOUR_KEY

{
  "messages": [
    {"role": "user", "content": "My name is Riley. I'm on-call this week. Please page me by SMS after 8pm."},
    {"role": "assistant", "content": "Got it. I’ll page you by SMS after 8pm while you’re on-call."}
  ],
  "user_id": "riley_123",
  "infer": false
}
```

**Tip (Labs):** set `"infer": false` to **force storing** the message as a memory so `get-all`/`search` are deterministic.

---

### Search Memory

```bash
POST /v1/memories/search
Content-Type: application/json
X-API-Key: YOUR_KEY

{
  "query": "How should I notify Riley after hours?",
  "user_id": "riley_123",
  "limit": 10
}
```

---

### Get All Memories

```bash
POST /v1/memories/get-all
Content-Type: application/json
X-API-Key: YOUR_KEY

{
  "user_id": "riley_123"
}
```

---

### Update Memory

```bash
PUT /v1/memories/update
Content-Type: application/json
X-API-Key: YOUR_KEY

{
  "memory_id": "uuid-here",
  "data": "Updated memory text"
}
```

---

### Delete Memory

```bash
DELETE /v1/memories/delete
Content-Type: application/json
X-API-Key: YOUR_KEY

{
  "memory_id": "uuid-here"
}
```

---

## Interactive Documentation

Visit: `http://YOUR_EC2_IP:8000/docs`

- Browse all endpoints
- Test directly from browser
- See request/response schemas
- Authentication built-in

---

## Response Format

### Success

```json
{
  "status": "success",
  "data": { ... }
}
```

### Error

```json
{
  "detail": "Error message"
}
```

---

## Common Fields

| Field      | Type    | Required     | Description                   |
| ---------- | ------- | ------------ | ----------------------------- |
| `user_id`  | string  | No           | User identifier for isolation |
| `agent_id` | string  | No           | Agent identifier              |
| `run_id`   | string  | No           | Run/session identifier        |
| `messages` | array   | Yes (add)    | Conversation messages         |
| `query`    | string  | Yes (search) | Search query text             |
| `limit`    | integer | No           | Max results (default: 10)     |

---

## Quick Examples

### Python

```python
import requests

API_URL = "http://YOUR_EC2_IP:8000"
API_KEY = "your_api_key"

headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

# Add memory
response = requests.post(
    f"{API_URL}/v1/memories/add",
    headers=headers,
    json={
        "messages": [
            {"role": "user", "content": "I'm learning Terraform and I prefer short, step-by-step checklists."}
        ],
        "user_id": "riley_123",
        "infer": False
    }
)
print(response.json())

# Search
response = requests.post(
    f"{API_URL}/v1/memories/search",
    headers=headers,
    json={
        "query": "How should I format instructions for Riley?",
        "user_id": "riley_123"
    }
)
print(response.json())
```

### JavaScript

```javascript
const API_URL = "http://YOUR_EC2_IP:8000";
const API_KEY = "your_api_key";

const headers = {
  "Content-Type": "application/json",
  "X-API-Key": API_KEY,
};

// Add memory
const addMemory = async () => {
  const response = await fetch(`${API_URL}/v1/memories/add`, {
    method: "POST",
    headers,
    body: JSON.stringify({
      messages: [
        {
          role: "user",
          content:
            "I'm learning Docker. I like examples that show the exact commands to run.",
        },
      ],
      user_id: "riley_123",
      infer: false,
    }),
  });
  return response.json();
};

// Search
const searchMemory = async () => {
  const response = await fetch(`${API_URL}/v1/memories/search`, {
    method: "POST",
    headers,
    body: JSON.stringify({
      query: "What kind of examples does Riley prefer?",
      user_id: "riley_123",
    }),
  });
  return response.json();
};
```

---

**For complete API documentation:** See Swagger UI at `/docs`

---

## Demo: Seed 3 Users (Pop Culture)

These endpoints add a bunch of memories so search results are meaningful.
They use `infer=false` for deterministic seeding.

- `POST /v1/demo/seed/tony-stark`
- `POST /v1/demo/seed/leia-organa`
- `POST /v1/demo/seed/hermione-granger`

Notes:

- These endpoints have **no request body**. In Swagger, click **Authorize**, then **Execute**.
- If you get “not authenticated” in Swagger, refresh the page after authorizing.

### What to test / learn (quick checklist)

1. **User isolation**
   - Run `POST /v1/memories/get-all` with `user_id="tony_stark_001"` and confirm you only see Tony’s memories.
2. **Semantic search**
   - Try searches that don’t exactly match the stored text (you’re testing “meaning”, not keywords):
     - `user_id="tony_stark_001"`, query: `How should I page Tony during an incident?`
     - `user_id="leia_organa_001"`, query: `How often does Leia want outage updates?`
     - `user_id="hermione_granger_001"`, query: `What kind of instructions does Hermione prefer?`
3. **Why vectors matter**
   - Compare a keyword-y query vs a rephrased query and notice search still finds the right memory.

### More example queries (smart + cheeky)

Run these via `POST /v1/memories/search` with the matching `user_id`:

**Tony (`tony_stark_001`)**

- Smart:
  - `What is Tony’s preferred paging order?`
  - `What CI tool does Tony use?`
  - `What does Tony check first when debugging?`
  - `What dashboard panels does Tony care about?`
- Cheeky:
  - `How do I get Tony’s attention fast?` (should match the “STARK-LEVEL PRIORITY” label)
  - `What kind of incident updates does Tony want?` (should match “JARVIS-style” updates)
  - `If I ask Tony to edit YAML at 2am, what do I bring?` (yes, really)

**Leia (`leia_organa_001`)**

- Smart:
  - `How often does Leia want outage updates?`
  - `What does Leia want in an on-call message?`
  - `What does Leia require before applying Terraform in prod?`
  - `Which SLO metrics does Leia watch?`
- Cheeky:
  - `Does Leia like alert storms?` (should match “single channel / avoid alert fatigue”)
  - `What does Leia call incident updates?` (should match “mission briefings”)
  - `The graph looks like a moon. What does Leia assume?` (should match “scaling issue”)

**Hermione (`hermione_granger_001`)**

- Smart:
  - `What kind of instructions does Hermione prefer?`
  - `What is Hermione’s troubleshooting order?`
  - `What does Hermione want in docs?`
  - `What does Hermione want in git commits?`
- Cheeky:
  - `What happens if I forget to update the README?`
  - `Is this "magic" or is it configs/logs/permissions?` (should match her “rarely magic” preference)
  - `Does Hermione tolerate "final_final_v3" filenames?`

### Challenge mode (try to “trick” the search)

These should still work even though they don’t match exact wording:

- Tony: `Make the runbook fast. What format does Tony want?`
- Leia: `Keep me posted. How frequently?`
- Hermione: `Give me reproducible steps, not vibes. What’s her preference?`
