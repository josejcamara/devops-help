#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DESCRIPTION_____
This script allows you to loop into all the accounts in your organization and check the IAM users in them.
If will create CSV files grouping the accounts by their prefix (i.e "ont-dig" for "ont-dig-dev" and "ont-dig-pub").

NOTE____________
At the time of writing this script, not all the accounts have a "global" role to be assumed by an admin user.
That means we can only loop into some of them, the rest will return an empty list of user and print an alert.
For workarounding that, you'll need manuall to login with SSO in that particular account and run the script.

PRE-REQUISITES__
Your ".aws/credentials" file has to have these two entries:
1. [ont-core] with the keys for a Administrator user in ONT-CORE, able to assume and admin role in the rest of old-lz accounts
2. [ont-cor-sec] with the keys for a Administrator user in ont-cor-sec, able to assume and admin role in the rest of new-lz accounts

HOW TO USE______
a) Loop over the accounts allowed
    $> python iam_keys_age.py

b) Run over a single account
    $> export AWS_PROFILE=<YOUR_ROLE_NAME>
    $> aws sso login --profile=<YOUR_ROLE_NAME>
    $> python iam_keys_age.py current

"""

# ALSO: https://git.oxfordnanolabs.local/terraform/aws/infrastructure/ont-iam-scanner
# OR: https://stackoverflow.com/questions/45156934/getting-access-key-age-aws-boto3#57577221

import boto3, os, time, datetime, sys, json
import csv
from datetime import date
from botocore.exceptions import ClientError

# Create session using your current creds
main_client = boto3.client('sts')
new_lz_session = boto3.Session(profile_name='ont-cor-sec')
old_lz_session = boto3.Session(profile_name='ont-core')

# Role to assume when looping into an account
ROLE_TO_ASSUME_DAG = 'arn:aws:iam::$ID:role/DAG-AWS-ont-aws-admin'
ROLE_TO_ASSUME_CORE = 'arn:aws:iam::$ID:role/administrator'

# METRICHOR accounts.
MC_ACCOUNTS = [ 
    '290205048571', # - MC-ONT-PRODUCTION
    '324600724370', # - MC-ONT-BUILD
    '273908593667', # - MC-ONT-STAGING
    '805489086145', # - MC-ONT-SECURITY
    '931382113477', # - MC-ONT-DEVELOPMENT
]

# Accounts to skip from our report
IGNORE_ACCOUNTS = []
IGNORE_ACCOUNTS.extend(MC_ACCOUNTS)



def get_accounts_id_organization(exclude=[], debug=False):
    """ 
        Returns the list of [account_id, account_name] in the organization you are logged into.
        It needs new_lz_session permissions
    """
    # Create an Organizations client, ensuring proper credentials and permissions
    org_client = boto3.client('organizations')

    # Use a paginator to efficiently handle potentially large result sets
    paginator = org_client.get_paginator('list_accounts')

    # Iterate through all accounts in the organization, including those in nested OUs
    org_ids = []
    for response in paginator.paginate(MaxResults=10):
        for account in response['Accounts']:
            acc_id = account['Id']
            acc_name = account['Name']
            if acc_id in exclude: 
                if debug:
                    print(f"Excluding: Account ID: {acc_id}, Account Name: {acc_name}")
                continue

            if debug:
                print(f"Account ID: {acc_id} - {acc_name} - {account['Status']} - {account['Email']}")

            org_ids.append([acc_id, acc_name])

    return org_ids

def check_console_password_activity(iam_client, username, debug=False):
    """ Returns the last time the user accessed to the console or N/A if never """
    try:
        login_profile = iam_client.get_login_profile(UserName=username)
        last_used = login_profile.get('PasswordLastUsed')
        if last_used:
            if debug: print(f"Console password last used: {last_used}")
            return last_used
        elif debug:
            print(f"User {username} does not have a console password enabled.")

    except Exception as e:
        if debug: print(f"Error checking console password activity: {e}")
        return "Disabled"

    return "N/A"


def generate_iam_keys_report(caller_session, account_info, role_arn, region_name='eu-west-1', debug=False):
    """ Returns the list of rows with the iam_users information in the account provided """ 
    account_id, account_name = account_info

    if role_arn is None:
        new_session = caller_session
    else:
        try:
            stsresponse = caller_session.assume_role(RoleArn=role_arn, RoleSessionName='newsession')
        except Exception as e:
            print(f"   [ERROR] Unable to assume role {role_arn} in {account_info}")
            return None

        new_session = boto3.Session(aws_access_key_id=stsresponse['Credentials']['AccessKeyId'],
                            aws_secret_access_key=stsresponse['Credentials']['SecretAccessKey'],
                            aws_session_token=stsresponse['Credentials']['SessionToken'])

    iam_client = new_session.client('iam', config=boto3.session.Config(region_name=region_name))

    result = []
    paginator = iam_client.get_paginator('list_users')
    for response in paginator.paginate():
        for user in response['Users']:
            row = []
            username = user['UserName']
            if debug:
                print(f"Account ID: {account_id} - User Name: {username}")

            last_login = check_console_password_activity(iam_client, username)

            owner_tag, app_tag = '-', '-'
            userTags = iam_client.list_user_tags(UserName=username)
            for tag in userTags['Tags']:
                if tag['Key'] == 'Owner': owner_tag = tag['Value']
                if tag['Key'] == 'AppName': app_tag = tag['Value']

            # Add Information about the user
            row.extend([account_name, account_id, username, last_login, owner_tag, app_tag])

            # Add Information about their keys
            access_keys = iam_client.list_access_keys(UserName=username)
            for access_key in access_keys['AccessKeyMetadata']:
                currentdate = date.today()
                last_used_info = iam_client.get_access_key_last_used(AccessKeyId=access_key['AccessKeyId'])
                latest_access = last_used_info['AccessKeyLastUsed'].get('LastUsedDate', access_key['CreateDate'].date())
                key_status = access_key['Status']
                active_days = currentdate - access_key['CreateDate'].date()
                key_id = access_key['AccessKeyId']
                row.extend([key_id, key_status, str(active_days.days), latest_access.strftime('%Y/%m/%d')])

            result.append(row)

    return result


CSV_HEADER = [
    'AccountName',
    'AccountId',
    'UserName',
    'LastLogin',
    'Owner',
    'App',
    'Key1_Id',
    'Key1_Status',
    'Key1_AgeDays',
    'Key1_LastUsed',
    'Key2_Id',
    'Key2_Status',
    'Key2_AgeDays',
    'Key2_LastUsed'
]

if __name__ == '__main__':

    # Check arguments
    only_current_account = False
    if len(sys.argv) > 1:
        if sys.argv[1] == 'current':
            only_current_account = True
        else:
            print('[ERROR] Wrong arguments. Only "current" is available.')
            exit(0)

    print(main_client.get_caller_identity())
    if only_current_account:
        all_accounts = [ [main_client.get_caller_identity().get('Account'), 'current'] ]
        print(f"Checking current account...")
    else:
        print("Checking accounts in the organization....")
        all_accounts = get_accounts_id_organization(exclude=IGNORE_ACCOUNTS)
    print('Accounts:', len(all_accounts), '===>', all_accounts)


    # Iterate through each account and call the `list_account_users` function
    iam_by_group = {}
    for account_info in all_accounts:
        account_id, account_name = account_info
        print('>>>> Checking... ', account_info)

        # Group id for the csv creation
        group_id = '-'.join(account_name.split('-')[:2])

        if only_current_account or account_name in ('ONT CORE'): 
            lz_session = boto3.Session()
            role_to_assume = None
        else:
            lz_session = new_lz_session.client('sts')
            role_to_assume = ROLE_TO_ASSUME_DAG.replace('$ID',account_id)       # New LandingZone
            if account_name == account_name.upper():
                lz_session = old_lz_session.client('sts')
                role_to_assume = ROLE_TO_ASSUME_CORE.replace('$ID',account_id)  # Old LandingZone

        iam_list = generate_iam_keys_report(lz_session, account_info, role_arn=role_to_assume)
        if iam_list is None:
            continue # Error

        current = iam_by_group.get(group_id,[])
        current.extend(iam_list)
        iam_by_group[group_id] = current


    for group_id in iam_by_group:
        filename = f"iam_report_{group_id}.csv"
        with open(filename, 'w') as csv_file:
            wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
            wr.writerow(CSV_HEADER)
            for row in iam_by_group[group_id]:
                wr.writerow(row)

    print("Done")