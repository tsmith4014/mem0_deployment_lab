locals {
  tags = {
    Project = var.project_name
    Owner   = var.owner
  }

  # Providers for the app (passed into .env)
  llm_provider      = var.ai_mode == "aws" ? "aws_bedrock" : "openai"
  embedder_provider = var.ai_mode == "aws" ? "aws_bedrock" : "openai"

  # Keys (auto-generate if blank) - each key is independently generated
  effective_api_key       = var.api_key != "" ? var.api_key : random_password.api_key.result
  effective_admin_api_key = var.admin_api_key != "" ? var.admin_api_key : random_password.admin_api_key.result

  # SSM parameter prefix
  ssm_prefix = "/${var.project_name}"
}

resource "aws_key_pair" "my_key" {
  key_name   = "kh_try2"
  public_key = file("~/.ssh/kh_try2.pub")
}


data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

data "aws_ami" "al2023" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}



resource "random_password" "api_key" {
  length  = 32
  special = false
}

resource "random_password" "admin_api_key" {
  length  = 32
  special = false
}

resource "aws_security_group" "mem0" {
  name        = "${var.project_name}-sg"
  description = "Mem0 deployment lab security group"
  vpc_id      = data.aws_vpc.default.id
  tags        = local.tags
}

resource "aws_security_group_rule" "egress_all" {
  type              = "egress"
  security_group_id = aws_security_group.mem0.id
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"]
}

resource "aws_security_group_rule" "ingress_api" {
  type              = "ingress"
  security_group_id = aws_security_group.mem0.id
  from_port         = var.api_port
  to_port           = var.api_port
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  description       = "FastAPI API/Swagger"
}

resource "aws_security_group_rule" "ingress_ssh" {
  count             = var.ssh_key_name != "" ? 1 : 0
  type              = "ingress"
  security_group_id = aws_security_group.mem0.id
  from_port         = 22
  to_port           = 22
  protocol          = "tcp"
  cidr_blocks       = [var.allowed_ssh_cidr]
  description       = "SSH (optional)"
}

resource "aws_security_group_rule" "ingress_qdrant" {
  count             = var.expose_qdrant_public ? 1 : 0
  type              = "ingress"
  security_group_id = aws_security_group.mem0.id
  from_port         = var.qdrant_http_port
  to_port           = var.qdrant_http_port
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  description       = "Qdrant HTTP (optional)"
}

resource "aws_iam_role" "ec2" {
  name               = "${var.project_name}-ec2-role"
  assume_role_policy = data.aws_iam_policy_document.ec2_assume.json
  tags               = local.tags
}

data "aws_iam_policy_document" "ec2_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "ssm_read_params" {
  statement {
    actions = [
      "ssm:GetParameter",
      "ssm:GetParameters",
    ]
    resources = concat(
      [
        aws_ssm_parameter.api_key.arn,
        aws_ssm_parameter.admin_api_key.arn,
      ],
      var.ai_mode == "openai" ? [aws_ssm_parameter.openai_api_key[0].arn] : []
    )
  }

  # Allow writing to API key parameters for key rotation
  statement {
    actions = [
      "ssm:PutParameter",
    ]
    resources = [
      aws_ssm_parameter.api_key.arn,
      aws_ssm_parameter.admin_api_key.arn,
    ]
  }

  # Needed to decrypt/encrypt SecureString parameters (lab-friendly, broad)
  statement {
    actions   = ["kms:Decrypt", "kms:Encrypt", "kms:GenerateDataKey"]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "ssm_read_params" {
  name   = "${var.project_name}-ssm-read"
  policy = data.aws_iam_policy_document.ssm_read_params.json
  tags   = local.tags
}

resource "aws_iam_role_policy_attachment" "ssm_read_attach" {
  role       = aws_iam_role.ec2.name
  policy_arn = aws_iam_policy.ssm_read_params.arn
}

# Optional: Bedrock permissions for AWS-only track
data "aws_iam_policy_document" "bedrock_invoke" {
  statement {
    actions = [
      "bedrock:ListFoundationModels",
      "bedrock:InvokeModel",
      "bedrock:InvokeModelWithResponseStream",
    ]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "bedrock_invoke" {
  count  = var.ai_mode == "aws" ? 1 : 0
  name   = "${var.project_name}-bedrock"
  policy = data.aws_iam_policy_document.bedrock_invoke.json
  tags   = local.tags
}

resource "aws_iam_role_policy_attachment" "bedrock_attach" {
  count      = var.ai_mode == "aws" ? 1 : 0
  role       = aws_iam_role.ec2.name
  policy_arn = aws_iam_policy.bedrock_invoke[0].arn
}

resource "aws_iam_instance_profile" "ec2" {
  name = "${var.project_name}-instance-profile"
  role = aws_iam_role.ec2.name
  tags = local.tags
}

# SSM params used to build .env on the instance.
# NOTE: These may still appear in Terraform state; do not commit tfstate.
resource "aws_ssm_parameter" "api_key" {
  name  = "${local.ssm_prefix}/API_KEY"
  type  = "SecureString"
  value = local.effective_api_key
  tags  = local.tags
}

resource "aws_ssm_parameter" "admin_api_key" {
  name  = "${local.ssm_prefix}/ADMIN_API_KEY"
  type  = "SecureString"
  value = local.effective_admin_api_key
  tags  = local.tags
}

resource "aws_ssm_parameter" "openai_api_key" {
  count = var.ai_mode == "openai" ? 1 : 0
  name  = "${local.ssm_prefix}/OPENAI_API_KEY"
  type  = "SecureString"
  value = var.openai_api_key
  tags  = local.tags
}

resource "aws_instance" "mem0" {
  ami                         = data.aws_ami.al2023.id
  instance_type               = var.instance_type
  subnet_id                   = element(data.aws_subnets.default.ids, 0)
  vpc_security_group_ids      = [aws_security_group.mem0.id]
  iam_instance_profile        = aws_iam_instance_profile.ec2.name
  associate_public_ip_address = true

  key_name = aws_key_pair.my_key.key_name

  root_block_device {
    volume_size = var.root_volume_size_gb
    volume_type = "gp3"
  }

  user_data = templatefile("${path.module}/user_data.sh.tftpl", {
    project_name          = var.project_name
    repo_url              = var.repo_url
    repo_ref              = var.repo_ref
    api_port              = var.api_port
    api_host              = var.api_host
    ssm_prefix            = local.ssm_prefix
    llm_provider          = local.llm_provider
    embedder_provider     = local.embedder_provider
    aws_region_runtime    = var.aws_region_runtime
    openai_base_url       = var.openai_base_url
    llm_model             = var.llm_model
    llm_temperature       = var.llm_temperature
    embedder_model        = var.embedder_model
    docker_network_name   = var.docker_network_name
    api_container_name    = var.api_container_name
    api_image_name        = var.api_image_name
    qdrant_container_name = var.qdrant_container_name
    qdrant_image          = var.qdrant_image
    qdrant_volume_name    = var.qdrant_volume_name
    qdrant_http_port      = var.qdrant_http_port
    qdrant_grpc_port      = var.qdrant_grpc_port
  })

  tags = merge(local.tags, {
    Name = "${var.project_name}-ec2"
  })
}


