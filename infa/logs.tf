# Creates the logging resources
resource "aws_cloudwatch_log_group" "jobs" {
  name = "${var.resource_prefix}jobs-log-group"
}
