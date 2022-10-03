module "eventbridge_ecs_start" {
  source = "../../"

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

