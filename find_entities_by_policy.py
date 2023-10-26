# Report which IAM entities have a given policy attached (passed as argument)
# Uses environment for authentication to AWS.
#
# v 1.0 2023-10-25 by Simone Bazzi.

# Arguments
#   -p: Name or ARN of the policy

import boto3
import argparse

argParser = argparse.ArgumentParser()
argParser.add_argument("-p", "--policy", help="policy name or ARN")

args = argParser.parse_args()

if args.policy == None:
    exit()

policy = args.policy

iamclient = boto3.client('iam')
stsclient = boto3.client('sts')
accountid = stsclient.get_caller_identity()['Account']

roles_list = []
users_list = []
groups_list = []

marker = None

while True:
    if marker is None:
        response = iamclient.list_roles()
    else:
        response = iamclient.list_roles(Marker = marker)
    
    for x in response['Roles']:
        roles_list.append(x['RoleName'])
    
    if response['IsTruncated'] == False:
        break
    else:
        marker = response['Marker']

marker = None

while True:
    if marker is None:
        response = iamclient.list_groups()
    else:
        response = iamclient.list_groups(Marker = marker)
    
    for x in response['Groups']:
        groups_list.append(x['GroupName'])
    
    if response['IsTruncated'] == False:
        break
    else:
        marker = response['Marker']

marker = None

while True:
    if marker is None:
        response = iamclient.list_users()
    else:
        response = iamclient.list_users(Marker = marker)
    
    for x in response['Users']:
        users_list.append(x['UserName'])
    
    if response['IsTruncated'] == False:
        break
    else:
        marker = response['Marker']

roles_matched = []

for x in roles_list:

    marker = None

    while True:
        if marker is None:
            response = iamclient.list_attached_role_policies(RoleName = x)
        else:
            response = iamclient.list_attached_role_policies(RoleName = x, Marker = marker)
        
        for xx in response['AttachedPolicies']:
            if xx['PolicyName'] == policy or xx['PolicyArn'] == policy:
                roles_matched.append(x)
        
        if response['IsTruncated'] == False:
            break
        else:
            marker = response['Marker']

groups_matched = []

for x in groups_list:

    marker = None

    while True:
        if marker is None:
            response = iamclient.list_attached_group_policies(GroupName = x)
        else:
            response = iamclient.list_attached_group_policies(GroupName = x, Marker = marker)
        
        for xx in response['AttachedPolicies']:
            if xx['PolicyName'] == policy or xx['PolicyArn'] == policy:
                groups_matched.append(x)
        
        if response['IsTruncated'] == False:
            break
        else:
            marker = response['Marker']

users_matched = []

for x in users_list:

    marker = None

    while True:
        if marker is None:
            response = iamclient.list_attached_user_policies(UserName = x)
        else:
            response = iamclient.list_attached_user_policies(UserName = x, Marker = marker)
        
        for xx in response['AttachedPolicies']:
            if xx['PolicyName'] == policy or xx['PolicyArn'] == policy:
                users_matched.append(x)
        
        if response['IsTruncated'] == False:
            break
        else:
            marker = response['Marker']

print(f'\nPolicy {policy} is currently attached to the following entities in account {accountid}.')
print(f'\nRoles:\n')

if roles_matched == []:
    print(f'\t* No match *')
else:
    for x in roles_matched:
        print(f'\t{x}')

print(f'\nGroups:\n')

if groups_matched == []:
    print(f'\t* No match *')
else:
    for x in groups_matched:
        print(f'\t{x}')

print(f'\nUsers:\n')

if users_matched == []:
    print(f'\t* No match *')
else:
    for x in users_matched:
        print(f'\t{x}')

print(f'\n')
