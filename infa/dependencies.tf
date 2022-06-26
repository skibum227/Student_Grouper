# Fresh VPS for App
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "2.77.0"

  name            = "${var.resource_prefix}-vpc"
  cidr            = "10.0.0.0/16"
  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  public_subnets  = ["10.0.0.0/27", "10.0.2.0/27"]
  private_subnets = ["10.0.1.0/24"]

  # Required for private EKS API access
  enable_dns_hostnames = true

  enable_nat_gateway = true

}

# Endpoints to allow communicating with the AWS services from ECS soley through private traffic
# Note: This is currently not used
module "endpoints" {
  source             = "terraform-aws-modules/vpc/aws//modules/vpc-endpoints"
  vpc_id             = module.vpc.vpc_id
  security_group_ids = [module.endpoint_sg.this_security_group_id]
  version            = "3.7.0"

  endpoints = {
    ecr = {
      service             = "ecr"
      private_dns_enabled = true
      subnet_ids          = module.vpc.private_subnets
      tags = {
        Name = "${var.resource_prefix}-ecr-api-vpc-endpoint"
      }
    },
    s3 = {
      service         = "s3"
      service_type    = "Gateway"
      route_table_ids = module.vpc.private_route_table_ids
      tags = {
        Name = "${var.resource_prefix}-s3-vpc-endpoint"
      }
    },
    ecs = {
      service             = "ecs"
      private_dns_enabled = true
      subnet_ids          = module.vpc.private_subnets
      tags = {
        Name = "${var.resource_prefix}-ecs-vpc-endpoint"
      }
    },
    logs = {
      service             = "logs"
      private_dns_enabled = true
      subnet_ids          = module.vpc.private_subnets
      tags = {
        Name = "${var.resource_prefix}-logs-vpc-endpoint"
      }
    }
  }
}
