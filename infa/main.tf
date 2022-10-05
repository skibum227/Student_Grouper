# Main Configuration
# Need to pass in env vars: AWS_PROFILE=personal

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
  region  = local.region
  profile = "personal"
}

# General Locals
locals {
  region         = "us-east-1"
  container_port = 5050
  enable_scheduling = false
  start_time =  "cron(30 11 ? * Mon-Fri *)"
  stop_time  =  "cron(0 19 ? * Mon-Fri *)"
}

# Definition for each task to be ran by ECS Fargate
locals {
  exposed_specs = [
    {
      name              = "student-grouper"
      job_type          = "application"
      image_version     = "v3"
      cpu               = 0.25
      memory            = 0.5
      container_port    = local.container_port
      health_check_path = "/healthcheck"
      path_patterns     = ["/*"]
      # command           = 'an override command'
    }
  ]
}

# Create an object for all tasks defined above
#  - Converting the job specs into a map is useful because of its compatibility
#  -  with `for_each`. It also gives us a convenient mechanism for looking up job
#  -  specific policies.
locals {
  spec_map_exposed = {
    for instance in local.exposed_specs :
    "${instance.name}-${instance.job_type}-${instance.image_version}" => instance
  }
  #spec_map = merge(local.spec_map_batch, local.spec_map_exposed)
  spec_map = local.spec_map_exposed
}

# Target group object due to the spcific requireemnts of the AWS ALB module 
# - We prefer to use maps to handle the specs for the ECS jobs. However, the `alb` module
# -  interface requires us to define and reference target groups based on a positional index.
# -  This mapping simply declares that association.
locals {
  target_group_index_map = zipmap(keys(local.spec_map_exposed), range(length(local.spec_map_exposed)))
}
