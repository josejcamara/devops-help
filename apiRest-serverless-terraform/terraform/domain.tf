# resource "aws_api_gateway_domain_name" "domain" {
#   domain_name = "mydomain.com"
#   certificate_name = "example-api"
#   certificate_body = "${file("${path.module}/example.com/example.crt")}"
#   certificate_chain = "${file("${path.module}/example.com/ca.crt")}"
#   certificate_private_key = "${file("${path.module}/example.com/example.key")}"  
# }
# resource "aws_api_gateway_base_path_mapping" "base_path_mapping" {
#   api_id      = "${aws_api_gateway_rest_api.api.id}"
  
#   domain_name = "${aws_api_gateway_domain_name.domain.domain_name}"
# }