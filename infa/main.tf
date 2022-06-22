# Main Configuration
# Need to pass in env vars: AWS_PROFILE=personal
# Resources:
#   https://engineering.finleap.com/posts/2020-02-20-ecs-fargate-terraform/
#   https://github.com/finleap/tf-ecs-fargate-tmpl

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

locals {
  region          = "us-east-1"
  container_port     = 5000
  container_image = "301599272037.dkr.ecr.us-east-1.amazonaws.com/student-grouper-repository:v0.0.2"
  # computed
  # mlflow_dns          = "${aws_service_discovery_service.exposed_service["mlflow_server-tracking-v1"].name}.${aws_service_discovery_private_dns_namespace.exposed_service["mlflow_server-tracking-v1"].name}"
  # mlflow_artifact_uri = "s3://${aws_s3_bucket.job_artifacts.bucket}/mlflow_server/v1" # must follow convention defined in `permissions.tf`: `bucket/name/version`
  # mlflow_db_uri       = "mysql+pymysql://${aws_rds_cluster.backend_store.master_username}:${aws_rds_cluster.backend_store.master_password}@${aws_rds_cluster.backend_store.endpoint}:${aws_rds_cluster.backend_store.port}/${aws_rds_cluster.backend_store.database_name}"
}

locals {
  exposed_specs = [
    {
      name              = "mlflow_server"
      version           = "v1"
      job_type          = "tracking"
      cpu               = 1
      memory            = 2
      #command           = "--static-prefix /mlflow --host=0.0.0.0 --port=${local.mlflow_port} --default-artifact-root=${local.mlflow_artifact_uri} --backend-store-uri=${local.mlflow_db_uri}\""
      container_port    = local.mlflow_port
      health_check_path = "/mlflow/#/"
      path_patterns     = ["/mlflow/*"]
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
  spec_map = merge(local.spec_map_batch, local.spec_map_exposed)
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

resource "aws_db_subnet_group" "rds" {
  name       = "${var.resource_prefix}-rds"
  subnet_ids = aws_subnet.rds.*.id
}

data "aws_availability_zones" "available" {
  state = "available"
}

resource "aws_subnet" "rds" {
  count             = 2
  cidr_block        = cidrsubnet(module.vpc.vpc_cidr_block, 4, (5 + count.index))
  vpc_id            = module.vpc.vpc_id
  availability_zone = data.aws_availability_zones.available.names[count.index]
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
      cidr_blocks = "23.23.65.159/32"
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






