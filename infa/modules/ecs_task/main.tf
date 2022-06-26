# A module for creating ECS tasks
# - ECS tasks are the main work-horse so this module makes it easy to 
# -   add as many as are required, within the same network

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "3.75.1"
    }
  }
}

locals {
  container_name  = var.task_name
  log_stream_name = var.task_name
  task_name       = "${aws_ecs_task_definition.this.family}-${aws_ecs_task_definition.this.revision}"
}

resource "aws_ecs_task_definition" "this" {
  family = "${var.resource_prefix}-${var.task_name}-task-definition"

  requires_compatibilities = ["FARGATE"]

  # this is the role used by the container
  task_role_arn = var.task_role_arn

  # this is the role used by ECS to appropriate resources
  execution_role_arn = aws_iam_role.ecs_orchestration.arn

  # note that `network_mode`, `cpu` and `memory` are *required* for fargate usage.
  network_mode = "awsvpc"
  # https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-cpu-memory-error.html
  cpu    = tostring(var.cpu * 1024)
  memory = tostring(var.memory * 1024)

  container_definitions = jsonencode([
    {
      name      = local.container_name
      image     = "${var.image_repository_url}:${var.image_tag}"
      essential = true
      logConfiguration = {
        logDriver = "awslogs",
        options = {
          awslogs-group         = var.log_group_name,
          awslogs-region        = var.region,
          awslogs-stream-prefix = local.log_stream_name
        }
      }
      # https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_PortMapping.html
      portMappings = var.container_port != null ? [{ containerPort = var.container_port }] : []
      # Injects the override command if one exists
      command      = var.command != null ? [var.command] : []
    }
  ])
}
