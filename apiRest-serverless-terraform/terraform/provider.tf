terraform {
  required_version = "~> 0.12.0"
  backend "s3" {
    bucket = "jjc-terraform-states"
    key = "apiRest-terraform.tfstate"
    region = "eu-west-2"
  }
}

provider "aws" {
  profile = var.aws_profile
  region  = var.aws_region
}

variable aws_profile {
  type = string
}

variable aws_region {
  type = string
}
