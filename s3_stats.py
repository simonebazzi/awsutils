# Statistics about S3 buckets in accounts so you will quickly have an
# overview of main configuration parameters and resource consumption.
# Uses environment for authentication to AWS.
#
# v 1.0 2023-11-10 by Simone Bazzi.

import boto3
from datetime import date
from datetime import timedelta

# rangestart = str(date.today() - timedelta(days=1)) + "T00:00"
# rangeend = str(date.today() - timedelta(days=1)) + "T01:00"
rangestart = str(date.today() - timedelta(days=1)) + "T00:00"
rangeend = str(date.today()) + "T00:00"

separator = ","

s3client = boto3.client('s3')

buckets_list = []

response = s3client.list_buckets()

print(f"\n*** PROGRAM START ***\n")

waitplease = 0

for x in response['Buckets']:
    bucket = x['Name']
    region = s3client.get_bucket_location(Bucket=bucket)['LocationConstraint']

    if region == None: region = "us-east-1"
    
    setregion = boto3.setup_default_session(region_name = region)
    s3client = boto3.client('s3')
    cwclient = boto3.client('cloudwatch')

    resp = s3client.get_bucket_versioning(Bucket=bucket)
    try: versioning = resp['Status']
    except: versioning = "Disabled"
    try: mfa_delete = resp['MFADelete']
    except: mfa_delete = "Disabled"

    resp = s3client.get_bucket_encryption(Bucket=bucket)
    encryption = ""
    count = 0
    for x in resp['ServerSideEncryptionConfiguration']['Rules']:
        encryption += x['ApplyServerSideEncryptionByDefault']['SSEAlgorithm']
        count += 1
        if count > 1:
            encryption += ","
    enc = [encryption]

    try:
        resp = s3client.get_bucket_policy_status(Bucket=bucket)
        policy = resp['PolicyStatus']['IsPublic']
    except:
        policy = "N/A"

    try:
        resp = s3client.get_bucket_replication(Bucket=bucket)
        for x in resp['ReplicationConfiguration']['Rules']:

            try: rep_id = x['ID']
            except: rep_id = "-"

            try: rep_prefix = x['Prefix']
            except: rep_prefix = "-"

            try: rep_status = x['Status']
            except: rep_status = "-"

            try: rep_dstbukt = x['Destination']['Bucket']
            except: rep_dstbukt = "-"

            try: rep_dstacct = x['Destination']['Account']
            except: rep_dstacct = "-"

            try: rep_dstcls = x['Destination']['StorageClass']
            except: rep_dstcls = "-"

            try: rep_delmrk = x['DeleteMarkerReplication']
            except:rep_delmrk = {'Status': 'N/A'}

            replication = [rep_id,rep_prefix,rep_status,rep_dstbukt,rep_dstacct,rep_dstcls,rep_delmrk]
    except:
        replication = []
    
    resp = cwclient.get_metric_data(
        MetricDataQueries=[
                {
                    'Id': 'bucketSizeBytes',
                    'MetricStat': {
                        'Metric': {
                            'Namespace': 'AWS/S3',
                            'MetricName': 'BucketSizeBytes',
                            'Dimensions': [
                                {
                                    'Name': 'BucketName',
                                    'Value': bucket
                                },
                                {
                                    'Name': 'StorageType',
                                    'Value': 'StandardStorage'
                                }
                            ]
                        },
                    'Period': 60,
                    'Stat': 'Average'
                    }
                },
                {
                    'Id': 'numberOfObjects',
                    'MetricStat': {
                        'Metric': {
                            'Namespace': 'AWS/S3',
                            'MetricName': 'NumberOfObjects',
                            'Dimensions': [
                                {
                                    'Name': 'BucketName',
                                    'Value': bucket
                                },
                                {
                                    'Name': 'StorageType',
                                    'Value': 'AllStorageTypes'
                                }
                            ]
                        },
                    'Period': 60,
                    'Stat': 'Average'
                    }
                }
            ],
            StartTime=rangestart,
            EndTime=rangeend
        )
    
    try: standardstorage = resp['MetricDataResults'][0]['Values'][0] / (1024**3)
    except: standardstorage = float(0)
    try: numberofobjects = int(resp['MetricDataResults'][1]['Values'][0])
    except: numberofobjects = 0

    buckets_list.append((bucket,region,versioning,mfa_delete,enc,policy,replication,standardstorage,numberofobjects))

    waitplease += 1
    if waitplease / 10 == int(waitplease / 10):
        print(f"{waitplease} buckets examined and counting...")

    # if waitplease > 50: break   # Debug

print(f"\nDone. {waitplease} total buckets found:")

print(f"\nBucket{separator}Region{separator}Versioning{separator}MFA delete{separator}Encription{separator}Public{separator}Replicated{separator}Standard storage (GB){separator}Objects")

replica_list = []

for x in buckets_list:
    if x[6] == []:
        repl = "No"
    else:
        repl = "Yes"
        repdel = x[6][6]['Status']
        replica_list.append((x[0],x[1],x[6][0],x[6][1],x[6][2],x[6][3].replace("arn:aws:s3:::",""),x[6][4],x[6][5],repdel))


    print(f"{x[0]}{separator}{x[1]}{separator}{x[2]}{separator}{x[3]}{separator}{x[4]}{separator}{x[5]}{separator}{repl}{separator}{x[7]:.2f}{separator}{x[8]}")

print(f"\nReplication rules:")
print(f"Bucket{separator}Region{separator}Rule ID{separator}Prefix{separator}Status{separator}Destination bucket{separator}Other account{separator}Storage class{separator}Replicate deletes")

for y in replica_list:
    print(f"{y[0]}{separator}{y[1]}{separator}{y[2]}{separator}{y[3]}{separator}{y[4]}{separator}{y[5]}{separator}{y[6]}{separator}{y[7]}{separator}{y[8]}")

print(f"\n*** PROGRAM END ***")
