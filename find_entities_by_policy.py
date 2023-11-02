# Report which IAM entities have a given policy attached (passed as argument)
# Uses environment for authentication to AWS.
#
# v 1.0 2023-10-25 by Simone Bazzi.

# Arguments
#   -p: Name or ARN of the policy

import boto3
import argparse
# import pprint

argParser = argparse.ArgumentParser()
argParser.add_argument("-p", "--policy", help="policy name or ARN")

args = argParser.parse_args()

if args.policy == None:
    exit()

policy = args.policy

iamclient = boto3.client('iam')
stsclient = boto3.client('sts')
accountid = stsclient.get_caller_identity()['Account']

# pp = pprint.PrettyPrinter(indent=2, compact=False, sort_dicts=False)

groups = []
users = []
roles = []

try:
    response = iamclient.list_entities_for_policy(PolicyArn = policy)
except:
    policy = 'arn:aws:iam::aws:policy/' + policy
    response = iamclient.list_entities_for_policy(PolicyArn = policy)

for x in response['PolicyGroups']:
    groups.append(x)
for x in response['PolicyUsers']:
    users.append(x)
for x in response['PolicyRoles']:
    roles.append(x)

loopchecker = response['IsTruncated']

while loopchecker is True:

    marker = response['Marker']

    response = iamclient.list_entities_for_policy(PolicyArn = policy, Marker = marker, MaxItems = 1)

    for x in response['PolicyGroups']:
        groups.append(x)
    for x in response['PolicyUsers']:
        users.append(x)
    for x in response['PolicyRoles']:
        roles.append(x)

    loopchecker = response['IsTruncated']

print(f"\nPolicy {policy} is currently attached to the following entities in account {accountid}.")
print(f"\nRoles:\n")

if roles == []:
    print(f"\t* No match *")
else:
    print("\t{}\t\t\t{}".format("Role ID", "Role name"))
    for x in roles:
        print(f"\t{x['RoleId']}\t{x['RoleName']}")

print(f"\nGroups:\n")

if groups == []:
    print(f"\t* No match *")
else:
    print("\t{}\t\t{}".format("Group ID", "Group name"))
    for x in groups:
        print(f"\t{x['GroupId']}\t{x['GroupName']}")

print(f"\nUsers:\n")

if users == []:
    print(f"\t* No match *")
else:
    print("\t{}\t\t\t{}".format("User ID", "User name"))
    for x in users:
        print(f"\t{x['UserId']}\t{x['UserName']}")

print(f"\n")
