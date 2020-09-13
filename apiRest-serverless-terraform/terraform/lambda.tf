# Uploading of the backend code will be using the base64 hash of the zipfile of the code. 
# The code will need to be first compressed and zipped before taking this action. (init.sh)
# This lambda function will need the permissions to write to the dynamoDB table.
resource "aws_lambda_function" "main" {
  filename = var.zipfile_name
  function_name = var.project_name
  role = aws_iam_role.main.arn
  handler = "email.handler"

  source_code_hash = filebase64sha256(var.zipfile_name)

  runtime = "nodejs12.x"
}

# To establish trust between the 2 AWS services (lambda & api-gateway)
resource "aws_iam_role" "main" {
  name = "${var.project_name}-iam_lambda"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

# To give permission for the lambda function access the database resource and perform the PutItem action. 
# Details of the policy is interpolated via a template file (lambda_policy.tmpl)
resource "aws_iam_policy" "main" {
  name = "main"
  path = "/"
  description = "IAM policy for lambda to write to dynamodb table and logging"

  policy = templatefile("${path.module}/lambda_policy.tmpl", { dynamodb_arn = aws_dynamodb_table.main.arn })
}

# To bind the aws_iam_role to the aws_iam_policy on the lambda function
resource "aws_iam_role_policy_attachment" "main" {
  role = aws_iam_role.main.name
  policy_arn = aws_iam_policy.main.arn
}

# To allow API Gateway to be able to integrate the lambda function and invoke it
resource "aws_lambda_permission" "main" {
  statement_id = "AllowExecutionFromAPIGateway"
  action = "lambda:InvokeFunction"
  function_name = aws_lambda_function.main.function_name
  principal = "apigateway.amazonaws.com"

  source_arn = "${aws_api_gateway_rest_api.main.execution_arn}/*/*/*"
}