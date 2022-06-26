resource "aws_ecr_repository" "jobs" {
  for_each = local.spec_map

  name                 = "${var.resource_prefix}-${each.value.name}-${each.value.job_type}"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}
