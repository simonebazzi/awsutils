# Extract statistics about jobs from all regions.
# Uses environment for authentication to AWS.
#
# v 1.0 2023-10-25 by Simone Bazzi.

import boto3

ec2client = boto3.client('ec2')

regions = ec2client.describe_regions()

joblist = []

for reg in regions['Regions']:
    region = reg['RegionName']
    setregion = boto3.setup_default_session(region_name = region)

    glue_client = boto3.client('glue')

    token = 'T'

    while token != None:

        try:
            if token == 'T':
                response = glue_client.list_jobs()
            else:
                response = glue_client.list_jobs(NextToken = token)


            for x in response['JobNames']:
                glue_version = glue_client.get_job(JobName=x)['Job']['GlueVersion']
                try:
                    last_exec = glue_client.get_job_runs(JobName=x,MaxResults=1)['JobRuns'][0]['StartedOn'].strftime("%Y-%m-%d")
                except:
                    last_exec = 'unknown'
                joblist.append([region,last_exec,glue_version,x])

        except:
            pass

        try:
            token = response['NextToken']
        except:
            token = None

print("\n{:15}{:15}{:8}{}".format("Region", "Last exec", "Version", "Job name"))
print("{:15}{:15}{:8}{}".format("------", "---------", "-------", "--------"))
for x in joblist:
    print(f'{x[0]:15}{x[1]:15}{x[2]:8}{x[3]}')
