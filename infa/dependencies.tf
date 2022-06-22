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

# resource "aws_vpc" "main" {
#   cidr_block = var.cidr
# }

# data "aws_availability_zones" "available" {
#   state = "available"
# } 

# resource "aws_internet_gateway" "main" {
#   vpc_id = aws_vpc.main.id
# }

# resource "aws_subnet" "private" {
#   vpc_id            = aws_vpc.main.id
#   cidr_block        = element(var.private_subnets, count.index)
#   availability_zone = data.aws_availability_zones.available.names[count.index]
#   count             = length(var.private_subnets)
# }

# resource "aws_subnet" "public" {
#   vpc_id                  = aws_vpc.main.id
#   cidr_block              = element(var.public_subnets, count.index)
#   availability_zone       = data.aws_availability_zones.available.names[count.index]
#   count                   = length(var.public_subnets)
#   map_public_ip_on_launch = true
# }

# resource "aws_route_table" "public" {
#   vpc_id = aws_vpc.main.id
# }

# resource "aws_route" "public" {
#   route_table_id         = aws_route_table.public.id
#   destination_cidr_block = "0.0.0.0/0"
#   gateway_id             = aws_internet_gateway.main.id
# }

# resource "aws_route_table_association" "public" {
#   count          = length(var.public_subnets)
#   subnet_id      = element(aws_subnet.public.*.id, count.index)
#   route_table_id = aws_route_table.public.id
# }
