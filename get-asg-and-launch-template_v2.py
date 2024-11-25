import json
import boto3

def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    
    # Extract relevant information from the event
    #backup_job_id = event['detail']['backupJobId']
    backup_job_id = event['backupJobId']
    set_max_capacity_equal_to_desired = event.get('setMaxCapacityEqualToDesiredCapacity', True)
    # Initialize AWS Backup and EC2 clients
    backup = boto3.client('backup')
    ec2 = boto3.client('ec2')
    asg = boto3.client('autoscaling')
    
    # Get details of the backup job
    response = backup.describe_backup_job(BackupJobId=backup_job_id)
    
    # Extract the AMI ID
    recovery_point_arn = response['RecoveryPointArn']
    ami_id = recovery_point_arn.split('/')[-1]
    
    # Extract the resource ARN (which contains the instance ID)
    resource_arn = response['ResourceArn']
    instance_id = resource_arn.split('/')[-1]
    
    print(f"AMI ID: {ami_id}")
    print(f"Instance ID: {instance_id}")
    
    # If you need more details about the instance, you can use the EC2 client
    instance_response = ec2.describe_instances(InstanceIds=[instance_id])
    instance = instance_response['Reservations'][0]['Instances'][0]
    
    asg_name = None
    for tag in instance['Tags']:
        if tag['Key'] == 'aws:autoscaling:groupName':
            asg_name = tag['Value']
            break

    launch_template_name = None
    launch_template_id = None
    if 'LaunchTemplate' in instance:
        launch_template_name = instance['LaunchTemplate']['LaunchTemplateName']
        launch_template_id = instance['LaunchTemplate']['LaunchTemplateId']
    else:
        asg_response = asg.describe_auto_scaling_groups(AutoScalingGroupNames=[asg_name])
        asg_group = asg_response['AutoScalingGroups'][0]
        if 'LaunchTemplate' in asg_group:
            launch_template_name = asg_group['LaunchTemplate']['LaunchTemplateName']
            launch_template_id = asg_group['LaunchTemplate']['LaunchTemplateId']

    
    
    
        
    original_max_capacity = None
    if set_max_capacity_equal_to_desired:
        asg_response = asg.describe_auto_scaling_groups(AutoScalingGroupNames=[asg_name])
        asg_group = asg_response['AutoScalingGroups'][0]
        desired_capacity = asg_group['DesiredCapacity']
        original_max_capacity = asg_group['MaxSize']

        asg.update_auto_scaling_group(
            AutoScalingGroupName=asg_name,
            MaxSize=desired_capacity
        )

    return {
        'AutoScalingGroupName': asg_name,
        'LaunchTemplateName': launch_template_name,
        'LaunchTemplateId': launch_template_id,
        'BackupAMIId': ami_id,
        'InstanceId': instance_id,
        'OriginalMaxCapacity': original_max_capacity,
        'InstanceType': instance['InstanceType']
    }
    
    
