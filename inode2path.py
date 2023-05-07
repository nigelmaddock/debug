#!/usr/bin/env python3

"""
ONTAP REST API Sample Scripts

This script was developed by NetApp to help demonstrate NetApp technologies.
This script is not officially supported as a
standard NetApp product.

Purpose: This Module will provide an output of file paths from a number of inodes

Usage: inode2path.py [-h] -c CLUSTER [-u API_USER] [-p API_PASS]
inode2path.py: the following arguments are required: -c/--cluster,
-u admin, -p/--password

Copyright (c) 2020 NetApp, Inc. All Rights Reserved.

Licensed under the BSD 3-Clause “New” or Revised” License (the "License");
you may not use this file except in compliance with the License.

You may obtain a copy of the License at
https://opensource.org/licenses/BSD-3-Clause
"""
import base64
import argparse
import logging
from getpass import getpass
#import texttable as tt
import requests
import urllib3 as ur
ur.disable_warnings()
import re
import json

def inode2path(cluster: str, headers_inc: str, vserver: str, volume: str, inode_number: str):
    endpoint = "api/private/cli/volume/file/inode"

    url = "https://{}/{}?vserver={}&volume={}&inode-number={}".format(cluster, endpoint, vserver,volume,inode_number)

    response = requests.get(
        url,
        headers=headers_inc,
        verify=False)

    if (response.status_code == 200):
        data = json.loads(response.text)
        return data['records'][0]['file_path']


def get_system_node_power(cluster: str, headers_inc: str):
    "Get system node power CLI command"
    endpoint = "api/private/cli/system/node/power"
    url = "https://{}/{}?fields=node,status".format(
        cluster, endpoint)
    print(url)
    response = requests.get(url, headers=headers_inc, verify=False)
    print (response.json())
    return response.json()


def get_system_node(cluster: str, headers_inc: str):
    "Display system node status output"
    ctr = 0
    print()
    tmp = dict(get_system_node_power(cluster, headers_inc))
    vols = tmp['records']
    tab = tt.Texttable()
    header = ['Node', 'Status']
    tab.header(header)
    tab.set_cols_align(['c', 'c'])
    for eventlist in vols:
        ctr = ctr + 1
        node = eventlist['node']
        status = eventlist['status']
        row = [node, status]
        tab.set_cols_width([20, 20])
        tab.add_row(row)
        tab.set_cols_align(['c', 'c'])
    setdisplay = tab.draw()
    print(setdisplay)
    print("\n Number of records displayed: {}".format(ctr))


def parse_args() -> argparse.Namespace:
    """Parse the command line arguments from the user"""
    parser = argparse.ArgumentParser(
        description="This script will list system fru-check command in CLI")
    parser.add_argument(
        "-c", "--cluster", required=True, help="API server IP:port details")
    parser.add_argument(
        "-u",
        "--api_user",
        default="admin",
        help="API Username")
    parser.add_argument("-p", "--api_pass", help="API Password")
    parser.add_argument("-i", "--input_file", help="Input filename from ndmpdump", required=True)
    parser.add_argument("-o", "--output_file", help="Output filename of paths", required=True)

    parsed_args = parser.parse_args()
    # collect the password without echo if not already provided
    if not parsed_args.api_pass:
        parsed_args.api_pass = getpass()
    return parsed_args


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)5s] [%(module)s:%(lineno)s] %(message)s",
    )
    ARGS = parse_args()
    BASE64STRING = base64.encodebytes(
        ('%s:%s' %
         (ARGS.api_user, ARGS.api_pass)).encode()).decode().replace('\n', '')
    headers = {
        'authorization': "Basic %s " % BASE64STRING,
        'content-type': "application/json",
        'accept': "application/json"
    }
    


#    inode2path(ARGS.cluster, headers, "norton", "kenny_iso", "96")
    
    volume = ''

    with open(ARGS.input_file, 'r') as ndmpFile:
        for line in ndmpFile:
            #print (line.rstrip())
            x = re.search("creating \"/(.+)/(.+)/\.\./\S+\" snapshot.",line.rstrip())
            if (x):
                vserver = x.group(1)
                volume = x.group(2)

            x = re.search("Encountered WAFL data inconsistency due to disk errors while processing inode (\d+)", line.rstrip())
            if (x):
                inode = x.group(1)
                path = inode2path(ARGS.cluster, headers, vserver, volume, inode)
                print (inode + "," + path)
