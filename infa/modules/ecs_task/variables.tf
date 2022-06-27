# These variables are what is required when the module is defined

variable "resource_prefix" {
  type        = string
  description = "Used as a prefix for all resources in a module."
}

variable "task_name" {
  type        = string
  description = "A name used to identify resources belonging to the task."
}

variable "task_role_arn" {
  type        = string
  description = "The ARN of the Role used by the running container."
}

variable "log_group_arn" {
  type        = string
  description = "The ARN of the AWS log group."
}

variable "log_group_name" {
  type        = string
  description = "The name of the AWS log group."
}

variable "cpu" {
  type        = string
  description = "The number of CPUs required to run the task. Specified as the integer or fractional value desired. Must satisfy Fargate constraints."
}

variable "memory" {
  type        = string
  description = "The memory in GBs required to run the task. Specified as the integer or fractional value desired. Must satisfy Fargate constraints."
}

variable "image_tag" {
  type        = string
  description = "The image repository tag."
}

variable "image_repository_url" {
  type        = string
  description = "URL of the ECR repo"
}

variable "region" {
  type        = string
  description = "The AWS region."
}

variable "command" {
  type        = string
  description = "Command to run when container is built"
  default     = null
}

variable "container_port" {
  type        = number
  description = "Port inside container to expose. Optional."
  default     = null
}