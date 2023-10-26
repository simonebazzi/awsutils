# Cloudwatch statistics for all available regions. Retention days + Gbytes used.
# Uses environment for authentication to AWS.
#
# v 1.0 2023-10-25 by Simone Bazzi.

import boto3

ec2client = boto3.client('ec2')

regions = ec2client.describe_regions()

unordered_logs = []

for reg in regions['Regions']:
    region = reg['RegionName']
    setregion = boto3.setup_default_session(region_name = region)

    logsclient = boto3.client('logs')
    token = 'T'

    while token != None:

        try:
            if token == 'T':
                response = logsclient.describe_log_groups()
                # print(response)
            else:
                response = logsclient.describe_log_groups(nextToken=token)
                # print(response)
        except:
            break

        for x in response['logGroups']:
            groupname =x['logGroupName']
            try:
                retention = str(x['retentionInDays'])
            except:
                retention = 'Forever'
            storedbytes = x['storedBytes']
            unordered_logs.append((region,groupname,retention,storedbytes))

        try:
            token = response['nextToken']
        except:
            token = None
        
ordered_logs = sorted(unordered_logs,key=lambda item: item[3],reverse=True)

print('\n{:10} {:5} {:15} {}'.format('Gbytes','Days','Region','Log group name'))
print('{:10} {:5} {:15} {}'.format('------','----','------','--------------'))

tot_logfiles = 0
tot_gigs = 0

for x in ordered_logs:

    xr = x[0]
    xn = x[1]
    xd = x[2]
    xg = x[3] / (1024 * 1024 * 1024)
    print(f'{xg:10.2f} {xd:10} {xr:15} {xn}')

    tot_logfiles += 1
    tot_gigs += xg

print(f'\nTotal log files: {tot_logfiles}. Total Gbytes used: {tot_gigs:6.2f}.')