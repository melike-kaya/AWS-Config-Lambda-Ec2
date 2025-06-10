import boto3
import json

def lambda_handler(event, context):
    ec2_client = boto3.client('ec2')
    config_client = boto3.client('config')
    compliance_status = "NON_COMPLIANT"  # Default to NON_COMPLIANT

    config = json.loads(event['invokingEvent'])
    configuration_item = config.get("configurationItem")

    # Defensive check for None
    if not configuration_item or not configuration_item.get("configuration"):
        return config_client.put_evaluations(
            Evaluations=[
                {
                    'ComplianceResourceType': 'AWS::EC2::Instance',
                    'ComplianceResourceId': configuration_item.get('resourceId', 'Unknown') if configuration_item else 'Unknown',
                    'ComplianceType': 'NOT_APPLICABLE',
                    'Annotation': 'Configuration item not available.',
                    'OrderingTimestamp': config.get('notificationCreationTime')
                }
            ],
            ResultToken=event['resultToken']
        )

    instance_id = configuration_item['configuration'].get('instanceId')
    instance = ec2_client.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]

    if instance['Monitoring']['State'] == "enabled":
        compliance_status = "COMPLIANT"

    return config_client.put_evaluations(
        Evaluations=[
            {
                'ComplianceResourceType': 'AWS::EC2::Instance',
                'ComplianceResourceId': instance_id,
                'ComplianceType': compliance_status,
                'Annotation': 'Detailed monitoring is enabled.' if compliance_status == "COMPLIANT" else 'Detailed monitoring is not enabled.',
                'OrderingTimestamp': config.get('notificationCreationTime')
            }
        ],
        ResultToken=event['resultToken']
    )
