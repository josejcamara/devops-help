#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto3
import datetime

region_name = 'eu-west-1'
# client = new_session.client('iam', config=boto3.session.Config(region_name=region_name))


def get_iam_user_list(caller_sts, account_info, region_name='eu-west-1', debug=False):
    """ Returns the list of rows with the iam_users information in the account provided """ 
    account_id, account_name, role_name = account_info
    role_arn = f"arn:aws:iam::{account_id}:role/{role_name}"

    try:
        stsresponse = caller_sts.assume_role(RoleArn=role_arn, RoleSessionName='newsession')
    except Exception as e:
        print(f"[ERROR] {caller_sts.get_caller_identity().get('Arn')} was unable to assume role {role_arn} in {account_name}.")
        return None

    new_session = boto3.Session(aws_access_key_id=stsresponse['Credentials']['AccessKeyId'],
                        aws_secret_access_key=stsresponse['Credentials']['SecretAccessKey'],
                        aws_session_token=stsresponse['Credentials']['SessionToken'])

    client = new_session.client('iam', config=boto3.session.Config(region_name=region_name))

    result = []
    paginator = client.get_paginator('list_users')
    for response in paginator.paginate():
        for user in response['Users']:
            row = []
            username = user['UserName']
            if debug:
                print(f"Account ID: {account_id} - User Name: {username}")

            last_login = check_console_password_activity(client, username)

            owner_tag, app_tag = '-', '-'
            userTags = client.list_user_tags(UserName=username)
            for tag in userTags['Tags']:
                if tag['Key'] == 'Owner': owner_tag = tag['Value']
                if tag['Key'] == 'AppName': app_tag = tag['Value']

            # Add Information about the user
            user_info = [account_name, account_id, username, last_login, owner_tag, app_tag]
            # row.extend([account_name, account_id, username, last_login, owner_tag, app_tag])

            # Add Information about their keys
            access_keys = client.list_access_keys(UserName=username)
            if len(access_keys['AccessKeyMetadata']) == 0:
                row = user_info[:]
                row.append('NO KEYS')
                result.append(row)
            else:
                nkey = 0
                for access_key in access_keys['AccessKeyMetadata']:
                    nkey += 1
                    row = user_info[:]
                    currentdate = datetime.date.today()
                    last_used_info = client.get_access_key_last_used(AccessKeyId=access_key['AccessKeyId'])
                    latest_access = last_used_info['AccessKeyLastUsed'].get('LastUsedDate', access_key['CreateDate'].date())
                    key_status = access_key['Status']
                    active_days = currentdate - access_key['CreateDate'].date()
                    key_id = access_key['AccessKeyId']
                    row.extend([f"Key{nkey}", key_id, key_status, str(active_days.days), latest_access.strftime('%Y/%m/%d')])

                    result.append(row)

    return result

def check_console_password_activity(client, username, debug=False):
    """ Returns the last time the user accessed to the console or N/A if never """
    try:
        login_profile = client.get_login_profile(UserName=username)
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

