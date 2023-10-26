# Search for a resource name (or part of it) in all cloudformation stacks in all regions.
# Uses environment for authentication to AWS.
#
# v 1.0 2023-10-24 by Simone Bazzi.

# Arguments:
#   -r: resource's name (or part of it)

import boto3
import argparse
import pprint

argParser = argparse.ArgumentParser()
argParser.add_argument("-r", "--resource", help="resource to search")

args = argParser.parse_args()

if args.resource == None:
    exit()

print(f"\n*** BEGIN SEARCH ***")

pp = pprint.PrettyPrinter(indent=2, compact=False, sort_dicts=False)
resource = args.resource

ec2client = boto3.client('ec2')

regions = ec2client.describe_regions()

for reg in regions['Regions']:
    region = reg['RegionName']
    setregion = boto3.setup_default_session(region_name = region)
    cfclient = boto3.client('cloudformation')

    print(f'\nRegion: {region}\n')

    stack_list = []
    token = 'T'

    while token != None:

        try:
            if token == 'T':
                response = cfclient.list_stacks()
            else:
                response = cfclient.list_stacks(NextToken = token)

            for x in response['StackSummaries']:
                if x['StackStatus'] not in ['CREATE_IN_PROGRESS','CREATE_FAILED','DELETE_IN_PROGRESS','DELETE_COMPLETE']:
                    stack_list.append(x['StackName'])
        except:
            pass

        try:
            token = response['NextToken']
        except:
            token = None
    
    count_stacks = 0
    count_resources = 0

    for x in stack_list:
        count_stacks += 1

        token = 'T'

        while token != None:
            if token == 'T':
                response = cfclient.list_stack_resources(StackName = x)
            else:
                response = cfclient.list_stack_resources(StackName = x, NextToken = token)
            
            for xx in response['StackResourceSummaries']:
        
                try:
                    if resource in xx['PhysicalResourceId']:
                        r = cfclient.describe_stack_resource(StackName = x, LogicalResourceId = xx['LogicalResourceId'])
                        pp.pprint(r['StackResourceDetail'])
                        print("")
                    count_resources += 1
                except:
                    pass

            try:
                token = response['NextToken']
            except:
                token = None

    print(f'(Stacks evaluated: {count_stacks}. Resources evaluated: {count_resources}.)')

print(f"\n*** END SEARCH ***\n")
