import boto3

def lambda_handler(event, context):
    # Initialize the EC2 client
    ec2 = boto3.client('ec2')

    # Extract the instance ID and AMI ID from the event input
    instance_id = event['InstanceId']
    ami_id = event['AmiId']

    # Terminate the EC2 instance
    response = ec2.terminate_instances(InstanceIds=[instance_id])
    instance_state = response['TerminatingInstances'][0]['CurrentState']['Name']
    print(f'Instance {instance_id} state: {instance_state}')

    # Deregister the AMI
    try:
        ec2.deregister_image(ImageId=ami_id)
        print(f'AMI {ami_id} deregistered successfully')
    except Exception as e:
        print(f'Error deregistering AMI {ami_id}: {e}')

    return {
        'InstanceState': instance_state,
        'AmiStatus': f'AMI {ami_id} deregistered'
    }