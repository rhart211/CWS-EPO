#!/usr/bin/env python
import mcafee
import boto3
import argparse
import getpass


def request_args():
    # Arguments
    parser = argparse.ArgumentParser(description='Clean up and Remove Orphaned AWS Instances from ePO')
    parser.add_argument('-a', '--access_key', type=str, help='AWS Access Key', required=True)
    parser.add_argument('-s', '--secret_key', type=str, help='AWS Secret Key', required=True)
    parser.add_argument('-e', '--epo', type=str, help='ePO IP or FQDN', required=True)
    parser.add_argument('-t', '--epo_port', type=str, help='ePO Port', default='8443')
    parser.add_argument('-u', '--epo_user', type=str, help='ePO User Name', required=True)
    parser.add_argument('-p', '--epo_password', type=str, help='ePO Password')
    return parser.parse_args()

def get_ePO_password(epo_user):
    # Requests user for their ePO Password
    epo_password = getpass.getpass('Enter the password for your ePO username %s: ' % epo_user)
    return epo_password

def epoInstances(mc):
    # Queries ePO Database for System Name and AWS Instance Id for AWS VMs
    data = mc.core.executeQuery(target='MDCC_CLOUD_VM_PROPS_VW_awsSquid',
                                select='(select EPOLeafNode.NodeName MDCC_CLOUD_VM_PROPS_VW_awsSquid.instance_id)')
    return data

def epoInstanceIds(mc, data):
    # Generates a list of only the AWS Instance Ids for Systems in ePO Database
    instanceids = []
    for item in data:
        instanceids.append(item.get('MDCC_CLOUD_VM_PROPS_VW_awsSquid.instance_id'))
    return instanceids

def getePOInstanceName(mc, data, instance_id):
    # Prints the System Name for the specified AWS Instance Id
    for item in data:
        if instance_id == item.get('MDCC_CLOUD_VM_PROPS_VW_awsSquid.instance_id'):
            return item.get('EPOLeafNode.NodeName')

def deleteInstance(mc, endpoint_name):
    # Deletes the specified System from ePO database
    deleted_systems = mc.system.delete(endpoint_name)
    return deleted_systems

def awsInstanceIds(access_key, secret_key):
    # Lists all instance ids in all  AWS regions
    # Reference: http://boto3.readthedocs.io/en/latest/reference/services/ec2.html?highlight=ec2.Instance#instance
    instance_ids = []
    client = boto3.client('ec2', aws_access_key_id=access_key, aws_secret_access_key=secret_key,
                          region_name='us-east-1')

    for region in client.describe_regions().get('Regions'):
        conn = boto3.resource('ec2', aws_access_key_id=access_key, aws_secret_access_key=secret_key,
                              region_name=region.get('RegionName'))
        instances = conn.instances.filter()
        for instance in instances:
            instance_ids.append(str(instance.id))
    return instance_ids

def ePOnotinAWS(endpoints, aws_instanceids):
    # Return a list of AWS Instance Ids that remain in the ePO Database but no longer exist in AWS
    dupes = set(endpoints).intersection(aws_instanceids)
    diffs = set(endpoints) - set(dupes)
    return list(diffs)

def deleteEPOUniqueInstances(mc, data, uniques):
    # Deletes all systems that remain in ePO Database but no longer exist in AWS
    # Prints Deleted Systems
    for unique in uniques:
        endpoint_name = getePOInstanceName(mc, data, instance_id)
        deleted = deleteInstance(mc, endpoint_name)
        for item in deleted:
            print '%s: %s' % (item.get('name'), item.get('message'))

def main():
    # Main Function
    args = request_args()
    if args.epo_password is None:
        args.epo_password = get_ePO_password(args.epo_user)

    # Connect to ePO
    mc = mcafee.client(args.epo, args.epo_port, args.epo_user, args.epo_password)

    # Grab ePO managed Instance Ids and System Names
    endpoint_instances = epoInstances(mc)

    # Create list of only the AWS Instance Ids for Systems in ePO Database
    endpoint_instanceids = epoInstanceIds(mc, endpoint_instances)

    # Create a list of all instance ids in all  AWS regions
    aws_instances = awsInstanceIds(args.access_key, args.secret_key)

    # Create a list of AWS Instance Ids that remain in the ePO Database but no longer exist in AWS
    uniques = ePOnotinAWS(endpoint_instanceids, aws_instances)

    # Delete all systems that remain in ePO Database but no longer exist in AWS
    deleteEPOUniqueInstances(mc, endpoint_instances, uniques)

if __name__ == '__main__':
    main()
