import boto3
import time

def lambda_handler(event, context):
    ami_id = event['BackupAMIId']
    ec2 = boto3.client('ec2')

    response = ec2.describe_images(ImageIds=[ami_id])
    if response['Images']:
        ami_description = response['Images'][0]
        ami_state = ami_description['State']
        if ami_state == 'available':
            return {'amiState': ami_state, 'amiId': ami_id}
        elif ami_state == 'pending':
            return {'amiState': ami_state, 'amiId': ami_id}
    else:
        print(f'AMI {ami_id} not found or in the process of being created')