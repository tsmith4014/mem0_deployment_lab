# Mem0 Deployment Lab - Instructor Guide

## Lab Overview

**Duration:** 60-90 minutes  
**Difficulty:** Intermediate  
**Prerequisites:** Basic Linux, Docker, AWS knowledge

---

## Learning Objectives

By the end of this lab, students will be able to:
1. Deploy a containerized FastAPI application to AWS EC2
2. Configure and run a Qdrant vector database
3. Integrate OpenAI embeddings for semantic search
4. Test RESTful API endpoints
5. Use Swagger UI for API exploration

---

## Lab Structure

### Part 1: Environment Setup (20 min)
- Connect to EC2
- Install Docker & Docker Compose
- Upload project files

### Part 2: Configuration (10 min)
- Configure environment variables
- Generate API keys
- Understand configuration options

### Part 3: Docker Deployment (15 min)
- Build custom Docker image
- Start Qdrant database
- Start FastAPI application
- Verify deployment

### Part 4: Testing & Exploration (25 min)
- Run test script
- Use Swagger UI
- Test with curl/Postman
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

## Common Student Issues

### Issue 1: "Docker command not found"
**Solution:** User needs to log out and back in after adding to docker group

### Issue 2: "Can't connect to API from browser"
**Solution:** Check EC2 security group - port 8000 must be open

### Issue 3: "OpenAI API error"
**Solution:** Verify OPENAI_API_KEY is set correctly in .env

### Issue 4: "Container keeps restarting"
**Solution:** Check logs with `sudo docker logs mem0_api`

---

## Checkpoints

### Checkpoint 1: Docker Installed
```bash
docker --version
docker-compose --version
```

### Checkpoint 2: Files Uploaded
```bash
ls ~/mem0_deployment_lab
# Should see: src/, deployment/, SETUP.md, etc.
```

### Checkpoint 3: Environment Configured
```bash
cat ~/mem0_deployment_lab/.env | grep -v "^#"
# Should see OPENAI_API_KEY and API_KEY filled in
```

### Checkpoint 4: Containers Running
```bash
sudo docker ps
# Should see mem0_api and mem0_qdrant running
```

### Checkpoint 5: Health Check Pass
```bash
curl http://localhost:8000/health
# Should return {"status": "healthy", ...}
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
3. Monitor OpenAI costs via /metrics endpoint

### Advanced Extensions
1. Modify the FastAPI code to add a custom endpoint
2. Set up nginx reverse proxy with SSL
3. Implement rate limiting

---

## Assessment Ideas

### Knowledge Check Questions
1. What is the difference between a vector database and a relational database?
2. Why do we use Docker networks instead of localhost?
3. What authentication method does this API use?
4. How are embeddings generated in this system?

### Practical Assessment
1. Successfully deploy the stack to EC2
2. Add and search memories via API
3. Explain the role of each component
4. Demonstrate Swagger UI usage

---

## Troubleshooting Tips

### For Instructors

**If containers won't start:**
```bash
# Check available memory
free -h

# Check disk space
df -h

# Remove old containers/images
sudo docker system prune -a
```

**If OpenAI is slow:**
- Could be rate limiting
- Check OpenAI dashboard for quota
- Consider using smaller model for demo

**If Qdrant connection fails:**
- Ensure Qdrant container started first
- Check Docker network: `sudo docker network inspect mem0_network`
- Verify QDRANT_HOST env var is set to "mem0_qdrant"

---

## Time Management

| Activity | Estimated Time | Critical? |
|----------|---------------|-----------|
| EC2 connection | 5 min | Yes |
| Docker installation | 15 min | Yes |
| File upload | 5 min | Yes |
| Configuration | 10 min | Yes |
| Docker build | 10 min | Yes |
| Start services | 5 min | Yes |
| Testing | 15 min | Yes |
| Swagger exploration | 10 min | No |
| Discussion | 10 min | No |

**Critical path:** ~55 minutes  
**Full lab:** 85 minutes

---

## Pre-Lab Preparation

### Before Class
1. Provision EC2 instances for students
2. Ensure security groups have ports 22, 8000 open
3. Test deployment on one instance
4. Have OpenAI API key ready (or students bring their own)

### Materials Needed
- EC2 SSH keys (one per student)
- This repository URL or zip file
- OpenAI API keys
- Projected screen for demos

---

## Post-Lab Debrief

### Discussion Questions
1. What challenges did you face during deployment?
2. How would you modify this for production use?
3. What other use cases could benefit from vector databases?
4. What security improvements would you add?

### Follow-Up Resources
- Mem0 documentation: https://docs.mem0.ai
- Qdrant documentation: https://qdrant.tech
- FastAPI documentation: https://fastapi.tiangolo.com

---

## Cost Management

**Per Student:**
- EC2 t3.medium: $0.0416/hour × 2 hours = $0.08
- OpenAI API: ~$0.01 for testing
- **Total: ~$0.10 per student**

**For 30 students:** ~$3.00 total

**Remember to terminate EC2 instances after lab!**

---

## Success Criteria

Students should be able to:
- ✅ Deploy the full stack independently
- ✅ Successfully add and search memories
- ✅ Explain the architecture
- ✅ Use the Swagger UI
- ✅ Troubleshoot basic issues

---

## Additional Notes

- Have a backup demo instance ready
- Screenshot key steps for presentation
- Encourage students to experiment after deployment
- This can be extended to a multi-day project

---

**Questions?** Contact the course instructor.

