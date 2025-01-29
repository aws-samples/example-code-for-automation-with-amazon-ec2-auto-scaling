import boto3
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Lambda handler to cleanup EC2 instance and AMI.
    """
    try:
        # Validate input
        if 'InstanceId' not in event or 'AmiId' not in event:
            error_msg = "Missing required parameters: InstanceId or AmiId"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Extract the instance ID and AMI ID from the event input
        instance_id = event['InstanceId']
        ami_id = event['AmiId']
        
        logger.info(f"Starting cleanup for Instance: {instance_id}, AMI: {ami_id}")

        # Initialize the EC2 client
        ec2 = boto3.client('ec2')

        # Terminate the EC2 instance
        try:
            response = ec2.terminate_instances(InstanceIds=[instance_id])
            instance_state = response['TerminatingInstances'][0]['CurrentState']['Name']
            logger.info(f"Instance {instance_id} state: {instance_state}")
        except Exception as e:
            logger.error(f"Error terminating instance {instance_id}: {str(e)}")
            raise

        # Deregister the AMI
        try:
            ec2.deregister_image(ImageId=ami_id)
            logger.info(f"AMI {ami_id} deregistered successfully")
        except Exception as e:
            logger.error(f"Error deregistering AMI {ami_id}: {str(e)}")
            raise

        return {
            'InstanceState': instance_state,
            'AmiStatus': f'AMI {ami_id} deregistered'
        }

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise
