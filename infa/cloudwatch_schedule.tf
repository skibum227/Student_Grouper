# Resource docs...
#   https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_rule

# These Eventbridge rules control bringing up and shutting down all running servivces
#   and tasks during certain hours to save money
resource "aws_cloudwatch_event_rule" "lambda_start" {
  name                = "${var.resource_prefix}lambda-start-trigger"
  description         = "hits lambda for the start function"
  schedule_expression = "cron(30 11 ? * Mon-Fri *)"
}

resource "aws_cloudwatch_event_rule" "lambda_stop" {
  name                = "${var.resource_prefix}lambda-stop-trigger"
  description         = "hits lambda for the stop function"
  schedule_expression = "cron(0 19 ? * Mon-Fri *)"
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

