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

data "aws_iam_policy_document" "read-only" {
  count = "${var.skip_repo_sync ? 0 : 1}"

  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
    principals {
      type        = "AWS"
      identifiers = ["${aws_iam_role.this.arn}"]
    }
  }
}

data "aws_iam_policy_document" "deny-data-policy-doc" {
  count = "${var.skip_repo_sync ? 0 : 1}"

#reference: https://alestic.com/2015/10/aws-iam-readonly-too-permissive/
  statement {
    sid = "DenyData"
    effect = "Deny"
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
    "sdb:Select*",
    "sqs:ReceiveMessage",
    ]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "deny-data-policy" {
  count = "${var.skip_repo_sync ? 0 : 1}"

  name               = "deny-data-policy-${var.rand_id}"
  description        = "Use in combination with Amazon managed ReadOnlyAccess policy"
  policy = "${data.aws_iam_policy_document.deny-data-policy-doc.json}"
}

resource "aws_iam_role" "read-only-role" {
  count = "${var.skip_repo_sync ? 0 : 1}"

  name = "read-only-${var.rand_id}"
  assume_role_policy = "${data.aws_iam_policy_document.read-only.json}"
}

resource "aws_iam_role_policy_attachment" "deny-data" {
    role       = "${aws_iam_role.read-only-role.name}"
    policy_arn = "${aws_iam_policy.deny-data-policy.arn}"
}

resource "aws_iam_role_policy_attachment" "read-only" {
    role       = "${aws_iam_role.read-only-role.name}"
    policy_arn = "arn:aws:iam::aws:policy/ReadOnlyAccess"
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

output "read_only_role_arn" {
  description = "arn of the read only role"
  value = "${aws_iam_role.read-only-role.arn}"
}
