"""Retrieve JSON obj of required account information."""

import datetime

import boto3
import dateutil.parser

ec2 = boto3.client('ec2')

image_name = 'spel-minimal-centos-7.4-hvm-.*x86_64-gp2'


def get_sgs():
    """Retrieve list of security groups."""
    sgs = []
    response = ec2.describe_security_groups()
    for item in response['SecurityGroups']:
        security_group = {}
        for _key in item.items():
            security_group['Name'] = item['GroupName']
            security_group['GroupId'] = item['GroupId']
        if security_group:
            sgs.append(security_group)
    return sgs


def get_linux_amis():
    """Retrieve list of linux amis."""
    amis = []
    response = ec2.describe_images(
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


def get_windows_amis():
    """Retrieve list of windows amis."""
    amis = []
    response = ec2.describe_images(
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


def get_key_pairs():
    """Retrieve list of key pairs."""
    keys = []
    response = ec2.describe_key_pairs()
    for item in response['KeyPairs']:
        key = {}
        for _key in item.items():
            key['KeyName'] = item['KeyName']
        if key:
            keys.append(key)
    return keys


def get_vpcs():
    """Retrieve list of vpcs."""
    vpcs = []
    response = ec2.describe_vpcs(
        Filters=[
            {'Name': 'state', 'Values': ['available']}
        ])
    for item in response['Vpcs']:
        vpc = {}
        for _key in item.items():
            try:
                if item['Tags'][0]['Value']:
                    vpc['Name'] = item['Tags'][0]['Value']
                    vpc['VpcId'] = item['VpcId']
            except KeyError as e:
                continue
            if vpc:
                vpcs.append(vpc)
    return vpcs


def get_everything():
    """Return complete json object with all info."""
    sorted_dict = {}

    sorted_dict['amis'] = {
                           "linux": get_linux_amis(),
                           "windows": get_windows_amis()
                           }
    sorted_dict['key_paris'] = get_key_pairs()
    sorted_dict['vpcs'] = get_vpcs()
    sorted_dict['security_groups'] = get_sgs()

    return sorted_dict


# print(get_everything())
print(get_everything())
# print(date_check('2018-01-14T19:30:27.000Z'))
