# Statistics about all lambda functions in a given account.
# Uses environment for authentication to AWS.
#
# v 1.0 2023-11-16 by Simone Bazzi.

import boto3

print(f"\n*** PROGRAM START ***\n")

aclient = boto3.client('account')
response = aclient.list_regions()

regions = []

for reg in response['Regions']:
    if reg['RegionOptStatus'] != "DISABLED":
        regions.append(reg['RegionName'])

lambda_list = []
for region in regions:

    setregion = boto3.setup_default_session(region_name = region)
    lambdaclient = boto3.client('lambda')

    marker = "M"
    while marker != None:
        try:
            if marker != "M":
                response = lambdaclient.list_functions(Marker = marker)
            else:
                response = lambdaclient.list_functions()
                
            for x in response['Functions']:
                lambda_list.append((x['FunctionArn'],  x['Runtime'],x['CodeSize'],x['Timeout'],x['MemorySize'],x['PackageType'],x['Architectures'],x['EphemeralStorage']['Size']))

            try:
                marker = response['NextMarker']
            except:
                marker = None

        except:
            marker = None

separator = "\t"

print(f"ARN{separator}Runtime{separator}Size (Bytes){separator}Timeout (S){separator}Memory (MB){separator}Package type{separator}Architecture{separator}Storage (GB)")

for x in lambda_list:
    print(f"{x[0]}{separator}{x[1]}{separator}{x[2]}{separator}{x[3]}{separator}{x[4]}{separator}{x[5]}{separator}{x[6]}{separator}{x[7]}")

print(f"\n*** PROGRAM END ***")
