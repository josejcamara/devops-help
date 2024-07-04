""" List all the EC2 instances """

# pylint: disable=import-error,broad-exception-caught
# pyright: reportMissingImports=false, reportMissingModuleSource=false

import boto3
import botocore
import datetime
from dateutil.tz import tzlocal
import sys

import organization as org

DEFAULT_REGION = 'eu-west-1'

def assumed_role_session(role_arn: str, base_session: botocore.session.Session = None):
    base_session = base_session or boto3.session.Session()._session
    fetcher = botocore.credentials.AssumeRoleCredentialFetcher(
        client_creator = base_session.create_client,
        source_credentials = base_session.get_credentials(),
        role_arn = role_arn,
        extra_args = {
        #    'RoleSessionName': None # set this if you want something non-default
        }
    )
    creds = botocore.credentials.DeferredRefreshableCredentials(
        method = 'assume-role',
        refresh_using = fetcher.fetch_credentials,
        time_fetcher = lambda: datetime.datetime.now(tzlocal())
    )
    botocore_session = botocore.session.Session()
    botocore_session._credentials = creds
    return boto3.Session(botocore_session = botocore_session)

def get_instance_security_groups_cidr(client, instance, port):
    sg_list = [ sg['GroupId'] for sg in instance.get('SecurityGroups')]
    ls_cidr = []
    response = client.describe_security_groups(GroupIds=sg_list)
    for sg in response.get('SecurityGroups'):
        rules = sg.get('IpPermissions',[])
        for lnr in rules:
            if lnr.get("FromPort") == port:
                for ipr in lnr['IpRanges']:
                    ls_cidr.append(ipr.get('CidrIp'))
    return ls_cidr

def get_instances_in_account(sts, account_info, region=DEFAULT_REGION, debug=False):
    """ Get a list of rows with the ec2 in the account """
    account_id, account_name, role_name = account_info
    role_arn = f"arn:aws:iam::{account_id}:role/{role_name}"

    try:
        stsresponse = sts.assume_role(
            RoleArn=role_arn,
            RoleSessionName='newsession'
            )
    except Exception as e:
        print(f"[ERROR] {sts.get_caller_identity().get('Arn')} was unable to assume role {role_arn} in account {account_name}.")
        print(e)
        return []

    new_session = boto3.Session(
        aws_access_key_id=stsresponse['Credentials']['AccessKeyId'],
        aws_secret_access_key=stsresponse['Credentials']['SecretAccessKey'],
        aws_session_token=stsresponse['Credentials']['SessionToken'])

    try:
        ec2 = new_session.client(
            'ec2',
            config=boto3.session.Config(region_name=region)
            )
    except Exception as e:
        print(f"[ERROR] {sts.get_caller_identity().get('Arn')} was unable to create session on region {region} in account {account_name}.")
        print(e)
        return []

    try:
        response = ec2.describe_instances()
    except Exception as e:
        print(f"[ERROR] {sts.get_caller_identity().get('Arn')} was unable to describe instances on region {region} in account {account_name}.")
        print(e)
        return []

    result = []
    for reservation in response.get('Reservations'):
        for instance in reservation.get('Instances'):

            ins_id = instance.get('InstanceId')
            ami_id = instance.get('ImageId')
            ins_state = instance.get('State').get('Name')

            response = ec2.describe_images(ImageIds = [ami_id])
            if len(response['Images']) == 0: 
                ami = { 'Description': "EC2 can't retrieve the name because the AMI was either deleted or made private"}
            else:
                ami = response['Images'][0]

            ssh_cidr = get_instance_security_groups_cidr(ec2, instance, 22)

            result.append([
                account_id, 
                region,
                ins_id,
                ins_state,
                ami_id, 
                str(ami.get('Public')), 
                ami.get('Description',ami.get('Name','-')).replace(',',''),
                ';'.join(ssh_cidr)
                ])
    
    return result

# def main():
#     sts_client = boto3.client('sts')
#     caller = sts_client.get_caller_identity()
#     print(">>> RUNNING AS", caller.get('Arn'))

#     account_id = "799190859004"

#     session = assumed_role_session(f"arn:aws:iam::{account_id}:role/DAG-AWS-ont-aws-admin")
#     ec2 = session.client('ec2', region_name=DEFAULT_REGION)

#     custom_filter = [
#         # { 'Name':'tag:Owner', 'Values': ['user@example.com']}
#     ]

#     data = []   
#     response = ec2.describe_instances(Filters=custom_filter)
#     for reservation in response.get('Reservations'):
#         for instance in reservation.get('Instances'):

#             ins_id = instance.get('InstanceId')
#             ami_id = instance.get('ImageId')
#             ins_state = instance.get('State').get('Name')

#             response = ec2.describe_images(ImageIds = [ami_id])
#             if len(response['Images']) == 0: 
#                 ami = { 'Description': "EC2 can't retrieve the name because the AMI was either deleted or made private"}
#             else:
#                 ami = response['Images'][0]

#             ssh_cidr = get_instance_security_groups_cidr(ec2, instance, 22)

#             data.append([
#                 account_id, 
#                 ins_id,
#                 ins_state,
#                 ami_id, 
#                 str(ami.get('Public')), 
#                 ami.get('Description',ami.get('Name','-')).replace(',',''),
#                 ';'.join(ssh_cidr)
#                 ])

#     # Print
#     for lnd in data:
#         print(','.join(lnd))


if __name__ == "__main__":
    # opt = check_arguments()
    main()