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

# note: these are not currently set in `live`
# this allows usd to communicate with the AWS services from ECS soley through
# private traffic.
module "endpoints" {
  source             = "terraform-aws-modules/vpc/aws//modules/vpc-endpoints"
  vpc_id             = module.vpc.vpc_id
  security_group_ids = [module.endpoint_sg.this_security_group_id]
  version            = "3.7.0"

  endpoints = {
    ecr_api = {
      service             = "ecr.api"
      private_dns_enabled = true
      subnet_ids          = module.vpc.private_subnets
      tags = {
        Name = "${var.resource_prefix}-ecr-api-vpc-endpoint"
      }

    },
    ecr_dkr = {
      service             = "ecr.dkr"
      private_dns_enabled = true
      subnet_ids          = module.vpc.private_subnets
      tags = {
        Name = "${var.resource_prefix}-ecr-dkr-vpc-endpoint"
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
    ecs_agent = {
      service             = "ecs-agent"
      private_dns_enabled = true
      subnet_ids          = module.vpc.private_subnets
      tags = {
        Name = "${var.resource_prefix}-ecs-agent-vpc-endpoint"
      }

    },
    ecs_telemetry = {
      service             = "ecs-telemetry"
      private_dns_enabled = true
      subnet_ids          = module.vpc.private_subnets
      tags = {
        Name = "${var.resource_prefix}-ecs-telemetry-vpc-endpoint"
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

module "endpoint_sg" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "3.18.0"

  name        = "${var.resource_prefix}-analytics-db-access-sg"
  description = "Allow access to VPC security groups"
  vpc_id      = module.vpc.vpc_id

  egress_cidr_blocks = ["0.0.0.0/0"]
  egress_rules       = ["all-all"]

  ingress_cidr_blocks = module.vpc.private_subnets_cidr_blocks
  ingress_rules = ["https-443-tcp"]
}
