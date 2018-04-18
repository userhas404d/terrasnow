variable "repo_base" {}
variable "salt_version" {}

variable "create_archive" {
  default = "false"
}

variable "reposync_repo" {
  default = "https://github.com/userhas404d/terrasnow.git"
}

variable "reposync_ref" {
  default = "Develop"
}

locals {
  url_parts      = "${split("/", var.repo_base)}"
  bucket         = "${local.url_parts[3]}"
  key            = "${join("/", slice(local.url_parts, 4, length(local.url_parts)))}"
  skip_repo_sync = "${1 == 0}"
}

data "aws_partition" "current" {
  count = "${local.skip_repo_sync ? 0 : 1}"
}

data "http" "ip" {
  count = "${local.skip_repo_sync ? 0 : 1}"

  # Get local ip for security group ingress
  url = "http://ipv4.icanhazip.com"
}

data "aws_vpc" "this" {
  count = "${local.skip_repo_sync ? 0 : 1}"

  default = "true"
}

data "aws_ami" "this" {
  count = "${local.skip_repo_sync ? 0 : 1}"

  most_recent = true

  filter {
    name   = "name"
    values = ["amzn-ami-hvm-2017.09.*-x86_64-gp2"]
  }

  filter {
    name   = "owner-alias"
    values = ["amazon"]
  }

  name_regex = "amzn-ami-hvm-2017\\.09\\.\\d\\.[\\d]{8}-x86_64-gp2"
}

data "aws_iam_policy_document" "trust" {
  count = "${local.skip_repo_sync ? 0 : 1}"

  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "role" {
  count = "${local.skip_repo_sync ? 0 : 1}"

  statement {
    actions = [
      "s3:DeleteObject",
      "s3:GetObject",
      "s3:PutObject",
    ]

    resources = [
      "arn:${data.aws_partition.current.partition}:s3:::${local.bucket}/${local.key}/*",
    ]
  }

  statement {
    actions = [
      "s3:ListBucket",
    ]

    resources = [
      "arn:${data.aws_partition.current.partition}:s3:::${local.bucket}",
    ]
  }
}

resource "random_id" "this" {
  count = "${local.skip_repo_sync ? 0 : 1}"

  keepers = {
    # Generate a new id each time we change the salt version
    salt_version = "${var.salt_version}"
  }

  byte_length = 8
}

resource "aws_iam_role" "this" {
  count = "${local.skip_repo_sync ? 0 : 1}"

  name               = "salt-reposync-${random_id.this.hex}"
  assume_role_policy = "${data.aws_iam_policy_document.trust.json}"
}

resource "aws_iam_role_policy" "this" {
  count = "${local.skip_repo_sync ? 0 : 1}"

  name   = "salt-reposync-${random_id.this.hex}"
  role   = "${aws_iam_role.this.id}"
  policy = "${data.aws_iam_policy_document.role.json}"
}

resource "aws_iam_instance_profile" "this" {
  count = "${local.skip_repo_sync ? 0 : 1}"

  name = "salt-reposync-${random_id.this.hex}"
  role = "${aws_iam_role.this.name}"
}

resource "tls_private_key" "this" {
  count = "${local.skip_repo_sync ? 0 : 1}"

  algorithm = "RSA"
  rsa_bits  = "4096"
}

resource "aws_key_pair" "this" {
  count = "${local.skip_repo_sync ? 0 : 1}"

  key_name   = "salt-reposync-${random_id.this.hex}"
  public_key = "${tls_private_key.this.public_key_openssh}"
}

resource "aws_security_group" "this" {
  count = "${local.skip_repo_sync ? 0 : 1}"

  name   = "salt-reposync-${random_id.this.hex}"
  vpc_id = "${data.aws_vpc.this.id}"

  tags {
    Name = "salt-reposync-${random_id.this.hex}"
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["${chomp(data.http.ip.body)}/32"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_s3_bucket" "tftemplates" {
   bucket = "terraform-templates-${random_id.this.hex}"
   acl = "private"

   tags {
     Name        = "terraform-templates-${random_id.this.hex}"
     Environment = "Dev"
  }
}

resource "aws_s3_bucket" "tfstate" {
   bucket = "terraform-state-files-${random_id.this.hex}"
   acl = "private"

   tags {
     Name        = "terraform-state-files-${random_id.this.hex}"
     Environment = "Dev"
  }
}

resource "aws_instance" "this" {
  count = "${local.skip_repo_sync ? 0 : 1}"

  ami                    = "${data.aws_ami.this.id}"
  instance_type          = "t2.micro"
  iam_instance_profile   = "${aws_iam_instance_profile.this.name}"
  key_name               = "${aws_key_pair.this.id}"
  vpc_security_group_ids = ["${aws_security_group.this.id}"]

  tags {
    Name = "salt-reposync-${random_id.this.hex}"
  }

  provisioner "remote-exec" {
    inline = [
      "set -e",
      "sudo yum -y install git",
      "git clone -b ${var.reposync_ref} ${var.reposync_repo}",
      "PRIVATE_SSH_KEY=${join("", tls_private_key.this.*.private_key_pem)}"
    ]

    connection {
      port        = 22
      user        = "ec2-user"
      private_key = "${tls_private_key.this.private_key_pem}"
    }
  }
}

output "public_ip" {
  description = "Public IP of the EC2 instance"
  value       = "${join("", aws_instance.this.*.public_ip)}"
}

output "private_key" {
  description = "Private key for the keypair"
  value       = "${join("", tls_private_key.this.*.private_key_pem)}"
}
