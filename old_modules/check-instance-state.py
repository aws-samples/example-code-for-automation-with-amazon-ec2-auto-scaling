import boto3

def lambda_handler(event, context):
    # Create an EC2 client
    ec2 = boto3.client('ec2')

    # Get the instance ID from the event input
    instance_id = event.get('InstanceId')

    

    # Describe the instance status
    response = ec2.describe_instance_status(InstanceIds=[instance_id])

    if response['InstanceStatuses']:
        instance_status = response['InstanceStatuses'][0]
        instance_state = instance_status['InstanceState']['Name']
        system_status = instance_status['SystemStatus']['Status']
        instance_status_check = instance_status['InstanceStatus']['Status']
    
    
    # Return True if both instance and system status checks are "ok"
    if instance_status_check == 'ok' and system_status == 'ok':
        return {'system_status': system_status}
    else:
        return {'system_status': 'pending'}