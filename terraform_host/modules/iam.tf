variable "rand_id" {}
variable "aws_partition" {}
variable "skip_repo_sync" {}

data "aws_iam_policy_document" "trust" {
  count = "${var.skip_repo_sync ? 0 : 1}"

  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "deny-data-role" {
  count = "${var.skip_repo_sync ? 0 : 1}"

#reference: https://alestic.com/2015/10/aws-iam-readonly-too-permissive/
  statement {
    actions = [
    "cloudformation:GetTemplate",
    "dynamodb:GetItem",
    "dynamodb:BatchGetItem",
    "dynamodb:Query",
    "dynamodb:Scan",
    "ec2:GetConsoleOutput",
    "ec2:GetConsoleScreenshot",
    "ecr:BatchGetImage",
    "ecr:GetAuthorizationToken",
    "ecr:GetDownloadUrlForLayer",
    "kinesis:Get*",
    "lambda:GetFunction",
    "logs:GetLogEvents",
    "s3:GetObject",
    "sdb:Select*",
    "sqs:ReceiveMessage",
    ]

    resources = [
    "*",
    ]
  }
}

resource "aws_iam_role" "deny-data-role" {
  count = "${var.skip_repo_sync ? 0 : 1}"

  name               = "deny-data-${var.rand_id}"
  description        = "Use in combination with Amazon managed ReadOnlyAccess policy"
  assume_role_policy = "${data.aws_iam_policy_document.deny-data-role.json}"
}

data "aws_iam_policy_document" "role" {
  count = "${var.skip_repo_sync ? 0 : 1}"

  statement {
    actions = [
      "s3:DeleteObject",
      "s3:GetObject",
      "s3:PutObject",
    ]

    resources = [
      "arn:${var.aws_partition}:s3:::terraform-templates-${var.rand_id}/*",
      "arn:${var.aws_partition}:s3:::terraform-state-files-${var.rand_id}/*",
    ]
  }

  statement {
    actions = [
      "s3:ListBucket",
    ]

    resources = [
    "arn:${var.aws_partition}:s3:::terraform-templates-${var.rand_id}/*",
    "arn:${var.aws_partition}:s3:::terraform-state-files-${var.rand_id}/*",
    ]
  }
}

resource "aws_iam_role" "this" {
  count = "${var.skip_repo_sync ? 0 : 1}"

  name               = "terraform-host-${var.rand_id}"
  assume_role_policy = "${data.aws_iam_policy_document.trust.json}"
}

resource "aws_iam_role_policy" "this" {
  count = "${var.skip_repo_sync ? 0 : 1}"

  name   = "terraform-host-${var.rand_id}"
  role   = "${aws_iam_role.this.id}"
  policy = "${data.aws_iam_policy_document.role.json}"
}

output "host_role_name" {
  description = "name of the role being assinged to the host"
  value = "${aws_iam_role.this.name}"
}
