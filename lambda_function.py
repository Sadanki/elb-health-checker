import boto3
import os

elb = boto3.client('elbv2')
sns = boto3.client('sns')

TARGET_GROUP_ARN = os.environ['TARGET_GROUP_ARN']
SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']

def lambda_handler(event, context):
    response = elb.describe_target_health(TargetGroupArn=TARGET_GROUP_ARN)
    unhealthy = []
    
    for target in response['TargetHealthDescriptions']:
        instance_id = target['Target']['Id']
        status = target['TargetHealth']['State']
        if status != 'healthy':
            unhealthy.append((instance_id, status))

    if unhealthy:
        message = "🚨 Unhealthy instances detected:\n"
        for inst, stat in unhealthy:
            message += f"Instance ID: {inst}, Status: {stat}\n"

        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="ALB Health Alert 🚨",
            Message=message
        )
    else:
        print("✅ All instances are healthy.")
