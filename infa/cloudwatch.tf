# Resource docs...
#   https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_rule

# These Eventbridge rules control bringing up and shutting down all running services
#   and tasks during certain hours to save money
resource "aws_cloudwatch_event_rule" "lambda_start" {
  name                = "${var.resource_prefix}lambda-start-trigger"
  description         = "Sends payload to lambda to start the ecs cluster"
  is_enabled          = local.enable_scheduling
  schedule_expression = local.start_time 
}

resource "aws_cloudwatch_event_rule" "lambda_stop" {
  name                = "${var.resource_prefix}lambda-stop-trigger"
  description         = "Sends payload to lambda to stop the ecs cluster"
  is_enabled          = local.enable_scheduling
  schedule_expression = local.stop_time
}

resource "aws_cloudwatch_event_target" "lambda_start" {
  rule      = aws_cloudwatch_event_rule.lambda_start.id
  target_id = "send_start_msg"
  arn       = aws_lambda_function.lambda_ecs_control.arn
  input     = "{\"status\":\"start\", \"cluster\":\"${aws_ecs_cluster.jobs.name}\"}"
}

resource "aws_cloudwatch_event_target" "lambda_stop" {
  rule      = aws_cloudwatch_event_rule.lambda_stop.id
  target_id = "send_stop_msg"
  arn       = aws_lambda_function.lambda_ecs_control.arn
  input     = "{\"status\":\"stop\", \"cluster\":\"${aws_ecs_cluster.jobs.name}\"}"
}

