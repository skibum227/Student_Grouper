# ECR is set to mutable so that latest image can be used
resource "aws_ecr_repository" "main" {
  name                 = "${var.name}-repository"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

# This will make sure no more than 3 images are saved in the repo 
resource "aws_ecr_lifecycle_policy" "main" {
  repository = aws_ecr_repository.main.name

  policy = jsonencode({
   rules = [{
     rulePriority = 1
     description  = "keep last 10 images"
     action       = {
       type = "expire"
     }
     selection     = {
       tagStatus   = "any"
       countType   = "imageCountMoreThan"
       countNumber = 3
     }
   }]
  })
}

# S3 bucket - not needed yet
# resource "aws_s3_bucket" "job_artifacts" {
#   bucket        = "${local.res_prefix}-test-bucket"
#   acl           = "private"
#   force_destroy = true
# }
