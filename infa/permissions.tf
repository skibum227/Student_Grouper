resource "aws_iam_role" "ecs_task_execution_role" {
  name = "${var.name}-ecsTaskExecutionRole"
 
  assume_role_policy = <<EOF
{
 "Version": "2012-10-17",
 "Statement": [
   {
     "Action": "sts:AssumeRole",
     "Principal": {
       "Service": "ecs-tasks.amazonaws.com"
     },
     "Effect": "Allow",
     "Sid": ""
   }
 ]
}
EOF
}
 
resource "aws_iam_role_policy_attachment" "ecs-task-execution-role-policy-attachment" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

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
resource "aws_iam_role" "ecs_task_role" {
  name = "${var.name}-ecsTaskRole"
  description = "trying something"
  assume_role_policy = data.aws_iam_policy_document.trust_service_ecs_tasks.json 
  managed_policy_arns = [aws_iam_policy.ecr_power_user.arn]
}

resource "aws_iam_policy" "ecr_power_user" {
  name        = "${var.name}-ecr-power-user"
  path        = "/"
  description = "Allow read and write to ECR, but not ability to delete repositories or change policy documents."
  policy      = data.aws_iam_policy_document.ecr_power_user.json
}

data "aws_iam_policy_document" "ecr_power_user" {
  statement {
    effect = "Allow"
    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:GetDownloadUrlForLayer",
      "ecr:GetRepositoryPolicy",
      "ecr:DescribeRepositories",
      "ecr:ListImages",
      "ecr:DescribeImages",
      "ecr:BatchGetImage",
      "ecr:GetLifecyclePolicy",
      "ecr:GetLifecyclePolicyPreview",
      "ecr:ListTagsForResource",
      "ecr:DescribeImageScanFindings",
      "ecr:InitiateLayerUpload",
      "ecr:UploadLayerPart",
      "ecr:CompleteLayerUpload",
      "ecr:PutImage"
    ]
    resources = [aws_ecr_repository.main.arn]
  }

  statement {
    effect = "Allow"
    actions = [
      "ecr:GetAuthorizationToken"
    ]
    # need to authenticate at the registry, not repository, level
    # https://docs.aws.amazon.com/AmazonECR/latest/userguide/security_iam_id-based-policy-examples.html#security_iam_id-based-policy-examples-access-one-bucket
    resources = ["*"]
  }
}

