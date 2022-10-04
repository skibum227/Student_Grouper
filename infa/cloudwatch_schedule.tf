#https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_rule

resource "aws_cloudwatch_event_rule" "lambda_start" {
  name                = "${var.resource_prefix}-lambda-start-trigger"
  description         = "hits lambda for the start function"
  schedule_expression = "cron(30 11 ? * Mon-Fri *)"
}

resource "aws_cloudwatch_event_rule" "lambda_stop" {
  name                = "${var.resource_prefix}-lambda-stop-trigger"
  description         = "hits lambda for the stop function"
  schedule_expression = "cron(0 19 ? * Mon-Fri *)"
}

resource "aws_cloudwatch_event_target" "lambda_start" {
  rule      = aws_cloudwatch_event_rule.lambda_start
  target_id = "Send start msg"
  arn       = aws_lambda_function.lambda_ecs_control.arn 
  input_transformer {
    input_paths = {
      status  = "start"
      cluster = "jobs-cluster",
      service = "student-grouper-application-v3",
    }
    input_template = <<EOF 
    {
        "status":  <status>,
        "cluster": <cluster>,
        "service": <service>,
    }
    EOF
  }
}

resource "aws_cloudwatch_event_target" "lambda_stop" {
  rule      = aws_cloudwatch_event_rule.lambda_stop
  target_id = "Send start msg"
  arn       = aws_lambda_function.lambda_ecs_control.arn
  input_transformer {
    input_paths = {
      status  = "stop"
      cluster = "jobs-cluster",
      service = "student-grouper-application-v3",
    }
    input_template = <<EOF
    {
        "status":  <status>,
        "cluster": <cluster>,
        "service": <service>,
    }
    EOF
  }
}

