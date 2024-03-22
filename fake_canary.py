import boto3
import json
import logging
import os

from base64 import b64decode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

SLACK_CHANNEL = os.environ['slackChannel']
HOOK_URL = os.environ['hookUrl']
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info("Event: " + str(event))
    message = json.loads(event['Records'][0]['Sns']['Message'])
    logger.info("Message: " + str(message))

    alarm_name = message['AlarmName']
    alarm_description = message['AlarmDescription']
    old_state = message['OldStateValue']
    new_state = message['NewStateValue']
    reason = message['NewStateReason']
    change_time = message['StateChangeTime']
    metric_name = message['Trigger']['MetricName']
    namespace = message['Trigger']['Namespace']
    log_url = "https://ap-northeast-2.console.aws.amazon.com/cloudwatch/home?region=ap-northeast-2#alarmsV2:alarm/"
    form_name = alarm_name.replace('%', '$25')
    
    if "RDS" in alarm_name:
        watch_url = "https://ap-northeast-2.console.aws.amazon.com/cloudwatch/home?region=ap-northeast-2#home:dashboards/RDS"
        log_url = log_url + form_name
    elif "ECS" in alarm_name:
        watch_url = "https://ap-northeast-2.console.aws.amazon.com/cloudwatch/home?region=ap-northeast-2#home:dashboards/ECS:Cluster"
        log_url = log_url + form_name
    elif "EC2" in alarm_name:
        watch_url = "https://ap-northeast-2.console.aws.amazon.com/cloudwatch/home?region=ap-northeast-2#home:dashboards/EC2"
        log_url = log_url + form_name
    else:
        watch_url = "https://ap-northeast-2.console.aws.amazon.com/cloudwatch/home?region=ap-northeast-2#logsV2:log-groups"
    
    if "20" in alarm_name:
        color = "#edf511"
    elif "30" in alarm_name:
        color = "#f5b411"
    elif "50" in alarm_name:
        color = "#f59211"
    elif "70" in alarm_name:
        color = "#f54a11"
    elif "90" in alarm_name:
        color = "#f51111"
    else:
        color = "#8ef511"  
    
    slack_message = {
    "channel": SLACK_CHANNEL,
    "attachments": [{
        "color": color,
        "blocks": [
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": "*Metric:*\n" + metric_name
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*Type:*\n" + namespace
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*State:*\n" + new_state
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*Title:*\n" + alarm_name
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*Time:*\n" + change_time
                    }
                ]
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Cloud Watch :eyes:"
                        },
                        "style": "primary",
                        "url": watch_url
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "console Log :bookmark_tabs:"
                        },
                        "style": "primary",
                        "url": log_url
                    }
                ]
            }
        ]
    }],
    "blocks": [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": ":hatching_chick:짹짹\n*" + alarm_description + "*  짹짹짹!"
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": reason
                }
            ]
        }
    ]
    }

    req = Request(HOOK_URL, json.dumps(slack_message).encode('utf-8'), {'Content-Type': 'application/json'})
    try:
        response = urlopen(req)
        response.read()
        logger.info("Message posted to %s", slack_message['channel'])
    except HTTPError as e:
        logger.error("Request failed: %d %s", e.code, e.reason)
    except URLError as e:
        logger.error("Server connection failed: %s", e.reason)