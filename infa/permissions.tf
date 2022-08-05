# Runtime Role (Assumed by ECS instances)
# Needs ability to read/write to s3 bucket.
data "aws_iam_policy_document" "trust_service_ecs_tasks" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "task_resource_access" {
  for_each           = local.spec_map
  name               = "${var.resource_prefix}-${each.key}-task-role"
  description        = "Access resources from ECS runtime containers."
  assume_role_policy = data.aws_iam_policy_document.trust_service_ecs_tasks.json
}
