# Security group for the enpoints - only allows incoming from private network
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
      # Can set specific IPs here  
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