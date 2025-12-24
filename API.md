# API Quick Reference

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

- **Manual setup (following `SETUP.md`)**: it’s in your local `.env` file:

```bash
grep '^API_KEY=' .env
```

- **Terraform setup (`infra/terraform`)**:
  - On the EC2 instance: `/opt/<project_name>/repo/.env`
  - Or from your laptop (AWS CLI):

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
    {"role": "user", "content": "My name is John"},
    {"role": "assistant", "content": "Hi John!"}
  ],
  "user_id": "john_123"
}
```

---

### Search Memory
```bash
POST /v1/memories/search
Content-Type: application/json
X-API-Key: YOUR_KEY

{
  "query": "What is the user's name?",
  "user_id": "john_123",
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
  "user_id": "john_123"
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

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user_id` | string | No | User identifier for isolation |
| `agent_id` | string | No | Agent identifier |
| `run_id` | string | No | Run/session identifier |
| `messages` | array | Yes (add) | Conversation messages |
| `query` | string | Yes (search) | Search query text |
| `limit` | integer | No | Max results (default: 10) |

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
            {"role": "user", "content": "I love pizza"}
        ],
        "user_id": "user_123"
    }
)
print(response.json())

# Search
response = requests.post(
    f"{API_URL}/v1/memories/search",
    headers=headers,
    json={
        "query": "What does the user like?",
        "user_id": "user_123"
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
  "X-API-Key": API_KEY
};

// Add memory
const addMemory = async () => {
  const response = await fetch(`${API_URL}/v1/memories/add`, {
    method: "POST",
    headers,
    body: JSON.stringify({
      messages: [
        { role: "user", content: "I love pizza" }
      ],
      user_id: "user_123"
    })
  });
  return response.json();
};

// Search
const searchMemory = async () => {
  const response = await fetch(`${API_URL}/v1/memories/search`, {
    method: "POST",
    headers,
    body: JSON.stringify({
      query: "What does the user like?",
      user_id: "user_123"
    })
  });
  return response.json();
};
```

---

**For complete API documentation:** See Swagger UI at `/docs`

