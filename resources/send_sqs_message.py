import json
import os
import boto3
import uuid
import requests


def lambda_handler(event, context):
    # TODO: send sqs message
    print('sqs handler', event.get("body"))

    sqs = boto3.client("sqs")
    sqs.send_message(
        QueueUrl=os.getenv("SQS_QUEUE_URL"),
        MessageBody=event.get("body"),
        MessageGroupId=str(uuid.uuid4()),
        MessageDeduplicationId=str(uuid.uuid4()),
    )

    resp = requests.get("https://api.ipify.org?format=json")
    print("----- MY IP ----", resp)

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "message ": "success"
        })
    }
