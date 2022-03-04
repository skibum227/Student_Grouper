# Main Configuration
# Need to pass in env vars: AWS_PROFILE=personal

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
  region  = local.region
  profile = "personal"
}

locals {
  region = "us-east-1"
}
