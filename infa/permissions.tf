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
  name               = "${var.resource_prefix}${each.key}-task-role"
  description        = "Access resources from ECS runtime containers."
  assume_role_policy = data.aws_iam_policy_document.trust_service_ecs_tasks.json
}

# Enables Lambda to update parameters in running services
# The lambda function can affect all services in a cluster
#   which is why the permissions are pretty open
data "aws_iam_policy_document" "AWSLambdaTrustPolicy" {
  statement {
    actions = ["sts:AssumeRole"]
    effect  = "Allow"
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda_role" {
  name               = "${var.resource_prefix}lambda-ecs-control-role"
  assume_role_policy = data.aws_iam_policy_document.AWSLambdaTrustPolicy.json
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/AmazonECS_FullAccess",
  ]
}

resource "aws_iam_role_policy_attachment" "attach_iam_policy_to_iam_role" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# The below is all for dynamo db usage
resource "aws_iam_policy" "dynamodb" {
  name        = "${var.resource_prefix}task-policy-dynamodb"
  description = "Policy that allows access to DynamoDB"

  policy = <<EOF
{
   "Version": "2012-10-17",
   "Statement": [
       {
           "Effect": "Allow",
           "Action":["dynamodb:*"],
           "Resource": "*"
       }
   ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "ecs-task-role-policy-attachment" {
  for_each   = local.spec_map
  role       = "${var.resource_prefix}${each.key}-task-role"
  policy_arn = aws_iam_policy.dynamodb.arn
}
