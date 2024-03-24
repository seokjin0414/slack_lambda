import boto3
import json
import logging
import os
import urllib.parse
import requests
import gspread

from oauth2client.service_account import ServiceAccountCredentials
from base64 import b64decode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

SLACK_CHANNEL = os.environ['slackChannel']
HOOK_URL = os.environ['hookUrl']
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    body = urllib.parse.parse_qs(event.get('body'))
    trigger_word = body.get('trigger_word', [None])[0]
    
    logger.info("#################################body")
    logger.info(body)
    logger.info("#################################trigger_word")
    logger.info(trigger_word)
    logger.info("#################################base_message")
    logger.info(create_slack_message(trigger_word))
    
    
    # # Authenticate with Google Sheets API
    # scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    # creds = ServiceAccountCredentials.from_json_keyfile_name('credential파일.json', scope)
    # client = gspread.authorize(creds)

    # # Open the spreadsheet and select the worksheet by name
    # spreadsheet = client.open('스프레드시트이름')
    # worksheet = spreadsheet.worksheet('시트이름')

    # # Update a cell's value
    # row_num = 5
    # col_num = 5
    # cell = worksheet.cell(row_num, col_num)
    # cell.value = 'New Value'
    # worksheet.update_cell(row_num, col_num, 'TestValue')
    
    
    
    # req = Request(HOOK_URL, json.dumps(slack_message).encode('utf-8'), {'Content-Type': 'application/json'})
    # try:
    #     response = urlopen(req)
    #     response.read()
    #     logger.info("Message posted to %s", slack_message['channel'])
    # except HTTPError as e:
    #     logger.error("Request failed: %d %s", e.code, e.reason)
    # except URLError as e:
    #     logger.error("Server connection failed: %s", e.reason)
    
def create_slack_message(trigger_word):
    base_message = {
        "channel": SLACK_CHANNEL,
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": ""
                }
            },
            {
                "type": "divider"
            }
        ]
    }
    return base_message
    
    