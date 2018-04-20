variable "ServiceNowInstanceName" {
  type = "string"
  description = "Host name of the target ServiceNow Instance"
}

variable "salt_version" {
  default = 123
}

variable "sn_user_name" {
  type = "string"
  description = "User name of the ServiceNow account making the REST api calls."
}

variable "sn_pwd" {
  type = "string"
  description = "Password of the ServiceNow account making the REST api calls."
}

variable "host_user" {
  type = "string"
  description = "User name of the host's user."
  default = "ec2-user"
}

variable "create_archive" {
  default = "false"
}

variable "reposync_repo" {
  default = "https://github.com/userhas404d/terrasnow.git"
}

variable "reposync_ref" {
  default = "Develop"
}
