import boto3

def lambda_handler(event, context):
    launch_template_id = event['LaunchTemplateId']
    latest_ami_id = event['ImageId']
    asg_name = event['AutoScalingGroupName']
    launch_template_name = event['LaunchTemplateName']
    original_max_capacity = event.get('OriginalMaxCapacity')

    ec2_client = boto3.client(service_name='ec2')
    autoscaling_client = boto3.client(service_name='autoscaling')
    asg = boto3.client('autoscaling')

    versions = ec2_client.describe_launch_template_versions(
        LaunchTemplateName=launch_template_name
    )["LaunchTemplateVersions"]

    latest_version = max([version['VersionNumber'] for version in versions])
    current_ami_id = versions[-1]['LaunchTemplateData']['ImageId']

    print(f"Current AMI ID: {current_ami_id}")
    print(f"Latest AMI ID: {latest_ami_id}")
    print(f"Latest version: {latest_version}")

    if latest_ami_id != current_ami_id:
        print(f"Updating launch template {launch_template_name} with {latest_ami_id}")

        new_version = ec2_client.create_launch_template_version(
            LaunchTemplateName=launch_template_name,
            SourceVersion=str(latest_version),
            LaunchTemplateData={
                "ImageId": latest_ami_id
            }
        )['LaunchTemplateVersion']

        ec2_client.modify_launch_template(
            LaunchTemplateName=launch_template_name,
            DefaultVersion=str(new_version['VersionNumber'])
        )

        autoscaling_client.update_auto_scaling_group(
            AutoScalingGroupName=asg_name,
            LaunchTemplate={
                'LaunchTemplateName': launch_template_name,
                'Version': str(new_version['VersionNumber'])
            }
        )

        print(f"Updated Auto Scaling group {asg_name} with the new launch template version {new_version['VersionNumber']}")
    else:
        print(f"Current launch template version for {launch_template_name} is already up-to-date")
    
    print(f"original_max_capacity {original_max_capacity}")
    
    # Revert the maximum capacity of the Auto Scaling group to its original value
    if original_max_capacity is not None:
        asg.update_auto_scaling_group(
            AutoScalingGroupName=asg_name,
            MaxSize=original_max_capacity
        )

        print(f"Reverted maximum capacity of Auto Scaling group {asg_name} to {original_max_capacity}")

    return {
        "UpdateResult": {
            "AutoScalingGroupName": asg_name,
            "LaunchTemplateId": launch_template_id,
            "LaunchTemplateName": launch_template_name
        }
    }