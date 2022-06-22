# Runtime Role (Assumed by ECS instances)
# Needs ability to read/write to DS s3 bucket and retrieve the DB secret value.
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
  description        = "Access DS resources from ECS runtime containers."
  assume_role_policy = data.aws_iam_policy_document.trust_service_ecs_tasks.json
  managed_policy_arns = [
    aws_iam_policy.s3_task_artifact_access_read_write[each.key].arn
  ]
}

# Policies
# resource "aws_iam_policy" "s3_task_artifact_access_read_write" {
#   for_each = local.spec_map

#   name        = "${var.resource_prefix}-${each.key}-artifacts-read-write-policy"
#   description = "Read/Write permissions to objects with the prefix ${aws_s3_bucket.job_artifacts.bucket}/${each.value.name}/${each.value.version}/"
#   path        = "/"
#   policy      = data.aws_iam_policy_document.s3_task_artifact_access_read_write[each.key].json
# }

# data "aws_iam_policy_document" "s3_task_artifact_access_read_write" {
#   for_each = local.spec_map
#   # https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_examples_s3_rw-bucket.html
#   statement {
#     effect = "Allow"
#     actions = [
#       "s3:GetObject",
#       "s3:DeleteObject",
#       "s3:PutObject"
#     ]
#     resources = [
#       "${aws_s3_bucket.job_artifacts.arn}/${each.value.name}/${each.value.version}/*"
#     ]
#   }

#   statement {
#     effect = "Allow"
#     actions = [
#       "s3:ListBucket",
#     ]
#     resources = [
#       aws_s3_bucket.job_artifacts.arn
#     ]
#   }
# }