#!/bin/bash

sudo yum install -y python36
sudo pip-3.6 install invoke
sudo pip-3.6 install requests
sudo pip-3.6 install boto3

sudo yum install -y zip unzip

wget https://releases.hashicorp.com/terraform/0.11.3/terraform_0.11.3_linux_amd64.zip
unzip terraform_0.11.3_linux_amd64.zip
sudo mv terraform /usr/local/bin/
#Confirm terraform binary is accessible: terraform --version

curl -SsL https://github.com/kvz/json2hcl/releases/download/v0.0.6/json2hcl_v0.0.6_linux_amd64 \
  | sudo tee /usr/local/bin/json2hcl > /dev/null && sudo chmod 755 /usr/local/bin/json2hcl && json2hcl -version

# mkdir /home/ec2-user/tf_test
# mkdir /home/ec2-user/tools
