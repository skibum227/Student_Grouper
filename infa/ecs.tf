# Makes all resources availible for the ecs service
resource "aws_ecs_cluster" "jobs" {
  name = "${var.resource_prefix}jobs-cluster"
}

# Module for cleanly setting up ecs tasks
module "jobs" {
  source = "./modules/ecs_task"

  for_each = local.spec_map

  resource_prefix = var.resource_prefix
  region          = local.region

  # TODO: name task_id
  task_name = each.key

  log_group_arn  = aws_cloudwatch_log_group.jobs.arn
  log_group_name = aws_cloudwatch_log_group.jobs.name

  task_role_arn        = aws_iam_role.task_resource_access[each.key].arn
  image_repository_url = aws_ecr_repository.jobs[each.key].repository_url
  image_tag            = each.value.image_version
  cpu                  = each.value.cpu
  memory               = each.value.memory

  container_port = each.value.container_port
}
