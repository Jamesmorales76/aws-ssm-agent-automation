# AWS SSM Agent Automation

Automation that installs security and monitoring agents on new EC2 instances without manual setup.

## How it works
1. An Amazon EventBridge rule watches for "EC2 Instance State-change Notification" events.
2. When an instance enters the running state, it triggers the Lambda function (lambda_agent_install.py).
3. The Lambda confirms the instance is registered and online in AWS Systems Manager (SSM).
4. If it is, the Lambda runs an SSM Command document to install the required agent.

## Files
- lambda_agent_install.py: Lambda function that checks SSM status and sends the install command
- rapid7-linux.json: SSM document that installs the Rapid7 Insight Agent on Linux
- cloudwatch-agent.json: SSM document that installs and configures the Amazon CloudWatch Agent
- manageengine-windows.yaml: SSM document that installs the ManageEngine UEM agent on Windows from S3
- newrelic-windows.json: SSM document that installs New Relic on Windows

## Setup notes
- Replace placeholder values (your-bucket-name, tokens, API keys, account IDs) before use.
- Never commit real tokens or keys. Store them in AWS Secrets Manager or SSM Parameter Store.
- The Lambda execution role needs ssm:DescribeInstanceInformation and ssm:SendCommand.
- Target instances need the SSM agent and an instance profile with S3 read access to the installer bucket.

## Notes
The Lambda is adapted from a common AWS event-driven SSM pattern and extended for multi-agent installs and Windows support.
