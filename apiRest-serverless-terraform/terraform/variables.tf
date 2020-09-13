variable "project_name" {
  type = string
  default = "apiRest-serverless"
}

variable "stage" {
  type = string
  default = "dev"
}

variable "zipfile_name" {
  type = string
  default = "../apiRest-serverless.zip"
}

variable "dynamodb-read_capacity" {
  type = number
  default = 1
}

variable "dynamodb-write_capacity" {
  type = number
  default = 1
}

