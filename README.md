# awsutils
Tiny helper scripts for AWS

These are simple utilities I write for personal use whenever I need to solve simple tasks. Nothing like serious programming. You're welcome to use them if you feel like it and if you want to improve the functionalities just fork your on repo or get in touch and become a contributor.

Quick (unordered) list:

- **cloudwatch_logs_stats.py**: statistics about cloudwatch logs (storage + retention) from all regions.
- **find_entities_by_policy.py**: find which IAM entities (Roles, Groups and Users) have certain attached policies.
- **find_resource_in_stacks.py**: given a resource name or part of it, search Cloudformation stacks and returns any stack that matches in any region.
- **jobs_info.py**: list of Glue jobs in all regions along with last execution date and Glue version.
- **jobs_stats.py**: statistics about Glue jobs run history (work in progress).
- **month_spending_by_service.py**: last month spending (unblended) by AWS service.
- **single_job_stats.py**: summary of execution and exit states for a Glue job in a given time frame.
- **global_stack_drifts.py**: checks for drifted resources across all stacks in all regions.
- **s3_stats.py**: overview about buckets in one account (size, versioning, etc.)
- **lamda_stats.py**: gives statistics about lambda functions across regions for a given account.
