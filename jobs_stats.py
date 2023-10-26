# Report statistics about historical jobs executions.
#   NB: this is still a work in progress.
# Uses environment for authentication to AWS.
#
# v 1.0 beta 2023-10-26 by Simone Bazzi.

import boto3
from datetime import datetime
from dateutil.relativedelta import relativedelta

glue = boto3.client('glue')

jobs = glue.list_jobs(MaxResults=200).get('JobNames')

if jobs == []:
    exit

jobruns = []
stats_matrix = []
today = datetime.today()

datecheck = [today - relativedelta(days = 1),
             today - relativedelta(weeks = 1),
             today - relativedelta(months = 1),
             today - relativedelta(months = 6)]

for job in jobs: # Costruzione della matrice delle esecuzioni

    tokennumber = 0
    nexttoken = None

    while tokennumber == 0 or nexttoken != None:
        if nexttoken == None:
            result = glue.get_job_runs(JobName=job)
        else:
            result = glue.get_job_runs(JobName=job, NextToken=nexttoken)
        try:
            nexttoken = result['NextToken']
        except:
            nexttoken = None
        for j in result['JobRuns']:
            jobruns.append((job, j.get('Attempt'), j.get('StartedOn'), j.get('JobRunState'), j.get('AllocatedCapacity'), j.get('ExecutionTime'), j.get('MaxCapacity'), j.get('WorkerType'), j.get('NumberOfWorkers'), j.get('GlueVersion')))
        tokennumber += 1

for x in jobs: # Ciclo su tutti i job

    increment = [0,0,0,0,0]
    job_ok = [0,0,0,0,0]
    job_capacity = [0,0,0,0,0]
    job_time = [0,0,0,0,0]

    for y in jobruns: # Per ogni elemento della matrice

        if y[0] == x: # Considero il singolo job

            increment[0] += 1 # Incremento il numero di esecuzioni del job
            job_capacity[0] += y[4]
            job_time[0] += y[5]

            if y[3] == "SUCCEEDED":

                job_ok[0] += 1

            for dc in [ 1, 2, 3, 4 ]:
                if y[2].replace(tzinfo=None) > datecheck[dc - 1]:
                    increment[dc] += 1
                    job_capacity[dc] += y[4]
                    job_time[dc] += y[5]
                    if y[3] == "SUCCEEDED":
                        job_ok[dc] += 1
                
    stats_matrix.append({"JobName" : x,
                         "TotalExecutions" : increment[0],
                         "TotalSucceeded" : job_ok[0],
                         "TotalCapacity" : job_capacity[0],
                         "TotalTime" : job_time[0],
                         "LastDayExecutions" : increment[1],
                         "LastDaySucceeded" : job_ok[1],
                         "LastDayCapacity" : job_capacity[1],
                         "LastDayTime" : job_time[1],
                         "LastWeekExecutions" : increment[2],
                         "LastWeekSucceeded" : job_ok[2],
                         "LastWeekCapacity" : job_capacity[2],
                         "LastWeekTime" : job_time[2],
                         "LastMonthExecutions" : increment[3],
                         "LastMonthSucceeded" : job_ok[3],
                         "LastMonthCapacity" : job_capacity[3],
                         "LastMonthTime" : job_time[3],
                         "LastHalfExecutions" : increment[4],
                         "LastHalfSucceeded" : job_ok[4],
                         "LastHalfCapacity" : job_capacity[4],
                         "LastHalfTime" : job_time[4]
                         })


separator = ","

print(f"Nome job{separator}Esecuzioni totali{separator}% OK{separator}Ultimo giorno{separator}% OK{separator}Ultima settimana{separator}% OK{separator}Ultimo mese{separator}% OK{separator}Ultimo semestre{separator}% OK{separator}Costo ultimo mese(USD)")

sum_total_exec = 0
sum_total_succ = 0
sum_day_exec = 0
sum_day_succ = 0
sum_week_exec = 0
sum_week_succ = 0
sum_month_exec = 0
sum_month_succ = 0
sum_half_exec = 0
sum_half_succ =0
sum_cost = 0

for t in stats_matrix:

    if t['TotalExecutions'] == 0:
        successrate_tot = 0
    else:
        successrate_tot = int(t['TotalSucceeded'] / t['TotalExecutions'] * 100)
        sum_total_exec += t['TotalExecutions']
        sum_total_succ += t['TotalSucceeded']

    if t['LastDayExecutions'] == 0:
        successrate_day = 0
    else:
        successrate_day = int(t['LastDaySucceeded'] / t['LastDayExecutions'] * 100)
        sum_day_exec += t['LastDayExecutions']
        sum_day_succ += t['LastDaySucceeded']

    if t['LastWeekExecutions'] == 0:
        successrate_week = 0
    else:
        successrate_week = int(t['LastWeekSucceeded'] / t['LastWeekExecutions'] * 100)
        sum_week_exec += t['LastWeekExecutions']
        sum_week_succ += t['LastWeekSucceeded']

    if t['LastMonthExecutions'] == 0:
        successrate_month = 0
        monthly_cost = 0
    else:
        successrate_month = int(t['LastMonthSucceeded'] / t['LastMonthExecutions'] * 100)
        monthly_cost = int(t['LastMonthCapacity'] / t['LastMonthExecutions'] * t['LastMonthTime'] / 3600 * 0.44)
        sum_month_exec += t['LastMonthExecutions']
        sum_month_succ += t['LastMonthSucceeded']
        sum_cost += monthly_cost

    if t['LastHalfExecutions'] == 0:
        successrate_half = 0
    else:
        successrate_half = int(t['LastHalfSucceeded'] / t['LastHalfExecutions'] * 100)
        sum_half_exec += t['LastHalfExecutions']
        sum_half_succ += t['LastHalfSucceeded']
    
    print(f"{t['JobName']}{separator}" +
          f"{t['TotalExecutions']}{separator}{successrate_tot}{separator}" + 
          f"{t['LastDayExecutions']}{separator}{successrate_day}{separator}" +
          f"{t['LastWeekExecutions']}{separator}{successrate_week}{separator}" +
          f"{t['LastMonthExecutions']}{separator}{successrate_month}{separator}" +
          f"{t['LastHalfExecutions']}{separator}{successrate_half}{separator}" +
          f"{monthly_cost}"
          )

sum_successrate_tot = int(sum_total_succ / sum_total_exec * 100)
sum_successrate_day = int(sum_day_succ / sum_day_exec * 100)
sum_successrate_week = int(sum_week_succ / sum_week_exec * 100)
sum_successrate_month = int(sum_month_succ / sum_month_exec * 100)
sum_successrate_half = int(sum_half_succ / sum_half_exec * 100)

print(f"Totali{separator}" +
        f"{sum_total_exec}{separator}{sum_successrate_tot}{separator}" + 
        f"{sum_day_exec}{separator}{sum_successrate_day}{separator}" +
        f"{sum_week_exec}{separator}{sum_successrate_week}{separator}" +
        f"{sum_month_exec}{separator}{sum_successrate_month}{separator}" +
        f"{sum_half_exec}{separator}{sum_successrate_half}{separator}" +
        f"{sum_cost}"
        )
