# Creates the logging resources
esource "aws_cloudwatch_log_group" "jobs" {
  name = "${var.resource_prefix}jobs-log-group"
}
