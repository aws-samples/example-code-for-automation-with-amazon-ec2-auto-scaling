import boto3
import logging
from typing import Dict, Any
from botocore.exceptions import ClientError

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_latest_template_version(ec2_client, launch_template_name: str) -> tuple:
    """Get the latest template version and current AMI ID."""
    try:
        versions = ec2_client.describe_launch_template_versions(
            LaunchTemplateName=launch_template_name
        )["LaunchTemplateVersions"]
        
        latest_version = max(version['VersionNumber'] for version in versions)
        current_ami_id = versions[-1]['LaunchTemplateData']['ImageId']
        
        return latest_version, current_ami_id
    except ClientError as e:
        logger.error(f"Error getting launch template versions: {str(e)}")
        raise

def update_launch_template(ec2_client, launch_template_name: str, 
                         latest_version: int, latest_ami_id: str) -> Dict:
    """Update launch template with new AMI ID."""
    try:
        new_version = ec2_client.create_launch_template_version(
            LaunchTemplateName=launch_template_name,
            SourceVersion=str(latest_version),
            LaunchTemplateData={"ImageId": latest_ami_id}
        )['LaunchTemplateVersion']

        ec2_client.modify_launch_template(
            LaunchTemplateName=launch_template_name,
            DefaultVersion=str(new_version['VersionNumber'])
        )
        
        return new_version
    except ClientError as e:
        logger.error(f"Error updating launch template: {str(e)}")
        raise

def update_asg(autoscaling_client, asg_name: str, 
               launch_template_name: str, version_number: str) -> None:
    """Update Auto Scaling group with new launch template version."""
    try:
        autoscaling_client.update_auto_scaling_group(
            AutoScalingGroupName=asg_name,
            LaunchTemplate={
                'LaunchTemplateName': launch_template_name,
                'Version': version_number
            }
        )
    except ClientError as e:
        logger.error(f"Error updating Auto Scaling group: {str(e)}")
        raise

def revert_asg_capacity(asg_client, asg_name: str, 
                       original_max_capacity: int) -> None:
    """Revert ASG maximum capacity to original value."""
    try:
        asg_client.update_auto_scaling_group(
            AutoScalingGroupName=asg_name,
            MaxSize=original_max_capacity
        )
        logger.info(f"Reverted maximum capacity of ASG {asg_name} to {original_max_capacity}")
    except ClientError as e:
        logger.error(f"Error reverting ASG capacity: {str(e)}")
        raise

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict:
    """
    Update Auto Scaling group with new AMI ID.
    
    Args:
        event (dict): Must contain LaunchTemplateId, ImageId, AutoScalingGroupName,
                     LaunchTemplateName, and optionally OriginalMaxCapacity
        context (Any): Lambda context object
    
    Returns:
        dict: Update result containing ASG and launch template details
    """
    try:
        # Extract input parameters
        launch_template_id = event['LaunchTemplateId']
        latest_ami_id = event['ImageId']
        asg_name = event['AutoScalingGroupName']
        launch_template_name = event['LaunchTemplateName']
        original_max_capacity = event.get('OriginalMaxCapacity')

        # Initialize AWS clients with config for retries
        #config = boto3.Config(retries={'max_attempts': 3})
        ec2_client = boto3.client('ec2')
        autoscaling_client = boto3.client('autoscaling')

        # Get current template version and AMI ID
        latest_version, current_ami_id = get_latest_template_version(
            ec2_client, launch_template_name
        )

        logger.info(f"Current AMI ID: {current_ami_id}")
        logger.info(f"Latest AMI ID: {latest_ami_id}")
        logger.info(f"Latest version: {latest_version}")

        if latest_ami_id != current_ami_id:
            logger.info(f"Updating launch template {launch_template_name} with {latest_ami_id}")
            
            # Update launch template
            new_version = update_launch_template(
                ec2_client, launch_template_name, latest_version, latest_ami_id
            )
            
            # Update ASG
            update_asg(
                autoscaling_client, asg_name, launch_template_name, 
                str(new_version['VersionNumber'])
            )
            
            logger.info(f"Updated ASG {asg_name} with new launch template version {new_version['VersionNumber']}")
        else:
            logger.info(f"Current launch template version for {launch_template_name} is already up-to-date")

        # Revert ASG capacity if needed
        if original_max_capacity is not None:
            revert_asg_capacity(autoscaling_client, asg_name, original_max_capacity)

        return {
            "UpdateResult": {
                "AutoScalingGroupName": asg_name,
                "LaunchTemplateId": launch_template_id,
                "LaunchTemplateName": launch_template_name
            }
        }

    except KeyError as e:
        logger.error(f"Missing required parameter: {str(e)}")
        raise
    except ClientError as e:
        logger.error(f"AWS API error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise
