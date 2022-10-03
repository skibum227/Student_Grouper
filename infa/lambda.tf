# Defines the location of the lambda function code
data "archive_file" "zip_the_python_code" {
    type        = "zip"
    source_dir  = "lambda_functions/"
    output_path = "lambda_functions/ecs_control.zip"
}

resource "aws_lambda_function" "terraform_lambda_func" {
    filename      = "lambda_functions/ecs_control.zip"
    function_name = "ECS_Service_Control_Lambda_Function"
    role          = aws_iam_role.lambda_role.arn
    handler       = "ecs_control.lambda_handler"
    runtime       = "python3.9"
    # This makes sure the lambda function is build after the role is ready
    depends_on    = [aws_iam_role_policy_attachment.attach_iam_policy_to_iam_role]
}
