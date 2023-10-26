# Previous month spending (unblended) by service, sorted based on cost and rounded to the dollar.
# Uses environment for authentication to AWS.
#
# v 1.0 2023-10-25 by Simone Bazzi.

import boto3
import datetime

today = datetime.date.today()
startdate = str((today - datetime.timedelta(days=today.day)).replace(day=1))
enddate = str(today - datetime.timedelta(days=(today.day - 1)))

ceclient = boto3.client('ce')

response = ceclient.get_cost_and_usage(
    TimePeriod={
        'Start': startdate,
        'End': enddate
    },
    Granularity='MONTHLY',
    Metrics=[
        'UnblendedCost'
    ],
    GroupBy=[
        {
            'Type': 'DIMENSION',
            'Key': 'SERVICE'
        }
    ]
)

total_costs = []
for x in response['ResultsByTime'][0]['Groups']:
    service = x['Keys'][0]
    cost = int(float(x['Metrics']['UnblendedCost']['Amount']))
    total_costs.append((cost,service))

sorted_total_costs = sorted(total_costs,reverse=True)
print('\n{:10}{}'.format("USD", "Service"))
print('{:10}{}'.format("---", "-------"))

grand_total = 0
for x in sorted_total_costs:
    print('{:10}{}'.format(str(x[0]), x[1]))
    grand_total += x[0]

print(f'\nGrand total: {grand_total}')
