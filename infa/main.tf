# Main Configuration
# Need to pass in env vars: AWS_PROFILE=personal
# Resources:
#   https://engineering.finleap.com/posts/2020-02-20-ecs-fargate-terraform/
#   https://github.com/finleap/tf-ecs-fargate-tmpl

# Terraform State
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "3.75.1"
    }
  }

  backend "s3" {
    bucket = "skibum-terraform-state"
    key    = "state/terraform_state.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region     = local.region
  profile    = "personal"
}

# General Locals
locals {
  region          = "us-east-1"
  container_port  = 5000
  #container_image = "301599272037.dkr.ecr.us-east-1.amazonaws.com/student-grouper-repository:v0.0.2"
}

# Specific locals
locals {
  exposed_specs = [
    {
      name              = "student_grouper"
      version           = "v2"
      job_type          = "ui"
      cpu               = 0.25
      memory            = 0.5
      #command          = 'there is no override command' 
      container_port    = local.container_port
      health_check_path = "/student_grouper/#/"
      path_patterns     = ["/student_grouper/*"]
    }
  ]
}

# Converting the job specs into a map is useful because of its compatibility
# with `for_each`. It also gives us a convenient mechanism for looking up job
# specific policies.
locals {
  spec_map_exposed = {
    for instance in local.exposed_specs :
    "${instance.name}-${instance.job_type}-${instance.version}" => instance
  }
  #spec_map = merge(local.spec_map_batch, local.spec_map_exposed)
  spec_map = local.spec_map_exposed
}

locals {
  # We prefer to use maps to handle the specs for the ECS jobs. However, the `alb` module
  # interface requires us to define and reference target groups based on a positional index.
  # This mapping simply declares that association.
  target_group_index_map = zipmap(keys(local.spec_map_exposed), range(length(local.spec_map_exposed)))
}


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
  image_tag            = each.value.version
  cpu                  = each.value.cpu
  memory               = each.value.memory

  # POC
  # command        = each.value.command
  container_port = each.value.container_port
}

resource "aws_ecr_repository" "jobs" {
  for_each = local.spec_map

  name                 = "${var.resource_prefix}-${each.value.name}-${each.value.job_type}"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_cloudwatch_log_group" "jobs" {
  name = "${var.resource_prefix}-jobs-log-group"
}


resource "aws_ecs_cluster" "jobs" {
  name = "${var.resource_prefix}-jobs-cluster"
}


data "aws_availability_zones" "available" {
  state = "available"
}


module "lb_ecs_service_web_access_sg" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "3.18.0"

  name        = "${var.resource_prefix}-ecs-service-web-access-sg"
  description = "Allow web access to the ECS services"
  vpc_id      = module.vpc.vpc_id

  egress_cidr_blocks = ["0.0.0.0/0"]
  egress_rules       = ["all-all"]

  ingress_with_cidr_blocks = [
    {
      from_port = 80
      to_port   = 80
      protocol  = "tcp"
      # Allows traffic through the vpn
      #cidr_blocks = "23.23.65.159/32"
      cidr_blocks = "0.0.0.0/0"
    }
  ]
}

#  Security Group for internal ip
module "ecs_service_sg" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "3.18.0"

  name        = "${var.resource_prefix}-ecs_service_sg"
  description = "Allow access to ECS services."
  vpc_id      = module.vpc.vpc_id

  ingress_cidr_blocks = ["0.0.0.0/0"]
  ingress_rules       = ["all-all"]

  egress_cidr_blocks = ["0.0.0.0/0"]
  egress_rules       = ["all-all"]
}






