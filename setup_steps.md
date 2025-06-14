Assignment 19: Load Balancer Health Checker starting from absolute scratch, using the AWS Free Tier, including:
•	Launch
•	ing Ubuntu EC2 instances
•	Installing web server
•	Creating Target Group & Load Balancer
•	Creating SNS topic
•	Writing & deploying Lambda function (with Boto3)
•	Scheduling with CloudWatch
Step 1: Launch 2 Free EC2 Ubuntu Instances:
Do this twice.
1.	Go to EC2 > Launch Instance
2.	Name: UbuntuWebServer1
3.	AMI: Ubuntu Server 22.04 LTS
4.	Instance Type: t2.micro (Free Tier)
5.	Key Pair: Create or select existing (download .pem)
6.	Security Group:
o	Allow SSH (port 22)
o	Allow HTTP (port 80)
7.	User data (Advanced > Paste below):
#!/bin/bash
apt update
apt install apache2 -y
systemctl start apache2
echo "Hello from UbuntuWebServer1" > /var/www/html/index.html




Launch an instance: 1
 

 
 
 
 
 



Launch an instance: 2
 
 
 

 
 
 
 
 
Step 2: Create a Target Group
1.	Go to EC2 > Target Groups > Create Target Group
2.	Target Type: Instance
3.	Name: ubuntu-target-group
4.	Protocol: HTTP, Port: 80
5.	Health check path: /
6.	Register both Ubuntu instances
7.	Click Create

 

 
 
 
 

 





Step 3: Create Application Load Balancer (ALB)
1.	Go to EC2 > Load Balancers > Create Load Balancer
2.	Choose Application Load Balancer
3.	Name: ubuntu-health-alb
4.	Scheme: Internet-facing
5.	IP Type: IPv4
6.	Listener: HTTP (Port 80)
7.	Choose 2 public subnets (from different AZs)
8.	Forward to target group: ubuntu-target-group
9.	Click Create
⏳ Wait until it becomes active, then copy the DNS name and test in your browser.

 

 
 
 







Step 4: Create SNS Topic
1.	Go to SNS > Topics > Create Topic
2.	Type: Standard
3.	Name: elb-health-notify
4.	Click Create
5.	Click Create Subscription
o	Protocol: Email
o	Endpoint: your@email.com
6.	Open your email and confirm the subscription
 
 

 
 
 
 

Step 5: Create IAM Role for Lambda
1.	Go to IAM > Roles > Create Role
2.	Trusted Entity: Lambda
3.	Attach these policies:
o	AmazonEC2ReadOnlyAccess
o	ElasticLoadBalancingReadOnly
o	AmazonSNSFullAccess
4.	Name: LambdaELBHealthCheckerRole
 
 

 
 









Step 6: Create the Lambda Function
1.	Go to Lambda > Create Function
2.	Name: elb-health-checker
3.	Runtime: Python 3.12
4.	Role: Use existing role → LambdaELBHealthCheckerRole_Vignesh
5.	Create the function

 
Step 7: Add Lambda Code
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
 

Step 8: Add Environment Variables

Click Configuration > Environment variables > Edit:
Key	Value
TARGET_GROUP_ARN	Copy from EC2 → Target Groups → select → ARN
SNS_TOPIC_ARN	Copy from SNS → Topic → ARN
	
 
 

Step 9: Set Up CloudWatch Schedule
•  Go to CloudWatch > Rules (EventBridge) > Create Rule
•  Name: elb-health-check-schedule
•  Event Source:
•	Schedule: rate(10 minutes)
•  Target: Lambda → elb-health-checker
•  Click Create Rule
 

 



Testing & Output
Stop Apache on one EC2 manually:
sudo systemctl stop apache2
•  Wait for health check to fail (check Target Group status)
•  Lambda will trigger and send you an SNS email alert.





 









