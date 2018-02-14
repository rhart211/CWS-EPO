# CompareAWS2ePO
Clean up and Remove Orphaned AWS Instance being that were imported into ePO via Cloud Workload Security.

## Introduction
McAfee Cloud Workload Security automates the discovery and defense of elastic workloads to eliminate blind spots, deliver advanced threat defense, and simplify hybrid cloud management. When AWS Instances that have been imported into McAfee ePO have been terminated, there is no automated process that deletes associated, and not orphaned systems from McAfee ePO. This tool takes solves that issue by comparing the currently running AWS Instances to the AWS Systems in the McAfee ePO System Tree. Any AWS system that does not exist in AWS but does exist in ePO is deleted.

## Dependencies
Requires [boto3](https://github.com/boto/boto3), [McAfee Python Remote Client](https://www.mcafee.com/apps/downloads/my-products/login.aspx)

## Usage
To use this tool:
  run `python compareAWS2ePO.py`

You can also get to help by using -h switch:
```
usage: compareAWS2ePO.py [-h] -a ACCESS_KEY -s SECRET_KEY -e EPO 
                         [-t EPO_PORT] -u EPO_USER [-p EPO_PASSWORD]

Clean up and Remove Orphaned AWS Instances from ePO

optional arguments:
  -h, --help            show this help message and exit
  -a ACCESS_KEY, --access_key ACCESS_KEY
                        AWS Access Key
  -s SECRET_KEY, --secret_key SECRET_KEY
                        AWS Secret Key
  -e EPO, --epo EPO     ePO IP or FQDN
  -t EPO_PORT, --epo_port EPO_PORT
                        ePO Port
  -u EPO_USER, --epo_user EPO_USER
                        ePO User Name
  -p EPO_PASSWORD, --epo_password EPO_PASSWORD
                        ePO Password
```


## Todo
* Add Azure Support
* Output List of deleted systems to CSV, and XLSX
