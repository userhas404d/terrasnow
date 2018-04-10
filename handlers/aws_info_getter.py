"""Retrieve JSON obj of required account information."""

import datetime
import json
import logging

import boto3
import dateutil.parser

ec2 = boto3.client('ec2')
sts = boto3.client('sts')


def get_assume_role_input(role_arn, duration):
    """Create input for assume_role."""
    return {
        'RoleArn': role_arn,
        'RoleSessionName': 'get_account_info_script',
        'DurationSeconds': duration
    }


def assume_role(**kwargs):
    """Assume stack update role."""
    response = sts.assume_role(**kwargs)
    logging.info("assume_role: {}".format(response))
    return response


def get_elevated_session_input(response):
    """Create input for get_elevated_session."""
    return {
     'aws_access_key_id': response['Credentials']['AccessKeyId'],
     'aws_secret_access_key': response['Credentials']['SecretAccessKey'],
     'aws_session_token': response['Credentials']['SessionToken']
    }


def get_elevated_session(**kwargs):
    """Create new boto3 session with assumed role."""
    data_retrieval_session = boto3.Session(**kwargs)
    elevated_ec2_client = data_retrieval_session.client('ec2')
    return elevated_ec2_client


def get_sgs(assumed_role):
    """Retrieve list of security groups."""
    sgs = []
    response = assumed_role.describe_security_groups()
    for item in response['SecurityGroups']:
        security_group = {}
        for _key in item.items():
            security_group['Name'] = item['GroupName']
            security_group['GroupId'] = item['GroupId']
            security_group['VpcId'] = item['VpcId']
        if security_group:
            sgs.append(security_group)
    return sgs


def get_linux_amis(assumed_role):
    """Retrieve list of linux amis."""
    amis = []
    response = assumed_role.describe_images(
        Filters=[
            {'Name': 'state', 'Values': ['available']},
            {'Name': 'is-public', 'Values': ['true']},
            {'Name': 'owner-id', 'Values': ['701759196663']}
        ])
    for item in response['Images']:
        ami = {}
        for _key in item.items():
            if(date_check(item['CreationDate'])
               and "spel-minimal-centos-7" in item['Name']):
                ami['Name'] = item['Name']
                ami['ImageId'] = item['ImageId']
                ami['OSType'] = "CentOS"
            elif(date_check(item['CreationDate'])
                 and "spel-minimal-rhel-7" in item['Name']):
                ami['Name'] = item['Name']
                ami['ImageId'] = item['ImageId']
                ami['OSType'] = "RHEL7"
        if ami:
            amis.append(ami)
    return amis


def get_windows_amis(assumed_role):
    """Retrieve list of windows amis."""
    amis = []
    response = assumed_role.describe_images(
        Filters=[
            {'Name': 'state', 'Values': ['available']},
            {'Name': 'is-public', 'Values': ['true']},
            {'Name': 'owner-alias', 'Values': ['amazon']}
        ])
    for item in response['Images']:
        ami = {}
        for _key in item.items():
            if(item['CreationDate']
               and date_check(item['CreationDate'])
               and "Windows_Server-2016-English-Full-Base" in item['Name']
               and "LongIDTest-" not in item['Name']):
                ami['Name'] = item['Name']
                ami['ImageId'] = item['ImageId']
                ami['OSType'] = "Windows Server 2016"
            # elif(item['CreationDate']
            #      and date_check(item['CreationDate'])
            #      and "Windows_Server-2012-English-Full-Base" in item['Name']
            #      and "LongIDTest-" not in item['Name']):
            #     ami['Name'] = item['Name']
            #     ami['ImageId'] = item['ImageId']
            #     ami['OSType'] = "Windows Server 2012"
            # else:
            #     continue
        if ami:
            amis.append(ami)
    return amis


def date_check(date):
    """Check date is at least 60 days old."""
    # 2018-03-14T19:30:27.000Z
    today = datetime.date.today()
    margin = datetime.timedelta(days=30)
    d = dateutil.parser.parse(date)
    date = datetime.date(d.year, d.month, d.day)
    # check if date is within 60 days of today
    return date + margin >= today


def get_key_pairs(assumed_role):
    """Retrieve list of key pairs."""
    keys = []
    response = assumed_role.describe_key_pairs()
    for item in response['KeyPairs']:
        key = {}
        for _key in item.items():
            key['KeyName'] = item['KeyName']
        if key:
            keys.append(key)
    return keys


# def get_vpcs(assumed_role):
#     """Retrieve list of vpcs."""
#     vpcs = []
#     response = assumed_role.describe_vpcs(
#         Filters=[
#             {'Name': 'state', 'Values': ['available']}
#         ])
#     for item in response['Vpcs']:
#         vpc = {}
#         for _key in item.items():
#             try:
#                 if item['Tags'][0]['Value']:
#                     vpc['Name'] = item['Tags'][0]['Value']
#                     vpc['VpcId'] = item['VpcId']
#             except KeyError as e:
#                 continue
#             if vpc:
#                 vpcs.append(vpc)
#     return vpcs


def get_subnets(assumed_role):
    """Retrieve list of subnets."""
    subnets = []
    response = assumed_role.describe_subnets(
        Filters=[
            {'Name': 'state', 'Values': ['available']}
        ])
    for item in response['Subnets']:
        subnet = {}
        try:
            if item['Tags'][0]['Value']:
                subnet['Name'] = item['Tags'][0]['Value']
                subnet['SubnetId'] = item['SubnetId']
                subnet['VpcId'] = item['VpcId']
        except KeyError as e:
            continue
        if subnet:
            subnets.append(subnet)
    return(subnets)


def get_everything(assumed_role):
    """Return complete json object with all info."""
    sorted_dict = {}

    sorted_dict['amis'] = {
                           "linux": get_linux_amis(assumed_role),
                           "windows": get_windows_amis(assumed_role)
                           }
    sorted_dict['key_pairs'] = get_key_pairs(assumed_role)
    sorted_dict['subnets'] = get_subnets(assumed_role)
    sorted_dict['security_groups'] = get_sgs(assumed_role)

    return sorted_dict


def assumed_role_get_everything(role_to_assume_arn, duration):
    """Return complete json object with all info."""
    assume_role_input = get_assume_role_input(role_to_assume_arn, duration)
    assume_role_response = assume_role(**assume_role_input)
    logging.info("Assumed target role for {} seconds".format(duration))

    elevated_session_input = get_elevated_session_input(assume_role_response)
    elevated_ec2_client = get_elevated_session(**elevated_session_input)
    logging.info("Retrieved elevated ec2 client.")

    return json.dumps(get_everything(elevated_ec2_client))


# aassumed_role_get_everything('asdf', 900)
# print(get_everything())
# print(date_check('2018-01-14T19:30:27.000Z'))
