output "container_name" {
  value       = local.container_name
  description = "The container name in the task definition. Can be used to set container overrides."
}

output "log_stream_name" {
  value       = local.log_stream_name
  description = "The name of the log stream belonging to the task."
}

output "execution_role_arn" {
  value       = aws_iam_role.ecs_orchestration.arn
  description = "The execution role ARN."
}

output "task_name" {
  value       = local.task_name
  description = "The task name: '<task family>:<task revision>'"
}

output "task_arn" {
  value       = aws_ecs_task_definition.this.arn
  description = "The task ARN."
}

output "task_family" {
  value       = aws_ecs_task_definition.this.family
  description = "The task family."
}

output "task_revision" {
  value       = aws_ecs_task_definition.this.revision
  description = "The task revision."
}

output "task_role_arn" {
  value       = var.task_role_arn
  description = "The ARN of the Role used by the running container. User input."
}