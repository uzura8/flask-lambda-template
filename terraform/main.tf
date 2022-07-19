variable "prj_prefix" {}
variable "aws_region_default" {}
variable "route53_zone_id" {}
variable "domain_api_dev" {}
variable "domain_api_prd" {}

provider "aws" {
  region = var.aws_region_default
  alias  = "default"
}

terraform {
  backend "s3" {
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.74.2"
    }
  }
}

locals {
  fqdn = {
    api_dev = var.domain_api_dev
    api_prd = var.domain_api_prd
  }
}

resource "aws_acm_certificate" "api_dev" {
  provider          = aws.default
  domain_name       = local.fqdn.api_dev
  validation_method = "DNS"

  tags = {
    Name      = join("-", [var.prj_prefix, "acm"])
    ManagedBy = "terraform"
  }
}
resource "aws_acm_certificate" "api_prd" {
  provider          = aws.default
  domain_name       = local.fqdn.api_prd
  validation_method = "DNS"

  tags = {
    Name      = join("-", [var.prj_prefix, "acm"])
    ManagedBy = "terraform"
  }
}

# CNAME Record
resource "aws_route53_record" "api_dev_acm_c" {
  for_each = {
    for d in aws_acm_certificate.api_dev.domain_validation_options : d.domain_name => {
      name   = d.resource_record_name
      record = d.resource_record_value
      type   = d.resource_record_type
    }
  }
  zone_id         = var.route53_zone_id
  name            = each.value.name
  type            = each.value.type
  ttl             = 172800
  records         = [each.value.record]
  allow_overwrite = true
}
resource "aws_route53_record" "api_prd_acm_c" {
  for_each = {
    for d in aws_acm_certificate.api_prd.domain_validation_options : d.domain_name => {
      name   = d.resource_record_name
      record = d.resource_record_value
      type   = d.resource_record_type
    }
  }
  zone_id         = var.route53_zone_id
  name            = each.value.name
  type            = each.value.type
  ttl             = 172800
  records         = [each.value.record]
  allow_overwrite = true
}

## Related ACM Certification and CNAME record
resource "aws_acm_certificate_validation" "api_dev" {
  provider                = aws.default
  certificate_arn         = aws_acm_certificate.api_dev.arn
  validation_record_fqdns = [for record in aws_route53_record.api_dev_acm_c : record.fqdn]
}
resource "aws_acm_certificate_validation" "api_prd" {
  provider                = aws.default
  certificate_arn         = aws_acm_certificate.api_prd.arn
  validation_record_fqdns = [for record in aws_route53_record.api_prd_acm_c : record.fqdn]
}

# Cognito
resource "aws_cognito_user_pool" "prd" {
  provider                 = aws.default
  name                     = join("-", [var.prj_prefix, "cognito-user-pool"])
  auto_verified_attributes = ["email"]
  alias_attributes         = ["email"]
  schema {
    attribute_data_type = "String"
    name                = "email"
    required            = true
  }
  schema {
    attribute_data_type      = "String"
    name                     = "role"
    developer_only_attribute = true
    required                 = false
    #mutable                  = true

    string_attribute_constraints {
      max_length = "64"
      #min_length = "1"
    }
  }
  username_configuration {
    case_sensitive = false
  }
  lifecycle {
    ignore_changes = [schema]
  }

  tags = {
    Name      = join("-", [var.prj_prefix, "cognito", "user", "pool"])
    ManagedBy = "terraform"
  }
}

resource "aws_cognito_user_pool_client" "prd" {
  provider        = aws.default
  name            = join("-", [var.prj_prefix, "web_client"])
  user_pool_id    = aws_cognito_user_pool.prd.id
  generate_secret = false
  explicit_auth_flows = [
    "ALLOW_ADMIN_USER_PASSWORD_AUTH",
    "ALLOW_CUSTOM_AUTH",
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_USER_SRP_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH"
  ]
}

resource "aws_cognito_identity_pool" "prd" {
  provider                         = aws.default
  identity_pool_name               = join("-", [var.prj_prefix, "cognito-identity-pool"])
  allow_unauthenticated_identities = false

  cognito_identity_providers {
    client_id               = aws_cognito_user_pool_client.prd.id
    provider_name           = aws_cognito_user_pool.prd.endpoint
    server_side_token_check = false
  }

  #read_attributes = [
  #  "email",
  #  "custom:role",
  #]

  #write_attributes = [
  #  "email",
  #  "custom:role",
  #]

  tags = {
    Name      = join("-", [var.prj_prefix, "cognito", "identity", "pool"])
    ManagedBy = "terraform"
  }
}
