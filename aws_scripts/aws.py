#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" AWS Utils management """

# pylint: disable=import-error
# pyright: reportMissingImports=false, reportMissingModuleSource=false

import os
import yaml
import argparse
import boto3

# MyLibraries
import spreadsheet as xls
import iam
import organization as org

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

    old_role = 'administrator'
    dag_role = 'DAG-AWS-ont-aws-admin'
    cwg_role = '?'
    mc_role = '?'
    # --

    parent = None
    role = dag_role
    if acc_name == acc_name.upper():
        if acc_name.startswith('MC-'):
            parent = mc_account_alias
            role = mc_role
        else:
            parent = old_account_alias
            role = old_role

    elif acc_name.startswith('ont-cwg'):
        parent = cwg_account_alias
        role = cwg_role

    return (parent,role)


def generate_accounts_config():
    """ 
        If you don't have a aws.yml file, it will try to create one for you 
        Your .aws/credentials profile_name has to match the aws.yml groups_id
    """
    caller_account_alias = boto3.client('iam').list_account_aliases()['AccountAliases'][0]

    ls_acc = org.get_account_list()

    data = dict()
    for acc_id, acc_name in ls_acc:
        parent, role = get_account_parent_filtered(acc_name)
        if parent is None:
            parent = caller_account_alias

        if not parent in data:
            data[parent] = []

        data[parent].append(','.join([acc_id,acc_name, role]))

    with open(CFG_FILENAME, 'w') as outfile:
        yaml.dump(data, outfile, default_flow_style=False)


def read_accounts_config():
    cfg = {}
    with open(CFG_FILENAME) as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)

    return cfg

def get_iam_users_by_account(accounts_groups, output="iam_users.xls"):
    """ List of iam users """
    users_by_account = dict()

    for grp_id in accounts_groups:
        try:
            session = boto3.Session(profile_name=grp_id)
            print(f"Creating session with profile {grp_id}")
        except:
            print(f"[ERROR] Profile {grp_id} not found in your aws configuration")
            continue

        client = session.client('sts')
        for grp_row in accounts_groups[grp_id]:
            account_info = grp_row.split(',')
            account_name = account_info[1]
            print(f">> Getting users from {account_name}")
            users_by_account[account_name] = iam.get_iam_user_list(client, account_info)

    return users_by_account


def create_xls(data_dc, filename):
    if filename is None:
        filename = "output.xlsx"

    my_xls = xls.Spreadsheet()
    sheets_dc = dict()
    sheets_header = [
        'AccountName',
        'AccountId',
        'Username',
        'ConsoleLogin',
        'Tag_Owner',
        'Tag_App',
        'KeyNumber',
        'KeyId',
        'KeyStatus',
        'DaysActive',
        'LastDayUsed'
        ]

    for acc_name, user_list in data_dc.items():
        acc_group = '-'.join(acc_name.split('-')[:-1])   # Will group by account_name prefix
        
        if user_list is None:
            user_list = [['No Data']]

        if not acc_group in sheets_dc:
            user_list.insert(0, sheets_header)
            sheets_dc[acc_group] = my_xls.add_sheet(acc_group, user_list)
        else:
            my_xls.add_sheet_data(acc_group, user_list) 

    my_xls.save(filename)
    print(f"Result saved in {filename}")




def main(options):
    """ Main method """
    if not os.path.isfile(CFG_FILENAME):
        print(f"No config file '{CFG_FILENAME}' found. Generating one for you from... {default_account_alias} - {default_account_id}")
        generate_accounts_config()

    accounts = read_accounts_config()

    if options.action == "list_users":
        users_dc = get_iam_users_by_account(accounts)
        create_xls(users_dc, options.filename)
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
