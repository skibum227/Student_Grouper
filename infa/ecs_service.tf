resource "aws_ecs_cluster" "main" {
  name = "${var.name}-cluster-${var.environment}"
}

resource "aws_ecs_task_definition" "main" {
  family                   = "service"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = local.cpu
  memory                   = local.memory
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn
  container_definitions = jsonencode([
    {
       name        = "${var.name}-container-${var.environment}"
       image       = local.container_image
       essential   = true
       environment = [{"name":"${var.environment}"}]
       portMappings = [
        {
         protocol      = "tcp"
         containerPort = var.container_port
         hostPort      = var.container_port
        }
       ]
       logConfiguration = {
          logDriver = "awslogs"
          options = {
            awslogs-group = "${var.name}.cloudwatch_group"
            awslogs-region = "us-east-1"
            awslogs-stream-prefix = "ecs"
          }
        }
    }
  ])
}

resource "aws_ecs_service" "main" {
 name                               = "${var.name}-service-${var.environment}"
 cluster                            = aws_ecs_cluster.main.id
 task_definition                    = aws_ecs_task_definition.main.arn
 desired_count                      = 1
 deployment_minimum_healthy_percent = 50
 deployment_maximum_percent         = 200
 launch_type                        = "FARGATE"
 scheduling_strategy                = "REPLICA"
 depends_on                         = [aws_lb.main]
 
 network_configuration {
   security_groups  = [aws_security_group.ecs_tasks.id]
   subnets          = aws_subnet.private.*.id
   assign_public_ip = false
 }
 
 load_balancer {
   target_group_arn = aws_alb_target_group.main.arn
   container_name   = "${var.name}-container-${var.environment}"
   container_port   = var.container_port
 }
 
 lifecycle {
   ignore_changes = [task_definition]
 }
}
