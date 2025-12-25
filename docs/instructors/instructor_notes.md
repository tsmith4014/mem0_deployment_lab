# Quick Instructor Notes

Start: [`README.md`](README.md) • Student guide: [`../students/README.md`](../students/README.md)

## Pre-Class Setup (5 min)

1. Ensure students have AWS access (account + credentials) and can run Terraform
2. Ensure AWS Bedrock is enabled in the target region and model access is granted
3. Ensure the student IAM permissions (below) are in place
4. Test one deployment yourself (end-to-end) so you know what “good” looks like

### Required AWS permissions (student IAM)

Students need permission to run the Terraform in `infra/terraform/`. At a minimum they need to:

- **EC2**: launch and manage an instance + security group
  - `ec2:RunInstances`, `ec2:TerminateInstances`
  - `ec2:CreateSecurityGroup`, `ec2:DeleteSecurityGroup`
  - `ec2:AuthorizeSecurityGroupIngress`, `ec2:AuthorizeSecurityGroupEgress`, `ec2:RevokeSecurityGroupIngress`, `ec2:RevokeSecurityGroupEgress`
  - `ec2:Describe*` (AMIs, VPCs, subnets, instances, SGs)
  - `ec2:CreateTags`
- **IAM**: create an instance role + instance profile + attach inline/managed policies
  - `iam:CreateRole`, `iam:DeleteRole`, `iam:PassRole`
  - `iam:CreatePolicy`, `iam:DeletePolicy`
  - `iam:AttachRolePolicy`, `iam:DetachRolePolicy`
  - `iam:CreateInstanceProfile`, `iam:DeleteInstanceProfile`, `iam:AddRoleToInstanceProfile`, `iam:RemoveRoleFromInstanceProfile`
  - `iam:GetRole`, `iam:GetPolicy`, `iam:List*`
- **SSM Parameter Store**: create/read SecureString parameters for `.env`
  - `ssm:PutParameter`, `ssm:DeleteParameter`, `ssm:GetParameter`, `ssm:GetParameters`
- **KMS decrypt** (for SecureString reads)
  - `kms:Decrypt` (Terraform’s policy uses `*` for labs; production should be tighter)

Notes:

- This lab does **not require SSH** (we typically leave `ssh_key_name` blank in `terraform.tfvars`).
- If you want SSH for debugging, instructors can provide a key pair and restrict `allowed_ssh_cidr` to their IP.

### Ensure Bedrock model access is enabled

Bedrock model access is an account/region setting (Terraform can’t enable it automatically).

From the AWS Console:

- Go to **Amazon Bedrock → Model access**
- Request/enable access to:
  - an embeddings model (Titan): `amazon.titan-embed-text-v1`
  - a text LLM (e.g., Claude)

## Class Flow (90 min)

### Introduction (10 min)

- Explain what we're building
- Show final result
- Discuss use cases

### Hands-On Deployment (55 min)

- Students follow [`../students/setup.md`](../students/setup.md)
- Walk through steps together
- Help with troubleshooting

### Testing & Exploration (15 min)

- Run [`../../scripts/test_api.sh`](../../scripts/test_api.sh)
- Explore Swagger UI
- Try custom queries

### Wrap-Up (10 min)

- Q&A
- Discuss extensions
- Share resources

## Lab vs Assignment (Suggested)

### In-lab (guided)

- Deploy with Terraform (`terraform apply`) and verify `/health`
- Use Swagger:
  - Seed demo data for 3 users (`/v1/demo/seed/*`)
  - Run `search` queries and explain semantic search vs keyword search
- Show where config lives (`.env` on instance, SSM parameters, Terraform outputs)
- Discuss IAM role vs long-lived keys for Bedrock

### Assignment ideas (pick 1–3)

1. **SSM-first secrets (no tfvars for secrets)**
   - Move any student-provided secrets to SSM created out-of-band (AWS CLI / console), then modify Terraform to read them.
2. **Monitoring**
   - Add CloudWatch metrics/dashboards (CPU, disk, memory, container logs) and document what “healthy” looks like.
   - (Stretch) wire alerts into a chat tool.
3. **API / Swagger refactor**
   - Add a new endpoint (e.g., “rotate API keys”) or refactor request/response shapes and update docs.
4. **Separate API key vs Admin key**
   - Change Terraform to generate two distinct keys by default and update outputs + bootstrap.
5. **Data-minded extension**
   - Export `/admin/all-memories` results to a CSV and create a small analysis notebook (top topics, per-user counts, growth over time).

## Common Questions

Q: "Can I use this in production?"
A: Yes, but add: SSL, rate limiting, monitoring, backups

Q: "How much will this cost?"
A: Mostly EC2 cost (~$30/month for a single always-on instance). Bedrock usage varies by model/traffic and is typically pennies for lab testing.

Q: "Can I modify the code?"
A: Absolutely! It's yours. Check src/ directory.

Q: "What if OpenAI is down?"
A: If using the OpenAI provider track, the API will run but embedding/LLM features won’t work. In the default AWS track, this is not relevant.

Q: "Can we stay fully inside AWS (no OpenAI)?"
A: Yes. This is the default track for this lab. See [`../students/setup.md`](../students/setup.md) (Terraform recommended).

## Success Metrics

- All students deploy successfully
- Everyone can add & search memories
- Students understand the architecture
- Can explain vector vs relational DBs

## Cleanup After Class

sudo docker stop mem0_api mem0_qdrant
sudo docker rm mem0_api mem0_qdrant
Or terminate EC2 instances.

## Cost

Per student: ~$0.10 for 2-hour lab
Class of 30: ~$3.00 total

## Files Students Need

- README.md (overview)
- docs/students/setup.md (deployment steps)
- docs/students/api.md (endpoint reference)
- scripts/test_api.sh (testing)
- All code files (src/, deployment/, requirements.txt, .env.template)

## Files YOU Need

- docs/instructors/lab_guide.md (teaching guide)
- docs/instructors/instructor_notes.md (this file)

Good luck!
