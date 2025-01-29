import boto3
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        # Create an EC2 client
        ec2 = boto3.client('ec2')

        # Get the instance ID from the event input
        instance_id = event.get('InstanceId')
        logger.info(f"Checking status for instance: {instance_id}")

        # Describe the instance status
        try:
            response = ec2.describe_instance_status(InstanceIds=[instance_id])

            if response['InstanceStatuses']:
                instance_status = response['InstanceStatuses'][0]
                instance_state = instance_status['InstanceState']['Name']
                system_status = instance_status['SystemStatus']['Status']
                instance_status_check = instance_status['InstanceStatus']['Status']
                
                logger.info(f"Instance state: {instance_state}")
                logger.info(f"System status: {system_status}")
                logger.info(f"Instance status check: {instance_status_check}")
            
                # Return True if both instance and system status checks are "ok"
                if instance_status_check == 'ok' and system_status == 'ok':
                    return {'system_status': system_status}
                else:
                    return {'system_status': 'pending'}
            else:
                logger.warning(f"No status information found for instance {instance_id}")
                return {'system_status': 'pending'}

        except Exception as e:
            logger.error(f"Error checking instance status: {str(e)}")
            raise

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise
