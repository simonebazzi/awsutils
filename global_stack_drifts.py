# Outputs drift status for all Coudformation stacks in a coherent state.
# Optionally performs a new drift detection on the fly.
# Uses environment for authentication to AWS.
#
# v 1.0 2023-11-07 by Simone Bazzi.

import boto3
import argparse
import time

argParser = argparse.ArgumentParser()
argParser.add_argument("-d", "--detect", help="detect drifts (any value to enable / disabled by default)")

args = argParser.parse_args()

detect = args.detect

ec2client = boto3.client('ec2')

response = ec2client.describe_regions()

regions = []

print(f"\n*** START ***")
print(f"\nPlease note: at this time we only consider stacks in the following states:\n - CREATE_COMPLETE\n - UPDATE_COMPLETE\n - IMPORT_COMPLETE\n - ROLLBACK_COMPLETE\n - UPDATE_ROLLBACK_COMPLETE\n - REVIEW_IN_PROGRESS\n - IMPORT_ROLLBACK_COMPLETE")

for x in response['Regions']:
    regions.append(x['RegionName'])

stacks = []

print(f"\n Extracting stacks.")

for reg in regions:

    try:

        setregion = boto3.setup_default_session(region_name = reg)

        cfclient = boto3.client('cloudformation')

        token = 'T'

        while True:

            try: response = cfclient.list_stacks(StackStatusFilter = ['CREATE_COMPLETE', 'UPDATE_COMPLETE', 'IMPORT_COMPLETE', 'ROLLBACK_COMPLETE', 'UPDATE_ROLLBACK_COMPLETE', 'REVIEW_IN_PROGRESS', 'IMPORT_ROLLBACK_COMPLETE'], NextToken = token)
            except:
                try: response = cfclient.list_stacks(StackStatusFilter = ['CREATE_COMPLETE', 'UPDATE_COMPLETE', 'IMPORT_COMPLETE', 'ROLLBACK_COMPLETE', 'UPDATE_ROLLBACK_COMPLETE', 'REVIEW_IN_PROGRESS', 'IMPORT_ROLLBACK_COMPLETE'])
                except: break
            
            for x in response['StackSummaries']:
                stacks.append((reg,x['StackName']))

            try: token = response['NextToken']
            except: break 

    except:
        pass        

if detect != None:

    print(f"\nActivating new drift detection.")

    driftswaitlist = []

    for st in stacks:

        setregion = boto3.setup_default_session(region_name = st[0])
        
        cfclient = boto3.client('cloudformation')

        try:
            response = cfclient.detect_stack_drift(StackName = st[1])
            driftswaitlist.append((st[0], response['StackDriftDetectionId']))
        except:
            pass

    while driftswaitlist != []:

        for x in driftswaitlist:

            setregion = boto3.setup_default_session(region_name = x[0])

            cfclient = boto3.client('cloudformation')

            response = cfclient.describe_stack_drift_detection_status(StackDriftDetectionId = x[1])

            if response['DetectionStatus'] != 'DETECTION_IN_PROGRESS':
                driftswaitlist.remove((x[0], x[1]))

        time.sleep(.1)

print(f"\nFinding drifted resources.")

drifts = []

for st in stacks:

    setregion = boto3.setup_default_session(region_name = st[0])
    
    cfclient = boto3.client('cloudformation')

    token = 'T'

    while True:

        try: response = cfclient.describe_stack_resource_drifts(StackName = st[1], StackResourceDriftStatusFilters = ['MODIFIED', 'DELETED', 'NOT_CHECKED'], NextToken = token)
        except:
            try: response = cfclient.describe_stack_resource_drifts(StackName = st[1], StackResourceDriftStatusFilters = ['MODIFIED', 'DELETED', 'NOT_CHECKED'])
            except: break
        
        for x in response['StackResourceDrifts']:
            drifts.append((st[0], st[1], x['PhysicalResourceId'], x['ResourceType'], x['StackResourceDriftStatus'], x['Timestamp']))

        try: token = response['NextToken']
        except: break 

print(f"\nGenerating output.")

print("\n{},{},{},{},{},{},{}".format("Region","Stack","Resource","Type","Status","Date","Time"))
for dr in drifts:
    print("{},{},{},{},{},{},{}".format(dr[0], dr[1], dr[2], dr[3], dr[4], dr[5].strftime("%Y-%m-%d"), dr[5].strftime("%H:%M:%S")))

print(f"\n*** END ***")
