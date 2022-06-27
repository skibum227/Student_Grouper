# ECS Permissions
# Policies/roles required by the ECS cluster and its instances.

# Enables the ability to handle pulling ecr images and running ecs tasks
data "aws_iam_policy_document" "trust_service_ecs_tasks" {
  statement {
    actions = ["sts:AssumeRole"]

    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

# The iam role that is capable of pulling the image and running the ecs task
resource "aws_iam_role" "ecs_orchestration" {
  name               = "${var.resource_prefix}-ecs-instance-${var.task_name}-role"
  description        = "ECS task orchestrator - Manage Ec2 resources and adjacent resources (such as logging)."
  assume_role_policy = data.aws_iam_policy_document.trust_service_ecs_tasks.json
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role",
    aws_iam_policy.logging_read_write_access.arn
  ]
}

# This is the role for the ECS instance, to which the iam role will be attached
# - https://medium.com/devops-dudes/the-difference-between-an-aws-role-and-an-instance-profile-ae81abd700d
# - This is why Terraform/AWS Cloud is confusing...
resource "aws_iam_instance_profile" "ecs_orchestration" {
  name = "${var.resource_prefix}-ecs-profile-${var.task_name}-profile"
  role = aws_iam_role.ecs_orchestration.name
}

# Creates the policy from the policy document so it can be attached
resource "aws_iam_policy" "logging_read_write_access" {
  name        = "${var.resource_prefix}-manage-logging-${var.task_name}-policy"
  path        = "/"
  description = "Read/Write logs on the stream ${local.log_stream_name}."
  policy      = data.aws_iam_policy_document.logging_read_write_access.json
}

# Enables the ability to write logs to a cloudwatch log group
data "aws_iam_policy_document" "logging_read_write_access" {
  statement {
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:DescribeLogStreams"
    ]

    effect = "Allow"

    resources = ["${var.log_group_arn}:log-stream:${local.log_stream_name}"]
  }
}