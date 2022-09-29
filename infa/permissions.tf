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

# Normal Lambda policy
resource "aws_iam_policy" "iam_policy_for_lambda" {
  name         = "aws_iam_policy_for_terraform_aws_lambda_role"
  path         = "/"
  description  = "AWS IAM Policy for managing aws lambda role"
  policy = <<EOF
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "logs:CreateLogGroup",
                "Resource": "arn:aws:logs:us-east-1:301599272037:*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Resource": [
                    "arn:aws:logs:us-east-1:301599272037:log-group:/aws/lambda/start_fcn:*"
                ]
            }
        ]
    }
    EOF
}

# Lambda Role with policy to update ecs services
resource "aws_iam_role" "lambda_role" {
  name               = "${var.resource_prefix}lambda-${var.task_name}-role"
  description        = "Enable lambda to mess with ecs tasks"
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/AmazonECS_FullAccess",
  ]
}

# Attach the normal policy as well
resource "aws_iam_role_policy_attachment" "attach_iam_policy_to_iam_role" {
  role        = aws_iam_role.lambda_role.name
  policy_arn  = aws_iam_policy.iam_policy_for_lambda.arn
}


