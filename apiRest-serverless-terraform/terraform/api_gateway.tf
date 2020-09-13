# The API Gateway is required to expose the lambda function to be consumed by servers and websites via a URL endpoint. 
# The endpoint will be served over the HTTPS, which requires some extra configurations

resource "aws_api_gateway_rest_api" "main" {
  name = var.project_name
}

# Only 1 stage environment of stage for this example. 
# But you can setup a different stages to differentiate the staging and production environments.
resource "aws_api_gateway_stage" "main" {
  stage_name = var.stage
  rest_api_id = aws_api_gateway_rest_api.main.id
  deployment_id = aws_api_gateway_deployment.main.id
}

# Configures the deployment of the API. The explicit dependency is critical to ensure the 
# deployment is called into effect after all the necessary resources have been provisioned.
resource "aws_api_gateway_deployment" "main" {
  depends_on = [
    aws_api_gateway_integration_response.main,
    aws_api_gateway_method_response.main,
  ]
  rest_api_id = aws_api_gateway_rest_api.main.id
}

# Refers to each api route of this project (only 1 in this case)
resource "aws_api_gateway_resource" "main" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id = aws_api_gateway_rest_api.main.root_resource_id
  path_part = "email"
}

# Sets the integration to lambda proxy using POST HTTP method without any authorization
# (as specified by the aws_api_gateway_method configuration)
resource "aws_api_gateway_integration" "main" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.main.id
  http_method = aws_api_gateway_method.main.http_method
  integration_http_method = aws_api_gateway_method.main.http_method
  type = "AWS_PROXY"
  uri = aws_lambda_function.main.invoke_arn
}

# Responsible for handling the response from the lambda function. 
# This is where we could make changes to the headers returned from the lambda function.
# This is also the place to map and transform the response data from the backend to fit the desired data structure.
resource "aws_api_gateway_integration_response" "main" {
  depends_on = [aws_api_gateway_integration.main]

  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.main.id
  http_method = aws_api_gateway_method.main.http_method
  status_code = aws_api_gateway_method_response.main.status_code
}

resource "aws_api_gateway_method" "main" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.main.id
  http_method = "POST"
  authorization = "NONE"
}

# We can filter what response headers and data from aws_api_gateway_integration_response 
#  to pass on to the caller
resource "aws_api_gateway_method_response" "main" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.main.id
  http_method = aws_api_gateway_method.main.http_method
  status_code = "200"
}
# The transform and mapping of the headers and data from the backend (ie the lambda function) 
# in aws_api_gateway_integration_response and the filter of headers and data before passing 
# to the front end in aws_api_gateway_method_response is not needed in this sample application. 
# It is just good knowledge to have
#

resource "aws_api_gateway_method_settings" "main" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  stage_name = aws_api_gateway_stage.main.stage_name
  
  # settings not working when specifying the single method
  # refer to: https://github.com/hashicorp/terraform/issues/15119
  method_path = "*/*"

  settings {
    throttling_rate_limit = 5
    throttling_burst_limit = 10
  }
}


