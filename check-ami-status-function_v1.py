import boto3
import time
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Check AMI status and return its state.
    
    Args:
        event: Must contain 'BackupAMIId' key
        context: Lambda context object
    
    Returns:
        dict: Contains AMI state and ID
    """
    try:
        # Validate input
        if 'BackupAMIId' not in event:
            error_msg = "BackupAMIId not found in event"
            logger.error(error_msg)
            raise ValueError(error_msg)

        ami_id = event['BackupAMIId']
        logger.info(f"Checking status for AMI: {ami_id}")
        
        ec2 = boto3.client('ec2')

        response = ec2.describe_images(ImageIds=[ami_id])
        
        if response['Images']:
            ami_description = response['Images'][0]
            ami_state = ami_description['State']
            
            logger.info(f"AMI {ami_id} is in state: {ami_state}")
            
            if ami_state == 'available':
                return {'amiState': ami_state, 'amiId': ami_id}
            elif ami_state == 'pending':
                return {'amiState': ami_state, 'amiId': ami_id}
        else:
            error_msg = f'AMI {ami_id} not found or in the process of being created'
            logger.error(error_msg)
            raise ValueError(error_msg)
            
    except boto3.exceptions.ClientError as e:
        error_msg = f"AWS API error: {str(e)}"
        logger.error(error_msg)
        raise
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        raise
