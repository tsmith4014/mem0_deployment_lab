# Mem0 Deployment Lab - Instructor Guide

Start: [`README.md`](README.md) • Student guide: [`../students/README.md`](../students/README.md)

## Lab Overview

**Duration:** 60-90 minutes  
**Difficulty:** Intermediate  
**Prerequisites:** Basic Linux, Docker, AWS knowledge

---

## Learning Objectives

By the end of this lab, students will be able to:

1. Deploy a containerized FastAPI application to AWS EC2
2. Configure and run a Qdrant vector database
3. Integrate AWS Bedrock (Titan embeddings + Bedrock LLM) for semantic memory
4. Test RESTful API endpoints
5. Use Swagger UI for API exploration

---

## Lab Structure

### Part 1: Environment Setup (20 min)

- Deploy with Terraform (recommended)
- Instructor-only: if troubleshooting is needed, you can enable SSH in Terraform and then observe containers/logs

### Part 2: Configuration (10 min)

- Understand API key auth and where keys are stored (Terraform outputs / SSM)

### Part 3: Docker Deployment (15 min)

- Verify `/health` and if needed, troubleshoot with logs but will need to enable SSH in Terraform to do this.

### Part 4: Testing & Exploration (25 min)

- Use Swagger UI (primary workflow)
- (Optional) Show that Swagger is just authenticated HTTP requests (curl/Postman) after the lab
- Understand API responses

### Part 5: Integration Discussion (10 min)

- How to integrate with applications
- Best practices
- Q&A

---

## Key Teaching Points

### 1. Why Vector Databases?

- Traditional DBs: Exact match search
- Vector DBs: Semantic similarity search
- Use case: AI memory requires understanding meaning, not keywords

### 2. Why Docker?

- Consistent environment across machines
- Easy deployment and scaling
- Isolated dependencies

### 3. API Design

- RESTful principles
- Authentication with API keys
- Standard response formats

### 4. Production Considerations

- Environment variables for secrets
- Docker networking for service communication
- Persistent volumes for data

---

### Checkpoint: Health Check Pass

```bash
# Students should use Terraform output to open Swagger and verify /health there:
# terraform output -raw swagger_url
```

---

## Extension Activities

For students who finish early:

### Easy Extensions

1. Test all CRUD operations (Update, Delete)
2. Create memories for multiple users
3. Test user isolation

### Medium Extensions

1. Write a Python script to integrate with the API
2. Explore Qdrant dashboard at port 6333
3. Discuss model usage/costs and how to monitor usage (CloudWatch/Billing + app metrics)

### Advanced Extensions

1. Modify the FastAPI code to add a custom endpoint
2. Set up nginx reverse proxy with SSL
3. Implement rate limiting
4. Optional provider swap: switch to OpenAI

---

### Knowledge Check Questions

1. What is the difference between a vector database and a relational database?
2. Why do we use Docker networks instead of localhost?
3. What authentication method does this API use?
4. How are embeddings generated in this system?

### Practical Checkpoints

1. Successfully deploy the stack to EC2
2. Add and search memories via API
3. Explain the role of each component
4. Demonstrate Swagger UI usage

---

## Troubleshooting Tips

**If Qdrant connection fails:**

- Ensure Qdrant container started first
- Check Docker network: `sudo docker network inspect mem0_network`
- Verify the Qdrant host value is set correctly (the Terraform bootstrap runs Qdrant as `mem0_qdrant`)

---

## Time Management

| Activity            | Estimated Time |
| ------------------- | -------------- |
| Terraform apply     | 5 min          |
| Wait for bootstrap  | 5 min          |
| Swagger auth        | 3 min          |
| Seed + search demo  | 10-15 min      |
| Testing             | 10-15 min      |
| Swagger exploration | 10-30 min      |
| Discussion          | 10 min         |

---

## Pre-Lab Preparation

### Before Class

Discover with Bedrock model access is enabled in what AWS account/region

### Materials Needed

- This repository URL
- AWS account access with Bedrock enabled (and model access granted)

---

## Post-Lab Debrief

### Discussion Questions

1. What challenges did you face during deployment?
2. How to make this more engaging for the students?
3. What other use cases could benefit from vector databases?
4. What security improvements would you add?

### Follow-Up Resources

- Mem0 documentation: `https://docs.mem0.ai`
- Qdrant documentation: `https://qdrant.tech`
- FastAPI documentation: `https://fastapi.tiangolo.com`

---

## Cost Management

**Per Student:**

- EC2 (example): t3.small is usually enough for the lab; t3.medium is a safer default if builds are slow.
- Bedrock usage: varies by model and traffic (typically pennies for lab usage)
- **Total: ~$0.10 per student**

**For 30 students:** ~$3.00 total

**Remember to clean up after lab:** run `terraform destroy` from `infra/terraform`.

---

## Success Criteria

Students should be able to:

- Deploy the full stack independently
- Successfully add and search memories
- Explain the architecture
- Use the Swagger UI
- Troubleshoot basic issues

---

## Additional Notes

- Screenshot key steps for presentation
- Encourage students to experiment after deployment
- This can be extended to a multi-day project

---

**Questions?** Contact the course instructor.
