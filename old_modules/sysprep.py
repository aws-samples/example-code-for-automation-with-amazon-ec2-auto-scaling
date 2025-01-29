import boto3

ec2 = boto3.client('ec2')
ssm = boto3.client('ssm')

def lambda_handler(event, context):
    instance_id = event['InstanceId']

    # Execute the Sysprep command using AWS Systems Manager
    response = ssm.send_command(
        InstanceIds=[instance_id],
        DocumentName="AWSEC2-RunSysprep",
        TimeoutSeconds=3600  # Set a timeout value in seconds
    )

    # Print the command execution ID
    print(f"Command execution ID: {response['Command']['CommandId']}")

    return {
        'statusCode': 200,
        'body': f"Sysprep executed on EC2 instance {instance_id}"
    }