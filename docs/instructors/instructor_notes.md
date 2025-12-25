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

### Copy/paste IAM policy (attach to the student group)

An instructor can attach a single IAM policy to the student IAM group to make this lab work.

Below is a **lab-friendly** policy. It is intentionally broader than production least-privilege.
For real environments, tighten this with tag-based conditions and scoped resources.

**How to use:**

- Create a managed policy in IAM (or inline policy on the group)
- Paste the JSON below
- Attach it to the student group

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "EC2RunAndDescribe",
      "Effect": "Allow",
      "Action": [
        "ec2:RunInstances",
        "ec2:TerminateInstances",
        "ec2:CreateTags",
        "ec2:Describe*"
      ],
      "Resource": "*"
    },
    {
      "Sid": "SecurityGroups",
      "Effect": "Allow",
      "Action": [
        "ec2:CreateSecurityGroup",
        "ec2:DeleteSecurityGroup",
        "ec2:AuthorizeSecurityGroupIngress",
        "ec2:AuthorizeSecurityGroupEgress",
        "ec2:RevokeSecurityGroupIngress",
        "ec2:RevokeSecurityGroupEgress"
      ],
      "Resource": "*"
    },
    {
      "Sid": "IAMForEC2InstanceRoleAndProfile",
      "Effect": "Allow",
      "Action": [
        "iam:CreateRole",
        "iam:DeleteRole",
        "iam:GetRole",
        "iam:List*",
        "iam:PassRole",
        "iam:CreatePolicy",
        "iam:DeletePolicy",
        "iam:GetPolicy",
        "iam:AttachRolePolicy",
        "iam:DetachRolePolicy",
        "iam:CreateInstanceProfile",
        "iam:DeleteInstanceProfile",
        "iam:AddRoleToInstanceProfile",
        "iam:RemoveRoleFromInstanceProfile"
      ],
      "Resource": "*"
    },
    {
      "Sid": "SSMParameterStoreForEnv",
      "Effect": "Allow",
      "Action": [
        "ssm:PutParameter",
        "ssm:DeleteParameter",
        "ssm:GetParameter",
        "ssm:GetParameters"
      ],
      "Resource": "*"
    },
    {
      "Sid": "DecryptSecureStringParameters",
      "Effect": "Allow",
      "Action": ["kms:Decrypt"],
      "Resource": "*"
    }
  ]
}
```

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

- Explore Swagger UI
- Seed demo users (`/v1/demo/seed/*`) and run a few searches
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

### Assignments

#### Required (do these in order)

1. **Separate API key vs Admin key**
   - Change Terraform to generate **two distinct keys by default** and update outputs + bootstrap.
   - First step: generate a distinct `ADMIN_API_KEY` using `random_password` (the same way `API_KEY` is generated), then write it to SSM and into the instance `.env`.

2. **Rotate API keys (new endpoint + Swagger testing)**
   - Create an **admin-only** Swagger endpoint that rotates/creates new API keys.
   - Suggested shape: `POST /admin/keys/rotate` (requires `X-Admin-Key`)
   - Requirements (keep it simple for a bootcamp assignment):
     - returns the new key(s) in the response
     - after rotation, old keys should no longer work
     - update docs with how to use it from Swagger
   - Design choice (students explain tradeoffs):
     - **Easy mode**: rotate keys in-memory (works until the container restarts)
     - **Real mode**: write the new key into **SSM Parameter Store** and restart/reload the API so it takes effect

#### Optional (pick any 2 — SSM-first does NOT count toward the 2)

1. **Monitoring (Qdrant → CloudWatch dashboard)**
   - Send Qdrant metrics to **CloudWatch** and build a dashboard.
   - Make it “vector DB-specific” (not just CPU/RAM): things like collection size / point count growth, search request latency, and vector index behavior (what you graph will depend on what Qdrant exposes).
   - Implementation hint: Qdrant exposes Prometheus-style metrics; students can scrape them and publish to CloudWatch (multiple valid approaches).
   - (Stretch) wire alerts into Slack.

2. **API / Swagger refactor**
   - Add a new endpoint or refactor request/response shapes and update docs.

3. **Data-minded extension**
   - Export `/admin/all-memories` results to a CSV and create a small analysis notebook (top topics, per-user counts, growth over time). Or combine this with one of the other assignments.

4. **SSM-first secrets (bonus / optional, does not count toward the “pick any 2”)**
   - Move any student-provided secrets to SSM created out-of-band (AWS CLI / console), then modify Terraform to read them.

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

Default (Terraform):

```bash
cd infra/terraform
terraform destroy
```

## Cost

Per student: ~$0.10 for 2-hour lab
Class of 30: ~$3.00 total

## Files Students Need

- README.md (overview)
- docs/students/setup.md (deployment steps)
- docs/students/api.md (endpoint reference)
- All code files (src/, deployment/, requirements.txt, .env.template)

## Files YOU Need

- docs/instructors/lab_guide.md (teaching guide)
- docs/instructors/instructor_notes.md (this file)

Good luck!
