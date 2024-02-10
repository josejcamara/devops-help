#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" AWS IAM management """

import argparse
import spreadsheet as xls

# import click


def check_arguments():
    """ Alternative arguments with argparse """
    parser = argparse.ArgumentParser(description='AWS IAM management')
    parser.add_argument('action', choices=["list_users", "set_tag"])
    parser.add_argument('-f', '--filename')
    parser.add_argument('-v', '--verbose')

    args = parser.parse_args()
    return args


# @click.command()
# @click.argument('action', default="")
# @click.option('--filename', prompt='Filename', help='The person to greet.')
# def main(action, filename=None):
#     """Simple program that greets NAME for a total of COUNT times."""
#     print("ssss")

def list_iam_users(output="iam_users.xls"):
    """ List of iam users """
    xls1 = xls.Spreadsheet()

    xid1 = "sheet1"
    xls1.add_sheet(xid1)

    data1 = [["Title1", "Title2"], ["row1_col1", "row1_col2"]]
    xls1.set_sheet_data(xid1, data1)

    xls1.save(output)
    print(f"Result saved in {output}")


if __name__ == "__main__":
    opt = check_arguments()

    if opt.action == "list_users":
        list_iam_users()
    elif opt.action == "set_tag":
        print("Coming....")
    else:
        print("Invalid option")

    # main()
