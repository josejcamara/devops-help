#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" AWS Utils management """

# pylint: disable=import-error
# pyright: reportMissingImports=false, reportMissingModuleSource=false

import os
import yaml
import argparse
# import click
import boto3

# MyLibraries
import spreadsheet as xls
import iam

CFG_FILENAME = "aws.yml"


def check_arguments():
    """ Alternative arguments with argparse """
    parser = argparse.ArgumentParser(description='AWS IAM management')
    parser.add_argument('action', choices=["list_users", "set_tag"])
    parser.add_argument('-f', '--filename')
    parser.add_argument('-v', '--verbose')

    args = parser.parse_args()
    return args

def get_account_parent_filtered(acc_name):
    """ Tries to split the accounts according their parent """
    # Attempt to organise old-lz
    old_account_alias = "ont-core"
    mc_account_alias = "MC-ONT-SECURITY"
    cwg_account_alias = "Unknown"

    parent = None
    if acc_name == acc_name.upper():
        if acc_name.startswith('MC-'):
            parent = mc_account_alias
        else:
            parent = old_account_alias
    elif acc_name.startswith('ont-cwg'):
        parent = cwg_account_alias

    return parent


def generate_accounts_config():
    """ If you don't have a aws.yml file, it will try to create one for you """
    caller_account_alias = boto3.client('iam').list_account_aliases()['AccountAliases'][0]
    ls_acc = get_accounts_id_organization()

    data = dict()
    for acc_id, acc_name in ls_acc:
        parent = get_account_parent_filtered(acc_name)
        if parent is None:
            parent = caller_account_alias
        if not parent in data:
            data[parent] = []
        data[parent].append(','.join([acc_id,acc_name]))

    with open(CFG_FILENAME, 'w') as outfile:
        yaml.dump(data, outfile, default_flow_style=False)


def read_accounts_config():
    cfg = {}
    with open(CFG_FILENAME) as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)

    return cfg

# @click.command()
# @click.argument('action', default="")
# @click.option('--filename', prompt='Filename', help='The person to greet.')
# def main(action, filename=None):
#     """Simple program that greets NAME for a total of COUNT times."""
#     print("ssss")

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

def list_iam_users(output="iam_users.xls"):
    """ List of iam users """
    xls1 = xls.Spreadsheet()

    xid1 = "sheet1"
    xls1.add_sheet(xid1)

    data1 = [["Title1", "Title2"], ["row1_col1", "row1_col2"]]
    xls1.set_sheet_data(xid1, data1)

    xls1.save(output)
    print(f"Result saved in {output}")


def main(options):
    """ Main method """
    if not os.path.isfile(CFG_FILENAME):
        print(f"No config file '{CFG_FILENAME}' found. Generating one for you from... {default_account_alias} - {default_account_id}")
        generate_accounts_config()

    accounts_cfg = read_accounts_config()

    if options.action == "list_users":
        list_iam_users()
    elif options.action == "set_tag":
        print("Coming....")
    else:
        print("Invalid option")

if __name__ == "__main__":
    opt = check_arguments()

    default_user = boto3.client('sts').get_caller_identity().get('Arn')
    default_account_id = boto3.client('sts').get_caller_identity().get('Account')
    default_account_alias = boto3.client('iam').list_account_aliases()['AccountAliases'][0]
    print("#"*50)
    print("ATTENTION:")
    print(f"You are running this script as '{default_user}' from '{default_account_alias} - {default_account_id}' ")
    print("#"*50)

    answer = ""
    while answer.lower() not in ["y", "n"]:
        print('OK to continue??')
        answer = input()
    if answer.lower() != 'y':
        exit(0)

    main(opt)
