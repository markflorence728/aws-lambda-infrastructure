import json
import requests


def lambda_handler(event, context):
    # TODO: sqs event handler
    print('sqs handler', event)

    records = event.get("Records")
    for record in records:
        body = record.get("body")
        body = json.loads(body)
        print("----------", body)

        resp = requests.get("https://api.ipify.org?format=json")
        print("----- MY IP ----", resp)

        # TODO: process body
