import os
import logging
import boto3

ssm = boto3.client("ssm")
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Name of the SSM document to run on new instances
DOCUMENT_NAME = os.environ.get("SSM_DOCUMENT_NAME", "Rapid7SSMAgentsInstallDocument")


def lambda_handler(event, context):
    logger.debug("Raw event: %s", event)

    # Only act on EC2 state-change events
    if event.get("detail-type") != "EC2 Instance State-change Notification":
        logger.info("Not an EC2 state-change event, exiting")
        return {"status": "ignored"}

    # Only act when the instance is running
    state = event["detail"]["state"]
    if state != "running":
        logger.info("Instance state is %s, exiting", state)
        return {"status": "ignored"}

    instance_id = event["detail"]["instance-id"]
    logger.info("Instance ID: %s", instance_id)

    # Confirm the instance is registered with SSM
    response = ssm.describe_instance_information(
        InstanceInformationFilterList=[
            {"key": "InstanceIds", "valueSet": [instance_id]}
        ]
    )
    info_list = response.get("InstanceInformationList", [])
    if not info_list:
        logger.info("Instance is not registered with SSM, exiting")
        return {"status": "not_managed"}

    info = info_list[0]
    logger.info(
        "SSM status: %s | OS: %s %s (%s)",
        info["PingStatus"],
        info.get("PlatformName"),
        info.get("PlatformVersion"),
        info.get("PlatformType"),
    )

    # Only send the command if the SSM agent is online
    if info["PingStatus"] != "Online":
        logger.info("SSM agent is not online, exiting")
        return {"status": "offline"}

    result = ssm.send_command(
        InstanceIds=[instance_id],
        DocumentName=DOCUMENT_NAME,
        Comment="Automated agent installation triggered by Lambda",
    )
    command_id = result["Command"]["CommandId"]
    logger.info("Sent command %s to %s", command_id, instance_id)
    return {"status": "sent", "commandId": command_id}
