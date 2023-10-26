# Returns statistics about a given job (summary of exit states within the given time frame).
# Uses environment for authentication to AWS.
#
# v 1.0 2023-10-25 by Simone Bazzi.

# Arguments
#   -n: Job name
#   -s: Start date
#   -e: End date
#   -r: Region (optional)

import boto3
import argparse
from datetime import datetime



argParser = argparse.ArgumentParser()
argParser.add_argument("-n", "--name", help="job name")
argParser.add_argument("-s", "--start", help="start date (YYYY-MM-DD)")
argParser.add_argument("-e", "--end", help="end date (YYYY-MM-DD)")
argParser.add_argument("-r", "--region", help="AWS region")

args = argParser.parse_args()

if args.name == None or args.start == None or args.end == None:
    exit()

job = args.name
start = datetime.strptime(args.start, '%Y-%m-%d').date()
end = datetime.strptime(args.end, '%Y-%m-%d').date()

try:
    region = args.region
    setregion = boto3.setup_default_session(region_name = region)
except:
    pass

count = 0
nexttoken = None
states = []

glue_client = boto3.client('glue')


while True:

    if nexttoken == None:
        response = glue_client.get_job_runs(JobName = job)

    else:
        response = glue_client.get_job_runs(JobName = job, NextToken = nexttoken)

    for x in response['JobRuns']:
        if x['StartedOn'].date() >= start and x['StartedOn'].date() <= end:
            states.append(x['JobRunState'])

    try:
        nexttoken = response['NextToken']
    except:
        nexttoken = None
    count += 1

    if (nexttoken == None and count > 0) or x['StartedOn'].date() <= start:
        break

states_sorted = sorted(states)

states_stats = []

ssindex = 0
for y in states_sorted:
    if ssindex == 0:
        states_stats = [[y,1]]
        ssindex += 1
    elif ssindex > 0 and states_stats[ssindex - 1][0] == y:
        states_stats[ssindex - 1][1] += 1
    else:
        states_stats.append([y,1])
        ssindex += 1

print(f'\nJob name: {job}\nStart date: {start}\nEnd date: {end}\n\nStates\n-----')
for out in states_stats:
    print(f'{out[0]:10}: {out[1]:6}')
