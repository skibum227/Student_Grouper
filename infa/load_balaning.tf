# Service to do the following
# - Creates tasks
# - Makes sure one task is always running
# - Create connection and work with ALB
resource "aws_ecs_service" "exposed_service" {
  for_each         = local.spec_map_exposed
  name             = "${var.resource_prefix}-${each.key}"
  cluster          = aws_ecs_cluster.jobs.id
  task_definition  = module.jobs[each.key].task_arn
  desired_count    = 1
  launch_type      = "FARGATE"
  platform_version = "1.4.0"

  network_configuration {
    subnets         = module.vpc.private_subnets
    security_groups = [module.ecs_service_sg.this_security_group_id]
  }

  load_balancer {
    target_group_arn = module.alb.target_group_arns[local.target_group_index_map[each.key]]
    container_name   = module.jobs[each.key].container_name
    container_port   = local.container_port
  }

  service_registries {
    registry_arn = aws_service_discovery_service.exposed_service[each.key].arn
  }

  lifecycle {
    ignore_changes = [desired_count]
  }

  depends_on = [
    # if we don't have this terraform apply can fail when TF attempts to create the service before the ALB
    module.alb
  ]
}

resource "aws_service_discovery_private_dns_namespace" "exposed_service" {
  for_each    = local.spec_map_exposed
  name        = "${var.resource_prefix}-${each.key}"
  description = "Private DNS"
  vpc         = module.vpc.vpc_id
}

resource "aws_service_discovery_service" "exposed_service" {
  for_each = local.spec_map_exposed
  name     = "${var.resource_prefix}-${each.key}"

  dns_config {
    namespace_id = aws_service_discovery_private_dns_namespace.exposed_service[each.key].id

    dns_records {
      ttl  = 10
      type = "A"
    }
  }
}

# Lood balancer module that facilitates all connections and secuity
module "alb" {
  source  = "terraform-aws-modules/alb/aws"
  version = "~> 6.0"

  name = "${var.resource_prefix}-ecs-alb"

  load_balancer_type = "application"

  vpc_id          = module.vpc.vpc_id
  subnets         = module.vpc.public_subnets
  security_groups = [module.lb_ecs_service_web_access_sg.this_security_group_id]

  access_logs = {
  }

  # Boundries in DNS space 
  http_tcp_listeners = [
    {
      port     = 80
      protocol = "HTTP"

      action_type = "fixed-response"
      fixed_response = {
        content_type = "text/plain"
        message_body = "Not found!"
        status_code  = "404"
      }
    }
  ]

  # The action that should be taken for every target
  http_tcp_listener_rules = [
    for key, instance in local.spec_map_exposed :
    {
      http_tcp_listener_index = 0

      actions = [{
        type               = "forward"
        target_group_index = local.target_group_index_map[key]
      }]

      conditions = [{
        path_patterns = instance.path_patterns
      }]
    }
  ]

  # Health check path - if this fails, entire website will not load
  target_groups = [
    for key, instance in local.spec_map_exposed :
    {
      backend_protocol = "HTTP"
      backend_port     = instance.container_port
      target_type      = "ip"
      argets           = []
      health_check = {
        path = instance.health_check_path
        port = instance.container_port
      }
    }
  ]
  tags = {}
}