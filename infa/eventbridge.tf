https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_rule

resource "aws_cloudwatch_event_rule" "lambda_start" {
  name                = "${var.resource_prefix}-lambda-start-trigger"
  description         = "hits lambda for the start function"
  schedule_expression = "cron(30 11 ? * Mon-Fri *)"
}

resource "aws_cloudwatch_event_rule" "lambda_stop" {
  name                = "${var.resource_prefix}-lambda-start-trigger"
  description         = "hits lambda for the start function"
  schedule_expression = "cron(0 19 ? * Mon-Fri *)"
}

# NEED TO ADD PAYLOAD!!!!!!!!!
resource "aws_cloudwatch_event_target" "lambda_start" {
  rule      = aws_cloudwatch_event_rule.console.lambda_start
  target_id = "Send start msg"
  arn       = aws_lambda_function.lambda_ecs_control.arn 
}

resource "aws_cloudwatch_event_target" "lambda_stop" {
  rule      = aws_cloudwatch_event_rule.console.lambda_stop
  target_id = "Send start msg"
  arn       = aws_lambda_function.lambda_ecs_control.arn
}




???????????
module "eventbridge_ecs_start" {
  source = "terraform-aws-modules/eventbridge/aws"

  create_bus = false

  rules = {
    crons = {
      description         = "Trigger ECS Control Lambda in morning, Mon-Fri"
      schedule_expression = "rate(5 minutes)"
    }
  }

  targets = {
    crons = [
      {
        name  = "lambda-loves-cron"
        arn   = module.lambda.lambda_function_arn
        input = jsonencode({ "job" : "cron-by-rate" })
      }
    ]
  }
}

another option??????

  bus_name = "my-bus"

  rules = {
    logs = {
      description   = "Capture log data"
      event_pattern = jsonencode({ "source" : ["my.app.logs"] })
    }
  }

  targets = {
    logs = [
      {
        name = "send-logs-to-sqs"
        arn  = aws_sqs_queue.queue.arn
      },
      {
        name = "send-logs-to-cloudwatch"
        arn  = aws_cloudwatch_log_stream.logs.arn
      }
    ]
  }
}

