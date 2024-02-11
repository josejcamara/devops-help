#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto3

# Create an Organizations client, ensuring proper credentials and permissions
client = boto3.client('organizations')

def get_account_list(exclude=[], debug=False):
    """ 
        Returns the list of [account_id, account_name] in the organization you are logged into.
        It needs new_lz_session permissions
    """

    # Use a paginator to efficiently handle potentially large result sets
    paginator = client.get_paginator('list_accounts')

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

