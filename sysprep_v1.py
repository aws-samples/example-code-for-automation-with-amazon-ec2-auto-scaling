import boto3
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        instance_id = event['InstanceId']
        logger.info(f"Starting Sysprep for instance: {instance_id}")

        # Initialize AWS clients
        ssm = boto3.client('ssm')

        try:
            # Execute the Sysprep command using AWS Systems Manager
            response = ssm.send_command(
                InstanceIds=[instance_id],
                DocumentName="AWSEC2-RunSysprep",
                TimeoutSeconds=3600  # Set a timeout value in seconds
            )
            
            command_id = response['Command']['CommandId']
            logger.info(f"Command execution ID: {command_id}")

            return {
                'statusCode': 200,
                'body': f"Sysprep executed on EC2 instance {instance_id}",
                'commandId': command_id
            }

        except Exception as e:
            logger.error(f"Error executing Sysprep command: {str(e)}")
            raise

    except KeyError as e:
        logger.error(f"Missing required parameter: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise
