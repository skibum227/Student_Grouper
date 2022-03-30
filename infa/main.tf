# Main Configuration
# Need to pass in env vars: AWS_PROFILE=personal
# Resources:
#   https://engineering.finleap.com/posts/2020-02-20-ecs-fargate-terraform/
#   https://github.com/finleap/tf-ecs-fargate-tmpl

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "2.70.0"
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
  region = "us-east-1" 
  container_image = "301599272037.dkr.ecr.us-east-1.amazonaws.com/student-grouper-repository:v0.0.2"
  # The number of cpu units used by the task
  cpu = 256
  # The amount (in MiB) of memory used by the task
  memory = 512
}
